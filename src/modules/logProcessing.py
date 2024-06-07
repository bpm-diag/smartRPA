from datetime import datetime
import pandas
from multiprocessing.queues import Queue
import os
import utils.utils

try:
    from pm4py.objects.conversion.log import factory as conversion_factory
    from pm4py.objects.log.importer.xes import factory as xes_importer
    from pm4py.objects.log.exporter.xes import factory as xes_exporter
except ImportError as e:
    print("[PROCESS MINING] Process mining analysis has been disabled because 'pm4py' module is not installed."
          "See https://github.com/bpm-diag/smartRPA#1-pm4py")
    print(e)


def handle_log(status_queue: Queue,
               file_extension: str, filename: str, filepath: list, save_path: str, RPA_log_path: str):
    """
    Process event log.

    For each log:

    * import log into pandas dataframe
    * rename columns to match XES standard (concept:name, time:timestamp, org:resource)
    * generate caseIDs from timestamp
    * insert case:creator and lifecycle:transition columns

    Then all the processed event logs are merged into one.

    A dataframe is created from the merged event logs and will be used in the rest of the process.

    Dataframe is also exported in XES.

    :param status_queue: queue to print values in GUI
    :param file_extension: extension of input event log (either CSV or XES)
    :param filename: name of input log
    :param filepath: list of paths of input logs
    :param save_path: path where to save log
    :param RPA_log_path: path of RPA folder
    :return: processed event log
    """

    if file_extension == ".csv":

        def createCaseID(ts):
            try:
                # caseID = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f").strftime('%m%d%H%M%S%f')  # [:-3]
                caseID = datetime.fromisoformat(ts).strftime('%m%d%H%M%S%f')
                return caseID
            except Exception:
                caseID = datetime.strptime(
                    ts, "%Y-%m-%d %H:%M:%S:%f").strftime('%m%d%H%M%S%f')  # [:-3]
                return caseID

        # combine multiple csv into one and then export it to xes
        csv_to_combine = list()
        for i, csv_path in enumerate(filepath):

            # load csv in pandas dataframe,
            # rename columns to match xes standard,
            # remove rows that don't have timestamp
            # replace null values with empty string
            # sort by timestamp
            try:
                df = pandas \
                    .read_csv(csv_path, encoding='utf-8-sig') \
                    .rename(columns={'event_type': 'concept:name',
                                     'timestamp': 'time:timestamp',
                                     'user': 'org:resource'}) \
                    .dropna(subset=["time:timestamp"]) \
                    .fillna('') \
                    .sort_values(by='time:timestamp')
            except pandas.errors.ParserError:
                df = pandas \
                    .read_csv(csv_path, encoding='utf-8-sig', sep=';') \
                    .rename(columns={'event_type': 'concept:name',
                                     'timestamp': 'time:timestamp',
                                     'user': 'org:resource'}) \
                    .dropna(subset=["time:timestamp"]) \
                    .fillna('') \
                    .sort_values(by='time:timestamp')

            # Each csv should have a separate case ID, so I insert a column to the left of each csv and assign
            # number i. When I convert the combined csv to xes, all the rows with the same number will belong to a
            # single trace, so I will have i traces.

            # convert timestamp to ISO format
            # try:
            #     df['time:timestamp'] = df['time:timestamp'] \
            #         .apply((lambda ts: datetime.strptime(ts, "%Y-%m-%d %H:%M:%S:%f").isoformat()))
            # except ValueError:
            #     pass

            try:  # insert this column to create a unique trace for each csv
                df.insert(0, 'case:concept:name',
                          createCaseID(df['time:timestamp'][0]))
            except ValueError:  # column already present, replace case id values so they are sequential
                pass

            try:  # insert this column to create a unique trace for each csv
                df.insert(1, 'case:creator', 'SmartRPA by marco2012')
            except ValueError:  # column already present
                pass

            try:
                df.insert(2, 'lifecycle:transition', 'complete')
            except ValueError:  # column already present
                pass

            csv_to_combine.append(df)

        # dataframe of combined csv, sorted by timestamp
        combined_csv = pandas.concat(csv_to_combine)

        # remove rows containing path of temporary files
        combined_csv = combined_csv[~combined_csv['event_src_path'].str.contains(
            '~.*\.tmp|\.tmp.*~')]

        # convert case id to string
        # combined_csv['case:concept:name'] = combined_csv['case:concept:name'].astype(str)

        # insert index for each row
        # combined_csv.insert(0, 'row_index', range(0, len(combined_csv)))

        # dataframe = combined_csv

        # calculate csv path
        combined_csv_path = os.path.join(
            RPA_log_path, f'{filename}_combined.csv')

        # save dataframe as csv
        combined_csv.to_csv(combined_csv_path, index=False,
                            encoding='utf-8-sig')

        # convert csv to xes
        log = conversion_factory.apply(combined_csv)

        # sort by timestamp
        # log = sorting.sort_timestamp(log)

        # convert csv to xes
        xes_path = os.path.join(
            save_path, utils.utils.EVENT_LOG_FOLDER, f'{filename}.xes')
        xes_exporter.export_log(log, xes_path)
        # timestamp in xes file must have attribute date, not string
        utils.utils.fixTimestampFieldXES(xes_path)

        status_queue.put(f"[PROCESS MINING] Working directory is {save_path}")
        status_queue.put(f"[PROCESS MINING] Generated XES file")

        return combined_csv, log

    elif file_extension == ".xes":
        log = xes_importer.import_log(filepath)
        return None, log
    else:
        status_queue.put(
            "[PROCESS_MINING] Input file must be either .csv or .xes")
        return False
