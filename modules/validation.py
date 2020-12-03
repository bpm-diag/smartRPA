from datetime import datetime, timedelta
import faker
import random
import string
import pandas
from functools import reduce
import operator
import time
from modules.decisionPoints import DecisionPoints
from multiprocessing import Queue
import utils.utils
import csv
import numpy as np


# class ValidationOld:
#
#     def __init__(self, log_size: int, trace_size: int, events_size: int, decision_points: int):
#         #  parameters
#         self.log_size = log_size
#         self.trace_size = trace_size
#         self.events_size = events_size
#         self.decision_points = decision_points
#         # self.outgoing_arcs = outgoing_arcs
#
#         # fake data
#         self.fake_data()
#
#         # events
#         self.handleEvents()
#
#     # events
#     def handleEvents(self):
#         browser = [
#             "urlHashChange",
#             "contextMenu",
#             "clickCheckboxButton",
#             "clickRadioButton",
#             "navigateTo",
#             "clickTextField",
#             "clickButton",
#             "clickLink",
#             "selectOptions",
#             "selectText",
#             "submit",
#             "changeField",
#             "doubleClick",
#             "dragElement",
#             "cancelDialog",
#             "fullscreen",
#             "attachTab",
#             "detachTab",
#             "newBookmark",
#             "removeBookmark",
#             "modifyBookmark",
#             "moveBookmark",
#             "startDownload",
#             "erasedDownload",
#             "installBrowserExtension",
#             "uninstallBrowserExtension",
#             "enableBrowserExtension",
#             "disableBrowserExtension",
#             "closedNotification",
#             "clickedNotification",
#             "newWindow",
#             "closeWindow",
#             "newTab",
#             "closeTab",
#             "moveTab",
#             "mutedTab",
#             "unmutedTab",
#             "pinnedTab",
#             "unpinnedTab",
#             "audibleTab",
#             "zoomTab",
#             "changeHistory",
#             "link",
#             "typed",
#             "form_submit",
#             "reload"
#         ]
#         os = [
#             "created",
#             "modified",
#             "deleted",
#             "Mount",
#             "Unmount",
#             "moved",
#             "programOpen",
#             "programClose",
#             "selectFile",
#             "selectFolder",
#             "hotkey",
#             "insertUSB",
#             "printSubmitted",
#             "openFile",
#             "openFolder"
#         ]
#         clipboard = [
#             "copy",
#             "paste",
#             "cut"
#         ]
#         excel = [
#             "openWindow",
#             "closeWindow",
#             "resizeWindow",
#             "newWorkbook",
#             "openWorkbook",
#             "addWorksheet",
#             "beforeSaveWorkbook",
#             "saveWorkbook",
#             "printWorkbook",
#             "closeWorkbook",
#             "activateWorkbook",
#             "deactivateWorkbook",
#             "modelChangeWorkbook",
#             "newChartWorkbook",
#             "afterCalculate",
#             "selectWorksheet",
#             "deleteWorksheet",
#             "doubleClickCellWithValue",
#             "doubleClickEmptyCell",
#             "rightClickCellWithValue",
#             "rightClickEmptyCell",
#             "sheetCalculate",
#             "editCellSheet",
#             "deselectWorksheet",
#             "followHiperlinkSheet",
#             "pivotTableValueChangeSheet",
#             "getRange",
#             "getCell",
#             "worksheetTableUpdated",
#             "addinInstalledWorkbook",
#             "addinUninstalledWorkbook",
#             "XMLImportWorkbook",
#             "XMLExportWorkbook"
#         ]
#         word = [
#             "activateWindow",
#             "deactivateWindow",
#             "doubleClickWindow",
#             "rightClickWindow",
#             "newDocument",
#             "openDocument",
#             "changeDocument",
#             "saveDocument",
#             "printDocument"
#         ]
#         powerpoint = [
#             "activateWindow",
#             "deactivateWindow",
#             "rightClickPresentation",
#             "doubleClickPresentation",
#             "newPresentation",
#             "newPresentationSlide",
#             "closePresentation",
#             "savePresentation",
#             "openPresentation",
#             "printPresentation",
#             "slideshowBegin",
#             "nextSlideshow",
#             "clickNextSlideshow",
#             "previousSlideshow",
#             "slideshowEnd",
#             "SlideSelectionChanged"
#         ]
#
#         # events_dict = {
#         #    'Browser': browser,
#         #    'OperatingSystem': os + clipboard,
#         #    'MicrosoftOffice': excel + word + powerpoint
#         # }
#
#         self.events_reverse = {
#             str(browser): 'Browser',
#             str(os): 'OperatingSystem',
#             str(clipboard): 'OperatingSystem',
#             str(excel): 'Microsoft Excel',
#             str(word): 'Microsoft Word',
#             str(powerpoint): 'Microsoft PowerPoint'
#         }
#
#         self.excluded_events = []
#
#         categories = [browser, os + clipboard, excel + word + powerpoint]
#         amountOfCategoriesToTake = self.decision_points if self.decision_points <= len(categories) else len(categories)
#         self.categories_to_take = random.sample(categories, amountOfCategoriesToTake)
#         # print(self.categories_to_take)
#         self.events_sample = reduce(operator.concat, self.categories_to_take)
#
#         # categories = [browser, os + clipboard, excel, word, powerpoint]
#         # amountOfCategoriesToTake = self.decision_points if self.decision_points <= len(categories) else len(categories)
#         # categories_to_take = random.sample(categories, amountOfCategoriesToTake)
#         # categories_str = ["Browser", "OperatingSystem",
#         #                  "Microsoft Excel", "Microsoft Word", "Microsoft PowerPoint"]
#         # indexes_to_take = [categories.index(c) for c in categories_to_take]
#         # self.categories_str_to_take = [categories_str[x] for x in indexes_to_take]
#         # self.events_sample = reduce(operator.concat, self.categories_to_take)
#
#         # cat1 = [browser, os, clipboard]
#         # cat2 = [excel, word, powerpoint]
#         # amountOfCategoriesToTake = self.decision_points if self.decision_points <= len(cat1+cat2) else len(cat1+cat2)
#         # firstHalf = int()
#
#         if len(self.events_sample) > self.events_size:
#             self.events_sample = random.sample(self.events_sample, self.events_size)
#         # print(self.events_sample)
#
#     # fake data
#     def fake_data(self):
#         self.fake = faker.Faker()
#         n = 20
#         urls = [self.fake.url() for _ in range(int(n / 2))]
#         urls += [u + self.fake.word() for u in urls]
#         self.urls = urls
#         self.apps = ["SublimeText", "VisualStudioCode", "Notepad.exe", "Skype"]
#         self.files = [self.fake.file_path() for _ in range(n)]
#         self.clipboard = self.fake.sentences(n)
#         self.words = [""] + self.fake.words(n - 1)
#         self.workbooks = [f"Workbook{i}" for i in range(1, n)]
#         self.sheets = [f"Sheet{i}" for i in range(1, n)]
#         self.cell_ranges = [f"{random.choice(string.ascii_uppercase)}{random.randint(0, 20)}" for _ in range(n)]
#         self.eventQual = ['[]', '["serverRedirect","fromAddressBar"]', '["fromAddressBar"]', '["serverRedirect"]']
#         self.tag_category = ["", "A", "DIV", "IMG", "INPUT", "BUTTON"]
#         self.tag_type = {'INPUT': 'text', 'BUTTON': 'submit'}
#         self.tag_name = self.words
#         self.tag_value = ["", "True", "False"] + self.words
#         self.browser_id = ["", "click_btn", "check_link", "input_text"]
#         web_elems = ['div', 'section', 'image', 'button', 'html', 'div', 'body', 'aside', 'url', 'a', 'li']
#         self.xpath = [
#             f'id("{random.choice(self.words)}")',
#             f'id("{random.choice(self.words)}/{random.choice(web_elems)}[{random.randint(0, 4)}]")',
#             f'id("{random.choice(self.words)}/{random.choice(web_elems)}[{random.randint(0, 4)}]/{random.choice(web_elems)}[{random.randint(0, 4)}]")'
#         ]
#         self.slides = [list(range(random.randint(1, 6))) for _ in range(n)]
#         self.hotkeys = {
#             'alt+d': 'Select address bar',
#             'alt+F4': 'Close window',
#             'alt+esc': 'Cycle through windows',
#             'alt+tab': 'Cycle through open apps',
#             'alt+enter': 'Display item properties',
#             'alt+space+n': 'Minimise window',
#             'alt+space+x': 'Maximise window',
#             'ctrl+a': 'Select all',
#             # 'ctrl+c': 'Copy', # handled by clipboardEvents
#             'ctrl+d': 'Delete selected item',
#             'ctrl+e': 'Select search box',
#             'ctrl+f': 'Find',
#             'ctrl+h': 'Find and replace',
#             'ctrl+n': 'New',
#             'ctrl+r': 'Refresh',
#             'ctrl+s': 'Save',
#             'ctrl+p': 'Print',
#             # 'ctrl+v': 'Paste',
#             'ctrl+w': 'Close window',
#             'ctrl+x': 'Cut',
#             'ctrl+y': 'Undo',
#             'ctrl+z': 'Redo',
#             'ctrl+shift+t': 'Reopen closed tab',
#             'win+tab': 'Cycle through apps',
#             'win+d': 'Show/Hide desktop',
#             'win+e': 'Open explorer',
#             'win+f': 'Search for files',
#             'win+i': 'Open settings',
#             'win+m': 'Minimize all windows',
#             'win+p': 'Choose presentation display mode',
#             'win+r': 'Run',
#             'F1': 'Help',
#             'F2': 'Rename',
#             'F3': 'Search',
#             'F5': 'Refresh',
#         }
#
#     # timestamp
#     def generateISOTimestamp(self):
#         return self.fake.date_time_this_year().isoformat()
#
#     def addSecondsToISOTimestamp(self, ts):
#         return (datetime.fromisoformat(ts) + timedelta(seconds=random.randint(1, 60))).isoformat(
#             timespec='milliseconds')
#
#     def generateCaseId(self, ts):
#         return datetime.fromisoformat(ts).strftime('%m%d%H%M%S%f')
#
#     # compare dictionaries ignoring specific keys
#     def equal_dicts(self, a, b, ignore_keys=None):
#         if ignore_keys is None:
#             ignore_keys = ['case:concept:name', 'time:timestamp', 'org:resource']
#         if a is None or b is None:
#             return False
#         ka = set(a).difference(ignore_keys)
#         kb = set(b).difference(ignore_keys)
#         return ka == kb and all(a[k] == b[k] for k in ka)
#
#     # events
#     def generateEvent(self, caseid="", username="", timestamp="", category=-1):
#
#         if category == 0:
#             if self.decision_points % 2 != 0:  #  3,5
#                 events_to_choose = list(set(self.categories_to_take[0]) - set(self.excluded_events))
#             else:  # 2,4
#                 events_sample = reduce(operator.concat, self.categories_to_take[0:2])
#                 events_to_choose = list(set(events_sample) - set(self.excluded_events))
#         elif category == 1:
#             if self.decision_points % 2 != 0:  #  3,5
#                 events_sample = reduce(operator.concat, self.categories_to_take[1:])
#             else:  # 2,4
#                 events_sample = reduce(operator.concat, self.categories_to_take[2:])
#             events_to_choose = list(set(events_sample) - set(self.excluded_events))
#         else:
#             events_to_choose = list(set(self.events_sample) - set(self.excluded_events))
#         concept_name = random.choice(events_to_choose)
#         random_category = random.choice([category for events, category in self.events_reverse.items()
#                                          if concept_name in events])  # and category in self.categories_str_to_take])
#         category = random_category
#
#         application, clipboard_content, event_src_path, event_dest_path, \
#         browser_url, current_worksheet, eventQual, hotkey, description, \
#         workbook, worksheets, cell_content, cell_range, tag_category, \
#         tag_type, tag_value, tag_name, browser_id, xpath, slides, title = [""] * 21
#
#         # Office
#         if random_category in ["Microsoft Excel", "Microsoft Word", "Microsoft PowerPoint"]:
#             category = "MicrosoftOffice"
#             application = random_category
#             if 'save' in concept_name:
#                 event_src_path = random.choice(self.files)
#             if application == "Microsoft Excel":
#                 workbook = random.choice(self.workbooks)
#                 worksheets = random.sample(self.sheets, random.randint(1, 2))
#                 current_worksheet = worksheets[0]
#                 cell_content = random.choice(self.words)
#                 cell_range = random.choice(self.cell_ranges)
#             elif application == "Microsoft Word":
#                 event_src_path = random.choice(self.files)
#                 title = random.choice(self.words)
#             elif application == "Microsoft PowerPoint":
#                 slides = ', '.join(map(str, random.choice(self.slides)))
#                 event_src_path = random.choice(self.files)
#         # Clipboard
#         elif random_category == "Clipboard":
#             application = "Clipboard"
#             clipboard_content = random.choice(self.clipboard)
#         #  OS
#         elif random_category == "OperatingSystem":
#             if concept_name in ['programOpen', 'programClose']:
#                 application = random.choice(self.apps)
#             elif concept_name == "hotkey":
#                 hotkey = random.choice(list(self.hotkeys.keys()))
#                 description = self.hotkeys.get(hotkey)
#             else:
#                 application = "Explorer"
#                 event_src_path = random.choice(self.files)
#                 if concept_name == "moved":
#                     event_dest_path = random.choice(self.files)
#         # Browser
#         elif random_category == "Browser":
#             application = "Chrome"
#             browser_url = random.choice(self.urls)
#             eventQual = random.choices(self.eventQual, weights=(60, 20, 20, 20))[0]
#             tag_category = random.choices(self.tag_category, weights=(40, 20, 20, 20, 20, 20))[0]
#             tag_type = self.tag_type.get(tag_category, "")
#             tag_name = random.choice(self.tag_name)
#             tag_value = random.choice(self.tag_value)
#             browser_id = random.choices(self.browser_id, weights=(70, 10, 10, 10))[0]
#             xpath = random.choice(self.xpath)
#
#         return {
#             "case:concept:name": caseid,
#             "case:creator": "SmartRPA by marco2012",
#             "lifecycle:transition": "complete",
#             "time:timestamp": timestamp,
#             "org:resource": username,
#             "category": category,
#             "application": application,
#             "concept:name": concept_name,
#             "event_src_path": event_src_path,
#             "event_dest_path": event_dest_path,
#             "clipboard_content": clipboard_content,
#             "mouse_coord": "",
#             "workbook": workbook,
#             "current_worksheet": current_worksheet,
#             "worksheets": worksheets,
#             "sheets": "",
#             "cell_content": cell_content,
#             "cell_range": cell_range,
#             "cell_range_number": "",
#             "window_size": "",
#             "slides": slides,
#             "effect": "",
#             "hotkey": hotkey,
#             "id": browser_id,
#             "title": title,
#             "description": description,
#             "browser_url": browser_url,
#             "eventQual": eventQual,
#             "tab_moved_from_index": "",
#             "tab_moved_to_index": "",
#             "newZoomFactor": "",
#             "oldZoomFactor": "",
#             "tab_pinned": "",
#             "tab_audible": "",
#             "tab_muted": "",
#             "window_ingognito": "",
#             "file_size": "",
#             "tag_category": tag_category,
#             "tag_type": tag_type,
#             "tag_name": tag_name,
#             "tag_title": "",
#             "tag_value": tag_value,
#             "tag_checked": "",
#             "tag_html": "",
#             "tag_href": "",
#             "tag_innerText": "",
#             "tag_option": "",
#             "tag_attributes": "",
#             "xpath": xpath,
#             "xpath_full": xpath
#         }
#
#     def generateDataframe(self):
#         series = []
#
#         #  imposta estremi
#         half_trace_size = int(self.trace_size / 2)
#         min_rows_not_duplicated = []
#         max_rows_not_duplicated = []
#         # all true rows at beginning or end of trace
#         if self.decision_points in [1, 2]:
#             # select random amount (at most half) of first or last rows per trace to duplicate
#             # minimum_false_rows = 1
#             # start = random.randint(minimum_false_rows, self.trace_size)
#             # end = random.randint(0, self.trace_size - minimum_false_rows)
#             start = random.randint(half_trace_size, self.trace_size - 1)  # from here on
#             end = random.randint(0, half_trace_size)  # until here
#             l = list(range(0, self.trace_size))
#             try:
#                 random_duplicated_indexes = random.choice(list(filter(None, [l[start:], l[:end]])))
#             except Exception:
#                 random_duplicated_indexes = [0, 1]
#         # true rows in the middle of the trace
#         elif self.decision_points >= 3:
#             # start = random.randint(half_trace_size, self.trace_size - 2) #from here on
#             # end = random.randint(1, half_trace_size) #until here
#             # shift = random.randint(1,half_trace_size)
#             # l = list(range(shift, self.trace_size-end))
#             # try:
#             #    random_duplicated_indexes = random.choice(list(filter(None, [l[start:], l[:end]])))
#             # except Exception:
#             #    random_duplicated_indexes = [1,2]
#             # print(start,end,l,random_duplicated_indexes)
#
#             # random start index
#             start = random.randint(half_trace_size, self.trace_size - 2)  # from here on
#             # random end index
#             end = random.randint(2, half_trace_size)  # until here
#             shift = random.randint(2, half_trace_size)
#             l = list(range(shift, self.trace_size - end))
#             try:
#                 # all the rows with these indices should be duplicated
#                 random_duplicated_indexes = random.choice(list(filter(None, [l[start:], l[:end]])))
#                 rows_before_duplicated = list(range(0, l[0]))
#                 rows_after_duplicated = list(range(l[-1] + 1, self.trace_size))
#             except Exception:
#                 random_duplicated_indexes = [2, 3]
#                 rows_before_duplicated = [0, 1]
#                 rows_after_duplicated = list(range(4, self.trace_size))
#             # all the rows with these indices should have the same category
#             min_rows_not_duplicated = rows_before_duplicated if len(rows_before_duplicated) <= len(
#                 rows_after_duplicated) else rows_after_duplicated
#             # all the remain non duplicated rows should have more than 1 category
#             max_rows_not_duplicated = rows_before_duplicated if rows_before_duplicated != min_rows_not_duplicated else rows_after_duplicated
#
#         else:
#             # list of indices indicating duplicate rows
#             #  take a random amount of indices (>=1 and <= half the trace size) in each trace
#             random_duplicated_indexes = random.sample(
#                 range(0, self.trace_size),
#                 random.randint(1, int(self.trace_size / 2))
#             )
#         print(f"Duplicated rows: {random_duplicated_indexes}")
#
#         duplicated_events = {}
#         for index in random_duplicated_indexes:
#             e = self.generateEvent()
#             duplicated_events[index] = e
#             self.excluded_events.append(e['concept:name'])
#
#         for trace in range(self.log_size):
#             timestamp = self.generateISOTimestamp()
#             caseid = self.generateCaseId(timestamp)
#             username = self.fake.simple_profile()['username']
#
#             for event in range(self.trace_size):
#                 timestamp = self.addSecondsToISOTimestamp(timestamp)
#                 duplicated_event = duplicated_events.get(event)
#                 if event in min_rows_not_duplicated:
#                     random_event = self.generateEvent(caseid, username, timestamp, category=0)
#                 elif event in max_rows_not_duplicated:
#                     random_event = self.generateEvent(caseid, username, timestamp, category=1)
#                 else:
#                     random_event = self.generateEvent(caseid, username, timestamp)
#                 # min_rows_event = min_rows_not_duplicated_events.get(event)
#                 # print(event, min_rows_event)
#                 # max_rows_event = max_rows_not_duplicated.get(event)
#                 if duplicated_event:
#                     # need to create copy of object otherwise fields of the original would be modified
#                     tmp = duplicated_event.copy()
#                     tmp['case:concept:name'] = caseid
#                     tmp['org:resource'] = username
#                     tmp['time:timestamp'] = timestamp
#                 else:
#                     tmp = random_event
#                 series.append(tmp)
#
#         return pandas.DataFrame(series)
#
#     def test(self):
#         return self.generateDataframe()


