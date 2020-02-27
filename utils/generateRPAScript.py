# ******************************
# Generate RPA script
# Automatically generate RPA script from csv log file. Called by
# GUI when main process is terminated and csv is available.
# ******************************

import sys
sys.path.append('../')  # this way main file is visible from this file
import pandas
import os
from multiprocessing import Process
import utils.utils
from utils.config import MyConfig

# try:
#     from graphviz import Digraph
# except ImportError as e:
#     if utils.utils.WINDOWS:
#         print("Please install graphviz from 'https://graphviz.gitlab.io/_pages/Download/windows/graphviz-2.38.msi'")
#         sys.exit()
#     elif utils.utils.MAC:
#         print("Please install graphviz with 'brew install graphviz'")
#         sys.exit()


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
    csv_filename = os.path.splitext(os.path.basename(csv_file_path))[0]
    # RPA_directory is like /Users/marco/Desktop/ComputerLogger/RPA
    RPA_directory = os.path.join(MyConfig.get_instance().main_directory, 'RPA', csv_filename)
    utils.utils.createDirectory(RPA_directory)
    # RPA_filename is like 2020-02-25_23-21-57_RPA.py
    RPA_filename = csv_filename + RPA_type
    # RPA_filepath is like /Users/marco/Desktop/ComputerLogger/RPA/2020-02-25_23-21-57/2020-02-25_23-21-57_RPA.py
    RPA_filepath = os.path.join(RPA_directory, RPA_filename)
    return RPA_filepath


# Generate excel RPA python script
def generateExcelRPA(csv_file_path, df, RPA_filepath):
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
            path = row['event_src_path']
            script.write(f"# {row['timestamp']} {e}\n")
            if e == "newWorkbook":
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
                script.write(f"excel.read_cell({range_number})\n")
            elif e == "editCellSheet":
                script.write(f"print('Writing cell {cell_range}')\n")
                script.write(f'excel.write_cell({range_number}, "{value}")\n')
            elif e == "getRange":
                script.write(f"print('Reading cell_range {cell_range}')\n")
                script.write(f"excel.activate_range('{cell_range}')\n")
                script.write(f"excel.read_range('{cell_range}')\n")
            # elif e == "afterCalculate":
            #     script.write(f"print('Calculate')\n")
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


# Generate system RPA python script
def generateSystemRPA(csv_file_path, df, RPA_filepath):

    # import itertools
    # csv_filename = os.path.splitext(os.path.basename(csv_file_path))[0]
    # dot = Digraph(filename=csv_filename)
    # dot.attr('node', shape='doublecircle')
    # dot.node('start')
    # dot.node('end')
    # dot.attr('node', shape='circle')
    # events = list()
    # for index, row in df.iterrows():
    #     e = row['event_type']
    #     events.append(e)
    #     dot.node(e)
    # def pairwise(iterable):
    #     a, b = itertools.tee(iterable)
    #     next(b, None)
    #     return zip(a, b)
    # dot.edge('start', events[0])
    # for c, n in pairwise(events):
    #     dot.edge(c, n)
    # dot.edge(events[-1], 'end')
    # dot.render(os.path.join(os.path.dirname(RPA_filepath), csv_filename), view=True)

    with open(RPA_filepath, 'w') as script:
        script.write(createHeader(csv_file_path))
        for index, row in df.iterrows():
            e = row['event_type']
            cb = row['clipboard_content']
            app = row['application']
            path = row['event_src_path']
            dest_path = row['event_dest_path']
            item_name = path.replace('\\', r'\\') if type(path) == str else path
            item_name_dest = path.replace('\\', r'\\') if type(path) == str else path
            if e not in ["selectedFile", "selectedFolder"]: script.write(f"# {row['timestamp']} {e}\n")
            if e == "copy" or e == "cut":
                script.write(f"print('Setting clipboard text')\n")
                script.write(f"set_to_clipboard('{cb}')\n")
            elif e == "openFile":
                if os.path.exists(path):
                    script.write(f"print('Opening file {item_name}')\n")
                    script.write(f"open_file(r'{path}')\n")
                else:
                    script.write(f"print('Could not find {item_name} ')\n")
            elif e == "openFolder" and os.path.exists(path):
                script.write(f"print('Opening folder {item_name}')\n")
                script.write(f"show_folder(r'{path}')\n")
                pass
            elif e == "programOpen":
                script.write(f"print('Opening {app}')\n")
                script.write(f"if file_exists(r'{path}'): run(r'{path}')\n")
            elif e == "programClose":
                script.write(f"print('Closing {app}')\n")
                script.write(f"if file_exists(r'{path}'): kill_process(r'{path}')\n")
            elif e == "created":
                # check if i have a file (with extension)
                if os.path.splitext(path)[1]:
                    script.write(f"print('Creating file {item_name}')\n")
                    script.write(f"open(r'{path}', 'w')\n")
                # otherwise assume it's a directory
                else:
                    script.write(f"print('Creating directory {item_name}')\n")
                    script.write(f"create_folder(r'{path}')\n")
            elif e == "deleted":
                # check if i have a file (with extension)
                if os.path.splitext(path)[1]:
                    script.write(f"print('Removing file {item_name}')\n")
                    script.write(f"if file_exists(r'{path}'): remove_file(r'{path}')\n")
                # otherwise assume it's a directory
                else:
                    script.write(f"print('Removing directory {item_name}')\n")
                    script.write(f"if folder_exists(r'{path}'): remove_folder(r'{path}')\n")
            elif e == "moved":
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


# Generate browser RPA python script TODO
def generateBrowserRPA(csv_file_path, df, RPA_filepath):
    # with open(RPA_filepath, 'w') as script:
    #     script.write(createHeader(csv_file_path))
    #     for index, row in df.iterrows():
    #         e = row['event_type']
    pass


# file called by GUI when main script terminates and csv log file is created.
def generateRPAScript(csv_file_path):
    # check if given csv log file exists
    if not os.path.exists(csv_file_path):
        print(f"[RPA] Can't find specified csv_file_path {csv_file_path}")
        return False
    else:
        dataframe = pandas.read_csv(csv_file_path)
        excel_df = dataframe[(dataframe['application'] == "Microsoft Excel")]
        system_df = dataframe[(dataframe['category'] == "OperatingSystem") | (dataframe['category'] == "Clipboard")]
        browser_df = dataframe[(dataframe['application'] == "Chrome")]
        processes = list()

        if not excel_df.empty: # TODO add macOS support
            print(f"[RPA] Generating excel RPA")
            excel_RPA_filepath = createRPAFile(csv_file_path, "_ExcelRPA.py")
            p0 = Process(target=generateExcelRPA, args=(csv_file_path, excel_df, excel_RPA_filepath))
            processes.append(p0)
            p0.start()
        if not system_df.empty:
            print(f"[RPA] Generating system RPA")
            system_RPA_filepath = createRPAFile(csv_file_path, "_SystemRPA.py")
            p1 = Process(target=generateSystemRPA, args=(csv_file_path, system_df, system_RPA_filepath))
            processes.append(p1)
            p1.start()
        # if not browser_df.empty:
        #     print(f"[RPA] Generating browser RPA")
        #     browser_RPA_filepath = createRPAFile(csv_file_path, "_BrowserRPA.py")
        #     p2 = Process(target=generateBrowserRPA, args=(csv_file_path, browser_df, browser_RPA_filepath))
        #     processes.append(p2)
        #     p2.start()

        [p.join() for p in processes]

        return True
