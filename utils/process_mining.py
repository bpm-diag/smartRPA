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
    from pm4py.util import constants
    # importer
    from pm4py.objects.log.adapters.pandas import csv_import_adapter
    from pm4py.objects.log.importer.xes import factory as xes_importer
    from pm4py.objects.log.exporter.xes import factory as xes_exporter
    from pm4py.objects.conversion.log import factory as conversion_factory
    from pm4py.objects.petri.exporter import pnml as pnml_exporter
    # algorithms
    from pm4py.algo.discovery.alpha import factory as alpha_miner
    from pm4py.algo.discovery.heuristics import factory as heuristics_miner
    from pm4py.algo.discovery.dfg import factory as dfg_factory
    from pm4py.objects.conversion.dfg import factory as dfg_conv_factory
    # visualization
    from pm4py.visualization.petrinet import factory as vis_factory
    from pm4py.visualization.heuristics_net import factory as hn_vis_factory
    from pm4py.visualization.petrinet import factory as pn_vis_factory
    from pm4py.visualization.dfg import factory as dfg_vis_factory
    from pm4py.objects.log.util import sorting
    from pm4pybpmn.visualization.bpmn import factory as bpmn_vis_factory
    # BPMN
    from pm4pybpmn.objects.conversion.petri_to_bpmn import factory as bpmn_converter
    from pm4pybpmn.objects.bpmn.util import bpmn_diagram_layouter
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
        self.save_path = utils.utils.getRPADirectory(self.filename)
        self.__log = self._handle_log()

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

    def _handle_log(self):
        # create directory if does not exists
        utils.utils.createDirectory(self.save_path)

        if self.file_extension == ".csv":

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
                try:  # insert this column to create a unique trace for each csv
                    df.insert(0, 'case:concept:name', i)
                except ValueError:  # column already present
                    pass

                try:  # insert this column to create a unique trace for each csv
                    df.insert(1, 'case:creator', 'CSV2XES by marco2012')
                except ValueError:  # column already present
                    pass

                csv_to_combine.append(df)

            # dataframe of combined csv
            combined_csv = pandas.concat(csv_to_combine)

            # insert index for each row
            combined_csv.insert(0, 'row_index', range(0, len(combined_csv)))

            self.dataframe = combined_csv

            # calculate csv path
            combined_csv_path = os.path.join(self.save_path, f'{self.filename}_combined.csv')

            # save dataframe as csv
            combined_csv.to_csv(combined_csv_path, index=False, encoding='utf-8-sig')

            # convert csv to xes
            log = conversion_factory.apply(combined_csv)

            # sort by timestamp
            log = sorting.sort_timestamp(log)

            # convert csv to xes
            print(f"[PROCESS MINING] Generating XES file in {self.save_path}")
            xes_path = os.path.join(self.save_path, f'{self.filename}.xes')
            xes_exporter.export_log(log, xes_path)

            return log

        elif self.file_extension == ".xes":
            log = xes_importer.import_log(self.filepath)
            return log
        else:
            return "[PROCESS_MINING] Input file must be either .csv or .xes"

    def _create_image(self, gviz, img_name):
        img_path = os.path.join(self.save_path, f'{self.filename}_{img_name}.jpg')
        if img_name == "alpha_miner":
            vis_factory.save(gviz, img_path)
        elif img_name == "heuristic_miner":
            hn_vis_factory.save(gviz, img_path)
        elif img_name == "petri_net":
            pn_vis_factory.save(gviz, img_path)
        elif img_name == "dfg":
            dfg_vis_factory.save(gviz, img_path)
        elif img_name == "bpmn":
            bpmn_vis_factory.save(gviz, img_path)
        print(f"[PROCESS MINING] Generated {img_name} in {img_path}")

    def create_alpha_miner(self):
        net, initial_marking, final_marking = alpha_miner.apply(self.__log)
        gviz = vis_factory.apply(net, initial_marking, final_marking, parameters={"format": "jpg"})
        self._create_image(gviz, "alpha_miner")

    def create_heuristics_miner(self):
        heu_net = heuristics_miner.apply_heu(self.__log, parameters={"dependency_thresh": 0.99})
        gviz = hn_vis_factory.apply(heu_net, parameters={"format": "jpg"})
        self._create_image(gviz, "heuristic_miner")

    def create_dfg(self, log=None, parameters={}):
        # add custom columns to dfg

        # for trace in self.__log:
        #     for event in trace:
        #         event["customClassifier"] = f'{event["row_index"]}-{event["concept:name"]}'
                # try:
                #     event["customClassifier"] = f'{event["concept:name"]}-{event["browser_url"]}-{event["tag_value"]}'
                # except KeyError:
                #     event["customClassifier"] = event["concept:name"]

        # parameters = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "customClassifier"}
        # calculate dfg
        if log is None:
            log = self.__log
        dfg = dfg_factory.apply(log, variant="frequency", parameters=parameters)
        return dfg

    def _getSourceTargetNodes(self):
        # source and target nodes in dfg graph are the first and last line in log file
        events_list = self.dataframe['concept:name'].tolist()
        events_list = [value for value in events_list if value != 'enableBrowserExtension']
        source = events_list[0]
        target = events_list[-1]
        return source, target

    def _createImageParameters(self):
        source, target = self._getSourceTargetNodes()
        parameters = {"start_activities": [source], "end_activities": [target], "format": "jpg"}
        return parameters

    def save_dfg(self):
        dfg = self.create_dfg()
        parameters = self._createImageParameters()
        gviz = dfg_vis_factory.apply(dfg, log=self.__log, variant="frequency", parameters=parameters)
        self._create_image(gviz, "dfg")

    def mostFrequentPathInDFG(self):
        dfg = self.create_dfg()
        source, target = self._getSourceTargetNodes()
        graphPath = utils.graphPath.HandleGraph(dfg, source, target)
        graphPath.printPath()
        return graphPath.frequentPath()

    def create_petri_net(self, dfg=None):
        if dfg is None:
            dfg = self.create_dfg()
        net, im, fm = dfg_conv_factory.apply(dfg)
        return net, im, fm

    def save_petri_net(self):
        net, im, fm = self.create_petri_net()
        parameters = self._createImageParameters()
        gviz = pn_vis_factory.apply(net, im, fm, parameters=parameters)
        self._create_image(gviz, "petri_net")

    @staticmethod
    def _getHighLevelEvent(e):
        if e in ["copy", "cut", "paste"]:
            return "Copy and Paste"
        elif e in ["clickLink", "mouseClick", "clickButton", "clickTextField", "doubleClick"]:
            return "Click"
        elif e in ["submit", "formSubmit", "selectOptions"]:
            return "Submit"
        elif e in ["newTab", "selectTab", "closeTab", "clickTextField"]:
            return "BrowserTab"
        elif e in ["generated", "urlHashChange", "typed", "selectText", "changeField", "reload"]:
            return "Edit"
        elif e in ["activateWindow", "closeWindow", "deactivateWindow", "openWindow"]:
            return "WindowAction"
        elif e in ["deactivateWindow", "deselectWorksheet", "newWorkbook", "openWorkbook", "saveWorkbook"]:
            return "WorkbookAction"
        elif e in ["doubleClickCellWithValue", "doubleClickEmptyCell", "rightClickCellWithValue", "editCellSheet", "getCell", "getRange"]:
            return "EditCellExcell"
        else:
            return e

    def _aggregateDataForBpmn(self):
        # remove duplicate events in dataframe
        df = self.dataframe.drop_duplicates(subset="concept:name", keep='first')
        log = conversion_factory.apply(df)

        for trace in log:
            for event in trace:
                e = event["concept:name"]
                event["customClassifier"] = self._getHighLevelEvent(e)

        # with open("/Users/marco/Desktop/log.py", 'w') as f:
        #     f.write(str(log))

        dfg_parameters = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "customClassifier"}
        return log, dfg_parameters

    def _create_bpmn(self):

        log, dfg_parameters = self._aggregateDataForBpmn()

        dfg = self.create_dfg(log, dfg_parameters)
        # remove same pairs in dfg
        for w in list(dfg):
            if w[0] == w[1]:
                del (dfg[w])

        net, initial_marking, final_marking = self.create_petri_net(dfg)

        gviz = pn_vis_factory.apply(net, initial_marking, final_marking, parameters={"format": "jpg"})
        self._create_image(gviz, "petri_net")

        bpmn_graph, elements_correspondence, inv_elements_correspondence, el_corr_keys_map = bpmn_converter.apply(
            net, initial_marking, final_marking)

        try:
            bpmn_graph = bpmn_diagram_layouter.apply(bpmn_graph)
        except TypeError:
            pass

        return bpmn_graph, log

    def save_bpmn(self):
        bpmn_graph, log = self._create_bpmn()
        bpmn_figure = bpmn_vis_factory.apply(bpmn_graph, variant="frequency", parameters={"format": "jpg"})
        self._create_image(bpmn_figure, "bpmn")