# class Validation:
#     def __init__(self, log_size: int, trace_size: int, events_size: int, decision_points: int):
#         #  parameters
#         self.log_size = log_size
#         self.trace_size = trace_size
#         self.events_size = events_size
#         self.decision_points = decision_points
#         # fake data
#         self.fake_data()
#         self.handleEvents()
#         self.excluded_events = []
#
#     def handleEvents(self):
#         browser = [
#             "urlHashChange",
#             "contextMenu",
#             "clickCheckboxButton",
#             "clickRadioButton",
#             "navigateTo",
#             "clickTextField",
#             "clickButton",
#             "clickLink",
#             "selectOptions",
#             "selectText",
#             "submit",
#             "changeField",
#             "doubleClick",
#             "dragElement",
#             "cancelDialog",
#             "fullscreen",
#             "attachTab",
#             "detachTab",
#             "newBookmark",
#             "removeBookmark",
#             "modifyBookmark",
#             "moveBookmark",
#             "startDownload",
#             "erasedDownload",
#             "installBrowserExtension",
#             "uninstallBrowserExtension",
#             "enableBrowserExtension",
#             "disableBrowserExtension",
#             "closedNotification",
#             "clickedNotification",
#             "newWindow",
#             "closeWindow",
#             "newTab",
#             "closeTab",
#             "moveTab",
#             "mutedTab",
#             "unmutedTab",
#             "pinnedTab",
#             "unpinnedTab",
#             "audibleTab",
#             "zoomTab",
#             "changeHistory",
#             "link",
#             "typed",
#             "form_submit",
#             "reload"
#         ]
#         os = [
#             "created",
#             "modified",
#             "deleted",
#             "Mount",
#             "Unmount",
#             "moved",
#             "programOpen",
#             "programClose",
#             "selectFile",
#             "selectFolder",
#             "hotkey",
#             "insertUSB",
#             "printSubmitted",
#             "openFile",
#             "openFolder"
#         ]
#         clipboard = [
#             "copy",
#             "paste",
#             "cut"
#         ]
#         excel = [
#             "openWindow",
#             "closeWindow",
#             "resizeWindow",
#             "newWorkbook",
#             "openWorkbook",
#             "addWorksheet",
#             "beforeSaveWorkbook",
#             "saveWorkbook",
#             "printWorkbook",
#             "closeWorkbook",
#             "activateWorkbook",
#             "deactivateWorkbook",
#             "modelChangeWorkbook",
#             "newChartWorkbook",
#             "afterCalculate",
#             "selectWorksheet",
#             "deleteWorksheet",
#             "doubleClickCellWithValue",
#             "doubleClickEmptyCell",
#             "rightClickCellWithValue",
#             "rightClickEmptyCell",
#             "sheetCalculate",
#             "editCellSheet",
#             "deselectWorksheet",
#             "followHiperlinkSheet",
#             "pivotTableValueChangeSheet",
#             "getRange",
#             "getCell",
#             "worksheetTableUpdated",
#             "addinInstalledWorkbook",
#             "addinUninstalledWorkbook",
#             "XMLImportWorkbook",
#             "XMLExportWorkbook"
#         ]
#         word = [
#             "activateWindow",
#             "deactivateWindow",
#             "doubleClickWindow",
#             "rightClickWindow",
#             "newDocument",
#             "openDocument",
#             "changeDocument",
#             "saveDocument",
#             "printDocument"
#         ]
#         powerpoint = [
#             "activateWindow",
#             "deactivateWindow",
#             "rightClickPresentation",
#             "doubleClickPresentation",
#             "newPresentation",
#             "newPresentationSlide",
#             "closePresentation",
#             "savePresentation",
#             "openPresentation",
#             "printPresentation",
#             "slideshowBegin",
#             "nextSlideshow",
#             "clickNextSlideshow",
#             "previousSlideshow",
#             "slideshowEnd",
#             "SlideSelectionChanged"
#         ]
#         operatingSystem = os + clipboard
#         office = excel + word + powerpoint
#
#         fourty_percent = int(self.events_size * 0.40)
#         twenty_percent = int(self.events_size * 0.20)
#         self.events_dict = {
#             # take 40% events
#             'Browser': random.sample(browser,
#                                      fourty_percent if len(browser) > fourty_percent else len(browser)),
#             # take 20% events
#             'OperatingSystem': random.sample(operatingSystem,
#                                              twenty_percent if len(operatingSystem) > twenty_percent else len(
#                                                  operatingSystem)),
#             # take 40% events
#             'MicrosoftOffice': random.sample(office,
#                                              fourty_percent if len(office) > fourty_percent else len(office))
#         }
#
#         self.events_reverse = {
#             str(browser): 'Browser',
#             str(os): 'OperatingSystem',
#             str(clipboard): 'OperatingSystem',
#             str(excel): 'Microsoft Excel',
#             str(word): 'Microsoft Word',
#             str(powerpoint): 'Microsoft PowerPoint'
#         }
#         self.office_events_dict = {
#             str(excel): 'Microsoft Excel',
#             str(word): 'Microsoft Word',
#             str(powerpoint): 'Microsoft PowerPoint'
#         }
#
#     # fake data
#     def fake_data(self):
#         self.fake = faker.Faker()
#         n = 20
#         urls = [self.fake.url() for _ in range(int(n / 2))]
#         urls += [u + self.fake.word() for u in urls]
#         self.urls = urls
#         self.apps = ["SublimeText", "VisualStudioCode", "Notepad.exe", "Skype"]
#         self.files = [self.fake.file_path() for _ in range(n)]
#         self.clipboard = self.fake.sentences(n)
#         self.words = [""] + self.fake.words(n - 1)
#         self.workbooks = [f"Workbook{i}" for i in range(1, n)]
#         self.sheets = [f"Sheet{i}" for i in range(1, n)]
#         self.cell_ranges = [f"{random.choice(string.ascii_uppercase)}{random.randint(0, 20)}" for _ in range(n)]
#         self.eventQual = ['[]', '["serverRedirect","fromAddressBar"]', '["fromAddressBar"]', '["serverRedirect"]']
#         self.tag_category = ["", "A", "DIV", "IMG", "INPUT", "BUTTON"]
#         self.tag_type = {'INPUT': 'text', 'BUTTON': 'submit'}
#         self.tag_name = self.words
#         self.tag_value = ["", "True", "False"] + self.words
#         self.browser_id = ["", "click_btn", "check_link", "input_text"]
#         web_elems = ['div', 'section', 'image', 'button', 'html', 'div', 'body', 'aside', 'url', 'a', 'li']
#         self.xpath = [
#             f'id("{random.choice(self.words)}")',
#             f'id("{random.choice(self.words)}/{random.choice(web_elems)}[{random.randint(0, 4)}]")',
#             f'id("{random.choice(self.words)}/{random.choice(web_elems)}[{random.randint(0, 4)}]/{random.choice(web_elems)}[{random.randint(0, 4)}]")'
#         ]
#         self.slides = [list(range(random.randint(1, 6))) for _ in range(n)]
#         self.hotkeys = {
#             'alt+d': 'Select address bar',
#             'alt+F4': 'Close window',
#             'alt+esc': 'Cycle through windows',
#             'alt+tab': 'Cycle through open apps',
#             'alt+enter': 'Display item properties',
#             'alt+space+n': 'Minimise window',
#             'alt+space+x': 'Maximise window',
#             'ctrl+a': 'Select all',
#             # 'ctrl+c': 'Copy', # handled by clipboardEvents
#             'ctrl+d': 'Delete selected item',
#             'ctrl+e': 'Select search box',
#             'ctrl+f': 'Find',
#             'ctrl+h': 'Find and replace',
#             'ctrl+n': 'New',
#             'ctrl+r': 'Refresh',
#             'ctrl+s': 'Save',
#             'ctrl+p': 'Print',
#             # 'ctrl+v': 'Paste',
#             'ctrl+w': 'Close window',
#             'ctrl+x': 'Cut',
#             'ctrl+y': 'Undo',
#             'ctrl+z': 'Redo',
#             'ctrl+shift+t': 'Reopen closed tab',
#             'win+tab': 'Cycle through apps',
#             'win+d': 'Show/Hide desktop',
#             'win+e': 'Open explorer',
#             'win+f': 'Search for files',
#             'win+i': 'Open settings',
#             'win+m': 'Minimize all windows',
#             'win+p': 'Choose presentation display mode',
#             'win+r': 'Run',
#             'F1': 'Help',
#             'F2': 'Rename',
#             'F3': 'Search',
#             'F5': 'Refresh',
#         }
#
#     def generateEvent(self, caseid="", username="", timestamp="", category=""):
#
#         if not category:
#             category = random.choice(list(self.events_dict.keys()))
#         try:
#             events_to_choose = list(set(self.events_dict[category]) - set(self.excluded_events))
#         except Exception:
#             events_to_choose = self.events_dict[category]
#         concept_name = random.choice(events_to_choose)
#
#         application, clipboard_content, event_src_path, event_dest_path, \
#         browser_url, current_worksheet, eventQual, hotkey, description, \
#         workbook, worksheets, cell_content, cell_range, tag_category, \
#         tag_type, tag_value, tag_name, browser_id, xpath, slides, title = [""] * 21
#
#         try:
#             category_from_concept_name = random.choice(
#                 [category for events, category in self.office_events_dict.items() if concept_name in events])
#         except Exception:
#             category_from_concept_name = ""
#         # Office
#         if category_from_concept_name in ["Microsoft Excel", "Microsoft Word", "Microsoft PowerPoint"]:
#             application = category_from_concept_name
#             if 'save' in concept_name:
#                 event_src_path = random.choice(self.files)
#             if application == "Microsoft Excel":
#                 workbook = random.choice(self.workbooks)
#                 worksheets = random.sample(self.sheets, random.randint(1, 2))
#                 current_worksheet = worksheets[0]
#                 cell_content = random.choice(self.words)
#                 cell_range = random.choice(self.cell_ranges)
#             elif application == "Microsoft Word":
#                 event_src_path = random.choice(self.files)
#                 title = random.choice(self.words)
#             elif application == "Microsoft PowerPoint":
#                 slides = ', '.join(map(str, random.choice(self.slides)))
#                 event_src_path = random.choice(self.files)
#         # Clipboard
#         elif category == "Clipboard":
#             application = "Clipboard"
#             clipboard_content = random.choice(self.clipboard)
#         #  OS
#         elif category == "OperatingSystem":
#             if concept_name in ['programOpen', 'programClose']:
#                 application = random.choice(self.apps)
#             elif concept_name == "hotkey":
#                 hotkey = random.choice(list(self.hotkeys.keys()))
#                 description = self.hotkeys.get(hotkey)
#             elif concept_name in ["cut", "copy", "paste"]:
#                 # category = "Clipboard"
#                 application = "Clipboard"
#                 clipboard_content = random.choice(self.clipboard)
#             else:
#                 application = "Explorer"
#                 event_src_path = random.choice(self.files)
#                 if concept_name == "moved":
#                     event_dest_path = random.choice(self.files)
#         # Browser
#         elif category == "Browser":
#             application = "Chrome"
#             browser_url = random.choice(self.urls)
#             eventQual = random.choices(self.eventQual, weights=(60, 20, 20, 20))[0]
#             tag_category = random.choices(self.tag_category, weights=(40, 20, 20, 20, 20, 20))[0]
#             tag_type = self.tag_type.get(tag_category, "")
#             tag_name = random.choice(self.tag_name)
#             tag_value = random.choice(self.tag_value)
#             browser_id = random.choices(self.browser_id, weights=(70, 10, 10, 10))[0]
#             xpath = random.choice(self.xpath)
#
#         return {
#             "case:concept:name": caseid,
#             "case:creator": "SmartRPA by marco2012",
#             "lifecycle:transition": "complete",
#             "time:timestamp": timestamp,
#             "org:resource": username,
#             "category": category,
#             "application": application,
#             "concept:name": concept_name,
#             "event_src_path": event_src_path,
#             "event_dest_path": event_dest_path,
#             "clipboard_content": clipboard_content,
#             "mouse_coord": "",
#             "workbook": workbook,
#             "current_worksheet": current_worksheet,
#             "worksheets": worksheets,
#             "sheets": "",
#             "cell_content": cell_content,
#             "cell_range": cell_range,
#             "cell_range_number": "",
#             "window_size": "",
#             "slides": slides,
#             "effect": "",
#             "hotkey": hotkey,
#             "id": browser_id,
#             "title": title,
#             "description": description,
#             "browser_url": browser_url,
#             "eventQual": eventQual,
#             "tab_moved_from_index": "",
#             "tab_moved_to_index": "",
#             "newZoomFactor": "",
#             "oldZoomFactor": "",
#             "tab_pinned": "",
#             "tab_audible": "",
#             "tab_muted": "",
#             "window_ingognito": "",
#             "file_size": "",
#             "tag_category": tag_category,
#             "tag_type": tag_type,
#             "tag_name": tag_name,
#             "tag_title": "",
#             "tag_value": tag_value,
#             "tag_checked": "",
#             "tag_html": "",
#             "tag_href": "",
#             "tag_innerText": "",
#             "tag_option": "",
#             "tag_attributes": "",
#             "xpath": xpath,
#             "xpath_full": xpath
#         }
#
#     # timestamp
#     def generateISOTimestamp(self):
#         return self.fake.date_time_this_year().isoformat()
#
#     def addSecondsToISOTimestamp(self, ts):
#         return (datetime.fromisoformat(ts) + timedelta(seconds=random.randint(1, 60))).isoformat(
#             timespec='milliseconds')
#
#     def generateCaseId(self, ts):
#         return datetime.fromisoformat(ts).strftime('%m%d%H%M%S%f')
#
#     def generateIndexes(self):
#         if self.decision_points in [1, 2]:
#             split_size = 2
#         elif self.decision_points in [3, 4]:
#             split_size = 3
#         else:
#             split_size = 5
#         chunks = [*np.array_split(range(0, self.trace_size), split_size)]
#         return [x.tolist() for x in chunks]
#
#     def generateDuplicatedEvents(self, indexes, duplicated_events=None):
#         if not duplicated_events:
#             duplicated_events = {}
#         for index in indexes:
#             e = self.generateEvent()
#             duplicated_events[index] = e
#             self.excluded_events.append(e['concept:name'])
#         return duplicated_events
#
#     def split_list(self, a_list):
#         half = len(a_list) // 2
#         return a_list[:half], a_list[half:]
#
#     def handleEvent(self, event, indexes,
#                     firstCat, secondCat, thirdCat,
#                     timestamp, caseid, username):
#
#         # for i in [0, 2, 4]:
#         #     if len(indexes) > i and event in indexes[i]:
#         #         if self.decision_points % 2 == 1:
#         #             cat = thirdCat
#         #         else:
#         #             first_half, second_half = self.split_list(indexes[i])
#         #             cat = firstCat if event in first_half else secondCat
#         #         tmp = self.generateEvent(caseid, username, timestamp, category=cat)
#         #         return tmp
#
#         if event in indexes[0]:
#             if self.decision_points == 1:
#                 cat = firstCat
#             else:
#                 first_half, second_half = self.split_list(indexes[0])
#                 if event in first_half:
#                     cat = firstCat
#                 elif event in second_half:
#                     cat = secondCat
#             tmp = self.generateEvent(caseid, username, timestamp, category=cat)
#         elif len(indexes) > 2 and event in indexes[2]:
#             if self.decision_points == 3:
#                 cat = thirdCat
#             else:
#                 first_half, second_half = self.split_list(indexes[2])
#                 if event in first_half:
#                     cat = firstCat
#                 elif event in second_half:
#                     cat = secondCat
#             tmp = self.generateEvent(caseid, username, timestamp, category=cat)
#         elif len(indexes) > 4 and event in indexes[4]:
#             if self.decision_points == 5:
#                 cat = thirdCat
#             tmp = self.generateEvent(caseid, username, timestamp, category=cat)
#         # else:
#         #    tmp = self.generateEvent(caseid, username, timestamp)
#         return tmp
#
#     def generateDataframe(self):
#         series = []
#
#         events_categories = ["MicrosoftOffice", "Browser", "OperatingSystem"]
#         firstCat, secondCat, thirdCat = random.sample(events_categories, len(events_categories))
#
#         # list of sublist of indices
#         indexes = self.generateIndexes()
#         duplicated_events = self.generateDuplicatedEvents(indexes[1])
#         if len(indexes) == 5:
#             duplicated_events = self.generateDuplicatedEvents(indexes[3], duplicated_events)
#
#         for trace in range(self.log_size):
#             timestamp = self.generateISOTimestamp()
#             caseid = self.generateCaseId(timestamp)
#             username = self.fake.simple_profile()['username']
#
#             for event in range(self.trace_size):
#                 timestamp = self.addSecondsToISOTimestamp(timestamp)
#                 duplicated_event = duplicated_events.get(event)
#                 if duplicated_event:
#                     tmp = duplicated_event.copy()  # copy otherwise fields of the original would be modified
#                     tmp['case:concept:name'] = caseid
#                     tmp['org:resource'] = username
#                     tmp['time:timestamp'] = timestamp
#                 else:
#                     tmp = self.handleEvent(event, indexes,
#                                            firstCat, secondCat, thirdCat,
#                                            timestamp, caseid, username)
#                 series.append(tmp)
#
#         return pandas.DataFrame(series)

