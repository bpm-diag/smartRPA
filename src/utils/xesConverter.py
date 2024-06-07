# ******************************
# Convert csv to xes for process mining
# ******************************
from threading import Thread

import pandas
from datetime import datetime
from opyenxes.factory.XFactory import XFactory
from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, Comment


class CSV2XES:
    """This class convert csv to xes

    :param csv_filepath: List of csv files to convert (list of strings representing the path of each csv). Each csv generates a trace in xes file
    :param xes_filepath: Path of resulting xes file
    :param events_header: Name of the column in csv containing events
    :param timestamp_header: Name of the column in csv containing timestamps
    :param timestamp_format: Format of timestamps to be parsed
    :param attributes_to_consider: include only certain attributes in resulting xes, if empty include all attributes
    :return: boolean indicating success status
    :rtype: bool
    """

    def __init__(self, csv_filepath: list, xes_filepath: str = None,
                 csv_separator=',',
                 events_header="concept:name",
                 timestamp_header="time:timestamp",
                 timestamp_format="%Y-%m-%d %H:%M:%S:%f",
                 resource_header="org:resource",
                 attributes_to_consider: list = None):

        self.csv_filepath = csv_filepath
        self.csv_separator = csv_separator

        if xes_filepath:
            self.xes_filepath = xes_filepath
        else:
            self.xes_filepath = csv_filepath[-1].replace('.csv', '.xes')

        self.timestamp_header = timestamp_header
        self.timestamp_format = timestamp_format
        self.events_header = events_header
        self.resource_header = resource_header

        if attributes_to_consider is None:
            attributes_to_consider = []
        self.attributes_to_consider = attributes_to_consider
        # if self.attributes_to_consider is not empty, add timestamp and event fields because they are required
        # if self.attributes_to_consider is empty it means I should consider all events
        if self.attributes_to_consider:
            if self.timestamp_header not in self.attributes_to_consider:
                self.attributes_to_consider.append(self.timestamp_header)
            if self.events_header not in self.attributes_to_consider:
                self.attributes_to_consider.append(self.events_header)
            if self.resource_header not in self.attributes_to_consider:
                self.attributes_to_consider.append(self.resource_header)

    def run(self):
        t0 = Thread(target=self.csvToXes)
        t0.start()
        t0.join()

    def __isTimestamp(self, string):
        try:
            datetime.strptime(string, self.timestamp_format)
            return True
        except (ValueError, TypeError):
            return False

    def __convert_line_in_event(self, row: dict):
        attribute_map = XFactory.create_attribute_map()
        for column_header in row:
            value = row[column_header]

            # handle timestamp
            if column_header == self.timestamp_header:
                try:
                    ts = datetime.strptime(value, self.timestamp_format)
                    attribute = XFactory.create_attribute_timestamp("time:timestamp", ts)
                except (ValueError, TypeError):
                    continue

            # handle event
            elif column_header == self.events_header:
                attribute = XFactory.create_attribute_literal("concept:name", value)

            elif column_header == self.resource_header:
                attribute = XFactory.create_attribute_literal("org:resource", value)

            # if attributes_to_consider is empty I take all the attributes from csv, else only those in the list
            elif (self.attributes_to_consider == []) or (column_header in self.attributes_to_consider):
                attribute = XFactory.create_attribute_literal(column_header, value)

            else:
                continue

            attribute_map[attribute.get_key()] = attribute
        return XFactory.create_event(attribute_map)

    # create xml log, inserting a trace for each csv file
    def csvToXes(self):

        # single log file
        log = XFactory.create_log()

        for i, csv_path in enumerate(self.csv_filepath):

            # load csv in pandas dataframe,replace column names to match xes standard and replace null with empty string
            try:
                df = pandas.read_csv(csv_path, encoding='utf-8-sig', sep=self.csv_separator) \
                    .rename(columns={self.events_header: 'concept:name',
                                     self.timestamp_header: 'time:timestamp',
                                     self.resource_header: 'org:resource'}) \
                    .fillna('')  # https://www.w3resource.com/pandas/series/series-fillna.php
            except UnicodeDecodeError as e:
                print(f"[CSV2XES] Could not decode {csv_path}: {e}")
                return False

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

            # create dictionary with column name as key and row data as value, like
            # {'category': 'Browser', 'event_type': 'newTab'}
            # if attributes_to_consider is not empty I need to take only certain columns from csv
            if self.attributes_to_consider:
                dictionary = df[self.attributes_to_consider].to_dict(orient='records')
            else:  # take all columns
                dictionary = df.to_dict(orient='records')

            events = list()
            [events.append(self.__convert_line_in_event(row)) for row in dictionary]

            trace = XFactory.create_trace()
            [trace.append(e) for e in events]

            log.append(trace)

        # Save log in xes format
        with open(self.xes_filepath, "w") as file:
            XesXmlSerializer().serialize(log, file)

        # Add extensions to xes file
        extensions = [
            Element(
                'extension', {
                    'name': 'Concept',
                    'prefix': 'concept',
                    'uri': 'http://www.xes-standard.org/concept.xesext'
                }),
            Element(
                'extension', {
                    'name': 'Time',
                    'prefix': 'time',
                    'uri': 'http://www.xes-standard.org/time.xesext'
                }),
            Element(
                'extension', {
                    'name': 'Organizational',
                    'prefix': 'org',
                    'uri': 'http://www.xes-standard.org/org.xesext'
                }),
            Element(
                'extension', {
                    'name': 'Lifecycle',
                    'prefix': 'lifecycle',
                    'uri': 'http://www.xes-standard.org/lifecycle.xesext'
                }),
            Element(
                'classifier', {
                    'name': 'Activity',
                    'keys': 'concept:name'
                }),
            Element(
                'classifier', {
                    'name': "(Event Name AND Lifecycle transition)",
                    'keys': "concept:name lifecycle:transition"
                }),
            Element(
                'string', {
                    'key': 'concept:name',
                    'value': 'XES Event Log'
                }),
            Comment('Generated using CSV2XES library by https://github.com/marco2012/')
        ]
        tree = ElementTree.parse(self.xes_filepath)
        root = tree.getroot()

        [root.insert(0, ext) for ext in extensions]

        combined_csv = pandas.concat([pandas.read_csv(f, encoding="utf-8-sig") for f in self.csv_filepath])
        timestamp_list = combined_csv[self.timestamp_header].tolist()
        for i, trace in enumerate(root.findall("trace")):
            try:
                trace.insert(0,
                             Element('string', {
                                 'key': 'concept:name',
                                 'value': timestamp_list[i]
                             }))
            except IndexError:
                continue

        tree.write(self.xes_filepath, encoding='UTF-8', xml_declaration=True)

        print(f"[CSV2XES] Created {self.xes_filepath}")
