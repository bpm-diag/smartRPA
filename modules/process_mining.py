# ******************************
# Process mining techniques
# https://pm4py.fit.fraunhofer.de/documentation#discovery
# ******************************
import sys
sys.path.append('../')  # this way main file is visible from this file
import modules.eventAbstraction
import modules.logProcessing
import modules.mostFrequentRoutine
import os
from threading import Thread
import pandas
import utils.config
import utils.utils
import utils.utils
# from datetime import datetime, timedelta
from multiprocessing.queues import Queue
from deprecated.sphinx import deprecated

try:
    # constants
    from pm4py.util import constants
    from pm4py.util import xes_constants as xes_util
    # importer
    from pm4py.objects.log.adapters.pandas import csv_import_adapter
    from pm4py.objects.log.importer.xes import factory as xes_importer
    from pm4py.objects.log.exporter.xes import factory as xes_exporter
    from pm4py.objects.conversion.log import factory as conversion_factory
    # algorithms
    from pm4py.algo.discovery.alpha import factory as alpha_miner
    from pm4py.algo.discovery.heuristics import factory as heuristics_miner
    from pm4py.algo.discovery.dfg import factory as dfg_factory
    from pm4py.objects.conversion.dfg import factory as dfg_conv_factory
    from pm4py.algo.discovery.inductive import factory as inductive_miner
    # visualization
    from pm4py.visualization.petrinet import factory as vis_factory
    from pm4py.visualization.heuristics_net import factory as hn_vis_factory
    from pm4py.visualization.petrinet import factory as pn_vis_factory
    from pm4py.visualization.dfg import factory as dfg_vis_factory
    from pm4py.objects.log.util import sorting
    from pm4py.objects.petri.exporter import factory as pnml_factory
    # BPMN
    # from libraries.pm4pybpmn.visualization.bpmn import factory as bpmn_vis_factory
    # from libraries.pm4pybpmn.objects.conversion.petri_to_bpmn import factory as bpmn_converter
    # from libraries.pm4pybpmn.objects.bpmn.util import bpmn_diagram_layouter
except ImportError as e:
    print("[PROCESS MINING] Process mining analysis has been disabled because 'pm4py' module is not installed."
          "See https://github.com/bpm-diag/smartRPA#1-pm4py")
    print(e)