class Validation:
    def __init__(self, log_size: int, trace_size: int, events_size: int, decision_points: int):
        #  parameters
        self.log_size = log_size
        self.trace_size = trace_size
        self.events_size = events_size
        self.decision_points = decision_points
        # fake data
        self.fake_data()
        self.handleEvents()
        self.excluded_events = []

    def handleEvents(self):
        browser = [
            "urlHashChange",
            "contextMenu",
            "clickCheckboxButton",
            "clickRadioButton",
            "navigateTo",
            "clickTextField",
            "clickButton",
            "clickLink",
            "selectOptions",
            "selectText",
            "submit",
            "changeField",
            "doubleClick",
            "dragElement",
            "cancelDialog",
            "fullscreen",
            "attachTab",
            "detachTab",
            "newBookmark",
            "removeBookmark",
            "modifyBookmark",
            "moveBookmark",
            "startDownload",
            "erasedDownload",
            "installBrowserExtension",
            "uninstallBrowserExtension",
            "enableBrowserExtension",
            "disableBrowserExtension",
            "closedNotification",
            "clickedNotification",
            "newWindow",
            "closeWindow",
            "newTab",
            "closeTab",
            "moveTab",
            "mutedTab",
            "unmutedTab",
            "pinnedTab",
            "unpinnedTab",
            "audibleTab",
            "zoomTab",
            "changeHistory",
            "link",
            "typed",
            "form_submit",
            "reload"
        ]
        os = [
            "created",
            "modified",
            "deleted",
            "Mount",
            "Unmount",
            "moved",
            "programOpen",
            "programClose",
            "selectFile",
            "selectFolder",
            "hotkey",
            "insertUSB",
            "printSubmitted",
            "openFile",
            "openFolder"
        ]
        clipboard = [
            "copy",
            "paste",
            "cut"
        ]
        excel = [
            "openWindow",
            "closeWindow",
            "resizeWindow",
            "newWorkbook",
            "openWorkbook",
            "addWorksheet",
            "beforeSaveWorkbook",
            "saveWorkbook",
            "printWorkbook",
            "closeWorkbook",
            "activateWorkbook",
            "deactivateWorkbook",
            "modelChangeWorkbook",
            "newChartWorkbook",
            "afterCalculate",
            "selectWorksheet",
            "deleteWorksheet",
            "doubleClickCellWithValue",
            "doubleClickEmptyCell",
            "rightClickCellWithValue",
            "rightClickEmptyCell",
            "sheetCalculate",
            "editCellSheet",
            "deselectWorksheet",
            "followHiperlinkSheet",
            "pivotTableValueChangeSheet",
            "getRange",
            "getCell",
            "worksheetTableUpdated",
            "addinInstalledWorkbook",
            "addinUninstalledWorkbook",
            "XMLImportWorkbook",
            "XMLExportWorkbook"
        ]
        word = [
            "activateWindow",
            "deactivateWindow",
            "doubleClickWindow",
            "rightClickWindow",
            "newDocument",
            "openDocument",
            "changeDocument",
            "saveDocument",
            "printDocument"
        ]
        powerpoint = [
            "activateWindow",
            "deactivateWindow",
            "rightClickPresentation",
            "doubleClickPresentation",
            "newPresentation",
            "newPresentationSlide",
            "closePresentation",
            "savePresentation",
            "openPresentation",
            "printPresentation",
            "slideshowBegin",
            "nextSlideshow",
            "clickNextSlideshow",
            "previousSlideshow",
            "slideshowEnd",
            "SlideSelectionChanged"
        ]
        operatingSystem = os + clipboard
        office = excel + word + powerpoint

        fourty_percent = int(self.events_size * 0.40)
        twenty_percent = int(self.events_size * 0.20)
        self.events_dict = {
            # take 40% events
            'Browser': random.sample(browser,
                                     fourty_percent if len(browser) > fourty_percent else len(browser)),
            # take 20% events
            'OperatingSystem': random.sample(operatingSystem,
                                             twenty_percent if len(operatingSystem) > twenty_percent else len(
                                                 operatingSystem)),
            # take 40% events
            'MicrosoftOffice': random.sample(office,
                                             fourty_percent if len(office) > fourty_percent else len(office))
        }

        self.events_reverse = {
            str(browser): 'Browser',
            str(os): 'OperatingSystem',
            str(clipboard): 'OperatingSystem',
            str(excel): 'Microsoft Excel',
            str(word): 'Microsoft Word',
            str(powerpoint): 'Microsoft PowerPoint'
        }
        self.office_events_dict = {
            str(excel): 'Microsoft Excel',
            str(word): 'Microsoft Word',
            str(powerpoint): 'Microsoft PowerPoint'
        }

    # fake data
    def fake_data(self):
        self.fake = faker.Faker()
        n = 20
        urls = [self.fake.url() for _ in range(int(n / 2))]
        urls += [u + self.fake.word() for u in urls]
        self.urls = urls
        self.apps = ["SublimeText", "VisualStudioCode", "Notepad.exe", "Skype"]
        self.files = [self.fake.file_path() for _ in range(n)]
        self.clipboard = self.fake.sentences(n)
        self.words = [""] + self.fake.words(n - 1)
        self.workbooks = [f"Workbook{i}" for i in range(1, n)]
        self.sheets = [f"Sheet{i}" for i in range(1, n)]
        self.cell_ranges = [
            f"{random.choice(string.ascii_uppercase)}{random.randint(0, 20)}" for _ in range(n)]
        self.eventQual = ['[]', '["serverRedirect","fromAddressBar"]',
                          '["fromAddressBar"]', '["serverRedirect"]']
        self.tag_category = ["", "A", "DIV", "IMG", "INPUT", "BUTTON"]
        self.tag_type = {'INPUT': 'text', 'BUTTON': 'submit'}
        self.tag_name = self.words
        self.tag_value = ["", "True", "False"] + self.words
        self.browser_id = ["", "click_btn", "check_link", "input_text"]
        web_elems = ['div', 'section', 'image', 'button',
                     'html', 'div', 'body', 'aside', 'url', 'a', 'li']
        self.xpath = [
            f'id("{random.choice(self.words)}")',
            f'id("{random.choice(self.words)}/{random.choice(web_elems)}[{random.randint(0, 4)}]")',
            f'id("{random.choice(self.words)}/{random.choice(web_elems)}[{random.randint(0, 4)}]/{random.choice(web_elems)}[{random.randint(0, 4)}]")'
        ]
        self.slides = [list(range(random.randint(1, 6))) for _ in range(n)]
        self.hotkeys = {
            'alt+d': 'Select address bar',
            'alt+F4': 'Close window',
            'alt+esc': 'Cycle through windows',
            'alt+tab': 'Cycle through open apps',
            'alt+enter': 'Display item properties',
            'alt+space+n': 'Minimise window',
            'alt+space+x': 'Maximise window',
            'ctrl+a': 'Select all',
            # 'ctrl+c': 'Copy', # handled by clipboardEvents
            'ctrl+d': 'Delete selected item',
            'ctrl+e': 'Select search box',
            'ctrl+f': 'Find',
            'ctrl+h': 'Find and replace',
            'ctrl+n': 'New',
            'ctrl+r': 'Refresh',
            'ctrl+s': 'Save',
            'ctrl+p': 'Print',
            # 'ctrl+v': 'Paste',
            'ctrl+w': 'Close window',
            'ctrl+x': 'Cut',
            'ctrl+y': 'Undo',
            'ctrl+z': 'Redo',
            'ctrl+shift+t': 'Reopen closed tab',
            'win+tab': 'Cycle through apps',
            'win+d': 'Show/Hide desktop',
            'win+e': 'Open explorer',
            'win+f': 'Search for files',
            'win+i': 'Open settings',
            'win+m': 'Minimize all windows',
            'win+p': 'Choose presentation display mode',
            'win+r': 'Run',
            'F1': 'Help',
            'F2': 'Rename',
            'F3': 'Search',
            'F5': 'Refresh',
        }

    def generateEvent(self, caseid="", username="", timestamp="", category=""):

        if not category:
            category = random.choice(list(self.events_dict.keys()))
        try:
            events_to_choose = list(
                set(self.events_dict[category]) - set(self.excluded_events))
        except Exception as e:
            print(e)
            events_to_choose = self.events_dict[category]

        concept_name = random.choice(events_to_choose)

        application, clipboard_content, event_src_path, event_dest_path, browser_url, current_worksheet, eventQual, hotkey, description, workbook, worksheets, cell_content, cell_range, tag_category, tag_type, tag_value, tag_name, browser_id, xpath, slides, title = [
            ""] * 21
        try:
            category_from_concept_name = random.choice(
                [category for events, category in self.office_events_dict.items() if concept_name in events])
        except Exception:
            category_from_concept_name = ""
        # Office
        if category_from_concept_name in ["Microsoft Excel", "Microsoft Word", "Microsoft PowerPoint"]:
            application = category_from_concept_name
            if 'save' in concept_name:
                event_src_path = random.choice(self.files)
            if application == "Microsoft Excel":
                workbook = random.choice(self.workbooks)
                worksheets = random.sample(self.sheets, random.randint(1, 2))
                current_worksheet = worksheets[0]
                cell_content = random.choice(self.words)
                cell_range = random.choice(self.cell_ranges)
            elif application == "Microsoft Word":
                event_src_path = random.choice(self.files)
                title = random.choice(self.words)
            elif application == "Microsoft PowerPoint":
                slides = ', '.join(map(str, random.choice(self.slides)))
                event_src_path = random.choice(self.files)
        # Clipboard
        elif category == "Clipboard":
            application = "Clipboard"
            clipboard_content = random.choice(self.clipboard)
        #  OS
        elif category == "OperatingSystem":
            if concept_name in ['programOpen', 'programClose']:
                application = random.choice(self.apps)
                event_src_path = random.choice(self.files)
            elif concept_name == "hotkey":
                hotkey = random.choice(list(self.hotkeys.keys()))
                description = self.hotkeys.get(hotkey)
            elif concept_name in ["cut", "copy", "paste"]:
                # category = "Clipboard"
                application = "Clipboard"
                clipboard_content = random.choice(self.clipboard)
            else:
                application = "Explorer"
                event_src_path = random.choice(self.files)
                if concept_name == "moved":
                    event_dest_path = random.choice(self.files)
        # Browser
        elif category == "Browser":
            application = "Chrome"
            browser_url = random.choice(self.urls)
            eventQual = random.choices(
                self.eventQual, weights=(60, 20, 20, 20))[0]
            tag_category = random.choices(
                self.tag_category, weights=(40, 20, 20, 20, 20, 20))[0]
            tag_type = self.tag_type.get(tag_category, "")
            tag_name = random.choice(self.tag_name)
            tag_value = random.choice(self.tag_value)
            browser_id = random.choices(
                self.browser_id, weights=(70, 10, 10, 10))[0]
            xpath = random.choice(self.xpath)

        return {
            "case:concept:name": caseid,
            "case:creator": "SmartRPA by marco2012",
            "lifecycle:transition": "complete",
            "time:timestamp": timestamp,
            "org:resource": username,
            "category": category,
            "application": application,
            "concept:name": concept_name,
            "event_src_path": event_src_path,
            "event_dest_path": event_dest_path,
            "clipboard_content": clipboard_content,
            "mouse_coord": "",
            "workbook": workbook,
            "current_worksheet": current_worksheet,
            "worksheets": worksheets,
            "sheets": "",
            "cell_content": cell_content,
            "cell_range": cell_range,
            "cell_range_number": "",
            "window_size": "",
            "slides": slides,
            "effect": "",
            "hotkey": hotkey,
            "id": browser_id,
            "title": title,
            "description": description,
            "browser_url": browser_url,
            "eventQual": eventQual,
            "tab_moved_from_index": "",
            "tab_moved_to_index": "",
            "newZoomFactor": "",
            "oldZoomFactor": "",
            "tab_pinned": "",
            "tab_audible": "",
            "tab_muted": "",
            "window_ingognito": "",
            "file_size": "",
            "tag_category": tag_category,
            "tag_type": tag_type,
            "tag_name": tag_name,
            "tag_title": "",
            "tag_value": tag_value,
            "tag_checked": "",
            "tag_html": "",
            "tag_href": "",
            "tag_innerText": "",
            "tag_option": "",
            "tag_attributes": "",
            "xpath": xpath,
            "xpath_full": xpath
        }

    # timestamp
    def generateISOTimestamp(self):
        return self.fake.date_time_this_year().isoformat()

    def addSecondsToISOTimestamp(self, ts):
        return (datetime.fromisoformat(ts) +
                timedelta(seconds=random.randint(1, 60))).isoformat(
            timespec='milliseconds')

    def generateCaseId(self, ts):
        return datetime.fromisoformat(ts).strftime('%m%d%H%M%S%f')

    # def generateIndexes(self):
    #     if self.decision_points in [1, 2]:
    #         split_size = 2
    #     elif self.decision_points in [3, 4]:
    #         split_size = 3
    #     else:
    #         split_size = 5
    #     chunks = [*np.array_split(range(0, self.trace_size), split_size)]
    #     return [x.tolist() for x in chunks]

    def generateIndexes(self):
        mylist = range(0, self.trace_size)
        if self.decision_points in [1, 2]:
            seclist = [int(self.trace_size * 0.8), int(self.trace_size * 0.2)]
        elif self.decision_points in [3, 4]:
            seclist = [int(self.trace_size * 0.4),
                       int(self.trace_size * 0.2), int(self.trace_size * 0.4)]
        else:
            seclist = [int(self.trace_size * 0.25), int(self.trace_size * 0.13),
                       int(self.trace_size * 0.25), int(self.trace_size * 0.13), int(self.trace_size * 0.25)+1]
        chunks = [list(mylist[sum(seclist[:i]):sum(seclist[:i + 1])])
                  for i in range(len(seclist))]
        if self.decision_points >= 5:
            last = chunks[-1][-1]
            chunks[-1] += (range(last + 1, self.trace_size))
        return chunks

    def generateDuplicatedEvents(self, indexes, duplicated_events=None):
        if not duplicated_events:
            duplicated_events = {}
        for index in indexes:
            category = random.choice(["Browser", "MicrosoftOffice"])
            e = self.generateEvent(category=category)
            duplicated_events[index] = e
            self.excluded_events.append(e['concept:name'])
        return duplicated_events

    def split_list(self, a_list):
        half = len(a_list) // 2
        return a_list[:half], a_list[half:]

    def handleEvent(self, event, indexes,
                    firstCat, secondCat, thirdCat,
                    timestamp, caseid, username):

        # for i in [0, 2, 4]:
        #     if len(indexes) > i and event in indexes[i]:
        #         if self.decision_points % 2 == 1:
        #             cat = thirdCat
        #         else:
        #             first_half, second_half = self.split_list(indexes[i])
        #             cat = firstCat if event in first_half else secondCat
        #         tmp = self.generateEvent(caseid, username, timestamp, category=cat)

        if event in indexes[0]:
            if self.decision_points == 1:
                cat = firstCat
            else:
                first_half, second_half = self.split_list(indexes[0])
                if event in first_half:
                    cat = firstCat
                elif event in second_half:
                    cat = secondCat
            tmp = self.generateEvent(caseid, username, timestamp, category=cat)
        elif len(indexes) > 2 and event in indexes[2]:
            if self.decision_points == 3:
                cat = thirdCat
            else:
                first_half, second_half = self.split_list(indexes[2])
                if event in first_half:
                    cat = firstCat
                elif event in second_half:
                    cat = secondCat
            tmp = self.generateEvent(caseid, username, timestamp, category=cat)
        # elif len(indexes) > 4 and event in indexes[4]:
        elif len(indexes) > 4 and event in indexes[4]:
            if self.decision_points == 5:
                cat = thirdCat
            tmp = self.generateEvent(caseid, username, timestamp, category=cat)
        else:
            tmp = self.generateEvent(caseid, username, timestamp)
        return tmp

    def generateDataframe(self):
        series = []

        events_categories = ["MicrosoftOffice", "Browser", "OperatingSystem"]
        firstCat, secondCat, thirdCat = random.sample(
            events_categories, len(events_categories))

        number_duplicated_rows = random.randint(1, 2)

        # list of sublist of indices
        indexes = self.generateIndexes()
        print(indexes)
        duplicated_events_index = 1
        duplicated_events = self.generateDuplicatedEvents(
            indexes[duplicated_events_index])
        if len(indexes) == 5:
            duplicated_events = self.generateDuplicatedEvents(
                indexes[3], duplicated_events)

        for trace in range(self.log_size):
            timestamp = self.generateISOTimestamp()
            caseid = self.generateCaseId(timestamp)
            username = self.fake.simple_profile()['username']

            for event in range(self.trace_size):
                timestamp = self.addSecondsToISOTimestamp(timestamp)
                duplicated_event = duplicated_events.get(event)
                if duplicated_event:
                    # copy otherwise fields of the original would be modified
                    tmp = duplicated_event.copy()
                    tmp['case:concept:name'] = caseid
                    tmp['org:resource'] = username
                    tmp['time:timestamp'] = timestamp
                else:
                    tmp = self.handleEvent(event, indexes,
                                           firstCat, secondCat, thirdCat,
                                           timestamp, caseid, username)
                series.append(tmp)

        return pandas.DataFrame(series)


