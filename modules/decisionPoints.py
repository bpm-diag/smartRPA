import sys
sys.path.append('../')
import ntpath
import pandas
import utils.utils
import modules.GUI.decisionDialog
from collections import defaultdict


class DecisionPoints:

    def __init__(self, df: pandas.DataFrame):
        self.df = df
        self.df1 = self.__df_without_duplicates()

    # dataframe utils
    def __df_without_duplicates(self, ignore_index=True):
        # application name of browsers is set to Chrome for all traces,
        # otherwise there would be false positive decision points
        self.df.loc[self.df['application'].isin(['Firefox', 'Opera', 'Edge']), 'application'] = 'Chrome'
        # add hostname column to dataframe
        self.df['browser_url_hostname'] = \
            self.df['browser_url'].apply(lambda url: utils.utils.getHostname(url)).fillna('')
        # add duplicated column to dataframe, boolean indicating if each row is duplicated
        # The rows with duplicated = True are unique, the other ones should run in separate cases of a switch
        duplication_subset = ['concept:name', 'category', 'application', 'browser_url_hostname', 'xpath']
        self.df['duplicated'] = self.df.duplicated(subset=duplication_subset, keep=False)
        # dataframe without duplicates and with 'duplicated' column indicated if the row should go to main sequence or switch
        return self.df.drop_duplicates(subset=duplication_subset, ignore_index=ignore_index, keep='first')

    def __generateKeywordsDataframe(self, traces: list, decisionDataframe: pandas.DataFrame):
        s = []
        for trace in traces:
            df2 = decisionDataframe.loc[decisionDataframe['case:concept:name'] == trace]
            category = ','.join(df2['category'].unique())
            keywords = ''
            if 'Browser' in category:
                keywords = ','.join(filter(None, map(lambda x: ntpath.basename(x), df2['tag_value'].unique())))
            elif 'MicrosoftOffice' in category:
                keywords = ','.join(filter(None, map(lambda x: x[:30], df2['cell_content'].unique())))
            s.append({
                'case:concept:name': trace,
                'category': ','.join(df2['category'].unique()),
                'application': ','.join(df2['application'].unique()),
                'events': ', '.join(df2['concept:name'].unique()),
                'url': ', '.join(df2['browser_url_hostname'].unique()),
                'keywords': keywords,
                'path': ','.join(filter(None, df2['event_src_path'].unique())),
                'cells': ','.join(filter(None, df2['cell_range'].unique()))
            })
        keywordsDataframe = pandas.DataFrame(s)
        return keywordsDataframe

    def generateDecisionDataframe(self):
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
                keywordsDF = self.__generateKeywordsDataframe(traces=list(caseActivities.keys()),
                                                              decisionDataframe=decisionDataframe)

                # empty caseActivities dictionary for later use
                caseActivities.clear()

                # app = QtWidgets.QApplication(sys.argv)
                decisionDialog = modules.GUI.decisionDialog.DecisionDialog(keywordsDF)
                # decisionDialog.show()
                # when button is pressed
                if decisionDialog.exec_() in [0, 1]:
                    decidedDF = decisionDataframe.loc[
                        decisionDataframe['case:concept:name'] == decisionDialog.selectedTrace]
                    [series.append(row) for _, row in decidedDF.iterrows()]

            if lastIndex:
                # create and return new pandas datfaframe built from rows previously saved
                return pandas.DataFrame(series).sort_index()
