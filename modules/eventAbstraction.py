import pandas
import utils.utils
import ntpath

try:
    from pm4py.util import constants
    from pm4py.objects.conversion.log import factory as conversion_factory
except ImportError as e:
    print("[PROCESS MINING] Process mining analysis has been disabled because 'pm4py' module is not installed."
          "See https://github.com/bpm-diag/smartRPA#1-pm4py")
    print(e)


def _getHighLevelEvent(row):
    """
    Convert low-level dataframe row into high-level.

    Generate descriptive string for each row based on event type and other fields.

    :param row: row of the dataframe
    :return: high level description of the row
    """
    e = row["concept:name"]
    url = utils.utils.getHostname(row['browser_url'])
    app = row['application']
    cb = utils.utils.removeWhitespaces(row['clipboard_content'])
    # general
    if e in ["copy", "cut", "paste"] and cb:  # take only first 40 characters of clipboard
        cutoff = 40
        if len(cb) > cutoff:
            cb = cb[:cutoff] + '...'
        return f"[{app}] Copy and Paste -> '{cb}'"

    # browser
    elif e in ["clickRadioButton"]:
        return f"[{app}] Click {row['tag_type']} '{row['tag_name']}' with value '{row['tag_value']}' on {url}"
    elif e in ["clickButton", "clickTextField", "doubleClick", "clickTextField", "mouseClick",
               "clickCheckboxButton", "clickRadioButton"]:
        if row['tag_type'] == 'submit':
            return f"[{app}] Submit {row['tag_category'].lower()} on {url}"
        else:
            if row['tag_type'].lower() == row['tag_category'].lower():
                return f"[{app}] Click {row['tag_type']} '{row['tag_name']}' on {url}"
            else:
                return f"[{app}] Click {row['tag_type']} {row['tag_category'].lower()} '{row['tag_name']}' on {url}"
    elif e in ["clickLink"]:
        return f"[{app}] Click '{row['tag_innerText'][:40]}' on {url}"
    elif (e in ["link", "reload", "generated", "urlHashChange"]) or (
            e == "typed" and "fromAddressBar" in row['eventQual']):
        return f"[{app}] Navigate to {url}"
    elif e in ["submit", "formSubmit", "selectOptions"]:
        return "Submit"
    elif e in ["selectTab", "moveTab", "zoomTab"]:
        return "Browser Tab"
    elif e in ["newTab"]:
        return f"[{app}] Open tab"
    elif e in ["closeTab"]:
        return f"[{app}] Close tab"
    elif e in ["newWindow"]:
        return f"[{app}] Open window"
    elif e in ["closeWindow"]:
        return f"[{app}] Close window"
    elif e in ["typed", "selectText", "contextMenu"]:
        category = row['tag_category']
        if len(category) == 0:
            return f"[{app}] Edit on {url}"
        else:
            return f"[{app}] Edit {row['tag_category']} on {url}"
    elif e in ["changeField"]:
        # sometimes 2 out of 3 tags fields are equal, like TEXTAREA, textarea
        # I don't want to repeat them so I remove duplicates by creating a set and then print the remaining ones
        tags = [row['tag_type'], row['tag_category'].lower()]  # , row['tag_name']
        value = row['tag_value'].replace('\n', ', ')
        return f"[{app}] Write in {' '.join(tags)} '{row['tag_name']}' on {url} -> '{value}'"
    elif e in ["startDownload"]:
        return f"[{app}] Download started"

    # system
    elif e in ["itemSelected", "deleted", "created", "Mount", "openFile", "openFolder"]:
        path = row['event_src_path'].replace('\\', r'\\')
        name, extension = ntpath.splitext(path)
        name = ntpath.basename(path)
        fileorfolder = ""
        action = ""
        if extension:
            fileorfolder = "file"
        else:
            fileorfolder = "folder"
        if e in ["created", "Mount"]:
            action = "Create"
        elif e == "deleted":
            action = "Delete"
        elif e in ["openFile", "openFolder"]:
            action = "Open"
        return f"[OS] {action} {fileorfolder} '{path}'"
    elif e in ['moved', 'Unmount']:
        path = row['event_dest_path'] if e == "moved" else row['event_src_path']
        path = path.replace('\\', r'\\')
        _, extension = ntpath.splitext(path)
        if extension:
            return f"[{app}] Rename file as '{path}'"
        else:
            return f"[{app}] Rename folder as '{path}'"
    elif e in ["programOpen", "programClose"]:
        return f"[OS] Use program '{app}'"
    elif e in ["hotkey"]:
        return f"[{app}] Press '{row['description']}' hotkey ({row['id']})"

    # excel win
    elif e in ["newWorkbook", "openWorkbook", "activateWorkbook"]:
        if row['workbook']:
            return f"[Excel] Open {row['workbook']}"
        else:
            name = ntpath.basename(row['event_src_path'])
            return f"[Excel] Open '{name}'"
    elif e in ["getCell", "getRange", "WorksheetCalculated", "WorksheetFormatChanged"]:
        if row['current_worksheet'] != '':
            return f"[Excel] Edit Cell on {row['current_worksheet']}"
        else:
            return f"[Excel] Edit Cell"
    elif e in ["editCellSheet", "editCell", "editRange"]:
        return f"[Excel] Edit cell {row['cell_range']} on {row['current_worksheet']} with value '{row['cell_content']}'"
    elif e in ["addWorksheet", "deselectWorksheet", "selectWorksheet", "WorksheetActivated"]:
        return f"[Excel] Select {row['current_worksheet']}"

    # powerpoint
    elif e in ["newPresentation"]:
        return f"[PowerPoint] Open {row['title']}"
    elif e in ["newPresentationSlide", "savePresentation", "SlideSelectionChanged"]:
        return f"[PowerPoint] Edit presentation"

    # word
    elif e in ["newDocument"]:
        return f"[Word] Open document"
    elif e in ["changeDocument"]:
        return f"[Word] Edit document"

    else:
        return e