def calculate_time_dp(df1):
    count = 0

    start_time = time.time()
    s = df1.groupby('case:concept:name')['duplicated'].apply(
        lambda d: d.ne(d.shift()).cumsum())
    grouped_df = df1.groupby([s, 'category'])
    total_time = (time.time() - start_time)

    for _, group in grouped_df:
        d = group['duplicated'].unique()
        try:
            not_duplicated = not d
        except Exception:
            not_duplicated = not any(d)
        if len(group.groupby('case:concept:name')) >= 2 and not_duplicated:
            count += 1

    return total_time, count


def process_info(v, df, df1, total_time, number_of_decision_points, SAVE_FILE):
    current_daytime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{current_daytime}__{v.log_size}_{v.trace_size}_{v.events_size}_{v.decision_points}"
    path = f'/Users/marco/Desktop/validation/{filename}'

    process_info = f"[PROCESS] Process composed by {v.log_size} traces, each with {v.trace_size} events."
    process_info += f"\n[PROCESS] There are {v.events_size} different events to choose from."

    decision_points_ok = (number_of_decision_points == v.decision_points)
    at_least_one_true_event = True in df1['duplicated'].unique()
    success_bool = (decision_points_ok and at_least_one_true_event)

    s = 's' if number_of_decision_points > 1 else ''
    success_label = "[SUCCESS]" if success_bool else "[ FAIL  ]"
    success = f"{success_label} Discovered {number_of_decision_points} decision point{s} out of {v.decision_points}. "
    success_rate = int((number_of_decision_points / v.decision_points) * 100)
    # if success_rate > 100:
    #    success_rate = int((v.decision_points / number_of_decision_points) * 100)
    if not at_least_one_true_event:
        success += f"Success rate: 0%. (There aren't duplicated rows, all traces are different)."
    else:
        success += f"Success rate: {success_rate}%."

    total_time_ms = round(total_time, 8) * 1000
    execution_time = f"[ TIME  ] Total compute time: {format(total_time_ms, '.3f')} ms. Average compute time: {format(total_time_ms / v.log_size, '.3f')} ms per trace."

    print_str = f"---RESULT---\n{process_info}\n{success}\n{execution_time}"

    sep = '*' * 30
    summary = f"""
{sep}
{print_str.replace('---RESULT---', f'[  LOG  ] {current_daytime}.csv')}
{sep}
"""
    print(summary)

    if SAVE_FILE:
        df.to_csv(f"{path}.csv")

        with open(f"/Users/marco/Desktop/validation/results_summary.txt", 'a') as f:
            f.write(summary)

        fields = [
            f'{current_daytime}.csv',
            v.log_size,
            v.trace_size,
            v.events_size,
            number_of_decision_points,
            v.decision_points,
            f"{success_rate}%",
            format(total_time_ms, '.3f'),
            format(total_time_ms / v.log_size, '.3f'),
            utils.utils.removeWhitespaces(
                process_info).replace('\n', '') + ' ' + success
        ]
        with open('/Users/marco/Desktop/validation/results_summary.csv', 'a', newline='\n') as f:
            writer = csv.writer(f)
            writer.writerow(fields)

        print("Write OK")


