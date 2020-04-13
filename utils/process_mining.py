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
from multiprocessing.queues import Queue

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
    from pm4pybpmn.visualization.bpmn import factory as bpmn_vis_factory
    # BPMN
    from pm4pybpmn.objects.conversion.petri_to_bpmn import factory as bpmn_converter
    from pm4pybpmn.objects.bpmn.util import bpmn_diagram_layouter
except ImportError as e:
    print("[PROCESS MINING] Process mining analysis has been disabled because 'pm4py' module is not installed."
          "See https://github.com/marco2012/ComputerLogger#PM4PY")


class ProcessMining:

    def __init__(self, filepath: list, status_queue: Queue, merged=False):

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
        self._log = self._handle_log()

        if utils.config.MyConfig.get_instance().perform_process_discovery:
            print(f"[PROCESS MINING] Performing process discovery")
            # low level trace used for rpa generation
            self.mostFrequentCase = self.selectMostFrequentCase()

    def _create_directories(self):
        # create directory if does not exists
        if self.merged:
            self.save_path = utils.utils.getRPADirectory(self.filename + '_merged')
        else:
            self.save_path = utils.utils.getRPADirectory(self.filename)

        utils.utils.createDirectory(self.save_path)

        self.RPA_log_path = os.path.join(self.save_path, 'log')
        utils.utils.createDirectory(self.RPA_log_path)

        self.discovery_path = os.path.join(self.save_path, 'discovery')
        utils.utils.createDirectory(self.discovery_path)

    def _handle_log(self):

        if self.file_extension == ".csv":

            def createCaseID(ts):
                return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S:%f").strftime('%m%d%H%M%S%f')#[:-3]

            # combine multiple csv into one and then export it to xes
            csv_to_combine = list()
            for i, csv_path in enumerate(self.filepath):
                # load csv in pandas dataframe,
                # rename columns to match xes standard,
                # remove rows that don't have timestamp
                # replace null values with empty string
                # sort by timestamp
                df = pandas.read_csv(csv_path, encoding='utf-8-sig') \
                    .rename(columns={'event_type': 'concept:name',
                                     'timestamp': 'time:timestamp',
                                     'user': 'org:resource'}) \
                    .dropna(subset=["time:timestamp"])\
                    .fillna('')\
                    .sort_values(by='time:timestamp')
                # Each csv should have a separate case ID, so I insert a column to the left of each csv and assign
                # number i. When I convert the combined csv to xes, all the rows with the same number will belong to a
                # single trace, so I will have i traces.

                try:  # insert this column to create a unique trace for each csv
                    df.insert(0, 'case:concept:name', createCaseID(df['time:timestamp'][0]))
                except ValueError:  # column already present, replace case id values so they are sequential
                    pass

                try:  # insert this column to create a unique trace for each csv
                    df.insert(1, 'case:creator', 'CSV2XES by marco2012')
                except ValueError:  # column already present
                    pass

                try:
                    df.insert(2, 'lifecycle:transition', 'complete')
                except ValueError:  # column already present
                    pass

                csv_to_combine.append(df)

            # dataframe of combined csv, sort by timestamp
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
            # log = sorting.sort_timestamp(log)

            # convert csv to xes
            xes_path = os.path.join(self.save_path, 'log', f'{self.filename}.xes')
            xes_exporter.export_log(log, xes_path)
            self.status_queue.put(f"[PROCESS MINING] Working directory is {self.save_path}")
            self.status_queue.put(f"[PROCESS MINING] Generated XES file")

            return log

        elif self.file_extension == ".xes":
            log = xes_importer.import_log(self.filepath)
            return log
        else:
            self.status_queue.put("[PROCESS_MINING] Input file must be either .csv or .xes")
            return False

    # return most frequent case in log in order to build RPA script
    def selectMostFrequentCaseWithoutDuration(self, flattened=False):
        df = self.dataframe
        if df.empty:
            return None

        # flattening
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
            def func(name, threshold=90):
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
                self.status_queue.put(f"[PROCESS MINING] There is 1 variant, selecting first case")
            else:
                self.status_queue.put(
                    f"[PROCESS MINING] There are {len(variants)} variants available, all with 1 case. "
                    f"Variants {list(map(lambda x: x + 1, longest_variants))} are similar, "
                    f"selecting the first case of variant {longest_variant + 1}")
        else:
            # there is a frequent variant, pick first case
            self.status_queue.put(
                f"[PROCESS MINING] There are {len(variants)} variants available, "
                f"the most frequent one contains {len(longest_variants)} cases, selecting the first case")
            longest_variant = longest_variants[0]

        # return rows corresponding to selected trace
        case = df.loc[df['case:concept:name'] == longest_variant]

        return case

    def selectMostFrequentCase(self, flattened=False, threshold=85):
        df = self.dataframe
        if df.empty:
            return None

        # flattening
        # df['browser_url_hostname'] = df['browser_url'].apply(lambda url: utils.utils.getHostname(url))
        df['flattened'] = df[
            ['concept:name', 'category', 'application', "workbook"]].agg(','.join, axis=1)
        groupby_column = 'flattened' if flattened else 'concept:name'

        # Merge rows of each trace into one row, so the resulting dataframe has n rows where n is the number of traces
        # For example I get
        # case:concept:name     concept:name                            timestamp
        # 0                     Create Fine, Send Fine                  2020-03-20 17:09:06:308, 2020-03-20 17:09:06:3
        # 1                     Insert Fine Notification, Add penalty   2020-03-20 17:10:28:348, 2020-03-20 17:10:28:2
        df1 = df.groupby(['case:concept:name'])[[groupby_column, 'time:timestamp']].agg(', '.join).reset_index()

        # calculate duration in seconds for each row of dataframe
        # I get a new a new column like
        # duration
        # 25.123
        # 26.342
        # 22.324
        def getDuration(time):
            timestamps = time.split(',')
            start = datetime.strptime(timestamps[0].strip(), "%Y-%m-%d %H:%M:%S:%f")
            finish = datetime.strptime(timestamps[-1].strip(), "%Y-%m-%d %H:%M:%S:%f")
            duration = finish - start
            return duration.total_seconds()

        df1['duration'] = df1['time:timestamp'].apply(lambda time: getDuration(time))

        # calculate variants, grouping the previous dataframe if there are equal rows
        # concept:name                                          variants   duration
        # typed, clickTextField, changeField, mouseClick...	    [0, 1]    [25.123, 26.342]
        # typed, changeField, mouseClick, formSubmit, li...	    [2]       [22.324]
        df2 = df1.groupby([groupby_column], sort=False)[['case:concept:name', 'duration']].agg(
            list).reset_index().rename(columns={"case:concept:name": "variants"})

        # return the concept:case:id of the variant with shortest duration
        # not used when all traces are different
        def _findVariantWithShortestDuration(df1: pandas.DataFrame, most_frequent_variants):
            #  there are at least 2 equal variants, most_frequent_variants is an array like [0,1]
            # take only the most frequent rows in dataframe, like [0,1]
            most_frequent_variants_df = df1.iloc[most_frequent_variants, :]
            # find the row with the smallest duration
            durations = most_frequent_variants_df['duration'].tolist()
            # return the index of the row with the smallest duration
            min_duration_trace = most_frequent_variants_df.loc[most_frequent_variants_df['duration'] == min(durations)][
                'case:concept:name'].tolist()[0]
            return min_duration_trace, min(durations)

        # return case:concept:name of most frequent traces
        def _findMostFrequentTraces(df2: pandas.DataFrame, most_frequent_variants):
            try:
                # list composed by the first column (case:concept:name) of the most frequent rows
                # (selected by row index, because most_frequent_variants is a list of indices)
                most_frequent_traces = df2.iloc[most_frequent_variants, 1].values.tolist()
                # find the longest sublist of case:concept:name
                max_most_frequent_traces = max(most_frequent_traces, key=len)
                # if all the sublist have 1 element, I'm in case 2
                if len(max_most_frequent_traces) == 1:
                    return list(map(lambda a: a[0], most_frequent_traces))  # flattened list
                # else there is a sublist with more element, case 3 where there are equal traces
                else:
                    return max_most_frequent_traces
            except Exception:
                return most_frequent_variants

        # get variants as list, each item represents a trace in the log
        # [[0, 1], [2]]
        variants = df2['variants'].tolist()

        # longest variant is selected because it's the most frequent
        # [0, 1]
        most_frequent_variants = max(variants, key=len)

        if len(most_frequent_variants) == 1:
            # all variants are different, I need to check similarities or find the one with the
            # shortest duration in the whole dataset

            # Check similarities between all the strings in the log and return the most frequent one
            #  I don't need to check similarities in the other case, because there the strings are exactly the same
            def func(name):
                matches = df2.apply(lambda row: (fuzz.partial_ratio(row[groupby_column], name) >= threshold), axis=1)
                return [i for i, x in enumerate(matches) if x]

            df3 = df2.apply(lambda row: func(row[groupby_column]), axis=1)  # axis=1 means apply function to each row

            most_frequent_variants = max(df3.tolist(), key=len)
            if len(most_frequent_variants) == 1:
                # there are no similar strings, all are different, so I find the one with the smallest duration
                # in the whole dataset, I don't need to filter like in the other cases

                #  get all durations as list
                durations = df1['duration'].tolist()
                #  find smallest duration and select row in dataframe with that duration
                min_duration_trace = df1.loc[df1['duration'] == min(durations)]['case:concept:name'].tolist()[0]
                if len(variants) == 1:
                    self.status_queue.put(
                        f"[PROCESS MINING] There is only 1 trace with duration: {min(durations)} sec")
                else:
                    self.status_queue.put(
                        f"[PROCESS MINING] All {len(variants)} variants are different, "
                        f"case {min_duration_trace} is the shortest ({min(durations)} sec)")
            else:
                # some strings are similar, it should be like case below
                min_duration_trace, duration = _findVariantWithShortestDuration(df1, most_frequent_variants)
                most_frequent_traces = _findMostFrequentTraces(df2, most_frequent_variants)
                self.status_queue.put(
                    f"[PROCESS MINING] There are {len(variants)} variants, "
                    f"among the {len(most_frequent_traces)} similar traces, "
                    f"case {min_duration_trace} is the shortest ({duration} sec)")
                print(f"[PROCESS MINING] Traces {most_frequent_traces} are similar")
        else:
            min_duration_trace, duration = _findVariantWithShortestDuration(df1, most_frequent_variants)
            most_frequent_traces = _findMostFrequentTraces(df2, most_frequent_variants)
            self.status_queue.put(
                f"[PROCESS MINING] There are {len(variants)} variants, "
                f"among the {len(most_frequent_traces)} equal traces, "
                f"case {min_duration_trace} is the shortest ({duration} sec)")
            print(f"[PROCESS MINING] Traces {most_frequent_traces} are equal")

        case = df.loc[df['case:concept:name'] == min_duration_trace]

        # self.selected_trace = min_duration_trace

        return case

    def _create_image(self, gviz, img_name, verbose=False):
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
            elif "BPMN" in img_name:
                bpmn_vis_factory.save(gviz, img_path)

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
            elif "BPMN" in img_name:
                bpmn_vis_factory.save(gviz, img_path)
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

    # def mostFrequentPathInDFG(self):
    #     dfg = self._createCustomDFG()
    #     source, target = self._getSourceTargetNodes()
    #     graphPath = utils.graphPath.HandleGraph(dfg, source, target)
    #     graphPath.printPath()
    #     return graphPath.frequentPath()

    def _createDFG(self, log=None, parameters=None, high_level=False):
        # create high level dfg, aggregate all data, not only most frequent one
        if high_level:
            df, log, parameters = self.aggregateData(self.dataframe, remove_duplicates=False)
        else:
            if parameters is None:
                parameters = {}
            if log is None:
                log = self._log
        dfg = dfg_factory.apply(log, variant="frequency", parameters=parameters)
        return dfg, log

    def save_dfg(self, name="DFG", high_level=False):
        dfg, log = self._createDFG()
        parameters = self._createImageParameters(log=log, high_level=high_level)
        if high_level:
            gviz = dfg_vis_factory.apply(dfg, log=log, variant="frequency", parameters=parameters)
        else:
            gviz = dfg_vis_factory.apply(dfg, log=self._log, variant="frequency", parameters=parameters)
        self._create_image(gviz, name)

    @staticmethod
    def _getHighLevelEvent(row):

        e = row["concept:name"]
        url = utils.utils.getHostname(row['browser_url'])
        app = row['application']
        cb = utils.utils.removeWhitespaces(row['clipboard_content'])
        # general
        if e in ["copy", "cut", "paste"]:  # take only first 15 characters of clipboard
            if len(cb) > 80:
                return f"[{app}] Copy and Paste: '{cb[:80]}...'"
            if len(cb) == 0:
                return f"[{app}] Copy and Paste"
            else:
                return f"[{app}] Copy and Paste: '{cb}'"

        # browser
        elif e in ["clickButton", "clickTextField", "doubleClick", "clickTextField", "mouseClick",
                   "clickCheckboxButton", "clickRadioButton"]:
            if row['tag_type'] == 'submit':
                return f"[{app}] Submit {row['tag_category'].lower()} on {url}"
            else:
                if row['tag_type'].lower() == row['tag_category'].lower():
                    return f"[{app}] Click {row['tag_type']} '{row['tag_name']}' on {url}"
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
            category = row['tag_category']
            if len(category) == 0:
                return f"[{app}] Edit on {url}"
            else:
                return f"[{app}] Edit {row['tag_category']} on {url}"
        elif e in ["changeField"]:
            # sometimes 2 out of 3 tags fields are equal, like TEXTAREA, textarea, luoghi
            # I don't want to repeat them so I remove duplicates by creating a set and then print the remaining ones
            tags = list({row['tag_type'], row['tag_category'].lower(), row['tag_name']})
            value = row['tag_value'].replace('\n', ', ')
            return f"[{app}] Write in {' '.join(tags)} on {url}: '{value}'"

        # system
        elif e in ["itemSelected", "deleted", "created", "Mount", "openFile", "openFolder"]:
            path = row['event_src_path'].replace('\\', r'\\')
            name, extension = ntpath.splitext(path)
            name = ntpath.basename(path)
            if extension:
                return f"[{app}] Edit file '{path}'"
            else:
                return f"[{app}] Edit folder '{path}'"
        elif e in ['moved', 'Unmount']:
            path = row['event_dest_path'] if e == "moved" else row['event_src_path']
            path = path.replace('\\', r'\\')
            _, extension = ntpath.splitext(path)
            if extension:
                return f"[{app}] Rename file as '{path}'"
            else:
                return f"[{app}] Rename folder as '{path}'"
        elif e in ["programOpen", "programClose"]:
            return f"Use program '{app}'"
        elif e in ["hotkey"]:
            return f"[{app}] Press '{row['description']}' hotkey ({row['id']})"

        # excel win
        elif e in ["newWorkbook", "openWorkbook", "activateWorkbook"]:
            return f"[Excel] Open {row['workbook']}"
        elif e in ["getCell", "getRange", "WorksheetCalculated", "WorksheetFormatChanged"]:
            if row['current_worksheet'] != '':
                return f"[Excel] Edit Cell on {row['current_worksheet']}"
            else:
                return f"[Excel] Edit Cell"
        elif e in ["editCellSheet", "editCell", "editRange"]:
            return f"[Excel] Edit cell {row['cell_range']} on {row['current_worksheet']} with value '{row['cell_content']}'"
        elif e in ["addWorksheet", "deselectWorksheet", "selectWorksheet", "WorksheetActivated"]:
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

    # transforms low level actions used for RPA generation to high level used for DFG, petri net, BPMN
    def aggregateData(self, df: pandas.DataFrame = None, remove_duplicates=False):

        if df is None:
            df = self.mostFrequentCase

        # filter rows
        df = df[~df.browser_url.str.contains('chrome-extension://')]
        df = df[~df.eventQual.str.contains('clientRedirect')]
        df = df[~df.eventQual.str.contains('serverRedirect')]

        # remove rows that contain empty clipboard text
        # [df.drop(row_index, inplace=True) for row_index, row in df.iterrows() if
        #  row['concept:name'] == 'copy' and utils.utils.removeWhitespaces(row['clipboard_content']) == '']
        for row_index, row in df.iterrows():
            concept_name = row['concept:name']
            cb_content = row['clipboard_content']
            if (concept_name in ['cut', 'copy', 'paste']) and utils.utils.removeWhitespaces(cb_content) == '':
                df = df.drop(row_index)  # returns a copy, previously was inplace so it returned null and side-effect db

        rows_to_remove = ["activateWindow", "deactivateWindow", "openWindow", "newWindow", "closeWindow",
                          "selectTab", "moveTab", "zoomTab", "typed", "mouseClick", "submit", "formSubmit",
                          "installBrowserExtension", "enableBrowserExtension", "disableBrowserExtension",
                          "resizeWindow", "logonComplete", "startPage", "doubleClickCellWithValue",
                          "doubleClickEmptyCell", "rightClickCellWithValue", "rightClickEmptyCell", "afterCalculate",
                          "closePresentation", "SlideSelectionChanged", "closeWorkbook",
                          "deactivateWorkbook", "WorksheetAdded", "autoBookmark", "selectedFolder", "selectedFile",
                          "manualSubframe", "copy"]
        df = df[~df['concept:name'].isin(rows_to_remove)]

        # convert each row of events to high level
        df['customClassifier'] = df.apply(lambda row: self._getHighLevelEvent(row), axis=1)

        # check duplicates
        # print(df[df['customClassifier'].duplicated() == True])
        # remove duplicates
        if remove_duplicates:
            df = df.drop_duplicates(subset='customClassifier', keep='first')

        log = conversion_factory.apply(df)
        parameters = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "customClassifier"}
        return df, log, parameters

    def _create_petri_net(self, remove_duplicates=False):
        df, log, dfg_parameters = self.aggregateData(remove_duplicates=remove_duplicates)
        dfg = self._createDFG(log, dfg_parameters)
        parameters = self._createImageParameters(log=log, high_level=True)
        # gviz = dfg_vis_factory.apply(dfg, log=self._log, variant="frequency", parameters=parameters)
        # self._create_image(gviz, "DFG")
        net, im, fm = dfg_conv_factory.apply(dfg, parameters=parameters)
        return net, im, fm

    def save_petri_net(self, name):
        net, im, fm = self._create_petri_net()
        gviz = pn_vis_factory.apply(net, im, fm, parameters={"format": "pdf"})
        self._create_image(gviz, name)

    def _create_bpmn(self, df: pandas.DataFrame = None):
        df, log, parameters = self.aggregateData(df, remove_duplicates=True)
        net, initial_marking, final_marking = heuristics_miner.apply(log, parameters=parameters)
        # net, initial_marking, final_marking = self._create_petri_net(remove_duplicates=True)
        bpmn_graph, elements_correspondence, inv_elements_correspondence, el_corr_keys_map = bpmn_converter.apply(
            net, initial_marking, final_marking)
        return bpmn_graph

    def save_bpmn(self, df: pandas.DataFrame = None):
        bpmn_graph = self._create_bpmn(df)
        bpmn_figure = bpmn_vis_factory.apply(bpmn_graph, variant="frequency", parameters={"format": "pdf"})
        self._create_image(bpmn_figure, "BPMN")

    def highLevelDFG(self, name="DFG_model"):
        try:
            df, log, parameters = self.aggregateData(self.dataframe, remove_duplicates=False)
            dfg = dfg_factory.apply(log, variant="frequency", parameters=parameters)
            gviz_parameters = self._createImageParameters(log=log, high_level=True)
            gviz = dfg_vis_factory.apply(dfg, log=log, variant="frequency", parameters=gviz_parameters)
            self._create_image(gviz, name)
        except Exception as e:
            print(f"[PROCESS MINING] Could not create DFG: {e}")
            return False

    # Petri net on entire process
    def highLevelPetriNet(self):
        try:
            df, log, parameters = self.aggregateData(self.dataframe, remove_duplicates=False)
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

    def highLevelBPMN(self, df: pandas.DataFrame = None, name="BPMN"):
        try:
            df, log, parameters = self.aggregateData(df, remove_duplicates=True)
            net, initial_marking, final_marking = heuristics_miner.apply(log, parameters=parameters)
            bpmn_graph, elements_correspondence, inv_elements_correspondence, el_corr_keys_map = bpmn_converter.apply(
                net, initial_marking, final_marking)
            bpmn_figure = bpmn_vis_factory.apply(bpmn_graph, variant="frequency", parameters={"format": "pdf"})
            self._create_image(bpmn_figure, name)
            # try:
            #     if name == "BPMN_final":
            #         os.remove(os.path.join(self.discovery_path, f'{self.filename}_BPMN.pdf'))
            # except Exception as e:
            #     print(f"[PROCESS MINING] Could not delete old BPMN: {e}")
            #     pass
        except Exception as e:
            print(f"[PROCESS MINING] Could not create BPMN: {e}")
            return False

    # def createGraphs(self, df: pandas.DataFrame = None):
    #     self.save_bpmn(df)
    #     self.highLevelPetriNet()
