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
import utils.config
import utils
from utils.utils import CHROME, WINDOWS, LINUX, MAC
from pynput import mouse


# Adds import statements to generated python file
def createHeader(csv_file_path):
    return f"""# This file was auto generated based on {csv_file_path}
import sys, os
try:
    from automagica import *
except ImportError as e:
    print("Please install 'automagica' module running 'pip3 install -U automagica'")
    print("If you get openssl error check here https://github.com/marco2012/ComputerLogger#RPA")
    sys.exit()
\n"""


# Create and return rpa directory and file for each specific RPA
def createRPAFile(csv_file_path, RPA_type):
    # csv_file_path is like /Users/marco/Desktop/ComputerLogger/logs/2020-02-25_23-21-57.csv
    # csv_filename is like 2020-02-25_23-21-57
    csv_filename = utils.utils.getFilename(csv_file_path)
    # RPA_directory is like /Users/marco/Desktop/ComputerLogger/RPA
    RPA_directory = os.path.join(utils.utils.MAIN_DIRECTORY, 'RPA', csv_filename)
    utils.utils.createDirectory(RPA_directory)
    # RPA_filename is like 2020-02-25_23-21-57_RPA.py
    RPA_filename = csv_filename + RPA_type
    # RPA_filepath is like /Users/marco/Desktop/ComputerLogger/RPA/2020-02-25_23-21-57/2020-02-25_23-21-57_RPA.py
    RPA_filepath = os.path.join(RPA_directory, RPA_filename)
    return RPA_filepath


# Generate excel RPA python script
def generateExcelRPA(csv_file_path, dataframe):
    df = dataframe.query(' application=="Microsoft Excel" | category=="Clipboard" ')
    if df.empty: return False
    RPA_filepath = createRPAFile(csv_file_path, "_ExcelRPA.py")
    print(f"[RPA] Generating Excel RPA")
    with open(RPA_filepath, 'w') as script:
        script.write(createHeader(csv_file_path))
        # In excel I have two kind of events:
        # 1) beforeSave: filename is not yet known but here I know if the file is being saved for the first time
        # (using Save As...) or if it's just a normal save, set SaveAsUI variable
        # 2) after save: filename chosen by user is known so I know file path
        # If SaveAsUI is True I need to issue excel.save_as(path) command, else I just need excel.save()
        SaveAsUI = False
        for index, row in df.iterrows():

            e = row['event_type']
            wb = row['workbook']
            sh = row['current_worksheet']
            value = row['cell_content']
            cell_range = row['cell_range']
            range_number = row['cell_range_number']
            # assign path if not null
            path = ""
            if not pandas.isna(row['event_src_path']):
                path = row['event_src_path']
            mouse_coord = row['mouse_coord']
            cb = row['clipboard_content']

            script.write(f"# {row['timestamp']} {e}\n")

            # if mouse_coord field is not null for a given row
            if not pandas.isna(mouse_coord):
                # mouse_coord is like '[809, 743]', I need to take each component separately and remove the space
                m = list(map(lambda c: c.strip(), mouse_coord.strip('[]').split(',')))
                script.write(f"print('Moving mouse to {mouse_coord}')\n")
                script.write(f"move_mouse_to({m[0]}, {m[1]})\n")

            if (e == "copy" or e == "cut") and not pandas.isna(cb):
                script.write(f"print('Setting clipboard text')\n")
                script.write(f'set_to_clipboard("""{cb.rstrip()}""")\n')
            elif e == "newWorkbook":
                script.write(f"print('Opening Excel...')\n")
                script.write("excel = Excel()\n")
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
                script.write(f'excel.write_cell({range_number}, "{value}")\n')
            elif e == "getRange":
                script.write(f"print('Reading cell_range {cell_range}')\n")
                script.write(f"excel.activate_range('{cell_range}')\n")
                script.write(f"rc = excel.read_range('{cell_range}')\n")
                script.write(f"print('cell {cell_range} value = ' + str(rc))\n")
            elif e == "afterCalculate":
                script.write(f"print('Calculate')\n")
            elif e == "beforeSaveWorkbook":
                SaveAsUI = True if row["description"] == "SaveAs dialog box displayed" else False
            elif e == "saveWorkbook":  # case 2), after case
                script.write(f"print('saving workbook {wb}')\n")
                if SaveAsUI:  # saving for the first time
                    script.write(f"excel.save_as(r'{path}')\n")
                else:  # file already created
                    script.write(f"excel.save()\n")
            elif e == "printWorkbook" and not SaveAsUI:  # if file has already been saved and it's on disk
                script.write(f"print('Printing {wb}')\n")
                script.write(f"send_to_printer(r'{path}')\n")
            elif e == "closeWindow":
                script.write(f"print('Closing Excel...')\n")
                script.write("excel.quit()\n")
            # elif e == "resizeWindow":
            #     size = row["window_size"]
            #     width = size.split('x')[0]
            #     height = size.split('x')[1]
            #     script.write(f"print('Resizing window to {size}')\n")
            #     script.write(f"resize_window({wb} - Excel, 0, 0, {width}, {height})\n")
            # elif e == "doubleClickCellWithValue":
            #     script.write(f"print('Double clicking on cell {cell_range} with value {value}')\n")
            #     script.write(f"double_click_on_text_ocr(text='{value}')\n")
            # elif e == "rightClickCellWithValue":
            #     script.write(f"print('Right clicking on cell {cell_range} with value {value}')\n")
            #     script.write(f"right_click_on_text_ocr(text='{value}')\n")
    return True


