# ******************************
# Process mining techniques
# https://pm4py.fit.fraunhofer.de/documentation#discovery
# ******************************
try:
    import ntpath
except ModuleNotFoundError:
    import os
import os
from threading import Thread
import pandas
import utils.config
import utils.utils
from fuzzywuzzy import fuzz
from datetime import datetime

try:
    # constants
    from pm4py.util import constants
    from pm4py.util import xes_constants as xes_util
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
        self.filename = utils.utils.getFilename(self.last_csv).strip('_combined')
        self.file_extension = utils.utils.getFileExtension(self.last_csv)
        # path to save generated files, like /Users/marco/ComputerLogger/RPA/2020-03-06_12-50-28/
        self._create_directories()
        self._log = self._handle_log()
        self.mostFrequentCase = self.selectMostFrequentCase()


    def _create_directories(self):
        # create directory if does not exists
        self.save_path = utils.utils.getRPADirectory(self.filename)
        utils.utils.createDirectory(self.save_path)

        self.RPA_log_path = os.path.join(self.save_path, 'log')
        utils.utils.createDirectory(self.RPA_log_path)

        self.discovery_log_path = os.path.join(self.save_path, 'discovery')
        utils.utils.createDirectory(self.discovery_log_path)

    def _handle_log(self):

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

                try:
                    df.insert(2, 'lifecycle:transition', 'complete')
                except ValueError:
                    pass

                csv_to_combine.append(df)

            # dataframe of combined csv
            combined_csv = pandas.concat(csv_to_combine)

            # insert index for each row
            # combined_csv.insert(0, 'row_index', range(0, len(combined_csv)))

            self.dataframe = combined_csv

            # calculate csv path
            combined_csv_path = os.path.join(self.RPA_log_path, f'{self.filename}_combined.csv')

            # save dataframe as csv
            combined_csv.to_csv(combined_csv_path, index=False, encoding='utf-8-sig')

            # convert csv to xes
            log = conversion_factory.apply(combined_csv)

            # sort by timestamp
            log = sorting.sort_timestamp(log)

            # convert csv to xes
            xes_path = os.path.join(self.save_path, 'log', f'{self.filename}.xes')
            xes_exporter.export_log(log, xes_path)
            print(f"[PROCESS MINING] Generated XES file in {self.save_path}")

            return log

        elif self.file_extension == ".xes":
            log = xes_importer.import_log(self.filepath)
            return log
        else:
            return "[PROCESS_MINING] Input file must be either .csv or .xes"

    # return most frequent case in log in order to build RPA script
    def selectMostFrequentCase(self, flattened=False):
        df = self.dataframe
        if df.empty:
            return None

        df['browser_url_hostname'] = df['browser_url'].apply(lambda url: utils.utils.getHostname(url))
        df['flattened'] = df[
            ['concept:name', 'category', 'application', 'browser_url_hostname', "workbook", "cell_content",
             "cell_range", "cell_range_number", "slides"]].agg(','.join, axis=1)

        groupby_column = 'flattened' if flattened else 'concept:name'

        # Merge rows of each trace into one row, so the resulting dataframe has n rows where n is the number of traces
        # For example I get
        # ID  Trace   Action
        # 0   1   Create Fine, Send Fine
        # 1   2   Insert Fine Notification, Add penalty, Payment
        df1 = df.groupby('case:concept:name')[groupby_column].agg(', '.join).reset_index()

        # calculate variants, grouping the previous dataframe
        # concept:name  variants
        # typed, clickTextField, changeField, mouseClick...	    [0]
        # typed, changeField, mouseClick, formSubmit, li...	    [1]
        df2 = df1.groupby(groupby_column, sort=False)['case:concept:name'].agg(list).reset_index(name='variants')

        # get variants as list, each item represents a trace in the log
        # [[0], [1], [2], [3], [4,5]]
        variants = df2['variants'].tolist()

        # longest variant is selected because it's the most frequent
        longest_variants = max(variants, key=len)

        if len(longest_variants) == 1:
            # all the variants contain one case, need to check similarities

            # Check similarities between all the strings in the log and return the most frequent one
            def func(name, threshold=85):
                matches = df2.apply(lambda row: (fuzz.partial_ratio(row[groupby_column], name) >= threshold), axis=1)
                return [i for i, x in enumerate(matches) if x]
            df3 = df2.apply(lambda row: func(row[groupby_column]), axis=1)  # axis=1 means apply function to each row

            # In this example, elements 2 and 4 in variants list are similar to element 0 and so on
            # [[0, 2, 4], [1], [0, 2], [3], [0, 4]]
            match_id_list = df3.tolist()

            # longest variant is selected because it's the most frequent
            longest_variants = max(match_id_list, key=len)
            longest_variant = longest_variants[0]

            if len(longest_variants) == 1:
                print(f"[PROCESS MINING] There is 1 variant, selecting first case")
            else:
                print(f"[PROCESS MINING] There are {len(variants)} variants available, all with 1 case. "
                      f"Variants {list(map(lambda x: x+1, longest_variants))} are similar, "
                      f"selecting the first case of variant {longest_variant+1}")
        else:
            # there is a frequent variant, pick first case
            print(
                f"[PROCESS MINING] There are {len(variants)} variants available, "
                f"the most frequent one contains {len(longest_variants)} cases, selecting the first case")
            longest_variant = longest_variants[0]

        # return rows corresponding to selected trace
        case = df.loc[df['case:concept:name'] == longest_variant]

        return case

    def _create_image(self, gviz, img_name, verbose=False):
        img_path = os.path.join(self.save_path, self.discovery_log_path, f'{self.filename}_{img_name}.pdf')
        if img_name == "alpha_miner":
            vis_factory.save(gviz, img_path)
        elif img_name == "heuristic_miner":
            hn_vis_factory.save(gviz, img_path)
        elif "petri_net" in img_name:
            pn_vis_factory.save(gviz, img_path)
        elif img_name.lower() == "DFG":
            dfg_vis_factory.save(gviz, img_path)
        elif "BPMN" in img_name:
            bpmn_vis_factory.save(gviz, img_path)

        if verbose:
            print(f"[PROCESS MINING] Generated {img_name} in {img_path}")

    def create_alpha_miner(self):
        net, initial_marking, final_marking = alpha_miner.apply(self._log)
        gviz = vis_factory.apply(net, initial_marking, final_marking, parameters={"format": "pdf"})
        self._create_image(gviz, "alpha_miner")

    def create_heuristics_miner(self):
        heu_net = heuristics_miner.apply_heu(self._log, parameters={"dependency_thresh": 0.99})
        gviz = hn_vis_factory.apply(heu_net, parameters={"format": "pdf"})
        self._create_image(gviz, "heuristic_miner")

    def _getSourceTargetNodes(self, log=None, high_level=False):
        # source and target nodes in dfg graph are the first and last line in log file
        if log and high_level:
            events_list = [event["customClassifier"] for trace in log for event in trace]
        else:
            events_list = self.dataframe['concept:name'].tolist()
            events_list = [value for value in events_list if value != 'enableBrowserExtension']
        source = events_list[0]
        target = events_list[-1]
        return source, target

    def _createImageParameters(self, log=None, high_level=False):
        source, target = self._getSourceTargetNodes(log, high_level)
        parameters = {"start_activities": [source], "end_activities": [target], "format": "pdf"}
        return parameters

    def _createDFG(self, log=None, parameters=None):
        if parameters is None:
            parameters = {}
        if log is None:
            log = self._log
        dfg = dfg_factory.apply(log, variant="frequency", parameters=parameters)
        return dfg

    # def _createCustomDFG(self):
    #     window = 1
    #     for trace in self._log:
    #         for event in trace:
    #             event["customClassifier"] = f'{event["concept:name"]}-{event["row_index"]}'
    #
    #     parameters = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "customClassifier"}
    #     if constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
    #         parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    #     activity_key = parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    #     # dfgs = map((lambda t: [(t[i - window][activity_key], t[i][activity_key]) for i in range(window, len(t))]), log)
    #     dfgs = list()
    #     for t in self._log:
    #         for i in range(window, len(t)):
    #             dfgs.append([(t[i - window][activity_key], t[i][activity_key])])
    #     l_id = list()
    #     for lista in dfgs:
    #         for dfg in lista:
    #             l_id.append(dfg)
    #     counter_id = Counter(l_id)
    #     return counter_id
    #
    # def mostFrequentPathInDFG(self):
    #     dfg = self._createCustomDFG()
    #     source, target = self._getSourceTargetNodes()
    #     graphPath = utils.graphPath.HandleGraph(dfg, source, target)
    #     graphPath.printPath()
    #     return graphPath.frequentPath()
    #

    def save_dfg(self):
        dfg = self._createDFG()
        parameters = self._createImageParameters()
        gviz = dfg_vis_factory.apply(dfg, log=self._log, variant="frequency", parameters=parameters)
        self._create_image(gviz, "DFG")

    @staticmethod
    def _getHighLevelEvent(row):

        e = row["concept:name"]
        url = utils.utils.getHostname(row['browser_url'])
        app = row['application']
        cb = utils.utils.removeWhitespaces(row['clipboard_content'])

        # general
        if e in ["copy", "cut", "paste"]:  # take only first 15 characters of clipboard
            if len(cb) > 20:
                return f"Copy and Paste: {cb[:20]}..."
            if len(cb) == 0:
                return f"Copy and Paste"
            else:
                return f"Copy and Paste: {cb}"

        # browser
        elif e in ["clickButton", "clickTextField", "doubleClick", "clickTextField", "mouseClick", "clickCheckboxButton"]:
            if row['tag_type'] == 'submit':
                return f"[{app}] Submit {row['tag_category'].lower()} on {url}"
            else:
                return f"[{app}] Click {row['tag_type']} {row['tag_category'].lower()} '{row['tag_name']}' on {url}"
        elif e in ["clickLink"]:
            return f"[{app}] Click '{row['tag_innerText']}' on {url}"
        elif e in ["link", "reload", "generated", "urlHashChange", ]:
                return f"[{app}] Navigate to {url}"
        elif e in ["submit", "formSubmit", "selectOptions"]:
            return "Submit"
        elif e in ["selectTab", "moveTab", "zoomTab"]:
            return "Browser Tab"
        elif e in ["newTab"]:
            return f"[{app}] Open tab"
        elif e in ["closeTab"]:
            return f"[{app}] Close tab"
        elif e in ["newWindow"]:
            return f"[{app}] Open window"
        elif e in ["closeWindow"]:
            return f"[{app}] Close window"
        elif e in ["typed", "selectText", "contextMenu"]:
            return f"[{app}] Edit {row['tag_category']} on {url}"
        elif e in ["changeField"]:
            return f"[{app}] Write '{row['tag_value']}' in {row['tag_type']} {row['tag_category'].lower()} on {url}"

        # system
        elif e in ["itemSelected", "deleted", "moved", "created", "Mount", "Unmount", "openFile", "openFolder"]:
            path = row['event_src_path']
            name, extension = ntpath.splitext(path)
            name = ntpath.basename(path)
            if extension:
                return f"[{app}] Edit file '{name}'"
            else:
                return f"[{app}] Edit folder '{name}'"
        elif e in ["programOpen", "programClose"]:
            return f"Use program '{app.lower()}'"

        # excel
        elif e in ["newWorkbook", "openWorkbook", "activateWorkbook"]:
            return f"[Excel] Open {row['workbook']}"
        elif e in ["editCellSheet", "getCell", "getRange"]:
            if row['current_worksheet'] != '':
                # return f"[Excel] Edit Cell {row['cell_range']} on {row['current_worksheet']} with value '{row['cell_content']}'"
                return f"[Excel] Edit Cell on {row['current_worksheet']}"
            else:
                return f"[Excel] Edit Cell"
        elif e in ["addWorksheet", "deselectWorksheet", "selectWorksheet"]:
            return f"[Excel] Select {row['current_worksheet']}"

        # powerpoint
        elif e in ["newPresentation"]:
            return f"[PowerPoint] Open {row['title']}"
        elif e in ["newPresentationSlide", "savePresentation", "SlideSelectionChanged"]:
            return f"[PowerPoint] Edit presentation"

        # word
        elif e in ["newDocument"]:
            return f"[Word] Open document"
        elif e in ["changeDocument"]:
            return f"[Word] Edit document"

        else:
            return e

    def _aggregateData(self, remove_duplicates=False):

        df = self.mostFrequentCase

        # filter rows
        df = df[~df.browser_url.str.contains('chrome-extension://')]
        df = df[~df.eventQual.str.contains('clientRedirect')]
        df = df[~df.eventQual.str.contains('serverRedirect')]
        df = df[df['clipboard_content'].str.strip() == '']
        rows_to_remove = ["activateWindow", "deactivateWindow", "openWindow", "newWindow", "closeWindow",
                          "selectTab", "moveTab", "zoomTab", "typed", "mouseClick", "submit", "formSubmit",
                          "installBrowserExtension", "enableBrowserExtension", "disableBrowserExtension",
                          "resizeWindow", "logonComplete", "startPage", "doubleClickCellWithValue",
                          "doubleClickEmptyCell", "rightClickCellWithValue", "rightClickEmptyCell", "afterCalculate",
                          "programOpen", "programClose", "closePresentation", "SlideSelectionChanged", "closeWorkbook",
                          "deactivateWorkbook"]
        df = df[~df['concept:name'].isin(rows_to_remove)]

        # convert each row of events to high level
        df['customClassifier'] = df.apply(lambda row: self._getHighLevelEvent(row), axis=1)

        # check duplicates
        # print(df[df['customClassifier'].duplicated() == True])
        # remove duplicates
        if remove_duplicates:
            df = df.drop_duplicates(subset='customClassifier', keep='first')

        log = conversion_factory.apply(df)
        dfg_parameters = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "customClassifier"}
        return log, dfg_parameters

    def _create_petri_net(self, remove_duplicates):
        log, dfg_parameters = self._aggregateData(remove_duplicates)
        dfg = self._createDFG(log, dfg_parameters)
        parameters = self._createImageParameters(log=log, high_level=True)
        net, im, fm = dfg_conv_factory.apply(dfg, parameters=parameters)
        return net, im, fm

    def save_petri_net(self, name, only_most_frequent=True):
        net, im, fm = self._create_petri_net()
        gviz = pn_vis_factory.apply(net, im, fm, parameters={"format": "pdf"})
        self._create_image(gviz, name)

    def _create_bpmn(self, remove_duplicates):

        # petri net
        net, initial_marking, final_marking = self._create_petri_net(remove_duplicates)
        gviz = pn_vis_factory.apply(net, initial_marking, final_marking, parameters={"format": "pdf"})
        self._create_image(gviz, "petri_net")

        bpmn_graph, elements_correspondence, inv_elements_correspondence, el_corr_keys_map = bpmn_converter.apply(
            net, initial_marking, final_marking)

        return bpmn_graph

    def save_bpmn(self, remove_duplicates: bool):
        bpmn_graph = self._create_bpmn(remove_duplicates)
        bpmn_figure = bpmn_vis_factory.apply(bpmn_graph, variant="frequency", parameters={"format": "pdf"})
        if remove_duplicates:
            self._create_image(bpmn_figure, "BPMN_without_duplicates")
        else:
            self._create_image(bpmn_figure, "BPMN_with_duplicates")

    def createGraphs(self):
        self.save_dfg()
        self.save_bpmn(remove_duplicates=True)  # includes petri net
        self.save_bpmn(remove_duplicates=False)  # includes petri net
        print(f"[PROCESS MINING] Generated DFG, Petri Net and BPMN in {self.discovery_log_path}")