def validate():
    SAVE_FILE = True
    DEBUG_start_time = time.time()

    for log_size in [250, 500, 750, 1000]:
        for trace_size in [25, 50, 75, 100]:
            for events_size in [40, 80, 120]:
                for decision_point in [5]:  # [1, 2, 3, 4]

                    while True:
                        v = Validation(
                            log_size=log_size,
                            trace_size=trace_size,
                            events_size=events_size,
                            decision_points=decision_point
                        )

                        try:
                            df = v.generateDataframe()
                        except IndexError as e:
                            print(e)
                            continue

                        df1 = DecisionPoints(df, Queue()).handle_df()

                        try:
                            total_time, number_of_decision_points = calculate_time_dp(
                                df1)
                        except ValueError as e:
                            print(e)
                            continue

                        process_info(v, df, df1, total_time,
                                     number_of_decision_points, SAVE_FILE)

                        if number_of_decision_points == v.decision_points:
                            break

    DEBUG_total_time = (time.time() - DEBUG_start_time)
    print(
        f"[DEBUG] Total execution time: {round(DEBUG_total_time, 3)} seconds\n")


def test():
    v = Validation(
        log_size=750,
        trace_size=100,
        events_size=40,
        decision_points=5
    )

    df = v.generateDataframe()

    df1 = DecisionPoints(df, Queue()).handle_df()

    total_time, number_of_decision_points = calculate_time_dp(df1)

    process_info(v, df, df1, total_time, number_of_decision_points, True)


def test2():
    while True:
        v = Validation(
            log_size=750,
            trace_size=100,
            events_size=40,
            decision_points=2
        )

        try:
            df = v.generateDataframe()
        except IndexError as e:
            print(e)
            continue

        df1 = DecisionPoints(df, Queue()).handle_df()

        try:
            total_time, number_of_decision_points = calculate_time_dp(
                df1)
        except ValueError as e:
            print(e)
            continue

        process_info(v, df, df1, total_time,
                     number_of_decision_points, True)

        if number_of_decision_points == v.decision_points:
            break


if __name__ == '__main__':
    test2()
