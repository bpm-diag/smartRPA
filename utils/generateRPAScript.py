# ******************************
# Generate RPA script
# Automatically generate RPA script from csv log file. Called by
# GUI when main process is terminated and csv is available.
# https://automagica.readthedocs.io/activities.html
# ******************************

import sys

sys.path.append('../')  # this way main file is visible from this file
import pandas
import os
from threading import Thread
import utils.config
import utils
from utils.utils import CHROME, DESKTOP, getActiveWindowInfo


class RPAScript:
    """This class generate RPA scripts for a given csv

    :param csv_file_path: Path of the csv to analyse
    :param generate_all_scripts: If True, all RPA scripts are generated, both individual (like excel, browser) and unified
    :param unified_RPA_script: if True, a single RPA script is generated containing all the events in the log
    :return: boolean indicating success status
    :rtype: bool
    """

    def __init__(self, csv_file_path: str, generate_all_scripts=True, unified_RPA_script=False, delay_between_actions=0.5):
        self.csv_file_path = csv_file_path
        self.unified_RPA_script = unified_RPA_script
        self.generate_all_scripts = generate_all_scripts
        self.__delay_between_actions = delay_between_actions
        self.__SaveAsUI = False
        self.eventsToIgnore = ["openWindow", "activateWorkbook", "newWorkbook", "selectedFile", "selectedFolder",
                               "newWindow", "closeWindow", "typed", "submit", "formSubmit", "enableBrowserExtension",
                               "newWindow", "newTab", "startPage", "activateWorkbook", "openWindow", "click", "clickTextField"]
        try:
            self.__dataframe = pandas.read_csv(csv_file_path, encoding='utf-8-sig')
        except UnicodeDecodeError as e:
            print(f"[CSV2XES] Could not decode {csv_file_path}: {e}")

    def run(self):
        if not os.path.exists(self.csv_file_path):
            print(f"[CSV2XES] {self.csv_file_path} does not exist")
            return False
        t0 = Thread(target=self.generateRPAScript)
        t0.start()
        t0.join()

    # Adds import statements to generated python file
    def __createHeader(self):
        return f"""
# This file was auto generated based on {self.csv_file_path}
import sys, os
from time import sleep
try:
    from automagica import *
except ImportError as e:
    print("Please install 'automagica' module running 'pip3 install automagica==2.0.25'")
    print("If you get errors check here https://github.com/marco2012/ComputerLogger#automagica")
    sys.exit()
\n"""

    def __createBrowserHeader(self):
        return """
try:
    from selenium.common.exceptions import *
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
    from selenium.webdriver.common.by import By
    print("Opening Chrome...")
    browser = Chrome(incognito=False, focus_window=True)
    browser.get('about:blank') 
except WebDriverException as e:
    print(e)
    print("If you get 'Permission denied' you did not set the correct permissions, run 'utils/fix_automagica_permissions.py' first.")
    sys.exit()
    \n"""

    # Create and return rpa directory and file for each specific RPA
    def __createRPAFile(self, RPA_type):
        # csv_file_path is like /Users/marco/Desktop/ComputerLogger/logs/2020-02-25_23-21-57.csv
        # csv_filename is like 2020-02-25_23-21-57
        csv_filename = utils.utils.getFilename(self.csv_file_path)
        # RPA_directory is like /Users/marco/Desktop/ComputerLogger/RPA
        RPA_directory = os.path.join(utils.utils.MAIN_DIRECTORY, 'RPA', csv_filename)
        utils.utils.createDirectory(RPA_directory)
        # RPA_filename is like 2020-02-25_23-21-57_RPA.py
        RPA_filename = csv_filename + RPA_type
        # RPA_filepath is like /Users/marco/Desktop/ComputerLogger/RPA/2020-02-25_23-21-57/2020-02-25_23-21-57_RPA.py
        RPA_filepath = os.path.join(RPA_directory, RPA_filename)
        return RPA_filepath

    def __handle_excel_events(self, script, row):
        e = row['event_type']
        wb = row['workbook']
        sh = row['current_worksheet']
        cell_value = row['cell_content']
        cell_range = row['cell_range']
        range_number = row['cell_range_number']
        # assign path if not null
        path = ""
        if not pandas.isna(row['event_src_path']):
            path = row['event_src_path']
        mouse_coord = row['mouse_coord']
        cb = row['clipboard_content']
        size = row["window_size"]

        if e not in self.eventsToIgnore:
            script.write(f"# {row['timestamp']} {e}\n")
            script.write(f"sleep({self.__delay_between_actions})\n")

        # if mouse_coord field is not null for a given row
        # if not pandas.isna(mouse_coord) and mouse_coord != "0,0":
        #     # mouse_coord is like '[809, 743]', I need to take each component separately and remove the space
        #     # m = list(map(lambda c: c.strip(), mouse_coord.strip('[]').split(',')))
        #     script.write(f"print('Clicking {mouse_coord}')\n")
        #     script.write(f"click({mouse_coord})\n")

        if (e == "copy" or e == "cut") and not pandas.isna(cb):
            script.write(f"print('Setting clipboard text')\n")
            script.write(f'set_to_clipboard("""{cb.rstrip()}""")\n')
        elif e == "paste":
            script.write(f"print('Pasting clipboard text')\n")
            script.write(f'type_text("""{cb}""")\n')
        elif e == "newWorkbook":
            script.write(f"print('Opening Excel...')\n")
            script.write("excel = Excel()\n")
            x, y, width, height = size.split(',')
            # script.write(f"resize_window(GetWindowText(GetForegroundWindow()), {x}, {y}, {width}, {height})\n")
        elif e == "resizeWindow": # TODO
            x, y, width, height = size.split(',')
            script.write(f"print('Resizing window to {size}')\n")
            # script.write(f"resize_window(GetWindowText(GetForegroundWindow()), {x}, {y}, {width}, {height})\n")
        elif e == "addWorksheet":
            script.write(f"print('Adding worksheet {sh}')\n")
            script.write(f"excel.add_worksheet('{sh}')\n")
        elif e == "selectWorksheet":
            script.write(f"print('Selecting worksheet {sh}')\n")
            script.write(f"excel.activate_worksheet('{sh}')\n")
        elif e == "getCell":
            script.write(f"print('Reading cell {cell_range}')\n")
            script.write(f"excel.activate_range('{cell_range}')\n")
            script.write(f"rc = excel.read_cell({range_number})\n")
            script.write(f"print('cell {cell_range} value = ' + str(rc))\n")
        elif e == "editCellSheet":
            script.write(f"print('Writing cell {cell_range}')\n")
            script.write(f'excel.write_cell({range_number}, "{cell_value}")\n')
        elif e == "getRange":
            script.write(f"print('Reading cell_range {cell_range}')\n")
            script.write(f"excel.activate_range('{cell_range}')\n")
            script.write(f"rc = excel.read_range('{cell_range}')\n")
            script.write(f"print('cell {cell_range} value = ' + str(rc))\n")
        elif e == "afterCalculate":
            script.write(f"print('Calculate')\n")
        # In excel I have two kind of events:
        # 1) beforeSave: filename is not yet known but here I know if the file is being saved for the first time
        # (using Save As...) or if it's just a normal save, set SaveAsUI variable
        # 2) saveWorkbook: filename chosen by user is known so I know file path
        # If SaveAsUI is True I need to issue excel.save_as(path) command, else I just need excel.save()
        elif e == "beforeSaveWorkbook":
            self.__SaveAsUI = True if row["description"] == "SaveAs dialog box displayed" else False
        elif e == "saveWorkbook":  # case 2), after case
            script.write(f"print('saving workbook {wb}')\n")
            if self.__SaveAsUI:  # saving for the first time
                script.write(f"excel.save_as(r'{path}')\n")
            else:  # file already created
                script.write(f"excel.save()\n")
        elif e == "printWorkbook" and not self.__SaveAsUI:  # if file has already been saved and it's on disk
            script.write(f"print('Printing {wb}')\n")
            script.write(f"send_to_printer(r'{path}')\n")
        elif e == "closeWindow":
            script.write(f"print('Closing Excel...')\n")
            script.write("excel.quit()\n")
        # elif e == "doubleClickCellWithValue":
        #     script.write(f"print('Double clicking on cell {cell_range} with value {value}')\n")
        #     script.write(f"double_click_on_text_ocr(text='{value}')\n")
        # elif e == "rightClickCellWithValue":
        #     script.write(f"print('Right clicking on cell {cell_range} with value {value}')\n")
        #     script.write(f"right_click_on_text_ocr(text='{value}')\n")

    def __handle_powerpoint_events(self, script, row):
        e = row['event_type']
        # assign path if not null
        path = ""
        if not pandas.isna(row['event_src_path']):
            path = row['event_src_path']
        cb = row['clipboard_content']
        presentation_name = row['title']
        slides = row['slides']

        if e not in self.eventsToIgnore:
            script.write(f"# {row['timestamp']} {e}\n")
            script.write(f"sleep({self.__delay_between_actions})\n")
        if (e == "copy" or e == "cut") and not pandas.isna(cb):
            script.write(f"print('Setting clipboard text')\n")
            script.write(f'set_to_clipboard("""{cb.rstrip()}""")\n')
        elif e == "paste":
            script.write(f"print('Pasting clipboard text')\n")
            script.write(f'type_text("""{cb}""")\n')
        elif e == "newPresentation":
            script.write(f"print('Opening Powerpoint...')\n")
            script.write("powerpoint = Powerpoint(visible=True, path=None)\n")
        elif e == "newPresentationSlide":
            script.write(f"print('Adding slide to presentation')\n")
            script.write(f"powerpoint.add_slide()\n")
        elif e == "savePresentation":  # case 2), after case
            script.write(f"print('saving presentation {presentation_name}')\n")
            path = os.path.join(DESKTOP, 'presentation.pptx')
            script.write(f"powerpoint.save_as(r'{path}')\n")
        # elif e == "printPresentation" and not self.__SaveAsUI:  # if file has already been saved and it's on disk
        #     script.write(f"print('Printing {presentation_name}')\n")
        #     script.write(f"send_to_printer(r'{path}')\n")
        elif e == "closePresentation":
            script.write(f"print('Closing Powerpoint...')\n")
            script.write("powerpoint.quit()\n")

    def __handle_system_events(self, script, row):
        # union of all other handlers
        e = row['event_type']
        cb = row['clipboard_content']
        app = row['application']
        # assign path if not null
        path = ""
        item_name = path.replace('\\', r'\\')
        dest_path = ""
        if not pandas.isna(row['event_src_path']):
            path = row['event_src_path']
        if not pandas.isna(row['event_dest_path']):
            dest_path = row['event_dest_path']

        if e not in self.eventsToIgnore:
            script.write(f"# {row['timestamp']} {e}\n")
            script.write(f"sleep({self.__delay_between_actions * 2})\n")

        if (e == "copy" or e == "cut") and not pandas.isna(cb):
            script.write(f"print('Setting clipboard text')\n")
            script.write(f'set_to_clipboard("""{cb.rstrip()}""")\n')
        elif e == "openFile" and path:
            script.write(f"print('Opening file {item_name}')\n")
            script.write(f"if file_exists(r'{path}'): open_file(r'{path}')\n")
        elif e == "openFolder" and path:
            script.write(f"print('Opening folder {item_name}')\n")
            script.write(f"if file_exists(r'{path}'): show_folder(r'{path}')\n")
        elif e == "programOpen" and os.path.exists(path):
            script.write(f"print('Opening {app}')\n")
            script.write(f"if file_exists(r'{path}'): run(r'{path}')\n")
        elif e == "programClose" and os.path.exists(path):
            script.write(f"print('Closing {app}')\n")
            script.write(f"if file_exists(r'{path}'): kill_process(r'{path}')\n")
        elif e == "created" and path:
            # check if i have a file (with extension)
            if os.path.splitext(path)[1]:
                script.write(f"print('Creating file {item_name}')\n")
                script.write(f"open(r'{path}', 'w')\n")
            # otherwise assume it's a directory
            else:
                script.write(f"print('Creating directory {item_name}')\n")
                script.write(f"create_folder(r'{path}')\n")
        elif e == "deleted" and path:
            # check if i have a file (with extension)
            if os.path.splitext(path)[1]:
                script.write(f"print('Removing file {item_name}')\n")
                script.write(f"if file_exists(r'{path}'): remove_file(r'{path}')\n")
            # otherwise assume it's a directory
            else:
                script.write(f"print('Removing directory {item_name}')\n")
                script.write(f"if folder_exists(r'{path}'): remove_folder(r'{path}')\n")
        elif e == "moved" and path:
            # check if file has been renamed, so source and dest path are the same
            if os.path.dirname(path) == os.path.dirname(dest_path):
                try:
                    import ntpath
                    new_name = ntpath.basename(dest_path)
                except ModuleNotFoundError:
                    new_name = os.path.basename(dest_path)
                # file
                if os.path.splitext(path)[1]:
                    script.write(f"print('Renaming file {item_name} to {new_name}')\n")
                    script.write(
                        f"if file_exists(r'{path}'): rename_file(r'{path}', new_name='{new_name}')\n")
                # directory
                else:
                    script.write(f"print('Renaming directory {item_name}')\n")
                    script.write(
                        f"if folder_exists(r'{path}'): rename_folder(r'{path}', new_name='{new_name}')\n")
            # else file has been moved to a different folder
            else:
                if os.path.splitext(path)[1]:
                    script.write(f"print('Moving file {item_name}')\n")
                    script.write(f"if file_exists(r'{path}'): move_file(r'{path}', r'{dest_path}')\n")
                # otherwise assume it's a directory
                else:
                    script.write(f"print('Moving directory {item_name}')\n")
                    script.write(f"if folder_exists(r'{path}'): move_folder(r'{path}', r'{dest_path}')\n")
        elif e == "pressHotkey":
            hotkey = row["title"]
            hotkey_param = hotkey.split('+')
            meaning = row["description"]
            script.write(f"print('Pressing hotkey {hotkey} : {meaning}')\n")
            if len(hotkey_param) == 2:
                script.write(f"press_key_combination('{hotkey_param[0]}', '{hotkey_param[1]}')\n")
            elif len(hotkey_param) == 3:
                script.write(
                    f"press_key_combination('{hotkey_param[0]}', '{hotkey_param[1]}', '{hotkey_param[2]}')\n")

    def __handle_browser_events(self, script, row):
        e = row['event_type']
        cb = row['clipboard_content']
        url = "about:blank"
        if not pandas.isna(row['browser_url']):
            url = row['browser_url']
        id = ""
        if not pandas.isna(row['id']):
            id = row['id']
        xpath = ""
        if not pandas.isna(row['xpath']):
            xpath = row['xpath']
        value = row['tag_value']

        if e not in self.eventsToIgnore:
            script.write(f"# {row['timestamp']} {e}\n")
            script.write(f"sleep({self.__delay_between_actions})\n")

        if (e == "copy" or e == "cut") and not pandas.isna(cb):
            script.write(f"print('Setting clipboard text')\n")
            script.write(f'set_to_clipboard("""{cb.rstrip()}""")\n')
        elif e == "paste":
            script.write(f"print('Pasting clipboard text')\n")
            script.write(f'type_text("""{cb}""")\n')
        # elif e == "newWindow":
        #     script.write(f"print('Opening new window')\n")
        #     # TODO
        # When a window is opened, a new tab is automatically created at index 0 so I don't need to create it again
        elif e == "newTab" and int(row['id']) != 0:
            script.write(f"print('Opening new tab')\n")
            new_tab = f'window.open("''");'
            script.write(f"browser.execute_script('{new_tab}')\n")
        elif e == "selectTab":
            script.write(f"print('Selecting tab {id}')\n")
            script.write(f"""
if {id} <= len(browser.window_handles):
    browser.switch_to.window(browser.window_handles[{id}])\n
""")
        elif e == "closeTab":
            script.write(f"print('Closing tab')\n")
            script.write(f"browser.close()\n")
        elif e == "reload":
            script.write(f"print('Reloading page')\n")
            script.write(f"browser.refresh()\n")
        elif (e == "clickLink" or e == "link" or e == "typed") and ('chrome-extension' not in url):
            script.write(f"print('Loading link {url}')\n")
            script.write(f"browser.get('{url}')\n")
            script.write(
                f"WebDriverWait(browser, 2).until(expected_conditions.presence_of_element_located((By.TAG_NAME, 'body')))\n")
        elif e == "changeField":
            if row['tag_category'] == "SELECT":
                tag_value = row['tag_value']
                script.write(f"print('Selecting text')\n")
                # script.write(
                #     f"Select(browser.find_element_by_xpath('{xpath}')).select_by_value('{tag_value}')\n")
                script.write(f"""
try:
    Select(browser.find_element_by_xpath('{xpath}')).select_by_value('{tag_value}')
except Exception:
    pass
\n""")
            else:
                script.write(f"print('Inserting text')\n")
                # script.write(f"browser.find_element_by_xpath('{xpath}').send_keys('{value}')\n")
                script.write(f"""
try:
    browser.find_element_by_xpath('{xpath}').send_keys('{value}')
except Exception:
    pass
\n""")
        elif e == "clickButton" or e == "clickRadioButton" or e == "mouseClick":
            script.write(f"print('Clicking button')\n")
            script.write(f"""
try:
    browser.find_element_by_xpath('{xpath}').click()
except Exception:
    pass
\n""")
        elif e == "doubleClick" and xpath != '':
            script.write(f"print('Double click')\n")
            script.write(
                f"ActionChains(browser).double_click(browser.find_element_by_xpath('{xpath}')).perform()\n")
        elif e == "contextMenu" and xpath != '':
            script.write(f"print('Context menu')\n")
            # script.write(
            #     f"ActionChains(browser).context_click(browser.find_element_by_xpath('{xpath}')).perform()\n")
            script.write(f"""
try:
    f"ActionChains(browser).context_click(browser.find_element_by_xpath('{xpath}')).perform()
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
            # script.write(WebDriverWait"actions.move_to_element(browser.find_element_by_tag_name('body'))\n")
            script.write(f"""
try:
    actions.move_to_element(browser.find_element_by_tag_name('body'))
except Exception:
    pass
\n""")
            script.write(f"actions.moveByOffset({mouse_coord})\n")
            script.write(f"actions.click().build().perform()\n")

    # Generate excel RPA python script
    def _generateExcelRPA(self):
        df = self.__dataframe.query(' application=="Microsoft Excel" | category=="Clipboard" | category=="MouseClick" ')
        if df.empty:
            return False
        RPA_filepath = self.__createRPAFile("_ExcelRPA.py")
        with open(RPA_filepath, 'w') as script:
            script.write(self.__createHeader())
            script.write("from win32gui import GetForegroundWindow, GetWindowText\n\n")
            for index, row in df.iterrows():
                self.__handle_excel_events(script, row)
        return True

    # Generate powerpoint RPA python script
    def _generatePowerpointRPA(self):
        df = self.__dataframe.query('application=="Microsoft Powerpoint" | category=="Clipboard"')
        if df.empty:
            return False
        RPA_filepath = self.__createRPAFile("_PowerpointRPA.py")
        with open(RPA_filepath, 'w') as script:
            script.write(self.__createHeader())
            for index, row in df.iterrows():
                self.__handle_powerpoint_events(script, row)
        return True

    # Generate system RPA python script
    def _generateSystemRPA(self):
        df = self.__dataframe.query('category=="OperatingSystem" | category=="Clipboard"')
        if df.empty:
            return False
        RPA_filepath = self.__createRPAFile("_SystemRPA.py")
        with open(RPA_filepath, 'w') as script:
            script.write(self.__createHeader())
            for index, row in df.iterrows():
                self.__handle_system_events(script, row)
        return True

    # Generate browser RPA python script
    def _generateBrowserRPA(self):
        df = self.__dataframe.query('category=="Browser" | category=="Clipboard"')
        if df.empty:
            return False
        # chrome browser must be installed
        if not CHROME:
            print(f"[RPA] Google Chrome must be installed to generate RPA script.")
            return False

        RPA_filepath = self.__createRPAFile("_BrowserRPA.py")
        with open(RPA_filepath, 'w') as script:
            script.write(self.__createHeader())
            script.write(self.__createBrowserHeader())
            for index, row in df.iterrows():
                self.__handle_browser_events(script, row)
        return True

    def _generateUnifiedRPA(self):

        df = self.__dataframe
        if df.empty:
            return False
        RPABrowser = not df.query('category=="Browser"').empty
        RPASystem = not df.query('category=="OperatingSystem"').empty

        RPA_filepath = self.__createRPAFile("_UnifiedRPA.py")
        with open(RPA_filepath, 'w') as script:
            script.write(self.__createHeader())
            # add browser header if browser is present in event log
            if RPABrowser:
                script.write(self.__createBrowserHeader())
            script.write("from win32gui import GetForegroundWindow, GetWindowText\n\n")
            for index, row in df.iterrows():

                # TODO fix

                # self.__handle_browser_events(script, row)
                # self.__handle_excel_events(script, row)
                # self.__handle_powerpoint_events(script, row)
                # self.__handle_system_events(script, row)

                e = row['event_type']
                wb = row['workbook']
                sh = row['current_worksheet']
                cell_value = row['cell_content']
                cell_range = row['cell_range']
                range_number = row['cell_range_number']
                # assign path if not null
                path = ""
                if not pandas.isna(row['event_src_path']):
                    path = row['event_src_path']
                app = row['application']
                # assign path if not null
                item_name = path.replace('\\', r'\\')
                mouse_coord = row['mouse_coord']
                cb = row['clipboard_content']
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
                value = row['tag_value']
                dest_path = ""
                if not pandas.isna(row['event_dest_path']):
                    dest_path = row['event_dest_path']


                if e not in self.eventsToIgnore:
                    script.write(f"# {row['timestamp']} {e}\n")
                    if RPASystem:
                        script.write(f"sleep({self.__delay_between_actions * 2})\n")
                    else:
                        script.write(f"sleep({self.__delay_between_actions})\n")

                # EXCEL

                # if mouse_coord field is not null for a given row TODO
                # if not pandas.isna(mouse_coord) and mouse_coord != "0,0":
                #     # mouse_coord is like '[809, 743]', I need to take each component separately and remove the space
                #     # m = list(map(lambda c: c.strip(), mouse_coord.strip('[]').split(',')))
                #     script.write(f"print('Clicking {mouse_coord}')\n")
                #     script.write(f"click({mouse_coord})\n")

                if (e == "copy" or e == "cut") and not pandas.isna(cb):
                    script.write(f"print('Setting clipboard text')\n")
                    script.write(f'set_to_clipboard("""{cb.rstrip()}""")\n')
                elif e == "paste":
                    script.write(f"print('Pasting clipboard text')\n")
                    script.write(f'type_text("""{cb}""")\n')
                elif e == "newWorkbook":
                    script.write(f"print('Opening Excel...')\n")
                    script.write("excel = Excel()\n")
                    x, y, width, height = size.split(',')
                    # script.write(f"resize_window(GetWindowText(GetForegroundWindow()), {x}, {y}, {width}, {height})\n")
                elif e == "resizeWindow":  # TODO
                    x, y, width, height = size.split(',')
                    script.write(f"print('Resizing window to {size}')\n")
                    # script.write(f"resize_window(GetWindowText(GetForegroundWindow()), {x}, {y}, {width}, {height})\n")
                elif e == "addWorksheet":
                    script.write(f"print('Adding worksheet {sh}')\n")
                    script.write(f"excel.add_worksheet('{sh}')\n")
                elif e == "selectWorksheet":
                    script.write(f"print('Selecting worksheet {sh}')\n")
                    script.write(f"excel.activate_worksheet('{sh}')\n")
                elif e == "getCell":
                    script.write(f"print('Reading cell {cell_range}')\n")
                    script.write(f"excel.activate_range('{cell_range}')\n")
                    script.write(f"rc = excel.read_cell({range_number})\n")
                    script.write(f"print('cell {cell_range} value = ' + str(rc))\n")
                elif e == "editCellSheet":
                    script.write(f"print('Writing cell {cell_range}')\n")
                    script.write(f'excel.write_cell({range_number}, "{cell_value}")\n')
                elif e == "getRange":
                    script.write(f"print('Reading cell_range {cell_range}')\n")
                    script.write(f"excel.activate_range('{cell_range}')\n")
                    script.write(f"rc = excel.read_range('{cell_range}')\n")
                    script.write(f"print('cell {cell_range} value = ' + str(rc))\n")
                elif e == "afterCalculate":
                    script.write(f"print('Calculate')\n")
                # In excel I have two kind of events:
                # 1) beforeSave: filename is not yet known but here I know if the file is being saved for the first time
                # (using Save As...) or if it's just a normal save, set SaveAsUI variable
                # 2) saveWorkbook: filename chosen by user is known so I know file path
                # If SaveAsUI is True I need to issue excel.save_as(path) command, else I just need excel.save()
                elif e == "beforeSaveWorkbook":
                    self.__SaveAsUI = True if row["description"] == "SaveAs dialog box displayed" else False
                elif e == "saveWorkbook":  # case 2), after case
                    script.write(f"print('saving workbook {wb}')\n")
                    if self.__SaveAsUI:  # saving for the first time
                        script.write(f"excel.save_as(r'{path}')\n")
                    else:  # file already created
                        script.write(f"excel.save()\n")
                elif e == "printWorkbook" and not self.__SaveAsUI:  # if file has already been saved and it's on disk
                    script.write(f"print('Printing {wb}')\n")
                    script.write(f"send_to_printer(r'{path}')\n")
                elif e == "closeWindow":
                    script.write(f"print('Closing Excel...')\n")
                    script.write("excel.quit()\n")
                # elif e == "doubleClickCellWithValue":
                #     script.write(f"print('Double clicking on cell {cell_range} with value {value}')\n")
                #     script.write(f"double_click_on_text_ocr(text='{value}')\n")
                # elif e == "rightClickCellWithValue":
                #     script.write(f"print('Right clicking on cell {cell_range} with value {value}')\n")
                #     script.write(f"right_click_on_text_ocr(text='{value}')\n")

                elif e == "paste":
                    script.write(f"print('Pasting clipboard text')\n")
                    script.write(f'type_text("""{cb}""")\n')

                #Browser

                # elif e == "newWindow":
                #     script.write(f"print('Opening new window')\n")
                #     # TODO
                # When a window is opened, a new tab is automatically created at index 0 so I don't need to create it again
                elif e == "newTab" and int(row['id']) != 0:
                    script.write(f"print('Opening new tab')\n")
                    new_tab = f'window.open("''");'
                    script.write(f"browser.execute_script('{new_tab}')\n")
                elif e == "selectTab":
                    script.write(f"print('Selecting tab {id}')\n")
                    script.write(f"""
if {id} <= len(browser.window_handles):
    browser.switch_to.window(browser.window_handles[{id}])\n
""")
                elif e == "closeTab":
                    script.write(f"print('Closing tab')\n")
                    script.write(f"browser.close()\n")
                elif e == "reload":
                    script.write(f"print('Reloading page')\n")
                    script.write(f"browser.refresh()\n")
                elif (e == "clickLink" or e == "link" or e == "typed") and ('chrome-extension' not in url):
                    script.write(f"print('Loading link {url}')\n")
                    script.write(f"browser.get('{url}')\n")
                    script.write(
                        f"WebDriverWait(browser, 2).until(expected_conditions.presence_of_element_located((By.TAG_NAME, 'body')))\n")
                elif e == "changeField":
                    if row['tag_category'] == "SELECT":
                        tag_value = row['tag_value']
                        script.write(f"print('Selecting text')\n")
                        # script.write(
                        #     f"Select(browser.find_element_by_xpath('{xpath}')).select_by_value('{tag_value}')\n")
                        script.write(f"""
try:
    Select(browser.find_element_by_xpath('{xpath}')).select_by_value('{tag_value}')
except Exception:
    pass
\n""")
                    else:
                        script.write(f"print('Inserting text')\n")
                        script.write(f"browser.find_element_by_xpath('{xpath}').send_keys('{value}')\n")
                elif e == "clickButton" or e == "clickRadioButton" or e == "mouseClick":
                    script.write(f"print('Clicking button')\n")
                    script.write(f"""
try:
    browser.find_element_by_xpath('{xpath}').click()
except Exception:
    pass
\n""")
                elif e == "doubleClick" and xpath != '':
                    script.write(f"print('Double click')\n")
                    script.write(
                        f"ActionChains(browser).double_click(browser.find_element_by_xpath('{xpath}')).perform()\n")
                elif e == "contextMenu" and xpath != '':
                    script.write(f"print('Context menu')\n")
                    script.write(
                        f"ActionChains(browser).context_click(browser.find_element_by_xpath('{xpath}')).perform()\n")
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
                    script.write(f"actions.move_to_element(browser.find_element_by_tag_name('body'))\n")
                    script.write(f"actions.moveByOffset({mouse_coord})\n")
                    script.write(f"actions.click().build().perform()\n")

                #system
                elif e == "openFile" and path:
                    script.write(f"print('Opening file {item_name}')\n")
                    script.write(f"if file_exists(r'{path}'): open_file(r'{path}')\n")
                elif e == "openFolder" and path:
                    script.write(f"print('Opening folder {item_name}')\n")
                    script.write(f"if file_exists(r'{path}'): show_folder(r'{path}')\n")
                elif e == "programOpen" and os.path.exists(path):
                    script.write(f"print('Opening {app}')\n")
                    script.write(f"if file_exists(r'{path}'): run(r'{path}')\n")
                elif e == "programClose" and os.path.exists(path):
                    script.write(f"print('Closing {app}')\n")
                    script.write(f"if file_exists(r'{path}'): kill_process(r'{path}')\n")
                elif e == "created" and path:
                    # check if i have a file (with extension)
                    if os.path.splitext(path)[1]:
                        script.write(f"print('Creating file {item_name}')\n")
                        script.write(f"open(r'{path}', 'w')\n")
                    # otherwise assume it's a directory
                    else:
                        script.write(f"print('Creating directory {item_name}')\n")
                        script.write(f"create_folder(r'{path}')\n")
                elif e == "deleted" and path:
                    # check if i have a file (with extension)
                    if os.path.splitext(path)[1]:
                        script.write(f"print('Removing file {item_name}')\n")
                        script.write(f"if file_exists(r'{path}'): remove_file(r'{path}')\n")
                    # otherwise assume it's a directory
                    else:
                        script.write(f"print('Removing directory {item_name}')\n")
                        script.write(f"if folder_exists(r'{path}'): remove_folder(r'{path}')\n")
                elif e == "moved" and path:
                    # check if file has been renamed, so source and dest path are the same
                    if os.path.dirname(path) == os.path.dirname(dest_path):
                        try:
                            import ntpath
                            new_name = ntpath.basename(dest_path)
                        except ModuleNotFoundError:
                            new_name = os.path.basename(dest_path)
                        # file
                        if os.path.splitext(path)[1]:
                            script.write(f"print('Renaming file {item_name} to {new_name}')\n")
                            script.write(
                                f"if file_exists(r'{path}'): rename_file(r'{path}', new_name='{new_name}')\n")
                        # directory
                        else:
                            script.write(f"print('Renaming directory {item_name}')\n")
                            script.write(
                                f"if folder_exists(r'{path}'): rename_folder(r'{path}', new_name='{new_name}')\n")
                    # else file has been moved to a different folder
                    else:
                        if os.path.splitext(path)[1]:
                            script.write(f"print('Moving file {item_name}')\n")
                            script.write(f"if file_exists(r'{path}'): move_file(r'{path}', r'{dest_path}')\n")
                        # otherwise assume it's a directory
                        else:
                            script.write(f"print('Moving directory {item_name}')\n")
                            script.write(f"if folder_exists(r'{path}'): move_folder(r'{path}', r'{dest_path}')\n")
                elif e == "pressHotkey":
                    hotkey = row["title"]
                    hotkey_param = hotkey.split('+')
                    meaning = row["description"]
                    script.write(f"print('Pressing hotkey {hotkey} : {meaning}')\n")
                    if len(hotkey_param) == 2:
                        script.write(f"press_key_combination('{hotkey_param[0]}', '{hotkey_param[1]}')\n")
                    elif len(hotkey_param) == 3:
                        script.write(
                            f"press_key_combination('{hotkey_param[0]}', '{hotkey_param[1]}', '{hotkey_param[2]}')\n")

        return True

    # file called by GUI when main script terminates and csv log file is created.
    def generateRPAScript(self):
        # check if given csv log file exists
        if not os.path.exists(self.csv_file_path):
            print(f"[RPA] Can't find specified csv_file_path {self.csv_file_path}")
            return False
        else:
            if self.generate_all_scripts:
                self._generateUnifiedRPA()
                self._generateExcelRPA()
                self._generatePowerpointRPA()
                self._generateSystemRPA()
                self._generateBrowserRPA()
            else:
                if self.unified_RPA_script:
                    self._generateUnifiedRPA()
                else:
                    self._generateExcelRPA()
                    self._generatePowerpointRPA()
                    self._generateSystemRPA()
                    self._generateBrowserRPA()
            print(f"[RPA] Generated RPA in {self.csv_file_path.strip('.csv')}")
            return True
