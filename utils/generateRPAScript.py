import sys

sys.path.append('../')  # this way main file is visible from this file
import pandas
import os
import utils.utils
from utils.config import MyConfig


# Adds import statements to generated python file
def createHeader(csv_file_path):
    return f"""# This file was auto generated based on {csv_file_path}
    import sys, os
    try:
        from automagica import *
    except ImportError as e:
        print("Please install 'automagica' module running 'pip3 install -U automagica'")
        print("If you get openssl error check here https://github.com/marco2012/ComputerLogger#rpa")
        sys.exit()
    \n"""


# Create rpa directory and file for each specific RPA
def createRPAFile(csv_file_path, RPA_type):
    # csv_file_path is like 2020-02-25_23-21-57.csv

    # RPA_directory is like /Users/marco/Desktop/ComputerLogger/RPA
    RPA_directory = os.path.join(MyConfig.get_instance().main_directory, 'RPA')
    utils.utils.createDirectory(RPA_directory)

    name = "_RPA.py"
    if RPA_type == "excel":
        name = "_ExcelRPA.py"
    elif RPA_type == "system":
        name = "_SystemRPA.py"
    elif RPA_type == "browser":
        name = "_BrowserRPA.py"

    # filename is like 2020-02-25_23-21-57_RPA.py
    RPA_filename = os.path.splitext(os.path.basename(csv_file_path))[0] + name
    # file_path is like /Users/marco/Desktop/ComputerLogger/RPA/2020-02-25_23-21-57_RPA.py
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
                script.write(f"print('Printing {wb}')")
                script.write(f"send_to_printer(r'{path}')")
            elif e == "closeWindow":
                script.write(f"print('Closing Excel...')\n")
                # script.write("excel.quit()\n")


# Generate system RPA python script
def generateSystemRPA(csv_file_path, df, RPA_filepath):
    with open(RPA_filepath, 'w') as script:
        script.write(createHeader(csv_file_path))
        for index, row in df.iterrows():
            e = row['event_type']
            cb = row['clipboard_content']
            path = row['event_src_path']
            if e == "copy" or e == "cut":
                script.write(f"Setting clipboard text\n")
                script.write(f"set_to_clipboard('{cb}')\n")
            elif e == "openFile":
                if os.path.exists(path):
                    script.write(f"Opening file r'{path}'\n")
                    script.write(f"open_file(r'{path}')\n")
                else:
                    script.write(f"Could not find r'{path}'\n")

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
        return None, None, None
    else:
        dataframe = pandas.read_csv(csv_file_path)
        excel_df = dataframe[(dataframe['application'] == "Microsoft Excel")]
        system_df = dataframe[(dataframe['category'] == "OperatingSystem") | (dataframe['category'] == "Clipboard")]
        browser_df = dataframe[(dataframe['application'] == "Chrome")]

    # check if opened csv files contains data related to microsoft excel or system
    if excel_df.empty and system_df.empty:
        print("[RPA] Can't generate RPA actions")
        return None, None, None
    else:
        excel_RPA_filepath = createRPAFile(csv_file_path, "excel")
        system_RPA_filepath = createRPAFile(csv_file_path, "system")
        browser_RPA_filepath = createRPAFile(csv_file_path, "browser")

        generateExcelRPA(csv_file_path, excel_df, excel_RPA_filepath)
        generateSystemRPA(csv_file_path, system_df, system_RPA_filepath)
        generateBrowserRPA(csv_file_path, system_df, browser_RPA_filepath)

        print(f"[RPA] Generated scripts: {excel_RPA_filepath, system_RPA_filepath}")
        return excel_RPA_filepath, system_RPA_filepath, None
