# ****************************** #
# Office logger
# Manages Excel, Word, Powerpoint, Outlook events
# ****************************** #

import sys
sys.path.append('../../')  # this way main file is visible from this file
from re import findall
import os
from shutil import rmtree
from itertools import chain
import utils.utils
from modules.consumerServer import SERVER_ADDR
import utils.config

if utils.utils.WINDOWS:
    from win32com.client import DispatchWithEvents
    import pythoncom
    from win32com import __gen_path__
    import ctypes


class ExcelEvents:
    """
    Excel application object events

    The parameters in each method of these class are passed automatically by the APIs when the event occurs.

    https://docs.microsoft.com/en-us/office/vba/api/excel.application(object)
    """
    def __init__(self):
        self.seen_events = {}
        self.Visible = 1
        # self.mouse = mouse.Controller()

        # This variable controls OnSheetSelectionChange, if True an actions is logged every time a cell is selected. It's
        # resource expensive, so it's possible to turn it off by setting variable to False
        self.LOG_EVERY_CELL = True

    def setApplication(self, application):
        self.application = application

    # ************
    # Utils
    # ************

    def getWorksheets(self, Sh, Wb):
        """
        return list of active worksheet in workbook

        :param Sh: worksheet
        :param Wb: workbook
        :return: list of active worksheet in workbook
        """
        if Sh:
            return list(map(lambda sh: sh.Name, Sh.Parent.Worksheets))
        elif Wb:
            return list(map(lambda sh: sh.Name, Wb.Worksheets))

    # ************
    # Window
    # ************

    def OnWindowActivate(self, Wb, Wn):
        """
        Triggers when excel windows is opened

        :param Wb: workbook
        :param Wn: window
        :return: openWindow event
        """
        self.seen_events["OnWindowActivate"] = None

        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} openWindow workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} window id:{Wn.WindowNumber} path: {Wb.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "openWindow",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "id": Wn.WindowNumber,
            "event_src_path": Wb.Path
        })

    def OnWindowDeactivate(self, Wb, Wn):
        """
        Triggers when excel windows is closed

        :param Wb: workbook
        :param Wn: window
        :return: closeWindow event
        """
        self.seen_events["OnWindowDeactivate"] = None
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} closeWindow workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} window id:{Wn.WindowNumber} path: {Wb.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "closeWindow",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "id": Wn.WindowNumber,
            "event_src_path": Wb.Path
        })

    def OnWindowResize(self, Wb, Wn):
        """
        Triggers when excel windows is resized

        :param Wb: workbook
        :param Wn: window
        :return: resizeWindow event
        """
        x, y, width, height = utils.utils.getActiveWindowInfo('size')
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} resizeWindow workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} window id:{Wn.WindowNumber} size {x},{y},{width},{height} ")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "resizeWindow",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "id": Wn.WindowNumber,
            "event_src_path": Wb.Path,
            "window_size": f"{x},{y},{width},{height}"
            # "window_size": f"{Wn.Width},{Wn.Height}"
        })

    # ************
    # Workbook
    # ************

    def OnNewWorkbook(self, Wb):
        """
        New workbook is created

        :param Wb: workbook
        :return: newWorkbook event
        """
        self.seen_events["OnNewWorkbook"] = None
        # get excel window size
        x, y, width, height = utils.utils.getActiveWindowInfo('size')
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} newWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path} window_size {x},{y},{width},{height}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "newWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": Wb.Path,
            "window_size": f"{x},{y},{width},{height}"
        })

    def OnWorkbookOpen(self, Wb):
        """
        Workbook is opened

        :param Wb: workbook
        :return: openWorkbook event
        """
        path = os.path.join(Wb.Path, Wb.Name)
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} openWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "openWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": path
        })

    def OnWorkbookNewSheet(self, Wb, Sh):
        """
        New sheet is created

        :param Wb: workbook
        :param Sh: worksheet
        :return: addWorksheet event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} addWorksheet workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "addWorksheet",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": Wb.Path,

        })

    def OnWorkbookBeforeSave(self, Wb, SaveAsUI, Cancel):
        """
        This is triggered right before a workbook is saved

        :param Wb: workbook
        :param SaveAsUI: 'save as' dialog box displayed to user
        :param Cancel: saving is canceled
        :return: beforeSaveWorkbook event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} saveWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} saveAs dialog {SaveAsUI}")
        if SaveAsUI:
            description = "SaveAs dialog box displayed"
        else:
            description = "SaveAs dialog box not displayed"
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "beforeSaveWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "description": description,

        })

    def OnWorkbookAfterSave(self, Wb, Success):
        """
        This event is triggered after a workbook has been saved.

        :param Wb: workbook
        :param Success: boolean value to indicate if saving was succesful
        :return: saveWorkbook event
        """
        savedPath = os.path.join(Wb.Path, Wb.Name)
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} saveWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {savedPath}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "saveWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": savedPath,

        })

    def OnWorkbookAddinInstall(self, Wb):
        """
        An AddIn is installed in excel

        :param Wb: workbook
        :return: addinInstalledWorkbook event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} addinInstalledWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "addinInstalledWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": Wb.Path
        })

    def OnWorkbookAddinUninstall(self, Wb):
        """
        An AddIn is uninstalled in excel

        :param Wb: workbook
        :return: addinUninstalledWorkbook event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} addinUninstalledWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "addinUninstalledWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": Wb.Path
        })

    def OnWorkbookAfterXmlImport(self, Wb, Map, Url, Result):
        """
        XML is imported into excel

        :param Wb: workbook
        :param Map:
        :param Url:
        :param Result: import result
        :return: XMLImportWorkbook event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} XMLImportWOrkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "XMLImportWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": Wb.Path
        })

    def OnWorkbookAfterXmlExport(self, Wb, Map, Url, Result):
        """
        XML is exported from excel

        :param Wb: workbook
        :param Map:
        :param Url:
        :param Result: import result
        :return: XMLExportWorkbook event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} XMLExportWOrkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "XMLExportWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": Wb.Path
        })

    def OnWorkbookBeforePrint(self, Wb, Cancel):
        """
        Print action is triggered in a workbook

        :param Wb: workbook
        :param Cancel: true if print is canceled
        :return: printWorkbook event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} printWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "printWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": Wb.Path,

        })

    def OnWorkbookBeforeClose(self, Wb, Cancel):
        """
        workbook is closed

        :param Wb: workbook
        :param Cancel: true if close is canceled
        :return: closeWorkbook event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} closeWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "closeWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": Wb.Path,

        })

    def OnWorkbookActivate(self, Wb):
        """
        workbook is activated (occurs when excel window is clicked and goes to foreground)

        :param Wb: workbook
        :return: activateWorkbook event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} activateWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "activateWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": Wb.Path,

        })

    def OnWorkbookDeactivate(self, Wb):
        """
        workbook is deactivated (occurs when excel window is not visible anymore)

        :param Wb: workbook
        :return: deactivateWorkbook event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} deactivateWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "deactivateWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": Wb.Path,

        })

    def OnWorkbookModelChange(self, Wb, Changes):
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} modelChangeWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "modelChangeWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": Wb.Path
        })

    def OnWorkbookNewChart(self, Wb, Ch):
        """
        A new chart is added to the open workbook

        :param Wb: workbook
        :param Ch: chart
        :return: newChartWorkbook event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} newChartWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "newChartWorkbook",
            "workbook": Wb.Name,
            "current_worksheet": Wb.ActiveSheet.Name,
            "worksheets": self.getWorksheets(None, Wb),
            "event_src_path": Wb.Path,
            "title": Ch.Name
        })

    def OnAfterCalculate(self):
        """
        This event occurs after a calculation has been performed

        :return: afterCalculate event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} afterCalculate")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "afterCalculate",
        })

    # ************
    # Worksheet
    # ************

    def filterNoneRangeValues(self, values):
        """
        When a range of cells is selected, Target.Value is a Tuple of tuples containing the value of every
        selected cell Target.Value = ((None, None, None, None), (None, 'prova', None, None)). I'm
        interested only in cells with meaningful value, so I create a single list with all the tuples in
        Target.Value (by chaining the tuples using chain.from_iterable(list)) obtaining [None, None, None,
        None, None, 'prova', None, None] Now I remove the elements that are None by applying a filter
        operator to the previous list

        :param values: tuple of values
        :return: tuple of values without None values
        """
        if values:
            try:
                # If entire column/row is selected, I consider only the first 10.000 to save memory
                # return list(filter(lambda s: s is not None, list(chain.from_iterable(list(values)))))
                return [s for s in list(chain.from_iterable(list(values[:8000]))) if s is not None]
            except TypeError:
                return values
        else:
            return ""

    def OnSheetActivate(self, Sh):
        """
        Occurs when a worksheet is selected

        :param Sh: worksheet
        :return: selectWorksheet event
        """
        # to get the list of active worksheet names, I cycle through the parent which is the workbook
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Microsoft Excel selectWorksheet {Sh.Name} {Sh.Parent.Name} {self.getWorksheets(Sh, None)}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "selectWorksheet",
            "workbook": Sh.Parent.Name,
            "current_worksheet": Sh.Name,
            "worksheets": self.getWorksheets(Sh, None),
            "event_src_path": Sh.Parent.Path,

        })

    def OnSheetBeforeDelete(self, Sh):
        """
        Occurs when a worksheet is deleted

        :param Sh: worksheet
        :return: deleteWorksheet event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Microsoft Excel deleteWorksheet {Sh.Name} {Sh.Parent.Name} {self.getWorksheets(Sh, None)}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "deleteWorksheet",
            "workbook": Sh.Parent.Name,
            "current_worksheet": Sh.Name,
            "worksheets": self.getWorksheets(Sh, None),

        }),

    def OnSheetBeforeDoubleClick(self, Sh, Target, Cancel):
        """
        Triggered when double clicking on a cell

        :param Sh: worksheet
        :param Target: cell clicked
        :param Cancel: true if event is canceled
        :return: doubleClickCellWithValue/doubleClickEmptyCell event
        """
        event_type = "doubleClickEmptyCell"
        value = ""
        if Target.Value:  # cell has value
            event_type = "doubleClickCellWithValue"
            value = Target.Value

        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Microsoft Excel {event_type} {Sh.Name} {Sh.Parent.Name} {Target.Address.replace('$', '')} {value}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": event_type,
            "workbook": Sh.Parent.Name,
            "current_worksheet": Sh.Name,
            "cell_range": Target.Address.replace('$', ''),
            "cell_content": value,

        })

    def OnSheetBeforeRightClick(self, Sh, Target, Cancel):
        """
        Triggered when right clicking on a cell

        :param Sh: worksheet
        :param Target: cell clicked
        :param Cancel: true if event is canceled
        :return: rightClickCellWithValue/rightClickEmptyCell event
        """
        event_type = "rightClickEmptyCell"
        value = ""
        if Target.Value:  # cell has value
            event_type = "rightClickCellWithValue"
            value = Target.Value
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Microsoft Excel {event_type} {Sh.Name} {Sh.Parent.Name} {Target.Address.replace('$', '')} {value}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": event_type,
            "workbook": Sh.Parent.Name,
            "current_worksheet": Sh.Name,
            "cell_range": Target.Address.replace('$', ''),
            "cell_content": value,

        })

    def OnSheetCalculate(self, Sh):
        """
        Occurs when a calculation is performed

        :param Sh: worksheet
        :return: sheetCalculate event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Microsoft Excel sheetCalculate {Sh.Name} {Sh.Parent.Name} ")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "sheetCalculate",
            "workbook": Sh.Parent.Name,
            "current_worksheet": Sh.Name,

        })

    def OnSheetChange(self, Sh, Target):
        """
        Occurs when a cell is edited

        :param Sh: worksheet
        :param Target: edited cell
        :return: editCellSheet event
        """

        # if entire row/column is selected, get only the first 8000 occurrences to save space
        value = self.filterNoneRangeValues(Target.Value)
        cell_range_number = f"{Target.Column},{Target.Row}"
        entireColAddres = Target.EntireColumn.Address
        entireRowAddres = Target.EntireRow.Address
        cellAddress = Target.Address
        event_type = "editCellSheet"
        cell_range = cellAddress.replace('$', '')

        # can't detect if insertion or removal
        # # row inserted/deleted
        # if not cellAddress == entireColAddres:
        #     event_type = "deleteRow"
        #     cell_range_number = f"{Target.Row},{Target.Row}"
        # # column inserted/deleted
        # elif not cellAddress == entireRowAddres:
        #     event_type = "deleteColumn"
        #     cell_range_number = f"{Target.Column},{Target.Column}"

        # filterNoneRangeValues returns a list but if user selected a single cell I get a list of letters like
        # ['p', 'y', 't', 'h', 'o', 'n'] so if there is no ':' in selection i join the list to get the word back
        if not ':' in cell_range:
            try:
                value = ''.join(value)
            except TypeError:
                pass

        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Microsoft Excel editCellSheet {Sh.Name} {Sh.Parent.Name} {cell_range} ({cell_range_number}) {value}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": event_type,
            "workbook": Sh.Parent.Name,
            "current_worksheet": Sh.Name,
            "cell_range": cell_range,
            "cell_range_number": cell_range_number,
            "cell_content": value,

        })

    def OnSheetDeactivate(self, Sh):
        """
        Occurs when a worksheet is deselected

        :param Sh: worksheet
        :return: deselectWorksheet event
        """
        self.seen_events["OnSheetDeactivate"] = None
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Microsoft Excel deselectWorksheet {Sh.Name} {Sh.Parent.Name} {self.getWorksheets(Sh, None)}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "deselectWorksheet",
            "workbook": Sh.Parent.Name,
            "current_worksheet": Sh.Name,
            "worksheets": self.getWorksheets(Sh, None),
            "event_src_path": Sh.Parent.Path,

        })

    def OnSheetFollowHyperlink(self, Sh, Target):
        """
        Occurs when a link is clicked

        :param Sh: worksheet
        :param Target: cell clicked
        :return: followHiperlinkSheet event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Microsoft Excel followHiperlinkSheet {Sh.Name} {Sh.Parent.Name} {Target.Range.Address.replace('$', '')} {Target.Address}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "followHiperlinkSheet",
            "workbook": Sh.Parent.Name,
            "current_worksheet": Sh.Name,
            "cell_range": Target.Range.Address.replace('$', ''),
            "browser_url": Target.Address,

        })

    def OnSheetPivotTableAfterValueChange(self, Sh, TargetPivotTable, TargetRange):
        """
        Occurs when values in a pivot table change.

        :param Sh: worksheet
        :param TargetPivotTable: target table
        :param TargetRange: range modified
        :return: pivotTableValueChangeSheet event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Microsoft Excel pivotTableValueChangeSheet {Sh.Name} {Sh.Parent.Name} {TargetRange.Address.replace('$', '')} {TargetRange.Value}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "pivotTableValueChangeSheet",
            "workbook": Sh.Parent.Name,
            "current_worksheet": Sh.Name,
            "cell_range": TargetRange.Address.replace('$', ''),
            "cell_content": TargetRange.Value if TargetRange.Value else ""
        })

    def OnSheetSelectionChange(self, Sh, Target):
        """
        Occurs when a cell or range of cells is selected

        :param Sh: worksheet
        :param Target: selected range
        :return: getCell/getRange event
        """
        # value returned is in the format $B$3:$D$3, I remove $ sign
        cells_selected = Target.Address.replace('$', '')
        cell_range_number = f"{Target.Column},{Target.Row}"
        event_type = "getCell"
        value = Target.Value if Target.Value else ""
        rangeSelected = (':' in cells_selected)  # True if the user selected a range of cells
        # if a range of cells has been selected
        if rangeSelected:
            event_type = "getRange"
            # Returns values of selected cells removing empty cells
            value = self.filterNoneRangeValues(Target.Value)

        # If LOG_EVERY_CELL is False and a user selects a single cell the event is not logged
        if rangeSelected or self.LOG_EVERY_CELL:
            print(
                f"{utils.utils.timestamp()} {utils.utils.USER} Microsoft Excel {event_type} {Sh.Name} {Sh.Parent.Name} {cells_selected} ({cell_range_number}) {value}")
            utils.utils.session.post(SERVER_ADDR, json={
                "timestamp": utils.utils.timestamp(),
                "user": utils.utils.USER,
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": event_type,
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "cell_range": cells_selected,
                "cell_range_number": cell_range_number,
                "cell_content": value,

            })

    def OnSheetTableUpdate(self, Sh, Target):
        """
        Occurs when a table is updated

        :param Sh: worksheet
        :param Target: table
        :return: worksheetTableUpdated event
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Microsoft Excel worksheetTableUpdated {Sh.Name} {Sh.Parent.Name} ")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel",
            "event_type": "worksheetTableUpdated",
            "workbook": Sh.Parent.Name,
            "current_worksheet": Sh.Name,
        })


# Takes filename as input if user wants to open existing file
def excelEvents(status_queue, filepath=None):
    """
    Handle excel events on windows using pythoncom.

    Also manages exception in case excel instance fails to launch.

    :param status_queue: queue to pring messages on GUI
    :param filepath: optional path of excel file to open
    """

    try:
        # needed for thread
        pythoncom.CoInitialize()

        # start new instance of Excel
        e = DispatchWithEvents("Excel.Application", ExcelEvents)

        if filepath:
            # open existing workbook
            e.Workbooks.Open(filepath)
        else:
            # create new empty workbook that contains worksheet
            e.Workbooks.Add()

        runLoop(e)
        status_queue.put("[officeEvents] Excel logging started")
        if not CheckSeenEvents(e, ["OnNewWorkbook", "OnWindowActivate"]):
            sys.exit(1)

    except Exception as e:
        exception = str(e)
        print(f"Failed to launch Excel: {exception}")
        # https://stackoverflow.com/q/47608506/1440037
        if "win32com.gen_py" in exception:
            # https://stackoverflow.com/a/54422675/1440037  Deleting the gen_py output directory and re-running the
            # script should fix the issue find the corrupted directory to remove in gen_py path using regex (
            # directory is in the form 'win32com.gen_py.00020813-0000-0000-C000-000000000046x0x1x9) I should have a
            # string like '00020813-0000-0000-C000-000000000046x0x1x9'
            dirToRemove = findall(r"'(.*?)'", exception)[0].split('.')[-1]
            if not dirToRemove:
                # if regex failed use default folder
                dirToRemove = '00020813-0000-0000-C000-000000000046x0x1x9'
            pathToRemove = os.path.join(__gen_path__, dirToRemove)
            print(f"Trying to fix the error, deleting {pathToRemove}")
            rmtree(pathToRemove, ignore_errors=True)
            if not os.path.exists(pathToRemove):
                print("The error should now be fixed, try to execute the program again.")


def excelEventsMacServer(status_queue, excelFilepath=None):
    """
    Handle excel events on macOS using xlwings.

    The logging process is different on macOS.
    An excel Add-in in javascript is installed on excel and it sends data to a node.js server started by this function.

    :param status_queue: queue to print messages on GUI
    :param excelFilepath: optional path of excel file to open
    :return: openWorkbook event
    """
    import xlwings as xw
    macExcelAddinPath = os.path.join(utils.utils.MAIN_DIRECTORY, 'extensions', 'excelAddinMac')
    # os.system(f"cd {macExcelAddinPath} && npm run dev-server >/dev/null 2>&1") # hide output
    if not utils.utils.utils.utils.isPortInUse(3000):
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Excel (MacOS)",
            "event_type": "openWorkbook",
            "event_src_path": excelFilepath if excelFilepath else ""
        })
        if excelFilepath:
            app = xw.App(visible=True)
            book = xw.Book(excelFilepath)
        else:
            app = xw.App(visible=True)
            book = xw.Book()
        print("[officeEvents] Excel logging started")
        status_queue.put("[officeEvents] Remember to enable OfficeLogger Add-In by clicking 'Insert > My Add-Ins > "
                         "OfficeLogger' and then 'Home > Show Taskpane'")
        os.system(f"cd {macExcelAddinPath} && npm run dev-server")
    else:
        print(f"[officeEvents] Could not start Excel logging because port 3000 is in use.")


class WordEvents:
    """
    Application object events
    https://docs.microsoft.com/en-us/office/vba/api/word.application
    """

    def __init__(self):
        self.seen_events = {}
        self.Visible = 1

    # ************
    # Window
    # ************

    def OnWindowActivate(self, Doc, Wn):
        """
        Occurs when window is activated

        :param Doc: document
        :param Wn: window
        :return: activateWindow event
        """
        self.seen_events["OnWindowActivate"] = None
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} activateWindow")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Word",
            "event_type": "activateWindow",
        })

    def OnWindowDeactivate(self, Doc, Wn):
        """
        Occurs when window is deactivated

        :param Doc: document
        :param Wn: window
        :return: activateWindow event
        """
        self.seen_events["OnWindowDeactivate"] = None
        self.seen_events["OnWindowActivate"] = None
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} deactivateWindow")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Word",
            "event_type": "deactivateWindow",
        })

    def OnWindowBeforeDoubleClick(self, Sel, Cancel):
        """
        Occurs when double clicking on document

        https://docs.microsoft.com/en-us/office/vba/api/word.selection#properties

        :param Sel: selection
        :param Cancel: true if action is canceled
        :return: doubleClickWindow event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} doubleClickWindow")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Word",
            "event_type": "doubleClickWindow",
        })

    def OnWindowBeforeRightClick(self, Sel, Cancel):
        """
        Occurs when right clicking on document

        :param Sel: selection
        :param Cancel: true if action is canceled
        :return: rightClickWindow event
        """

        print(f"{utils.utils.timestamp()} {utils.utils.USER} rightClickWindow")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Word",
            "event_type": "rightClickWindow",
        })

    # Too much spam
    # def OnWindowSelectionChange(self, Sel):
    #     print(f"{utils.utils.timestamp()} {utils.utils.USER} selectionChangeWindow")
    #     utils.utils.session.post(SERVER_ADDR, json={
    #         "timestamp": utils.utils.timestamp(),
    #         "user": utils.utils.USER,
    #         "category": "MicrosoftOffice",
    #         "application": "Microsoft Word",
    #         "event_type": "selectionChangeWindow",
    #     })

    # ************
    # Document
    # ************

    def OnNewDocument(self, Doc):
        """
        Occurs when a new document is created

        :param Doc: document
        :return: newDocument event
        """
        self.seen_events["OnNewDocument"] = None
        print(f"{utils.utils.timestamp()} {utils.utils.USER} newDocument")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Word",
            "event_type": "newDocument",
        })

    def OnDocumentOpen(self, Doc):
        """
        Occurs when a new document is opened

        :param Doc: document
        :return: openDocument event
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} openDocument")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Word",
            "event_type": "openDocument",
        })

    def OnDocumentChange(self):
        """
        Occurs when a document is changed

        :return: changeDocument event
        """
        self.seen_events["OnDocumentChange"] = None
        print(f"{utils.utils.timestamp()} {utils.utils.USER} changeDocument")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Word",
            "event_type": "changeDocument",
        })

    def OnDocumentBeforeSave(self, Doc, SaveAsUI, Cancel):
        """
        Occurs when a document is saved

        :param Doc: document
        :param SaveAsUI: true if 'save as' dialog is displayed
        :param Cancel: true if event is canceled
        :return: saveDocument event
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} saveDocument")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Word",
            "event_type": "saveDocument",
        })

    def OnDocumentBeforePrint(self, Doc, Cancel):
        """
       Occurs when a document is printed

       :param Doc: document
       :param Cancel: true if event is canceled
       :return: saveDocument event
       """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} printDocument")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Word",
            "event_type": "printDocument",
        })

    def OnQuit(self):
        self.seen_events["OnQuit"] = None


