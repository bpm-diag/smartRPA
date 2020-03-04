# ******************************
# Convert csv to xes for process mining
# http://www.xes-standard.org/downloads/doc/org/deckfour/xes/factory/XFactory.html
# ******************************

from datetime import datetime
import utils.utils
import os
from opyenxes.factory.XFactory import XFactory
from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


def csvToXes(csv_filepath):

    # leave this list EMPTY if you want to take ALL attributes of csv
    ATTRIBUTES_TO_CONSIDER = ["category", "application", "event_src_path", "event_dest_path", "clipboard_content"]

    def _convert_line_in_event(type_for_attribute: dict, attribute_list: list):
        attribute_map = XFactory.create_attribute_map()
        for index in range(0, len(attribute_list)):
            attribute_string = attribute_list[index]
            attribute_type = type_for_attribute.get(str(index))
            if attribute_type == "timestamp":
                attribute = XFactory.create_attribute_timestamp("time:timestamp", datetime.strptime(attribute_string, "%Y-%m-%d %H:%M:%S:%f"))
            elif attribute_type == "event_type":
                attribute = XFactory.create_attribute_literal("concept:name", attribute_string)
            # if ATTRIBUTES_TO_CONSIDER is empty I take all the attributes from csv, else only those in the list
            elif (not ATTRIBUTES_TO_CONSIDER) or (attribute_type in ATTRIBUTES_TO_CONSIDER):
                attribute = XFactory.create_attribute_literal(attribute_type, attribute_string)
            else:
                continue

            attribute_map[attribute.get_key()] = attribute
        return XFactory.create_event(attribute_map)

    with open(csv_filepath) as file:
        dictionary = {}
        first_line = file.readline().split(",")
        for i in range(len(first_line)):
            dictionary[str(i)] = first_line[i].strip("\n")
        first_event = file.readline().split(",")
        log = XFactory.create_log()
        trace = XFactory.create_trace()
        trace.append(_convert_line_in_event(dictionary, first_event))
        for line in file.readlines():
            line_list = line.split(",")
            event = _convert_line_in_event(dictionary, line_list)
            log.append(trace)
            trace = XFactory.create_trace()
            trace.append(event)

    # Save log in xes format
    csv_filename = utils.utils.getFilename(csv_filepath)
    xes_filepath = os.path.join(utils.utils.MAIN_DIRECTORY, 'RPA', csv_filename, csv_filename + '.xes')
    with open(xes_filepath, "w") as file:
        XesXmlSerializer().serialize(log, file)

    # Add elements to xes format
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
    tree = ElementTree.parse(xes_filepath)
    root = tree.getroot()
    # trace = tree.find('trace')
    for ext in extensions:
        root.insert(0, ext)
    tree.write(xes_filepath)

    print(f"[XES CONVERTER] Created {os.path.join('RPA', csv_filename, csv_filename + '.xes')}")
