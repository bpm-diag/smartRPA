import modules.GUI.decisionDialog
import modules.GUI.decisionDialogWebView
import modules.events.systemEvents
import utils.utils
import pandas
import pandas.core.groupby.generic
import ntpath
import sys
from multiprocessing import Queue
sys.path.append('../')


class DecisionPoints:
    """
    Decision points class
    """

    def __init__(self, df: pandas.DataFrame, status_queue: Queue):
        """
        Decision points class

        :param df: pandas dataframe of entire process
        :param status_queue: queue to print values in the GUI
        """

        self.status_queue = status_queue

        self.df = df

        # values to find duplicated rows
        self.duplication_subset = ['category', 'application', 'concept:name', 'event_src_path', 'event_dest_path',
                                   'browser_url_hostname', 'xpath']  # 'tag_value', 'clipboard_content', 'cell_range'

        # need to check separately for compatibility reasons, previous logs did not have this column
        if 'hotkey' in self.df.columns:
            self.duplication_subset.append('hotkey')

        self.df1 = self.handle_df()

    def handle_df(self):
        """
        Pre-process dataframe.

        * filter irrelevant rows
        * add hostname column
        * mark duplicated rows

        :return: processed dataframe df1
        """
        df1 = self.df

        # *************
        # preprocessing
        # *************

        # filter irrelevant rows
        # opening excel is already managed, no need for this row
        excelMask = ~((df1['concept:name'] == 'programOpen') &
                      (df1['application'] == 'EXCEL.EXE') &
                      (df1['event_src_path'].str.contains('EXCEL.EXE')))
        # these events are irrelevant for decision mining and rpa bot
        # browserUrlMask = ~df1['browser_url'].isin(
        #     ['about:blank', 'chrome://newtab/', 'chrome-search://local-ntp/local-ntp.html'])
        browserUrlMask = ~(
                (df1['browser_url'].isin(['about:blank', 'chrome://newtab/',
                                          'chrome-search://local-ntp/local-ntp.html'])) &
                ~(df1['concept:name'] == 'startDownload')
        )
        eventsMask = ~df1['concept:name'].isin(
            ['zoomTab', 'enableBrowserExtension', 'logonComplete', 'getCell', 'afterCalculate',
             'newWindow', 'selectText', 'KernelDropped', 'selectTab', 'newTab', 'doubleClick',
             'paste', 'mouseClick'])  # formSubmit
        appsMask = ~df1['application'].isin(modules.events.systemEvents.programs_to_ignore)
        df1 = df1[browserUrlMask & excelMask & appsMask & eventsMask]
        # application name of browsers is set to Chrome for all traces,
        # otherwise there would be false positive decision points
        df1.loc[df1['application'].isin(
            ['Firefox', 'Opera', 'Edge']), 'application'] = 'Chrome'
        # add hostname column to dataframe
        df1['browser_url_hostname'] = df1['browser_url'].apply(lambda url: utils.utils.getHostname(url)).fillna('')
        # remove query parameters from formSubmit url
        formSubmitMask = df1['concept:name'] == 'formSubmit'
        df1.loc[formSubmitMask, 'browser_url'] = df1.loc[formSubmitMask, 'browser_url'].apply(lambda url: url.split('?')[0])

        # *************
        # marking duplicates among all distinct groups
        # *************

        # Use crosstab for get counts per ID and combinations (url_host, action)
        df_temp = pandas.crosstab(
            [df1[col] for col in self.duplication_subset],
            df1['case:concept:name']
        )

        # test only rows with greater like 1 for match at least one value in all groups
        df_temp = (df_temp.reset_index().loc[
            df_temp.gt(0).all(axis=1).to_numpy(),
            self.duplication_subset
        ])

        # use DataFrame.merge with indicator parameter for test if match filtered rows in original data
        mask = df1.merge(df_temp, how='left', indicator=True)[
            '_merge'].eq('both')

        # generate duplicated column from mask
        df1['duplicated'] = mask.to_list()

        return df1

    # def add_end_marker(self):
    #     """
    #     Adds an artifical end event for each unique case ID with a timestamp 1 millisecond after the last event.

    #     :param df: A pandas DataFrame containing the event log data.
    #     """
    #     # Group by case ID
    #     grouped_df = self.df1.groupby("case:concept:name")
    #     self.df1['time:timestamp'] = pandas.to_datetime(self.df1['time:timestamp'])
    #     # Get the last timestamp for each case
    #     last_timestamps = grouped_df["time:timestamp"].max()

    #     # Add 1 millisecond to the last timestamps
    #     end_timestamps = last_timestamps + pandas.Timedelta(milliseconds=1)

    #     # Create a DataFrame with the end markers
    #     end_markers = pandas.DataFrame({"case:concept:name": last_timestamps.index, 
    #                                     "time:timestamp": end_timestamps,
    #                                     "case:creator":	"SmartRPA by marco2012", # Could be added dynamically
    #                                     "lifecycle:transition": "complete", # Could be added dynamically
    #                                     "concept:name": "endMarker",
    #                                     "application": "", # May be None, Design decision
    #                                     'duplicated': True, # Could be calculated; as it is equal for all it is True
    #                                     'category': "EndMarker"                              
    #                                     })

    #     # Combine the event log data with the end markers
    #     self.df1 = pandas.concat([self.df1, end_markers], ignore_index=True)
    #     # Replace NaN values with empty strings in all columns
    #     self.df1.fillna('', inplace=True)


    def number_of_decision_points(self):
        """
        Calculates the number of decision points in a trace

        :return: number of decision points
        """
        count = 0
        # self.add_end_marker()
        # self.df1.sort_values(by=['case:concept:name', 'time:timestamp'], ascending=True, inplace=True)
        self.df1.to_csv("checking.csv")
        s = self.df1.groupby('case:concept:name')['duplicated'].apply(lambda d: d.ne(d.shift()).cumsum())
        
        #Issue 32: Intention is to get the number of changes in each process from the base line
        # If there are more than one cumsum values in the col s, than there is a variation point
        # Suggestion: Merge s with df1 and test if there are more than 1 s values per case.
        #    if yes: Variation points detected, Amount = max(s) - min(s) value
        #    if no: There is no variation point in this variant identified (still may be another process)
        for _, group in self.df1.groupby([s, 'category']):
        # for _, group in self.df1.groupby('case:concept:name'): 
            if len(group.groupby('case:concept:name')) >= 2 and not group['duplicated'].unique():
                count += 1
        return count

    def __generateKeywordsDataframe(self, dataframe: pandas.DataFrame):
        """
        Generate keywords dataframe, used in GUI when selecting decision points

        :param dataframe: pandas dataframe
        :return: keywords dataframe with duplicates removed and values sorted
        """

        series = []
        for group, df2 in dataframe.groupby('case:concept:name'):
            category = ','.join(df2['category'].unique())
            application = ','.join(df2['application'].unique())
            keywords = ''
            if 'Browser' in category:
                # keywords = ','.join(filter(None, map(lambda x: ntpath.basename(x), df2['tag_value'].unique()))) + ','
                # keywords += ','.join(filter(None, map(lambda x: ntpath.basename(x), df2['id'].unique())))
                # remove empty values
                a = filter(None, df2['tag_value'].unique())
                b = filter(None, df2['id'].unique())
                # create set of values from the two lists to remove duplicates
                results_union = set().union(*[a, b])
                # convert to string
                keywords = ', '.join(sorted(results_union))
            if 'Excel' in application:
                keywords = ','.join(
                    filter(None, map(lambda x: x[:30], df2['cell_content'].unique())))

            hotkeys = ''
            if 'hotkey' in df2.columns:
                hotkeys = ','.join(filter(None, df2['hotkey'].unique()))

            series.append({
                'case:concept:name': df2['case:concept:name'].unique()[0],
                'category': category,
                'application': application,
                'events': ', '.join(sorted(df2['concept:name'].unique())),
                'hostname': '\n'.join(df2['browser_url_hostname'].unique()),
                'url': '\n'.join(map(lambda url: url, df2['browser_url'].unique())),
                'keywords': keywords,
                'path': '\n'.join(filter(None, df2['event_src_path'].unique())),
                'clipboard': ','.join(filter(None, df2['clipboard_content'].unique())),
                'cells': ','.join(filter(None, df2['cell_range'].unique())),
                'hotkeys': hotkeys,
            })
        keywordsDataframe = pandas.DataFrame(series)
        # remove duplicate decision points, considering all fields except caseID, which is the first one
        # sort rows
        # subset = keywordsDataframe.columns.tolist()[1:]
        subset = ['category', 'application', 'events', 'hostname', 'url', 'path', 'clipboard', 'cells', 'hotkeys', 'keywords']
        keywordsDataframe = keywordsDataframe\
            .drop_duplicates(subset=subset, ignore_index=True)\
            .sort_values(['hostname', 'category','application', 'path', 'clipboard', 'cells'])
        return keywordsDataframe

    def generateDecisionDataframe(self) -> pandas.DataFrame:
        """
        Find decision points in dataframe, ask user which decisions to take and generate final trace built from decisions.

        :return: dataframe built from user decisions
        """

        df = self.df1

        # there must be at least 2 traces in order to make a decision
        assert len(df['case:concept:name'].drop_duplicates()) >= 2

        # list to store all groups, from which to build final dataframe with decisions
        dataframes = []
        # variables to save previous decision
        previousDataframe = None
        previousDecision = None
        selectedTrace = None

        # number of decision points
        n = self.number_of_decision_points()
        status = f"[DECISION POINTS] Discovered {n} decision point"
        if n > 1:
            status += "s" # Adding s to string > points
        self.status_queue.put(status)

        s = df.groupby('case:concept:name')['duplicated'].apply(lambda d: d.ne(d.shift()).cumsum())
        duplicated_groups = df.groupby([s, 'category'])

        for group_index, dataframe in duplicated_groups:

            try:
                duplicated = dataframe['duplicated'].unique()[0]
            except IndexError:
                duplicated = True
            except ValueError:
                duplicated = any(dataframe['duplicated'].unique())

            # if the current group is duplicated, all the rows in the group are present at least once per trace.
            # hence this group contains repeated rows. I only need to select a group of rows, so I pick the first
            # case id, select all the rows with that caseid and append them to the final dataframe
            # otherwise there would be many duplicated rows in the final dataframe
            if duplicated:
                # dataframes.append(dataframe)
                if selectedTrace:
                    dataframes.append(dataframe[dataframe['case:concept:name'] == selectedTrace])
                else:
                    first_caseid_in_group = dataframe['case:concept:name'].unique()[0]
                    dataframes.append(dataframe[dataframe['case:concept:name'] == first_caseid_in_group])

            # decision point if not duplicated and there are at least 2 traces in the current group
            elif not duplicated and len(dataframe.groupby('case:concept:name')) >= 2:

                # if the current group does not contain rows from selected trace, skip iteration
                if selectedTrace and selectedTrace not in dataframe['case:concept:name'].unique():
                    continue

                # in the first loop iteration previous decision is None, directly create keywords dataframe
                if previousDecision is not None and \
                        previousDataframe is not None and \
                        not previousDataframe['duplicated'].unique()[0]:

                    # Only the decisions belonging to the current path in the DFG should be selected
                    # To achieve this, the previous decision is stored in a variable along with the previous group
                    # First I select all the traces that have all the rows from previousDecision in their dataframe
                    # To do this, previousDecision rows is joined with previousDataframe on duplication_subset.
                    # Then, only the traces that have at least the same number of rows as previousDecision rows are taken
                    # Finally, the case id of each trace is returned as a list
                    # decisionTraces is a list of case ids; it indicates the traces that include the previous decision made
                    on = ['category', 'application', 'concept:name', 'event_src_path', 'event_dest_path',
                          'clipboard_content', 'cell_range', 'browser_url_hostname', 'browser_url']  # xpath
                    try:
                        decisionTraces = pandas \
                            .merge(previousDataframe, previousDecision, on=on) \
                            .groupby('case:concept:name_x')['case:concept:name_x'] \
                            .filter(lambda group: len(group) >= len(previousDecision) * 0.76) \
                            .unique().tolist()
                    except KeyError:
                        decisionTraces = pandas \
                            .merge(previousDataframe, previousDecision, on=on) \
                            .groupby('case:concept:name')['case:concept:name'] \
                            .filter(lambda group: len(group) >= len(previousDecision) * 0.76) \
                            .unique().tolist()

                    # only the selected traces should appear in the keywords dataframe
                    # this only considers the next decision point, but it should consider all decision points instead
                    # filtered_df = dataframe.loc[dataframe['case:concept:name'].isin(decisionTraces)]
                    # filtered_df = None
                    filtered_df = []

                    # for each group, if the group in the current iteration is not the same as the previous dataframe
                    # and the current group is a decision point (is not duplicated), then find rows containing the
                    # caseID of the trace selected before. When found, break the loop
                    # for _, group in duplicated_groups:
                    #     if not group['duplicated'].unique() and not group.equals(previousDataframe):
                    #         filtered_df = group.loc[group['case:concept:name'].isin(decisionTraces)]
                    #         if not filtered_df.empty and selectedTrace in filtered_df['case:concept:name'].unique():
                    #             break

                    # for _, group in duplicated_groups:
                    #     if not group['duplicated'].unique() and not group.equals(previousDataframe):
                    #         mask = group['case:concept:name'].isin(decisionTraces)
                    #         filtered_df.append(group.loc[mask])
                    # filtered_df = pandas.concat(filtered_df).drop_duplicates(subset=self.duplication_subset)

                    # find all the keys in groupby
                    # p = previousDataframe group
                    # loop starts from group after p
                    # loop breaks if duplicated==True
                    # keys = list(duplicated_groups.groups.keys())
                    # prevDFGroupCount = keys.index(group_index)
                    # # handle case where first group is duplicated, skip to the next one
                    # if self.df1.iloc[duplicated_groups.groups[keys[prevDFGroupCount]]]['duplicated'].unique():
                    #     prevDFGroupCount += 1
                    # for index in range(prevDFGroupCount, len(keys)):
                    #     group = self.df1.iloc[duplicated_groups.groups[keys[index]]]
                    #     if not group['duplicated'].unique():
                    #         mask = group['case:concept:name'].isin(decisionTraces)
                    #         filtered_df.append(group.loc[mask])
                    #     else:
                    #         break

                    afterPreviousDataframe = False
                    for _, group in duplicated_groups:
                        if afterPreviousDataframe:
                            try:
                                not_duplicated = not group['duplicated'].unique()
                            except ValueError:
                                not_duplicated = not (any(group['duplicated'].unique()))
                            if not_duplicated:  # decision point
                                mask = group['case:concept:name'].isin(decisionTraces)
                                filtered_df.append(group.loc[mask])
                            else:
                                break
                        if group.equals(previousDataframe):
                            afterPreviousDataframe = True

                    try:
                        filtered_df = pandas.concat(filtered_df).drop_duplicates(subset=self.duplication_subset)
                    except ValueError:
                        filtered_df = []

                    if len(filtered_df) == 0 or \
                            filtered_df.empty:
                        continue
                    elif len(filtered_df.groupby('case:concept:name')) >= 2:
                        # there are at least 2 traces, create keywords dataframe and prompt user
                        keywordsDF = self.__generateKeywordsDataframe(filtered_df)
                    else:
                        # there is only 1 trace, append directly to dataframes without prompting decision and restart loop
                        dataframes.append(filtered_df)
                        previousDecision = filtered_df
                        previousDataframe = dataframe
                        continue
                else:
                    # create keywords dataframe to display to the user
                    keywordsDF = self.__generateKeywordsDataframe(dataframe)

                # open dialog UI
                decisionDialog = modules.GUI.decisionDialogWebView.DecisionDialogWebView(keywordsDF)

                # when button is pressed
                if decisionDialog.exec_() in [0, 1] and decisionDialog.selectedTrace is not None:
                    try:
                        selectedTrace = int(decisionDialog.selectedTrace)
                    except ValueError:
                        selectedTrace = decisionDialog.selectedTrace

                    decidedDF = dataframe.loc[dataframe['case:concept:name'] == selectedTrace]
                    dataframes.append(decidedDF)

                    previousDecision = decidedDF

            previousDataframe = dataframe

        # create and return new pandas dataframe built from rows previously saved
        final_duplication_subset = ['category', 'application', 'concept:name', 'event_src_path', 'event_dest_path',
                                    'browser_url_hostname', 'xpath', 'tag_value', 'clipboard_content', 'cell_range']
        

        return pandas\
            .concat(dataframes)\
            .drop_duplicates(subset=final_duplication_subset, ignore_index=False, keep='first')\
            .sort_index()