def wordEvents(filename=None):
    """
    Handle word events on windows using pythoncom.

    :param filename: optional name of file to open
    """

    try:
        # needed for thread
        pythoncom.CoInitialize()

        # start new instance of Excel
        e = DispatchWithEvents("Word.Application", WordEvents)

        if filename:
            # open existing document
            e.Documents.Open(filename)
        else:
            # create new empty document that contains worksheet
            e.Documents.Add()

        runLoop(e)
        print("[officeEvents] Word logging started")
        if not CheckSeenEvents(e, ["OnNewDocument", "OnWindowActivate"]):
            sys.exit(1)

    except Exception as e:
        print(e)


class PowerpointEvents:
    """
    Application object events
    https://docs.microsoft.com/en-us/office/vba/api/powerpoint.application
    """

    def __init__(self):
        self.seen_events = None
        self.Visible = 1
        self.presentationSlides = dict()
        # self.mouse = mouse.Controller()

    # ************
    # Utils
    # ************

    def addSlide(self, Sld):
        id = Sld.SlideID
        dict = self.presentationSlides
        if id not in dict:
            dict[id] = Sld

    def popSlide(self, Sld):
        id = Sld.SlideID
        dict = self.presentationSlides
        if id in dict:
            dict.pop(Sld.SlideID)

    def getSlides(self):
        return [slide.Name for slide in self.presentationSlides.values()]

    # ************
    # Window
    # ************

    def OnWindowActivate(self, Pres, Wn):
        """
        Occurs when powerpoint window is activated

        :param Pres: powerpoint presentation
        :param Wn: window
        :return: activateWindow event
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint activateWindow {Pres.Name} {Pres.Path} ")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "activateWindow",
            "title": Pres.Name,
            "event_src_path": Pres.Path,

        })

    def OnWindowDeactivate(self, Pres, Wn):
        """
        Occurs when powerpoint window is deactivated

        :param Pres: powerpoint presentation
        :param Wn: window
        :return: deactivateWindow event
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint deactivateWindow {Pres.Name} {Pres.Path} ")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "deactivateWindow",
            "title": Pres.Name,
            "event_src_path": Pres.Path,

        })

    def OnWindowBeforeRightClick(self, Sel, Cancel):
        """
        Occurs on right click on presentation

        :param Sel: selection
        :param Cancel: true if event is canceled
        :return: rightClickPresentation event
        """
        print(Sel.SlideRange)
        print(Sel.TextRange)
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint rightClickPresentation ")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "rightClickPresentation",

        })

    def OnWindowBeforeDoubleClick(self, Sel, Cancel):
        """
        Occurs on right click on presentation

        :param Sel: selection
        :param Cancel: true if event is canceled
        :return: doubleClickPresentation event
        """
        print(Sel.SlideRange)
        print(Sel.TextRange)
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint doubleClickPresentation ")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "doubleClickPresentation",

        })

    # ************
    # Presentation
    # ************

    def OnNewPresentation(self, Pres):
        """
        New presentation is created

        :param Pres: presentation
        :return: newPresentation event
        """
        self.presentationSlides.clear()
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint newPresentation {Pres.Name} {Pres.Path}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "newPresentation",
            "title": Pres.Name,
            "event_src_path": Pres.Path,

        })

    def OnPresentationNewSlide(self, Sld):
        """
        A slide is added to an open presentation

        :param Sld: slide
        :return: newPresentationSlide event
        """
        self.addSlide(Sld)
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint newPresentationSlide {Sld.Name} {Sld.SlideNumber} {self.getSlides()}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "newPresentationSlide",
            "title": Sld.Name,
            "id": Sld.SlideNumber,
            "slides": self.getSlides(),

        })

    def OnPresentationBeforeClose(self, Pres, Cancel):
        """
        Occurs when a presentation is closed

        :param Pres: presentation
        :param Cancel: true if event is canceled
        :return: closePresentation event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint closePresentation {Pres.Name} {self.getSlides()}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "closePresentation",
            "title": Pres.Name,
            "event_src_path": Pres.Path,
            "slides": self.getSlides(),

        })
        self.presentationSlides.clear()

    def OnPresentationBeforeSave(self, Pres, Cancel):
        """
        Occurs when a presentation is saved

        :param Pres: presentation
        :param Cancel: true if event is canceled
        :return: savePresentation event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint savePresentation {Pres.Name} {self.getSlides()}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "savePresentation",
            "title": Pres.Name,
            "event_src_path": Pres.Path,
            "slides": self.getSlides(),

        })

    def OnAfterPresentationOpen(self, Pres):
        """
        Occurs when a presentation is opened

        :param Pres: presentation
        :return: savePresentation event
        """
        self.presentationSlides.clear()
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint openPresentation {Pres.Name} {self.getSlides()}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "openPresentation",
            "title": Pres.Name,
            "event_src_path": Pres.Path,
            "slides": self.getSlides()
        })

    def OnAfterShapeSizeChange(self, shp):
        """
        Occurs when a shape in a presentation is resized

        :param shp: shape
        :return: shapeSizeChangePresentation event
        """
        self.presentationSlides.clear()
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint shapeSizeChangePresentation {shp.Type} ")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "shapeSizeChangePresentation",
            "description": shp.Type
        })

    def OnPresentationPrint(self, Pres):
        """
        Occurs when a presentation is printed

        :param Pres: presentation
        :return: printPresentation event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint printPresentation {Pres.Name} {self.getSlides()}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "printPresentation",
            "title": Pres.Name,
            "event_src_path": Pres.Path,
            "slides": self.getSlides()
        })

    def OnSlideShowBegin(self, Wn):
        """
        Occurs when slideshow begins

        :param Wn: slideshowview https://docs.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview
        :return: slideshowBegin event
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint slideshowBegin ")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "slideshowBegin",
            "title": Wn.SlideShowName,
            "description": Wn.State,
            # https://docs.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.state
            "newZoomFactor": Wn.Zoom,
            "slides": Wn.Slide.Name
        })

    def OnSlideShowOnNext(self, Wn):
        """
        Occurs when next slide is displayed during a slideshow

        :param Wn: slideshowview https://docs.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview
        :return: nextSlideshow
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint nextSlideshow ")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "nextSlideshow",
            "title": Wn.SlideShowName,
            "description": Wn.State,
            # https://docs.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.state
            "newZoomFactor": Wn.Zoom,
            "slides": Wn.Slide.Name
        })

    def OnSlideShowNextClick(self, Wn, nEffect):
        """
        Occurs when the next slide in a presentation is clicked during a slideshow

        https://docs.microsoft.com/en-us/office/vba/api/powerpoint.effect#properties

        :param Wn: slideshowview https://docs.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview
        :param nEffect: transition type
        :return: clickNextSlideshow event
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint clickNextSlideshow ")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "clickNextSlideshow",
            "title": Wn.SlideShowName,
            "description": Wn.State,
            # https://docs.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.state
            "newZoomFactor": Wn.Zoom,
            "slides": Wn.Slide.Name,
            "effect": nEffect.EffectType
        })

    def OnSlideShowOnPrevious(self, Wn):
        """
        Occurs when previous slide is clicked during a slideshow

        https://docs.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.state

        :param Wn: slideshowview https://docs.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview
        :return: previousSlideshow event
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint previousSlideshow ")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "previousSlideshow",
            "title": Wn.SlideShowName,
            "description": Wn.State,
            "newZoomFactor": Wn.Zoom,
            "slides": Wn.Slide.Name
        })

    def OnSlideShowEnd(self, Pres):
        """
        Occurs when a slideshow ends

        :param Pres: presentation
        :return: slideshowEnd event
        """
        print(
            f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint slideshowEnd {Pres.Name} {self.getSlides()}")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "slideshowEnd",
            "title": Pres.Name,
            "event_src_path": Pres.Path,
            "slides": self.getSlides()
        })

    def OnSlideSelectionChanged(self, SldRange):
        """
        occurs when text selection on a slide changes

        :param SldRange: range of slides
        :return: SlideSelectionChanged event
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Powerpoint SlideSelectionChanged")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Powerpoint",
            "event_type": "SlideSelectionChanged",
        })


