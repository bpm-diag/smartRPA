# ******************************
# Convert csv to xes for process mining
# http://www.xes-standard.org/downloads/doc/org/deckfour/xes/factory/XFactory.html
# ******************************
from threading import Thread

import pandas
from datetime import datetime
from opyenxes.factory.XFactory import XFactory
from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


class CSV2XES:
    """This class convert csv to xes

    :param csv_file_path: List of csv files to convert (list of strings representing the path of each csv). Each csv generates a trace in xes file
    :param xes_filepath: Path of resulting xes file
    :param events_header: Name of the column in csv containing events
    :param timestamp_header: Name of the column in csv containing timestamps
    :param timestamp_format: Format of timestamps to be parsed
    :param attributes_to_consider: include only certain attributes in resulting xes, if empty include all attributes
    :return: boolean indicating success status
    :rtype: bool
    """

    def __init__(self, csv_filepath: list, xes_filepath: str,
                 events_header="event_type", timestamp_header="timestamp", timestamp_format="%Y-%m-%d %H:%M:%S:%f",
                 attributes_to_consider=[]):

        self.csv_filepath = csv_filepath
        self.xes_filepath = xes_filepath
        self.timestamp_header = timestamp_header
        self.timestamp_format = timestamp_format
        self.events_header = events_header

        self.attributes_to_consider = attributes_to_consider
        # if self.attributes_to_consider is not empty, add timestamp and event fields because they are required
        # if self.attributes_to_consider is empty it means I should consider all events
        if self.attributes_to_consider and self.timestamp_header not in self.attributes_to_consider:
            self.attributes_to_consider.append(self.timestamp_header)
        if self.attributes_to_consider and self.events_header not in self.attributes_to_consider:
            self.attributes_to_consider.append(self.events_header)

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
                    attribute = XFactory.create_attribute_timestamp("time:timestamp",
                                                                    datetime.strptime(value, self.timestamp_format))
                except ValueError:
                    continue

            # handle event
            elif column_header == self.events_header:
                attribute = XFactory.create_attribute_literal("concept:name", value)

            # if attributes_to_consider is empty I take all the attributes from csv, else only those in the list
            elif (self.attributes_to_consider == []) or (column_header in self.attributes_to_consider):
                attribute = XFactory.create_attribute_literal(column_header, value)

            else:
                continue

            attribute_map[attribute.get_key()] = attribute
        return XFactory.create_event(attribute_map)

    # create xml log, inserting a trace for each csv file
    def csvToXes(self):

        log = XFactory.create_log()
        # timestamp_list_total = list()

        for csv_path in self.csv_filepath:

            # load csv in pandas dataframe and replace nan with None
            # https://www.w3resource.com/pandas/series/series-fillna.php
            try:
                df = pandas.read_csv(csv_path, encoding="latin").fillna(method='ffill')
            except UnicodeDecodeError as e:
                print(f"[CSV2XES] Could not decode {csv_path}: {e}")
                return False

            # create dictionary with column name as key and row data as value, like
            # {'category': 'Browser', 'event_type': 'newTab'}

            # if attributes_to_consider is not empty I need to take only certain columns from csv
            if self.attributes_to_consider:
                dictionary = df[self.attributes_to_consider].to_dict(orient='records')
            # else take all columns
            else:
                dictionary = df.to_dict(orient='records')

            # timestamp_list = list()
            events = list()
            for row in dictionary:
                timestamp = row['timestamp']
                if self.__isTimestamp(timestamp):
                    # timestamp_list.append(timestamp)
                    event = self.__convert_line_in_event(row)
                    events.append(event)
                else:
                    print(f"[CSV2XES] Can't decode timestamp {timestamp} with format {self.timestamp_format}")
                    continue

            trace = XFactory.create_trace()
            [trace.append(e) for e in events]
            log.append(trace)
            # timestamp_list_total.extend(timestamp_list)

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
                })
        ]
        tree = ElementTree.parse(self.xes_filepath)
        root = tree.getroot()

        for ext in extensions:
            root.insert(0, ext)

        combined_csv = pandas.concat([pandas.read_csv(f, encoding="latin") for f in self.csv_filepath])
        timestamp_list = combined_csv[self.timestamp_header].tolist()
        # timestamp_list = read_csv(csv_path, usecols=[self.timestamp_header])[self.timestamp_header].tolist()
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
