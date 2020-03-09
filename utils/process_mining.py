# ******************************
# Process mining techniques
# https://pm4py.fit.fraunhofer.de/documentation#discovery
# ******************************
import os
from threading import Thread

import pandas

import utils.config
import utils.utils

try:
    from pm4py.objects.log.adapters.pandas import csv_import_adapter
    from pm4py.objects.conversion.log import factory as conversion_factory
    from pm4py.objects.log.importer.xes import factory as xes_importer
    from pm4py.objects.log.exporter.xes import factory as xes_exporter
    from pm4py.algo.discovery.alpha import factory as alpha_miner
    from pm4py.algo.discovery.heuristics import factory as heuristics_miner
    from pm4py.algo.discovery.dfg import factory as dfg_factory
    from pm4py.visualization.petrinet import factory as vis_factory
    from pm4py.visualization.heuristics_net import factory as hn_vis_factory
    from pm4py.visualization.petrinet import factory as pn_vis_factory
    from pm4py.visualization.dfg import factory as dfg_vis_factory
    from pm4py.objects.log.util import sorting
except ImportError as e:
    print("[PROCESS MINING] Process mining analysis has been disabled because 'pm4py' module is not installed."
          "See https://github.com/marco2012/ComputerLogger#PM4PY")


class ProcessMining:

    def __init__(self, filepath: list):
        # list of csv paths
        self.filepath = filepath
        # last csv in the list, use its name
        self.last_csv = self.filepath[-1]
        # name and extension of the last csv in the list
        self.filename = utils.utils.getFilename(self.last_csv)
        self.file_extension = utils.utils.getFileExtension(self.last_csv)
        # path to save generated files, like /Users/marco/ComputerLogger/RPA/2020-03-06_12-50-28/
        self.save_path = os.path.join(utils.config.MyConfig().main_directory, 'RPA', self.filename)
        self.__log = self.__handle_log()

    def run(self):
        t0 = Thread(target=self.create_alpha_miner)
        t1 = Thread(target=self.create_heuristics_miner)
        t2 = Thread(target=self.create_dfg)
        t3 = Thread(target=self.create_petri_net)
        # t0.start()
        # t1.start()
        t2.start()
        # t3.start()
        # t0.join()
        # t1.join()
        t2.join()
        # t3.join()
        print(f"[PROCESS MINING] Generated files in {self.last_csv.strip('.csv')}")

    def __handle_log(self):
        if self.file_extension == ".csv":

            # create directory if does not exists
            utils.utils.createDirectory(self.save_path)

            # combine multiple csv into one and then export it to xes
            csv_to_combine = list()
            for i, csv_path in enumerate(self.filepath):
                # load csv in pandas dataframe, rename columns to match xes standard and replace null values with
                # empty string
                df = pandas.read_csv(csv_path, encoding='utf-8-sig') \
                    .rename(columns={'event_type': 'concept:name',
                                     'timestamp': 'time:timestamp',
                                     'user': 'org:resource'}) \
                    .fillna('')
                # Each csv should have a separate case ID, so I insert a column to the left of each csv and assign
                # number i. When I convert the combined csv to xes, all the rows with the same number will belong to a
                # single trace, so I will have i traces.
                df.insert(0, 'case:concept:name', i)
                csv_to_combine.append(df)

            combined_csv = pandas.concat(csv_to_combine)
            combined_csv_path = os.path.join(self.save_path, f'{self.filename}_combined.csv')
            combined_csv.to_csv(combined_csv_path, index=False, encoding='utf-8-sig')

            log = conversion_factory.apply(combined_csv)
            log = sorting.sort_timestamp(log)

            # convert csv to xes
            print(f"[PROCESS MINING] Generating XES file from {self.last_csv}")
            xes_path = os.path.join(self.save_path,
                                    f'{self.filename}.xes')  # self.last_csv.replace(self.file_extension, f'_pm4py.xes')
            xes_exporter.export_log(log, xes_path)

            return log
        elif self.file_extension == ".xes":
            log = xes_importer.import_log(self.filepath)
            return log
        else:
            return "[PROCESS_MINING] Input file must be either .csv or .xes"

    def __create_image(self, gviz, img_name):
        img_path = os.path.join(self.save_path, f'{self.filename}_{img_name}.jpg')
        if img_name == "alpha_miner":
            vis_factory.save(gviz, img_path)
        elif img_name == "heuristic_miner":
            hn_vis_factory.save(gviz, img_path)
        elif img_name == "petri_net":
            pn_vis_factory.save(gviz, img_path)
        elif img_name == "dfg":
            dfg_vis_factory.save(gviz, img_path)

    def create_alpha_miner(self):
        net, initial_marking, final_marking = alpha_miner.apply(self.__log)
        gviz = vis_factory.apply(net, initial_marking, final_marking)
        self.__create_image(gviz, "alpha_miner")

    def create_heuristics_miner(self):
        heu_net = heuristics_miner.apply_heu(self.__log, parameters={"dependency_thresh": 0.99})
        gviz = hn_vis_factory.apply(heu_net)
        self.__create_image(gviz, "heuristic_miner")

    def create_petri_net(self):
        net, im, fm = heuristics_miner.apply(self.__log, parameters={"dependency_thresh": 0.99})
        gviz = pn_vis_factory.apply(net, im, fm)
        self.__create_image(gviz, "petri_net")

    def create_dfg(self):
        # calculate dfg
        dfg = dfg_factory.apply(self.__log, variant="frequency")

        # write nodes to file
        with open(os.path.join(self.save_path, 'dfg_nodes.py'), 'w', encoding='utf-8-sig') as file:
            file.write("# This file contains the nodes of dfg image\n")
            file.write(str(dfg))

        # create graph
        gviz = dfg_vis_factory.apply(dfg, log=self.__log, variant="frequency")
        self.__create_image(gviz, "dfg")