def powerpointEvents(filename=None):
    """
    Handle powerpoint events on windows using pythoncom.

    :param filename: optional name of file to open
    """

    try:
        # needed for thread
        pythoncom.CoInitialize()

        # start new instance of Excel
        e = DispatchWithEvents("powerpoint.Application", PowerpointEvents)

        if filename:
            # open existing document
            e.Presentations.Open(filename)
        else:
            # create new empty document that contains worksheet
            e.Presentations.Add()

        runLoop(e)
        print("[officeEvents] Powerpoint logging started")
        if not CheckSeenEvents(e, ["OnNewPresentation", "OnWindowActivate"]):
            sys.exit(1)

    except Exception as e:
        print(e)


class OutlookEvents:
    """
    https://stackoverflow.com/questions/49695160/how-to-continuously-monitor-a-new-mail-in-outlook-and-unread-mails-of-a-specific
    """

    def __init__(self):
        self.seen_events = None
        # First action to do when using the class in the DispatchWithEvents
        # 6 is the inbox folder https://docs.microsoft.com/en-us/office/vba/api/outlook.oldefaultfolders
        inbox = self.Application.GetNamespace("MAPI").GetDefaultFolder(6)
        messages = inbox.Items
        # Check for unread emails when starting the event
        for message in messages:
            if message.UnRead:
                # Or whatever code you wish to execute.
                print(message.Subject)

    def OnStartup(self):
        """
        Occurs when outlook starts

        :return: startupOutlook event
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Outlook startupOutlook")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Outlook",
            "event_type": "startupOutlook",
        })

    def OnQuit(self):
        """
        Occurs when outlook quits

        :return: quitOutlook event
        """
        self.seen_events["OnQuit"] = None
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Outlook quitOutlook")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Outlook",
            "event_type": "quitOutlook",
        })
        # stopEvent.set() #Set the internal flag to true. All threads waiting for it to become true are awakened
        # To stop PumpMessages() when Outlook Quit
        #     # Note: Not sure it works when disconnecting!!
        #     ctypes.windll.user32.PostQuitMessage(0)

    def OnNewMailEx(self, receivedItemsIDs):
        """
        Occurs when a new mail is received

        :param receivedItemsIDs: id of received mail
        :return: receiveMail event
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Outlook receiveMail")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Outlook",
            "event_type": "receiveMail",
        })
        # RecrivedItemIDs is a collection of mail IDs separated by a ",".
        # You know, sometimes more than 1 mail is received at the same moment.
        for ID in receivedItemsIDs.split(","):
            mail = self.Session.GetItemFromID(ID)
            subject = mail.Subject
            print(subject)

    def OnItemSend(self, Item, Cancel):
        """
        Occurs when a new message is sent

        :param Item: message
        :param Cancel: true if action is canceled
        :return: sendMail event
        """
        print(Item)
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Outlook sendMail")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Outlook",
            "event_type": "sendMail",
        })

    def OnMAPILogonComplete(self):
        """
        Occurs when outlook checks for new mails

        :return: logonComplete event
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Outlook logonComplete")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Outlook",
            "event_type": "logonComplete",
        })

    def OnReminder(self, Item):
        """
        Occurs when there is a new reminder

        :param Item: reminder item
        :return: newReminder event
        """
        print(f"{utils.utils.timestamp()} {utils.utils.USER} Outlook newReminder")
        utils.utils.session.post(SERVER_ADDR, json={
            "timestamp": utils.utils.timestamp(),
            "user": utils.utils.USER,
            "category": "MicrosoftOffice",
            "application": "Microsoft Outlook",
            "event_type": "newReminder",
        })


def outlookEvents():
    """
    Handle outlook events using pythoncom
    """

    try:
        # needed for thread
        pythoncom.CoInitialize()

        # start new instance of outlook
        e = DispatchWithEvents("outlook.Application", OutlookEvents)

        e.Presentations.Add()

        runLoop(e)
        print("[officeEvents] Outlook logging started")
        if not CheckSeenEvents(e, ["OnNewPresentation", "OnWindowActivate"]):
            sys.exit(1)

    except Exception as e:
        print(e)


def runLoop(ob):
    while 1:
        pythoncom.PumpWaitingMessages()  # listen for events
        try:
            # Gone invisible - we need to pretend we timed out, so the app is quit.
            if not ob.Visible:
                print("Application has been closed. Shutting down...")
                return 0
        # Excel is busy (like editing the cell), ignore
        except pythoncom.com_error:
            pass
    # return 1


def CheckSeenEvents(o, events):
    rc = 1
    for e in events:
        if not e in o.seen_events:
            print("ERROR: Expected event did not trigger", e)
            rc = 0
    return rc


# used for debug
if __name__ == '__main__':
    args = sys.argv[1:]
    print(f"Launching {args[0]}...")
    if "word" in args:
        wordEvents()
    elif "excel" in args:
        excelEvents()
    elif "powerpoint" in args:
        powerpointEvents()
    elif "outlook" in args:
        outlookEvents()
