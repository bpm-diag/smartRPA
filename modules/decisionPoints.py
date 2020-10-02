from collections import defaultdict
import modules.GUI.decisionDialog
import utils.utils
import pandas
import ntpath
import sys

from PyQt5 import QtWidgets

sys.path.append('../')


class DecisionPoints:

    def __init__(self, df: pandas.DataFrame):
        self.df = df
        self.duplication_subset = [
            'concept:name', 'category', 'application', 'browser_url_hostname', 'xpath']
        self.df1 = self.__handle_df()

    def __handle_df(self):
        df1 = self.df

        # *************
        # preprocessing
        # *************

        # remove rows with 'about:blank' url and with irrelevant events
        df1 = df1[(df1['browser_url'] != 'about:blank') &
                  (~df1['concept:name'].isin(['zoomTab']))]
        # application name of browsers is set to Chrome for all traces,
        # otherwise there would be false positive decision points
        df1.loc[df1['application'].isin(
            ['Firefox', 'Opera', 'Edge']), 'application'] = 'Chrome'
        # add hostname column to dataframe
        df1['browser_url_hostname'] = \
            df1['browser_url'].apply(
                lambda url: utils.utils.getHostname(url)).fillna('')

        # *************
        # marking duplicates among all distinct groups
        # *************

        # Use crosstab for get counts per ID and combinations (url_host, action)
        df_temp = pandas.crosstab([
            df1['category'], df1['application'], df1['browser_url_hostname'],
            df1['concept:name'], df1['clipboard_content'], df1['event_src_path']
        ], df1['case:concept:name'])

        # test only rows with greater like 1 for match at least one value in all groups
        df_temp = (df_temp.reset_index().loc[
            df_temp.gt(0).all(axis=1).to_numpy(),
            ['category', 'application', 'browser_url_hostname',
             'concept:name', 'clipboard_content', 'event_src_path']
        ])

        # use DataFrame.merge with indicator parameter for test if match filtered rows in original data
        mask = df1.merge(df_temp, how='left', indicator=True)['_merge'].eq('both')

        # generate duplicated column from mask
        df1['duplicated'] = mask.to_list()

        return df1

    def __generateKeywordsDataframe(self, dataframe: pandas.DataFrame):
        s = []
        for group, df2 in dataframe.groupby('case:concept:name'):
            category = ','.join(df2['category'].unique())
            if 'Browser' in category:
                keywords = ','.join(
                    filter(None, map(lambda x: ntpath.basename(x), df2['tag_value'].unique())))
            elif 'MicrosoftOffice' in category:
                keywords = ','.join(
                    filter(None, map(lambda x: x[:30], df2['cell_content'].unique())))
            else:
                keywords = ''
            s.append({
                'case:concept:name': df2['case:concept:name'].unique()[0],
                'category': ','.join(df2['category'].unique()),
                'application': ','.join(df2['application'].unique()),
                'events': ', '.join(df2['concept:name'].unique()),
                'hostname': ', '.join(df2['browser_url_hostname'].unique()),
                'url': ', '.join(df2['browser_url'].unique()),
                'keywords': keywords,
                'path': ','.join(filter(None, df2['event_src_path'].unique())),
                'clipboard': ','.join(filter(None, df2['clipboard_content'].unique())),
                'cells': ','.join(filter(None, df2['cell_range'].unique()))
            })
        keywordsDataframe = pandas.DataFrame(s)
        # remove duplicate decision points, considering all fields except caseID, which is the first one
        keywordsDataframe = keywordsDataframe.drop_duplicates(
            subset=keywordsDataframe.columns.tolist()[1:], ignore_index=True)
        return keywordsDataframe

    def generateDecisionDataframe_old(self):
        df = self.df1
        # there must be at least 2 traces in order to make a decision
        assert len(df['case:concept:name'].drop_duplicates()) >= 2

        # list to store dataframe rows
        series = []
        # dictionary to store dataframe rows that should be XORed
        caseActivities = defaultdict(list)

        # When a change happens, nodes are added to sequence and lists are emptied
        df['previousDuplicated'] = df['duplicated'].shift(1)

        for index, row in df.iterrows():

            # define variables
            # duplicated row is only available when performing decision points
            duplicated = row['duplicated']
            previousDuplicated = row['previousDuplicated']
            caseid = row['case:concept:name']

            # define conditions used to determine when to append xml nodes to main sequence or switch
            # on last loop iteration all the remaining xml nodes should be written
            lastIndex = (index == len(df) - 1)
            # determine if entering switch block or vice versa
            enterSwitch = previousDuplicated is True and duplicated is False
            exitSwitch = previousDuplicated is False and duplicated is True

            # add to main sequence
            if duplicated:
                series.append(row)
            # add to switch case
            else:
                caseActivities[caseid].append(row)

            # handle switch
            # if decision analysis and there are at least 2 cases in switch and
            # the switch case is finished so the next row will go in main sequence
            # or this is the last index
            if len(caseActivities) >= 2 and (exitSwitch or lastIndex):
                # create dataframe containing only decision rows that should be XORed
                s = []
                [s.extend(v) for _, v in caseActivities.items()]
                decisionDataframe = pandas.DataFrame(s).sort_index()

                # create keywords dataframe to display to the user
                keywordsDF = self.__generateKeywordsDataframe(decisionDataframe)

                # empty caseActivities dictionary for later use
                caseActivities.clear()

                app = QtWidgets.QApplication(sys.argv)  # DEBUG, REMOVE TODO
                decisionDialog = modules.GUI.decisionDialog.DecisionDialog(
                    keywordsDF)
                # decisionDialog.show()
                # when button is pressed
                if decisionDialog.exec_() in [0, 1]:
                    decidedDF = decisionDataframe.loc[
                        decisionDataframe['case:concept:name'] == decisionDialog.selectedTrace]
                    [series.append(row) for _, row in decidedDF.iterrows()]

            if lastIndex:
                # create and return new pandas datfaframe built from rows previously saved
                return pandas.DataFrame(series) \
                    .sort_index() \
                    .drop_duplicates(subset=self.duplication_subset, ignore_index=True, keep='first')

    def generateDecisionDataframe(self):
        df = self.df1
        # there must be at least 2 traces in order to make a decision
        assert len(df['case:concept:name'].drop_duplicates()) >= 2
        # list to store all dataframes, from which to build final dataframe with decisions
        dataframes = []

        s = df.groupby('case:concept:name')['duplicated'].apply(lambda d: d.ne(d.shift()).cumsum())
        duplicated_groups = df.groupby(s)
        duplicated_groups_list = [df for _, df in duplicated_groups]
        groups_by_duplicated_and_category = []
        for grouped_df in duplicated_groups_list:
            for _, df in grouped_df.groupby('category'):
                groups_by_duplicated_and_category.append(df)

        for dataframe in groups_by_duplicated_and_category:
            try:
                d = dataframe['duplicated'].unique()[0]
            except IndexError:
                d = True
            if d:  # add to final dataframe
                dataframes.append(dataframe)
            else:  # decision point
                # create keywords dataframe to display to the user
                keywordsDF = self.__generateKeywordsDataframe(dataframe)
                # if, after removing duplicates, there is only 1 row, directly append that row to dataframes
                # without prompting user
                # open dialog UI
                decisionDialog = modules.GUI.decisionDialog.DecisionDialog(keywordsDF)
                # when button is pressed
                if decisionDialog.exec_() in [0, 1]:
                    decidedDF = dataframe.loc[dataframe['case:concept:name'] == decisionDialog.selectedTrace]
                    dataframes.append(decidedDF)

        # create and return new pandas datfaframe built from rows previously saved
        return pandas.concat(dataframes) \
            .drop_duplicates(subset=self.duplication_subset, ignore_index=True, keep='first')\
            .sort_index()
