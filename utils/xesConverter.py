# ******************************
# Convert csv to xes for process mining
# http://www.xes-standard.org/downloads/doc/org/deckfour/xes/factory/XFactory.html
# ******************************

import pandas
from datetime import datetime
from opyenxes.factory.XFactory import XFactory
from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


class CSV2XES:

    def __init__(self, csv_filepath, xes_filepath, csv_separator=',',
                 events_header="event_type", timestamp_header="timestamp", timestamp_format="%Y-%m-%d %H:%M:%S:%f",
                 attributes_to_consider=[]):

        self.csv_filepath = csv_filepath
        self.csv_separator = csv_separator
        self.xes_filepath = xes_filepath
        self.timestamp_header = timestamp_header
        self.timestamp_format = timestamp_format
        self.events_header = events_header

        self.attributes_to_consider = attributes_to_consider
        if self.timestamp_header not in self.attributes_to_consider:
            self.attributes_to_consider.append(self.timestamp_header)
        if self.events_header not in self.attributes_to_consider:
            self.attributes_to_consider.append(self.events_header)

    def __isTimestamp(self, str):
        try:
            datetime.strptime(str, self.timestamp_format)
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
                    attribute = XFactory.create_attribute_timestamp("time:timestamp", datetime.strptime(value, self.timestamp_format))
                except ValueError:
                    continue
            # handle event
            elif column_header == self.events_header:
                attribute = XFactory.create_attribute_literal("concept:name", value)
            # if attributes_to_consider is empty I take all the attributes from csv, else only those in the list
            elif (not self.attributes_to_consider) or (column_header in self.attributes_to_consider):
                attribute = XFactory.create_attribute_literal(column_header, value)
            else:
                continue
            attribute_map[attribute.get_key()] = attribute
        return XFactory.create_event(attribute_map)

    def csvToXes(self):
        # load csv in pandas dataframe and replace nan with None
        # https://www.w3resource.com/pandas/series/series-fillna.php
        df = pandas.read_csv(self.csv_filepath).fillna(method='ffill')

        # create dictionary with column name as key and row data as value, like
        # {'category': 'Browser', 'event_type': 'newTab'}
        if self.attributes_to_consider:
            # if attributes_to_consider is not empty I need to take only certain columns from csv
            dictionary = df[self.attributes_to_consider].to_dict(orient='records')
        else:
            # else take all columns
            dictionary = df.to_dict(orient='records')

        timestamp_list = list()
        log = XFactory.create_log()
        for row in dictionary:
            timestamp = row['timestamp']
            if self.__isTimestamp(timestamp):
                timestamp_list.append(timestamp)
                trace = XFactory.create_trace()
                event = self.__convert_line_in_event(row)
                trace.append(event)
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
                })
        ]
        tree = ElementTree.parse(self.xes_filepath)
        root = tree.getroot()

        for ext in extensions:
            root.insert(0, ext)

        # timestamp_list = read_csv(self.csv_filepath, usecols=[self.timestamp_header])[self.timestamp_header].tolist()
        for i, trace in enumerate(root.findall("trace")):
            try:
                trace.insert(0, Element(
                        'string', {
                            'key': 'concept:name',
                            'value': timestamp_list[i]
                        }
                    )
                )
            except IndexError:
                continue

        tree.write(self.xes_filepath, encoding='UTF-8', xml_declaration=True)

        print(f"[CSV2XES] Created {self.xes_filepath}")