def aggregateData(df: pandas.DataFrame, remove_duplicates=False):
    """
    Transforms low level actions used for RPA generation to high level used for DFG, petri net, BPMN.

    * rows with specific events are filtered because irrelevant for the analysis
    * rows with empty clipboard are removed because they don't need to be abstracted to high level
    * similar events are grouped together
    * a new column called 'customClassifier' is added to the dataframe, containing the high level description of each row, generated using _getHighLevelEvent() method
    * if remove_duplicates is true, duplicate rows are removed
    * dataframe with high level descriptions for each row is returned

    :param df: input dataframe
    :param remove_duplicates: if true, duplicate rows are removed
    :return: high-level dataframe, log, parameters to generate diagrams
    """

    # filter rows
    df = df[~df.browser_url.str.contains('chrome-extension://')]
    df = df[~df.eventQual.str.contains('clientRedirect')]
    # df = df[~df.eventQual.str.contains('serverRedirect')]

    # remove rows that contain empty clipboard text
    for row_index, row in df.iterrows():
        concept_name = row['concept:name']
        cb_content = row['clipboard_content']
        if (concept_name in ['cut', 'copy', 'paste']) and utils.utils.removeWhitespaces(cb_content) == '':
            df = df.drop(row_index)  # returns a copy, previously was inplace so it returned null and side-effect db

    rows_to_remove = ["activateWindow", "deactivateWindow", "openWindow", "newWindow", "closeWindow",
                      "selectTab", "moveTab", "zoomTab", "submit", "formSubmit",
                      "installBrowserExtension", "enableBrowserExtension", "disableBrowserExtension",
                      "resizeWindow", "logonComplete", "startPage", "doubleClickCellWithValue",
                      "doubleClickEmptyCell", "rightClickCellWithValue", "rightClickEmptyCell", "afterCalculate",
                      "closePresentation", "SlideSelectionChanged", "closeWorkbook",
                      "deactivateWorkbook", "WorksheetAdded", "autoBookmark", "selectedFolder", "selectedFile",
                      "manualSubframe", "KernelDropped", "keyword", "dragElement"]  # mouseclick

    df = df[~df['concept:name'].isin(rows_to_remove)]

    # convert each row of events to high level
    df['customClassifier'] = df.apply(lambda row: _getHighLevelEvent(row), axis=1)

    # check duplicates
    # print(df[df['customClassifier'].duplicated() == True])
    # remove duplicates
    if remove_duplicates:
        df = df.drop_duplicates(subset='customClassifier', keep='first')

    log = conversion_factory.apply(df)
    parameters = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "customClassifier"}

    return df, log, parameters