class ProcessMining:
    """
    Process Discovery component is initialised by the GUI when a calculation on a log file needs to be performed.
    """
    def __init__(self, filepath: list, status_queue: Queue, merged=False):
        """
        :param filepath: path of the csv file
        :param status_queue: queue to print messages on GUI
        :param merged: true if class has been called when merging multiple files
        """

        # queue to log messages to GUI
        self.status_queue = status_queue
        # true if class has been called when merging multiple files
        self.merged = merged
        # list of csv paths
        self.filepath = filepath
        # last csv in the list, use its name
        self.last_csv = self.filepath[-1]
        # name and extension of the last csv in the list
        self.filename = utils.utils.getFilename(self.last_csv).strip('_combined')
        self.file_extension = utils.utils.getFileExtension(self.last_csv)
        # path to save generated files, like /Users/marco/ComputerLogger/RPA/2020-03-06_12-50-28/
        self._create_directories()
        self.dataframe, self._log = modules.logProcessing.handle_log(self.status_queue,
                                                                     self.file_extension,
                                                                     self.filename,
                                                                     self.filepath,
                                                                     self.save_path,
                                                                     self.RPA_log_path)
        # self.dfg_path = os.path.join(self.discovery_path, f"{self.filename}_DFG_model.pdf")
        # self.bpmn_path = os.path.join(self.discovery_path, f"{self.filename}_BPMN.pdf")

        if utils.config.MyConfig.get_instance().enable_most_frequent_routine_analysis:
            print(f"[PROCESS MINING] Performing process discovery")
            # low level trace used for RPA generation
            self.mostFrequentCase = modules.mostFrequentRoutine.selectMostFrequentCase(self.dataframe, self.status_queue)

    def _create_directories(self):
        """
        Creates directories inside RPA folder where processed files will be saved.
        Directories include event_log, SW_robot, process_discovery.
        """
        # create directory if does not exists
        if self.merged:
            self.save_path = utils.utils.getRPADirectory(self.filename + '_merged')
        else:
            self.save_path = utils.utils.getRPADirectory(self.filename)
        utils.utils.createDirectory(self.save_path)

        self.RPA_log_path = os.path.join(self.save_path, utils.utils.EVENT_LOG_FOLDER)
        utils.utils.createDirectory(self.RPA_log_path)

        # self.discovery_path = os.path.join(self.save_path, utils.utils.PROCESS_DISCOVERY_FOLDER)
        # utils.utils.createDirectory(self.discovery_path)
        #
        # utils.utils.createDirectory(os.path.join(self.save_path, utils.utils.SW_ROBOT_FOLDER))
        # utils.utils.createDirectory(
        #     os.path.join(self.save_path, utils.utils.SW_ROBOT_FOLDER, utils.utils.UIPATH_FOLDER))

    def _create_image(self, gviz, img_name, verbose=False):
        """
        Create image file of the generated diagram (DFG,BPMN,Petr net)

        :param gviz: image file generated by pm4py
        :param img_name: name of the image to be saved
        :param verbose: display log while generating images
        """
        try:
            img_path = os.path.join(self.discovery_path, f'{self.filename}_{img_name}.pdf')
            if "alpha_miner" in img_name:
                vis_factory.save(gviz, img_path)
            elif "heuristic_miner" in img_name:
                hn_vis_factory.save(gviz, img_path)
            elif "petri_net" in img_name:
                pn_vis_factory.save(gviz, img_path)
            elif "DFG" in img_name:
                dfg_vis_factory.save(gviz, img_path)
            # elif "BPMN" in img_name:
            #     bpmn_vis_factory.save(gviz, img_path)

            if verbose:
                self.status_queue.put(f"[PROCESS MINING] Generated {img_name} in {img_path}")
        except PermissionError as e:
            print(f"[PROCESS MINING] Could not save image because of permission error: {e}")
            print(f"Trying to save image on desktop")
            img_path = os.path.join(utils.utils.DESKTOP, f'{self.filename}_{img_name}.pdf')
            if "alpha_miner" in img_name:
                vis_factory.save(gviz, img_path)
            elif "heuristic_miner" in img_name:
                hn_vis_factory.save(gviz, img_path)
            elif "petri_net" in img_name:
                pn_vis_factory.save(gviz, img_path)
            elif "DFG" in img_name:
                dfg_vis_factory.save(gviz, img_path)
            # elif "BPMN" in img_name:
            #     bpmn_vis_factory.save(gviz, img_path)
        except Exception as e:
            print(f"[PROCESS MINING] Could not save image: {e}")

    def create_alpha_miner(self):
        net, initial_marking, final_marking = alpha_miner.apply(self._log)
        gviz = vis_factory.apply(net, initial_marking, final_marking, parameters={"format": "pdf"})
        self._create_image(gviz, "alpha_miner")

    def create_heuristics_miner(self):
        heu_net = heuristics_miner.apply_heu(self._log, parameters={"dependency_thresh": 0.99})
        gviz = hn_vis_factory.apply(heu_net, parameters={"format": "pdf"})
        self._create_image(gviz, "heuristic_miner")

    def _getSourceTargetNodes(self, log=None, high_level=False):
        """
        Identifies the first and the last line in the event log, and mark them as source and target node.
        Used to color first and last node in the generated diagrams.

        :param log: low level event log
        :param high_level:
        :return: source and target nodes
        """
        if log and high_level:
            events_list = [event["customClassifier"] for trace in log for event in trace]
        else:
            events_list = self.dataframe['concept:name'].tolist()
            events_list = [value for value in events_list if value != 'enableBrowserExtension']
        source = events_list[0]
        target = events_list[-1]
        return source, target

    def _createImageParameters(self, log=None, high_level=False):
        """
        Create parameters for diagrams that needs to ben generated.
        Parameters include source and target nodes as well as file format (diagrams are saved as pdf).

        :param log: event log
        :param high_level: boolean, if true generate high level diagram
        """
        source, target = self._getSourceTargetNodes(log, high_level)
        parameters = {"start_activities": [source], "end_activities": [target], "format": "pdf"}
        return parameters

    # def mostFrequentPathInDFG(self):
    #     dfg = self._createCustomDFG()
    #     source, target = self._getSourceTargetNodes()
    #     graphPath = utils.graphPath.HandleGraph(dfg, source, target)
    #     graphPath.printPath()
    #     return graphPath.frequentPath()

    def _createDFG(self, log=None, parameters=None, high_level=False):
        """
        create df using dataframe with all traces

        :param log: low-level event log
        :param parameters: ooptional parameters to generate image
        """
        if high_level:
            df, log, parameters = modules.eventAbstraction.aggregateData(self.dataframe, remove_duplicates=False)
        else:
            if parameters is None:
                parameters = {}
            if log is None:
                log = self._log
        dfg = dfg_factory.apply(log, variant="frequency", parameters=parameters)
        return dfg, log

    @deprecated(version='1.2.0', reason="Not in use anymore")
    def save_dfg(self, name="DFG", high_level=False):
        """
        Save DFG to file

        :param name: optional name of dfg file
        :param high_level: generate high level dfg
        """
        dfg, log = self._createDFG()
        parameters = self._createImageParameters(log=log, high_level=high_level)
        if high_level:
            gviz = dfg_vis_factory.apply(dfg, log=log, variant="frequency", parameters=parameters)
        else:
            gviz = dfg_vis_factory.apply(dfg, log=self._log, variant="frequency", parameters=parameters)
        self._create_image(gviz, name)

    @deprecated(version='1.2.0', reason="Not in use anymore")
    def _create_petri_net(self, remove_duplicates=False):
        """
        Generate low level petri net

        :param remove_duplicates:
        :return: petri net
        """
        df, log, dfg_parameters = modules.eventAbstraction.aggregateData(remove_duplicates=remove_duplicates)
        dfg = self._createDFG(log, dfg_parameters)
        parameters = self._createImageParameters(log=log, high_level=True)
        # gviz = dfg_vis_factory.apply(dfg, log=self._log, variant="frequency", parameters=parameters)
        # self._create_image(gviz, "DFG")
        net, im, fm = dfg_conv_factory.apply(dfg, parameters=parameters)
        return net, im, fm

    @deprecated(version='1.2.0', reason="Not in use anymore")
    def save_petri_net(self, name):
        """
        Save low level petri net in pdf format from low level event log

        :param name: name of the generated petri net
        """
        net, im, fm = self._create_petri_net()
        gviz = pn_vis_factory.apply(net, im, fm, parameters={"format": "pdf"})
        self._create_image(gviz, name)

    # def _create_bpmn(self, df: pandas.DataFrame = None):
    #     df, log, parameters = modules.eventAbstraction.aggregateData(df, remove_duplicates=True)
    #     net, initial_marking, final_marking = heuristics_miner.apply(log, parameters=parameters)
    #     bpmn_graph, elements_correspondence, inv_elements_correspondence, el_corr_keys_map = bpmn_converter.apply(
    #         net, initial_marking, final_marking)
    #     return bpmn_graph
    #
    # def save_bpmn(self, df: pandas.DataFrame = None):
    #     bpmn_graph = self._create_bpmn(df)
    #     bpmn_figure = bpmn_vis_factory.apply(bpmn_graph, variant="frequency", parameters={"format": "pdf"})
    #     self._create_image(bpmn_figure, "BPMN")

    def highLevelDFG(self):
        """
        Create high level DFG of entire process
        """
        try:
            df, log, parameters = modules.eventAbstraction.aggregateData(self.dataframe, remove_duplicates=False)
            dfg = dfg_factory.apply(log, variant="frequency", parameters=parameters)
            gviz_parameters = self._createImageParameters(log=log, high_level=True)
            gviz = dfg_vis_factory.apply(dfg, log=log, variant="frequency", parameters=gviz_parameters)
            self._create_image(gviz, "DFG_model")
        except Exception as e:
            print(f"[PROCESS MINING] Could not create DFG: {e}")
            return False

    def highLevelPetriNet(self):
        """
        Create high level petri net of entire process
        """
        try:
            df, log, parameters = modules.eventAbstraction.aggregateData(self.dataframe, remove_duplicates=False)
            dfg = dfg_factory.apply(log, variant="frequency", parameters=parameters)
            gviz_parameters = self._createImageParameters(log=log, high_level=True)
            net, im, fm = dfg_conv_factory.apply(dfg, parameters=gviz_parameters)
            pnml_factory.apply(net, im, os.path.join(self.discovery_path, f'{self.filename}_petri_net.pnml'),
                               final_marking=fm)
        # gviz = pn_vis_factory.apply(net, im, fm, parameters=gviz_parameters)
        # self._create_image(gviz, "petri_net")
        except Exception as e:
            print(f"[PROCESS MINING] Could not create Petri Net: {e}")
            return False

    # def highLevelBPMN(self, df: pandas.DataFrame = None, name="BPMN", decisionPoints=False):
    #     try:
    #         # during decision points analysis, the final BPMN may have unordered timestamps which may lead
    #         # to an incorrect representation. Since the order of events is given by row index, timestamps
    #         # are reset to sequential number starting from the first timestamp and adding 1 second for each row,
    #         # thus obtaining a linear BPMN
    #         # if decisionPoints:
    #         #     try:
    #         #         first_timestamp = datetime.fromisoformat(str(df.reset_index()['time:timestamp'].iloc[0]))
    #         #         for i, (index, row) in enumerate(df.iterrows()):
    #         #             df.loc[index, 'time:timestamp'] = first_timestamp + timedelta(minutes=i+1, seconds=i+1)
    #         #         # debug_path = "/Users/marco/Desktop/decided.csv"
    #         #         # if os.path.exists(debug_path):
    #         #         #     os.remove(debug_path)
    #         #         # df.to_csv(debug_path)
    #         #     except Exception as e:
    #         #         print(f"[PROCESS MINING] Could not reorder timestamps for BPMN: {e}")
    #         #         pass
    #         if df is None:
    #             df = self.mostFrequentCase
    #         df, log, parameters = modules.eventAbstraction.aggregateData(df, remove_duplicates=True)
    #         net, initial_marking, final_marking = heuristics_miner.apply(log, parameters=parameters)
    #         bpmn_graph, elements_correspondence, inv_elements_correspondence, el_corr_keys_map = bpmn_converter.apply(
    #             net, initial_marking, final_marking)
    #         bpmn_figure = bpmn_vis_factory.apply(bpmn_graph, variant="frequency", parameters={"format": "pdf"})
    #         self._create_image(bpmn_figure, name)
    #         # try:
    #         #     if name == "BPMN_final":
    #         #         os.remove(os.path.join(self.discovery_path, f'{self.filename}_BPMN.pdf'))
    #         # except Exception as e:
    #         #     print(f"[PROCESS MINING] Could not delete old BPMN: {e}")
    #         #     pass
    #     except Exception as e:
    #         print(f"[PROCESS MINING] Could not create BPMN: {e}")
    #         return False

    # def createGraphs(self, df: pandas.DataFrame = None):
    #     self.save_bpmn(df)
    #     self.highLevelPetriNet()
