import utils.utils
import pandas
from datetime import datetime
from fuzzywuzzy import fuzz
from multiprocessing.queues import Queue
from deprecated.sphinx import deprecated


@deprecated(version='1.2.0', reason="Replaced by decision points")
def selectMostFrequentCase(dataframe: pandas.DataFrame, status_queue: Queue, flattened=False, threshold=90):
    """
    Select the most frequent routine in the process by using levenhstein distance to calculate similarity between strings

    :param dataframe: low level pandas dataframe of process
    :param status_queue: queue to print messages in GUI
    :param flattened:
    :param threshold: threshold of similarity, traces are considered similar if they are equal by at least 90%
    :return: most frequent trace
    """

    df = dataframe
    if df.empty:
        return None

    # flattening
    df['browser_url_hostname'] = df['browser_url'].apply(lambda url: utils.utils.getHostname(url)).fillna('')
    df['flattened'] = df[
        ['concept:name', 'category', 'browser_url_hostname']].agg(','.join, axis=1)
    groupby_column = 'flattened' if flattened else 'concept:name'

    # Merge rows of each trace into one row, so the resulting dataframe has n rows where n is the number of traces
    # For example I get
    # case:concept:name     concept:name                            timestamp
    # 0                     Create Fine, Send Fine                  2020-03-20 17:09:06:308, 2020-03-20 17:09:06:3
    # 1                     Insert Fine Notification, Add penalty   2020-03-20 17:10:28:348, 2020-03-20 17:10:28:2
    df1 = df.groupby(['case:concept:name'])[[groupby_column, 'time:timestamp']].agg(', '.join).reset_index()

    def getDuration(time):
        """
        Get duration of a trace, taking the first and last timestam in the trace and calculating the difference

        :param time: timestamp column
        :return: time duration in seconds
        """
        timestamps = time.split(',')
        try:
            start = datetime.fromisoformat(timestamps[0].strip())
            finish = datetime.fromisoformat(timestamps[-1].strip())
            # start = datetime.strptime(timestamps[0].strip(), "%Y-%m-%dT%H:%M:%S.%f")
            # finish = datetime.strptime(timestamps[-1].strip(), "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
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

    def _findVariantWithShortestDuration(df1: pandas.DataFrame, most_frequent_variants, equal=False):
        """
        Find the trace with the minimum duration in seconds.
        Not used when all traces are different

        :param df1: dataframe of process
        :param most_frequent_variants: case ids of most frequent traces
        :param equal:
        :return: concept:case:id of the variant with shortest duration
        """
        # there are at least 2 equal variants, most_frequent_variants is an array like [0,1]
        # take only the most frequent rows in dataframe, like [0,1]
        if equal:
            most_frequent_variants_df = df1.loc[df1['case:concept:name'].isin(most_frequent_variants)]
        else:
            most_frequent_variants_df = df1.iloc[most_frequent_variants, :]
        # find the row with the smallest duration
        durations = most_frequent_variants_df['duration'].tolist()
        # return the index of the row with the smallest duration
        min_duration_trace = most_frequent_variants_df.loc[most_frequent_variants_df['duration'] == min(durations)][
            'case:concept:name'].tolist()[0]
        return min_duration_trace, min(durations)

    def _findMostFrequentTraces(df2: pandas.DataFrame, most_frequent_variants):
        """
        Find the most frequent trace

        :param df2: pandas dataframe
        :param most_frequent_variants:
        :return: case:concept:name of most frequent traces
        """
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
        # I don't need to check similarities in the other case, because there the strings are exactly the same
        def func(name):
            matches = df2.apply(lambda row: (fuzz.ratio(row[groupby_column], name) >= threshold), axis=1)
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
                status_queue.put(
                    f"[PROCESS MINING] There is only 1 trace with duration: {min(durations)} sec")
            else:
                status_queue.put(
                    f"[PROCESS MINING] All {len(variants)} variants are different, "
                    f"case {min_duration_trace} is the shortest ({min(durations)} sec)")
        else:
            # some strings are similar, it should be like case below
            min_duration_trace, duration = _findVariantWithShortestDuration(df1, most_frequent_variants)
            most_frequent_traces = _findMostFrequentTraces(df2, most_frequent_variants)
            status_queue.put(
                f"[PROCESS MINING] There are {len(variants)} variants, "
                f"among the {len(most_frequent_traces)} similar traces, "
                f"case {min_duration_trace} is the shortest ({duration} sec)")
            print(f"[PROCESS MINING] Traces {most_frequent_traces} are similar by at least {threshold}%")
    else:
        # min_duration_trace, duration = _findVariantWithShortestDuration(df1, most_frequent_variants)
        # most_frequent_traces = _findMostFrequentTraces(df2, most_frequent_variants)
        # self.status_queue.put(
        #     f"[PROCESS MINING] There are {len(variants)} variants, "
        #     f"among the {len(most_frequent_traces)} equal traces, "
        #     f"case {min_duration_trace} is the shortest ({duration} sec)")
        # print(f"[PROCESS MINING] Traces {most_frequent_traces} are equal")
        min_duration_trace, duration = _findVariantWithShortestDuration(df1, most_frequent_variants, equal=True)
        status_queue.put(
            f"[PROCESS MINING] There are {len(df1)} traces and {len(variants)} variants, "
            f"among the {len(most_frequent_variants)} equal traces, "
            f"case {min_duration_trace} is the shortest ({duration} sec)")
        print(f"[PROCESS MINING] Traces {most_frequent_variants} are equal")

    case = df.loc[df['case:concept:name'] == min_duration_trace]

    # self.selected_trace = min_duration_trace

    return case