# Generate system RPA python script
def generateSystemRPA(csv_file_path, dataframe):
    df = dataframe.query(' category=="OperatingSystem" | category=="Clipboard" ')
    if df.empty: return False
    print(f"[RPA] Generating System RPA")
    RPA_filepath = createRPAFile(csv_file_path, "_SystemRPA.py")
    with open(RPA_filepath, 'w') as script:
        script.write(createHeader(csv_file_path))
        for index, row in df.iterrows():
            e = row['event_type']
            cb = row['clipboard_content']
            app = row['application']
            # assign path if not null
            path = ""
            dest_path = ""
            if not pandas.isna(row['event_src_path']):
                path = row['event_src_path']
            if not pandas.isna(row['event_dest_path']):
                dest_path = row['event_dest_path']
            item_name = path.replace('\\', r'\\')
            item_name_dest = path.replace('\\', r'\\')

            if e not in ["selectedFile", "selectedFolder"]: script.write(f"# {row['timestamp']} {e}\n")
            if (e == "copy" or e == "cut") and not pandas.isna(cb):
                script.write(f"print('Setting clipboard text')\n")
                script.write(f'set_to_clipboard("""{cb.rstrip()}""")\n')
            elif e == "openFile" and os.path.exists(path):
                if os.path.exists(path):
                    script.write(f"print('Opening file {item_name}')\n")
                    script.write(f"open_file(r'{path}')\n")
                else:
                    script.write(f"print('Could not find {item_name} ')\n")
            elif e == "openFolder" and os.path.exists(path):
                script.write(f"print('Opening folder {item_name}')\n")
                script.write(f"show_folder(r'{path}')\n")
                pass
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
            elif e == "deleted" and os.path.exists(path):
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
                    # file
                    if os.path.splitext(path)[1]:
                        script.write(f"print('Renaming file {item_name} to {item_name_dest}')\n")
                        script.write(f"if file_exists(r'{path}'): rename_file(r'{path}', new_name='{item_name_dest}')\n")
                    # directory
                    else:
                        script.write(f"print('Renaming directory {item_name}')\n")
                        script.write(f"if folder_exists(r'{path}'): rename_folder(r'{path}', new_name='{item_name_dest}')\n")
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
                    script.write(f"press_key_combination('{hotkey_param[0]}', '{hotkey_param[1]}', '{hotkey_param[2]}')\n")
    return True


