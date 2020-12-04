# ******************************
# Generate RPA script
# Automatically generate RPA script from csv log file. Called by
# GUI when main process is terminated and csv is available.
# https://automagica.readthedocs.io/activities.html
# ******************************
import modules
from multiprocessing.queues import Queue
import pandas
import os
import ntpath
from threading import Thread
import utils.config
import utils
from utils.utils import CHROME, DESKTOP, getActiveWindowInfo, WINDOWS, MAC
import sys
sys.path.append('../')  # this way main file is visible from this file


class RPAScript:
    """
    This class generate python RPA SW robot for a given csv
    """

    def __init__(self,
                 csv_file_path: str,
                 status_queue: Queue,
                 delay_between_actions=0.2):

        """
        Initialize class and import csv event log into dataframe

        :param csv_file_path: path of event log to analyze
        :param status_queue: queue to sent messages to GUI
        :param delay_between_actions: delay between robot actions in milliseconds
        """

        self.status_queue = status_queue
        self._delay_between_actions = delay_between_actions
        self._SaveAsUI = False
        self.excelOpened = False
        self.eventsToIgnore = ["openWindow", "activateWorkbook", "newWorkbook", "selectedFile", "selectedFolder",
                               "newWindow", "closeWindow", "submit", "formSubmit", "enableBrowserExtension",
                               "newWindow", "startPage", "activateWorkbook", "openWindow", "click",
                               "clickTextField", "newTab", "disableBrowserExtension", "installBrowserExtension",
                               "logonComplete", "deleted", "programClose", "afterCalculate",
                               "resizeWindow", "selectText", "Mount"]

        self.csv_file_path = csv_file_path
        self.RPA_directory = utils.utils.getRPADirectory(self.csv_file_path)
        try:
            self._dataframe = pandas.read_csv(
                csv_file_path, encoding='utf-8-sig')
        except pandas.errors.ParserError:
            self._dataframe = pandas.read_csv(
                csv_file_path, encoding='utf-8-sig', sep=';')
        except UnicodeDecodeError as e:
            print(f"[RPA] Could not decode {csv_file_path}: {e}")

    def run(self):
        if not os.path.exists(self.csv_file_path):
            print(f"[CSV2XES] {self.csv_file_path} does not exist")
            return False
        t0 = Thread(target=self.generateRPAScript)
        t0.start()
        t0.join()

    def _createHeader(self):
        """
        Add import statements to generated python file with required packages like automagica

        :return: import statement
        """
        h = f"""
# -*- coding: utf-8 -*-
# This file was auto generated based on {self.csv_file_path}
import sys, os
from time import sleep
import pyperclip
try:
    from automagica import *
except ImportError as e:
    print("Please install 'automagica' module running 'pip3 install libraries/Automagica-2.0.25-py3-none-any.whl'")
    print("If you get errors check here https://github.com/bpm-diag/smartRPA#1-automagica")
    sys.exit()
\n"""
        if MAC:
            h += "import applescript\n" \
                 "import xlwings as xw\n"
        return h

    @staticmethod
    def _createBrowserHeader():
        """
        Create import statement for the browser (import selenium for automation).

        It is separated because those imports are added only if there are browser events.

        :return: browser import statement
        """
        return f"""
try:
    import importlib
    from selenium import webdriver
    import chromedriver_binary  # Adds chromedriver binary to path
    from selenium.common.exceptions import *
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
    from selenium.webdriver.common.by import By
    print("Opening Chrome...")
    browser = webdriver.Chrome()
    browser.get('about:blank') 
except WebDriverException as e:
    print(e)
    sys.exit()
    \n"""

    def _createOpenExcel(self, script, path):
        """
        Write instructions to open excel.

        :param script: file object to write to
        :param path: path of excel file to open
        """
        if not self.excelOpened:
            self.excelOpened = True
            script.write(f"print('Opening Excel...')\n")
            if MAC:
                script.write(
                    f"applescript.tell.app('Microsoft Excel', 'open')\n")
                script.write("app = xw.App(visible=True)\n")
                if path and os.path.splitext(path)[1] and os.path.exists(path):
                    script.write(f"wb = xw.Book('{path}')\n")
                else:
                    script.write("wb = xw.Book()\n")
                script.write(f"""
try:
    sht = wb.sheets.active
except Exception:
    pass
\n""")
            elif WINDOWS:
                if path and os.path.splitext(path)[1] and os.path.exists(path):
                    script.write(
                        f"excel = Excel(visible=True, file_path=r'{path}')\n")
                else:
                    script.write("excel = Excel(visible=True)\n")

    def _createRPAFile(self, RPA_type):
        """
        Generate path where to save python SW robot

        :param RPA_type: name of file
        :return: path of SW robot, like like /Users/marco/Desktop/ComputerLogger/RPA/2020-02-25_23-21-57/2020-02-25_23-21-57_RPA.py
        """
        # csv_file_path is like /Users/marco/Desktop/ComputerLogger/logs/2020-02-25_23-21-57.csv
        # csv_filename is like 2020-02-25_23-21-57
        utils.utils.createDirectory(self.RPA_directory)
        # RPA_filename is like 2020-02-25_23-21-57_RPA.py
        RPA_filename = utils.utils.getFilename(
            self.csv_file_path).strip('_combined') + RPA_type
        # RPA_filepath is like /Users/marco/Desktop/ComputerLogger/RPA/2020-02-25_23-21-57/2020-02-25_23-21-57_RPA.py
        RPA_filepath = os.path.join(
            self.RPA_directory, utils.utils.SW_ROBOT_FOLDER, RPA_filename)
        return RPA_filepath

    def _generateUnifiedRPA(self, df: pandas.DataFrame, filename="_UnifiedRPA.py"):
        """
        Core method of the class, generates python SW robot from trace.

        Each line of the dataframe is analyzed and the corresponding python instruction to automate it is generated.

        :param df: low-level dataframe of trace to automate
        :param filename: name of resulting sw robot
        """
        if df.empty:
            return False

        RPA_filepath = self._createRPAFile(filename)
        mac_source_filepath = ""
        mac_dest_filepath = ""
        with open(RPA_filepath, 'w') as script:
            script.write(self._createHeader())
            # add browser header if browser is present in event log
            if not df.query('category=="Browser"').empty:
                script.write(self._createBrowserHeader())
            if WINDOWS:
                script.write(
                    "from win32gui import GetForegroundWindow, GetWindowText\n\n")

            for index, row in df.iterrows():

                ######
                # Variables
                ######

                try:
                    e = row['event_type']
                    timestamp = row['timestamp']
                    user = row['user']
                except KeyError:
                    e = row['concept:name']
                    timestamp = row['time:timestamp']
                    user = row['org:resource']

                wb = row['workbook']
                sh = row['current_worksheet']
                cell_value = utils.utils.unicodeString(row['cell_content'])
                cell_range = row['cell_range']
                range_number = row['cell_range_number']

                # assign path if not null
                path = ""
                if not pandas.isna(row['event_src_path']) and row['event_src_path'] != '':
                    path = row['event_src_path']
                    # path = path.replace(user, utils.utils.USER, 1) # replace username with current user
                    path = utils.utils.formatPathForCurrentOS(path, user)
                    item_name = path.replace('\\', r'\\')

                dest_path = ""
                if not pandas.isna(row['event_dest_path']) and row['event_dest_path'] != '':
                    dest_path = row['event_dest_path']
                    # dest_path = dest_path.replace(user, utils.utils.USER, 1)
                    dest_path = utils.utils.formatPathForCurrentOS(
                        dest_path, user)

                app = row['application']
                mouse_coord = row['mouse_coord']

                cb = utils.utils.processClipboard(row['clipboard_content'])

                size = row["window_size"]
                url = "about:blank"
                if not pandas.isna(row['browser_url']):
                    url = row['browser_url']
                id = ""
                if not pandas.isna(row['id']):
                    id = row['id']
                xpath = ""
                if not pandas.isna(row['xpath']):
                    xpath = row['xpath']
                value = utils.utils.unicodeString(row['tag_value'])

                if e not in self.eventsToIgnore:
                    script.write(f"# {timestamp} {e}\n")
                    if row['category'] == "OperatingSystem":
                        script.write(
                            f"sleep({self._delay_between_actions * 2})\n")
                    else:
                        script.write(f"sleep({self._delay_between_actions})\n")

                ######
                # EXCEL
                ######

                # if mouse_coord field is not null for a given row TODO
                # if not pandas.isna(mouse_coord) and mouse_coord != "0,0":
                #     # mouse_coord is like '[809, 743]', I need to take each component separately and remove the space
                #     # m = list(map(lambda c: c.strip(), mouse_coord.strip('[]').split(',')))
                #     script.write(f"print('Clicking {mouse_coord}')\n")
                #     script.write(f"click({mouse_coord})\n")

                if e in ["newWorkbook"]:
                    self._createOpenExcel(script, path)

                elif e in ["openWorkbook"]:
                    self._createOpenExcel(script, path)

                elif e in ["addWorksheet", "WorksheetAdded"]:
                    self._createOpenExcel(script, path)
                    script.write(f"print('Adding worksheet {sh}')\n")
                    if WINDOWS:
                        script.write(f"""
try:
    excel.add_worksheet('{sh}')
except Exception:
    pass
\n""")
                    elif MAC:
                        script.write(f"""
try:
    sht = wb.sheets.add(name='{sh}')
except Exception:
    pass
\n""")

                elif e in ["selectWorksheet", "WorksheetActivated"]:
                    self._createOpenExcel(script, path)
                    script.write(f"print('Selecting worksheet {sh}')\n")
                    if WINDOWS:
                        script.write(f"""
try:
    excel.activate_worksheet('{sh}')
except Exception:
    pass
\n""")
                    elif MAC:
                        script.write(f"""
try:
    sht = wb.sheets['{sh}'].activate()
except Exception:
    pass
\n""")
                elif e == "getCell":
                    self._createOpenExcel(script, path)
                    script.write(f"print('Reading cell {cell_range}')\n")
                    if WINDOWS:
                        script.write(f"""
try:
    excel.activate_range('{cell_range}')
    rc = excel.read_cell({range_number})
    print('cell {cell_range} value = ' + str(rc))
except Exception:
    pass
\n""")
                    elif MAC:
                        script.write(f"""
try:
    rc = sht.range('{cell_range}').value
    print('cell {cell_range} value = ' + str(rc))
except Exception:
    pass
\n""")

                elif e in ["editCellSheet", "editCell", "editRange"]:
                    self._createOpenExcel(script, path)
                    script.write(f"print('Writing in cell {cell_range}')\n")
                    if WINDOWS:
                        if range_number:
                            script.write(f'''
try:
    excel.write_cell('{range_number}', """{cell_value}""")
except Exception:
    pass
\n''')
                        else:
                            script.write(f'''
try:
    excel.write_cell('{cell_range}', """{cell_value}""")
except Exception:
    pass
\n''')

                    elif MAC:
                        if not self.excelOpened:
                            self._createOpenExcel(script, path)
                        cell_content = row['cell_content'].strip(
                            '[]').strip('"').strip()
                        script.write(f'''
try:
    sht.range('{cell_range}').value = """{cell_content}"""
except Exception:
    pass
\n''')

                elif e == "getRange":
                    self._createOpenExcel(script, path)
                    script.write(f"print('Reading cell_range {cell_range}')\n")
                    if WINDOWS:
                        script.write(f"""
try:
    excel.activate_range('{cell_range}')
    rc = excel.read_range('{cell_range}')
    print('cell {cell_range} value = ' + str(rc))
except Exception:
    pass
\n""")
                    elif MAC:
                        script.write(f"""
try:
    excel.activate_range('{cell_range}')
    rc = excel.read_range('{cell_range}')
    print('cell {cell_range} value = ' + str(rc))
except Exception:
    pass
\n""")

                elif e == "afterCalculate":
                    # script.write(f"print('Calculate')\n")
                    pass

                # In excel I have two kind of events:
                # 1) beforeSave: filename is not yet known but here I know if the file is being saved for the first time
                # (using Save As...) or if it's just a normal save, set SaveAsUI variable
                # 2) saveWorkbook: filename chosen by user is known so I know file path
                # If SaveAsUI is True I need to issue excel.save_as(path) command, else I just need excel.save()
                elif e == "beforeSaveWorkbook":
                    self._SaveAsUI = True if row["description"] == "SaveAs dialog box displayed" else False
                elif e == "saveWorkbook":  # case 2), after case
                    self._createOpenExcel(script, path)
                    script.write(f"print('saving workbook {wb}')\n")
                    if WINDOWS:
                        if self._SaveAsUI:  # saving for the first time
                            script.write(f"excel.save_as(r'{path}')\n")
                        else:  # file already created
                            script.write(f"excel.save()\n")
                    elif MAC:
                        script.write(f"wb.save()\n")

                elif e == "printWorkbook" and not self._SaveAsUI:  # if file has already been saved and it's on disk
                    self._createOpenExcel(script, path)
                    if WINDOWS:
                        script.write(f"print('Printing {wb}')\n")
                        script.write(f"send_to_printer(r'{path}')\n")

                elif e == "closeWindow":
                    self._createOpenExcel(script, path)
                    script.write(f"print('Closing Excel...')\n")
                    if WINDOWS:
                        script.write("excel.quit()\n")
                    elif MAC:
                        script.write("wb.close()\n")

                # elif e == "doubleClickCellWithValue":
                #     script.write(f"print('Double clicking on cell {cell_range} with value {value}')\n")
                #     script.write(f"double_click_on_text_ocr(text='{value}')\n")

                # elif e == "rightClickCellWithValue":
                #     script.write(f"print('Right clicking on cell {cell_range} with value {value}')\n")
                #     script.write(f"right_click_on_text_ocr(text='{value}')\n")

                ######
                # Word
                ######
                elif e == "newDocument":
                    script.write(f"print('Opening Word...')\n")
                    if WINDOWS:
                        script.write("word = Word(visible=True, path=None)\n")
                    elif MAC and os.path.exists('/Applications/Microsoft Word.app'):
                        script.write(
                            f"applescript.tell.app('Microsoft Word', 'open')\n")

                #####
                # PowerPoint
                #####

                elif e == "newPresentation":
                    script.write(f"print('Opening Powerpoint...')\n")
                    if WINDOWS:
                        script.write(
                            "powerpoint = Powerpoint(visible=True, path=None)\n")
                    elif MAC and os.path.exists('/Applications/Microsoft PowerPoint.app'):
                        script.write(
                            f"applescript.tell.app('Microsoft PowerPoint', 'make new presentation')\n")
                elif e == "newPresentationSlide":
                    script.write(f"print('Adding slide to presentation')\n")
                    if WINDOWS:
                        script.write(f"powerpoint.add_slide()\n")
                    elif MAC:
                        script.write(
                            "applescript.tell.app('/Applications/Microsoft PowerPoint.app', 'set newSlide to make new slide at the end of active presentation')\n")
                elif e == "savePresentation":  # case 2), after case
                    presentation_name = row['title']
                    script.write(
                        f"print('saving presentation {presentation_name}')\n")
                    if WINDOWS:
                        path = os.path.join(DESKTOP, 'presentation.pptx')
                        script.write(f"powerpoint.save_as(r'{path}')\n")
                    elif MAC:
                        script.write(
                            f"applescript.tell.app('/Applications/Microsoft PowerPoint.app', 'save active presentation')\n")
                # elif e == "printPresentation" and not self._SaveAsUI:  # if file has already been saved and it's on disk
                #     script.write(f"print('Printing {presentation_name}')\n")
                #     script.write(f"send_to_printer(r'{path}')\n")
                elif e == "closePresentation":
                    script.write(f"print('Closing Powerpoint...')\n")
                    if WINDOWS:
                        script.write("powerpoint.quit()\n")
                    elif MAC:
                        script.write(
                            f"applescript.tell.app('/Applications/Microsoft PowerPoint.app', 'close active presentation')\n")

                ######
                # System
                ######

                elif (e == "copy" or e == "cut") and not pandas.isna(cb):
                    script.write(f"print('Setting clipboard text')\n")
                    if WINDOWS:
                        script.write(f'''
try:
    set_to_clipboard("""{cb}""")
except Exception:
    pass
\n''')
                    else:
                        script.write(f'pyperclip.copy("""{cb}""")\n')
                # paste in browser is handled elsewhere
                elif e == "paste" and row['category'] != 'Browser':
                    script.write(
                        f'print("Pasting clipboard text: {cb} in {row["title"]}")\n')
                    if WINDOWS:
                        script.write(f'''
try:
    set_window_to_foreground('{row['title']}')
    type_text("""{cb}"""+'\\n')
except Exception:
    pass
\n''')
                    # elif MAC:
                    #     cb_text = f'"{cb}")'
                    #     script.write(f"applescript.tell.app('System Events', 'keystroke {cb_text}')")

                elif e == "pressHotkey" and WINDOWS:
                    hotkey = row["id"]
                    hotkey_param = hotkey.split('+')
                    meaning = row["description"]

                    script.write(
                        f"print('Pressing hotkey {hotkey} : {meaning}')\n")
                    if len(hotkey_param) == 2:
                        script.write(f'''
try:
    set_window_to_foreground('{row['title']}')
    press_key_combination('{hotkey_param[0]}', '{hotkey_param[1]}')
except Exception:
    pass
\n''')
                    elif len(hotkey_param) == 3:
                        script.write(f'''
try:
    set_window_to_foreground('{row['title']}')
    press_key_combination('{hotkey_param[0]}', '{hotkey_param[1]}', '{hotkey_param[2]}')
except Exception:
    pass
\n''')

                # path and dest_path must be changed according to current user
                elif e == "openFile" and path:
                    script.write(f"print('Opening file {item_name}')\n")
                    script.write(f"""
try:
    if file_exists(r'{path}'): 
        open_file(r'{path}')
    else:
        print(f"Can not open file '{item_name}' because it does not exist")
except Exception:
    pass
\n""")
                    # script.write(f"if file_exists(r'{path}'): open_file(r'{path}')\n")
                elif e == "openFolder" and path:
                    script.write(f"print('Opening folder {item_name}')\n")
                    if WINDOWS:
                        script.write(
                            f"if folder_exists(r'{path}'): show_folder(r'{path}')\n")
                    elif MAC:
                        script.write(
                            f"if folder_exists(r'{path}'): open_file(r'{path}')\n")
                elif e == "programOpen":

                    # do not open excel manually if there are events related to excel in dataframe,
                    # because it is opened automatically above
                    try:
                        event_list = df['event_type'].tolist()
                    except KeyError:
                        event_list = df['concept:name'].tolist()
                    if (app in ["EXCEL.EXE", "Microsoft Excel", "Microsoft Excel (MacOS)"]) and any(
                            i in event_list for i in ["newWorkbook", "selectWorksheet", "WorksheetActivated"]):
                        pass
                    else:
                        if MAC:
                            if app == "notepad.exe":
                                script.write(f"print('Opening TextEdit')\n")
                                script.write(
                                    f"applescript.tell.app('TextEdit', 'open')\n")
                            elif os.path.exists(path):
                                script.write(f"print('Opening {app}')\n")
                                script.write(
                                    f"applescript.tell.app('{os.path.basename(path)}', 'open')\n")
                        elif WINDOWS and ntpath.basename(path) not in modules.events.systemEvents.programs_to_ignore:
                            if app == "TextEdit":
                                script.write(f"""
try:
    print('Opening Notepad')
    run(r'C:\\Windows\\System32\\notepad.exe')
except Exception:
    pass
\n""")
                            elif os.path.exists(path):
                                script.write(f"print('Opening {app}')\n")
                                script.write(f"""
try:
    run(r'{path}')
except Exception:
    pass
\n""")
                elif e == "programClose" and os.path.exists(path):
                    script.write(f"print('Closing {app}')\n")
                    if MAC:
                        script.write(
                            f"applescript.tell.app('{os.path.basename(path)}', 'quit')\n")
                    else:
                        script.write(f"kill_process(r'{path}')\n")
                elif e == "created" and path:
                    # check if i have a file (with extension)
                    if os.path.splitext(path)[1]:
                        script.write(f"print('Creating file {item_name}')\n")
                        script.write(f"open(r'{path}', 'w')\n")
                    # otherwise assume it's a directory
                    else:
                        script.write(
                            f"print('Creating directory {item_name}')\n")
                        script.write(f"create_folder(r'{path}')\n")
                elif e == "Mount":
                    mac_source_filepath = path
                elif e in ["moved", "Unmount"] and path:

                    if MAC:
                        path = mac_source_filepath
                        dest_path = item_name
                        mac_dest_filepath = item_name

                    # check if file has been renamed, so source and dest path are the same
                    if os.path.dirname(path) == os.path.dirname(dest_path):

                        new_name = ntpath.basename(dest_path)
                        new_name = utils.utils.unicodeString(new_name)

                        # file
                        if os.path.splitext(path)[1]:
                            script.write(
                                f'print("Renaming file {item_name} to {new_name}")\n')
                            script.write(
                                f'if file_exists(r"{path}"): rename_file(r"{path}", new_name="{new_name}")\n')
                        # directory
                        else:
                            script.write(
                                f'print("Renaming directory {item_name} to {new_name}")\n')
                            script.write(
                                f'if folder_exists(r"{path}"): rename_folder(r"{path}", new_name="{new_name}")\n')

                    # else file has been moved to a different folder
                    else:
                        if os.path.splitext(path)[1]:
                            script.write(f'print("Moving file {item_name}")\n')
                            script.write(
                                f'if file_exists(r"{path}"): move_file(r"{path}", r"{dest_path}")\n')
                        # otherwise it's a directory
                        else:
                            script.write(
                                f'print("Moving directory {item_name}")\n')
                            script.write(
                                f'if folder_exists(r"{path}"): move_folder(r"{path}", r"{dest_path}")\n')
                elif e == "deleted" and path:
                    if MAC and mac_dest_filepath:
                        path = mac_dest_filepath
                    # check if i have a file (with extension)
                    if os.path.splitext(path)[1]:
                        script.write(f'print("Removing file {item_name}")\n')
                        script.write(
                            f'if file_exists(r"{path}"): remove_file(r"{path}")\n')
                    # otherwise assume it's a directory
                    else:
                        script.write(
                            f'print("Removing directory {item_name}")\n')
                        script.write(
                            f'if folder_exists(r"{path}"): remove_folder(r"{path}")\n')
                ######
                # Browser
                ######

                # elif e == "newWindow":
                #     script.write(f"print('Opening new window')\n")
                #     # TODO

                # When a window is opened, a new tab is automatically created at index 0
                # so I don't need to create it again
                elif e == "newTab" and int(id) != 0:
                    script.write(f"print('Opening new tab')\n")
                    new_tab = f'window.open("''");'
                    script.write(f"browser.execute_script('{new_tab}')\n")
                    script.write(f"""
try:
    if 0 <= {id} < len(browser.window_handles):
        browser.switch_to.window(browser.window_handles[{id}])
    else:
        for i in range(0, {id}):
            browser.execute_script('window.open("");')
        browser.switch_to.window(browser.window_handles[{id}])
except Exception:
    pass
\n""")
                elif e == "selectTab":
                    script.write(f"print('Selecting tab {id}')\n")
                    script.write(f"""
try:
    if 0 <= {id} < len(browser.window_handles):
        browser.switch_to.window(browser.window_handles[{id}])
    else:
        for i in range(0, {id}):
            browser.execute_script('window.open("");')
        browser.switch_to.window(browser.window_handles[{id}])
    if browser.current_url == 'about:blank':
        browser.get('{url}') 
except Exception:
    pass
\n""")
                elif e == "closeTab":
                    script.write(f"print('Closing tab')\n")
                    script.write(f"browser.close()\n")
                elif e == "reload":
                    script.write(f"print('Reloading page')\n")
                    script.write(f"""
try:
    if browser.current_url != '{url}':
        browser.get('{url}')
    else: 
        browser.refresh()
except Exception:
    pass
""")
                elif (e == "clickLink" or e == "typed") and ('chrome-extension' not in url):  # or e == "link" # disable because if user edits fields, this url changes
                    script.write(f"print('Loading link {url}')\n")
                    script.write(f"browser.get('{url}')\n")
                    script.write(f"""
try:
    WebDriverWait(browser, 2).until(expected_conditions.presence_of_element_located((By.TAG_NAME, 'body')))
except selenium.common.exceptions.TimeoutException:
    pass
\n""")
                elif e == "mouseClick":
                    # if url:  # disable because if user edits fields, this url changes
                    #     script.write(f"print('Loading link {url}')\n")
                    #     script.write(f"browser.get('{url}')\n")
                    script.write(f"print('Clicking button ')\n")
                    script.write(f"""
try:
    if browser.current_url == 'about:blank':
        browser.get('{url}') 
    browser.find_element_by_xpath('{xpath}').click()
except Exception:
    pass
\n""")
                elif e == "changeField":
                    if row['tag_category'] == "SELECT":
                        tag_value = row['tag_value']
                        script.write(f"print('Selecting text')\n")
                        script.write(f"""
try:
    Select(browser.find_element_by_xpath('{xpath}')).select_by_value('{tag_value}')
except Exception:
    pass
\n""")
                    else:
                        script.write(f'print("Inserting text: {value}")\n')
                        script.write(f'''
try:
    if browser.current_url == 'about:blank':
        browser.get('{url}') 
    browser.find_element_by_xpath('{xpath}').clear()
    browser.find_element_by_xpath('{xpath}').send_keys("""{value}""")
except selenium.common.exceptions.NoSuchElementException:
    try:
        browser.find_element_by_name('{row['tag_name']}').clear()
        browser.find_element_by_name('{row['tag_name']}').send_keys("""{value}""") 
    except Exception:
        pass
except Exception:
    pass
\n''')

                elif e == "clickButton" or e == "clickRadioButton" or e == "clickCheckboxButton":
                    script.write(
                        f"print('Clicking button {row['tag_name']}')\n")
                    script.write(f"""
try:
    browser.find_element_by_xpath('{xpath}').click()
except Exception:
    pass
\n""")
                elif e == "doubleClick" and xpath != '':
                    script.write(f"print('Double click')\n")
                    script.write(f"""
try:
    ActionChains(browser).double_click(browser.find_element_by_xpath('{xpath}')).perform()
except Exception:
    pass
\n""")
                elif e == "contextMenu" and xpath != '':
                    script.write(f"print('Context menu')\n")
                    script.write(f"""
try:
    ActionChains(browser).context_click(browser.find_element_by_xpath('{xpath}')).perform()
except Exception:
    pass
\n""")
                elif e == "selectText":
                    pass
                elif e == "zoomTab":
                    # newZoomFactor is like 1.2 so I convert it to percentage
                    newZoom = int(float(row['newZoomFactor']) * 100)
                    script.write(f"print('Zooming page to {newZoom}%')\n")
                    script.write(
                        "browser.execute_script({}'{}%'{})\n".format('"document.body.style.zoom=', newZoom, '"'))
                # elif e == "submit":
                #     script.write(f"print('Submitting button')\n")
                #     script.write(f"browser.find_element_by_xpath('{xpath}').submit()\n")
                elif e == "mouse":  # TODO
                    mouse_coord = row['mouse_coord']
                    script.write(f"print('Mouse click')\n")
                    script.write(f"actions = ActionChains(browser)\n")
                    script.write(
                        f"actions.move_to_element(browser.find_element_by_tag_name('body'))\n")
                    script.write(f"actions.moveByOffset({mouse_coord})\n")
                    script.write(f"actions.click().build().perform()\n")

        # self.status_queue.put(f"[RPA] Generated RPA script {ntpath.basename(RPA_filepath)}")
        self.status_queue.put(f"[RPA] Generated Python RPA script")
        return True

    def generatePythonRPA(self, df: pandas.DataFrame):
        """
        Start generation of python SW robot

        called by GUI when main script terminates and csv log file is created.

        """
        self._generateUnifiedRPA(df, filename="_RPA.py")

    def generateRPAScript(self):
        # check if given csv log file exists
        if not os.path.exists(self.csv_file_path):
            print(
                f"[RPA] Can't find specified csv_file_path {self.csv_file_path}")
            return False
        else:
            self._generateUnifiedRPA(self._dataframe)
            print(f"[RPA] Generated RPA in {self.csv_file_path.strip('.csv')}")
            return True
