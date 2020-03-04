# ******************************
# Process mining techniques
# https://pm4py.fit.fraunhofer.de/documentation#discovery
# ******************************

from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.objects.conversion.log import factory as conversion_factory
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.algo.discovery.heuristics import factory as heuristics_miner
from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.visualization.petrinet import factory as vis_factory
from pm4py.visualization.heuristics_net import factory as hn_vis_factory
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.visualization.dfg import factory as dfg_vis_factory
import utils.utils


class ProcessMining:

    def __init__(self, filepath):
        self.filepath = filepath
        self.__log = self.__handle_log()

    def __handle_log(self):
        file_extension = utils.utils.getFileExtension(self.filepath)
        if file_extension == ".csv":
            dataframe = csv_import_adapter.import_dataframe_from_path(self.filepath, sep=",")
            log = conversion_factory.apply(dataframe)
            return log
        elif file_extension == ".xes":
            log = xes_importer.import_log(self.filepath)
            return log
        else:
            return "[PROCESS_MINING] Input file must be either .csv or .xes"

    def __create_image(self, gviz, img_name):
        file_extension = utils.utils.getFileExtension(self.filepath)
        img_path = self.filepath.replace(file_extension, f'_{img_name}.png')
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
        dfg = dfg_factory.apply(self.__log)
        gviz = dfg_vis_factory.apply(dfg, log=self.__log, variant="frequency")
        self.__create_image(gviz, "dfg")