# Generate browser RPA python script
def generateBrowserRPA(csv_file_path, dataframe):
    df = dataframe.query(' category=="Browser" | category=="Clipboard" ')
    if df.empty:
        return False
    # chrome browser must be installed
    if not CHROME:
        print(f"[RPA] Google Chrome must be installed to generate RPA script.")
        return False

    print(f"[RPA] Generating Browser RPA")
    RPA_filepath = createRPAFile(csv_file_path, "_BrowserRPA.py")
    with open(RPA_filepath, 'w') as script:
        script.write(createHeader(csv_file_path))
        script.write("""try:
    from selenium.common.exceptions import WebDriverException
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import Select
    print("Opening Chrome...")
    browser = Chrome(incognito=False, focus_window=True)
    browser.get('about:blank') 
except WebDriverException as e:
    print(e)
    print("If you get 'Permission denied' you did not set the correct permissions, run 'setup.py' first.")
    sys.exit()
\n""")
        for index, row in df.iterrows():

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

            script.write(f"# {row['timestamp']} {e}\n")
            if (e == "copy" or e == "cut") and not pandas.isna(cb):
                script.write(f"print('Setting clipboard text')\n")
                script.write(f'set_to_clipboard("""{cb.rstrip()}""")\n')
            # elif e == "newWindow":
            #     script.write(f"print('Opening new window')\n")
            #     # TODO
            elif e == "newTab":
                script.write(f"print('Opening new tab')\n")
                new_tab = f'window.open("{url}");'
                script.write(f"browser.execute_script('{new_tab}')\n")
            elif e == "selectTab":
                script.write(f"print('Selecting tab')\n")
                script.write(f"browser.switch_to.window(browser.window_handles[{id}])\n")
            elif e == "closeTab":
                script.write(f"print('Closing tab')\n")
                script.write(f"browser.close()\n")
            elif e == "reload":
                script.write(f"print('Reloading page')\n")
                script.write(f"browser.refresh()\n")
            elif e == "clickLink" or e == "link" or e == "typed":
                script.write(f"print('Load link')\n")
                script.write(f"browser.get('{url}')\n")
            elif e == "changeField":
                if row['tag_category'] == "SELECT":
                    tag_value = row['tag_value']
                    script.write(f"print('Selecting text')\n")
                    script.write(f"Select(browser.find_element_by_xpath('{xpath}')).select_by_value('{tag_value}'))\n")
                else:
                    script.write(f"print('Inserting text')\n")
                    script.write(f"browser.find_element_by_xpath('{xpath}').send_keys('{value}')\n")
            elif e == "clickButton" or e == "clickRadioButton" or e == "mouseClick":
                script.write(f"print('Clicking button')\n")
                script.write(f"browser.find_element_by_xpath('{xpath}').click()\n")
            elif e == "doubleClick":
                script.write(f"print('Double click')\n")
                script.write(f"ActionChains(driver).double_click(browser.find_element_by_xpath('{xpath}')).perform()\n")
            elif e == "contextMenu":
                script.write(f"print('Double click')\n")
                script.write(f"ActionChains(driver).context_click(browser.find_element_by_xpath('{xpath}')).perform()\n")
            elif e == "selectText":
                pass

    return True


# file called by GUI when main script terminates and csv log file is created.
def generateRPAScript(csv_file_path):
    # check if given csv log file exists
    if not os.path.exists(csv_file_path):
        print(f"[RPA] Can't find specified csv_file_path {csv_file_path}")
        return False
    else:
        dataframe = pandas.read_csv(csv_file_path)
        generateExcelRPA(csv_file_path, dataframe)
        generateSystemRPA(csv_file_path, dataframe)
        generateBrowserRPA(csv_file_path, dataframe)
        return True
