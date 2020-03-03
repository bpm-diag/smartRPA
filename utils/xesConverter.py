# ******************************
# Convert csv to xes for process mining
# http://www.xes-standard.org/downloads/doc/org/deckfour/xes/factory/XFactory.html
# ******************************

from datetime import datetime
from pprint import pprint
import utils.utils
import os
from opyenxes.factory.XFactory import XFactory
from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer

def csvToXes(csv_filepath):

    def _convert_line_in_event(type_for_attribute: dict, attribute_list: list):
        attribute_map = XFactory.create_attribute_map()
        for index in range(0, len(attribute_list)):
            attribute_string = attribute_list[index]
            attribute_type = type_for_attribute.get(str(index))
            if attribute_type == "timestamp":
                attribute = XFactory.create_attribute_timestamp("timestamp", datetime.strptime(attribute_string, "%Y-%m-%d %H:%M:%S:%f"))
            elif attribute_type in ["event_type", "category", "application", "event_src_path", "event_dest_path", "clipboard_content"]:
                attribute = XFactory.create_attribute_literal(attribute_type, attribute_string)
            else:
                continue
            attribute_map[attribute.get_key()] = attribute
            pprint(attribute_map)
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
        print(f"[XES CONVERTER] Created Xes file from {os.path.basename(csv_filepath)}")
