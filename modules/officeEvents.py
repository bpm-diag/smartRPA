import sys
sys.path.append('../')  # this way main file is visible from this file
from getpass import getuser  # user id
from re import findall
from os import path
from shutil import rmtree
from itertools import chain
from utils.utils import timestamp, session, WINDOWS, print_members, USER
from utils.consumerServer import SERVER_ADDR

if WINDOWS:
    from win32com.client import DispatchWithEvents, Dispatch, DispatchEx
    import pythoncom
    from win32com import __gen_path__
    import ctypes


def excelEvents(filename=None):
    # This variable controls OnSheetSelectionChange, if True an actions is logged every time a cell is selected. It's
    # resource expensive, so it's possible to turn it off by setting variable to False
    LOG_EVERY_CELL = True

    # ************
    # Application object events
    # https://docs.microsoft.com/en-us/office/vba/api/excel.application(object)
    # ************
    class ExcelEvents:
        def __init__(self):
            self.seen_events = {}
            self.Visible = 1

        def setApplication(self, application):
            self.application = application

        # ************
        # Utils
        # ************

        # return list of active worksheet in workbook
        def getWorksheets(self, Sh, Wb):
            if Sh:
                return list(map(lambda sh: sh.Name, Sh.Parent.Worksheets))
            elif Wb:
                return list(map(lambda sh: sh.Name, Wb.Worksheets))

        # ************
        # Window
        # ************

        def OnWindowActivate(self, Wb, Wn):
            self.seen_events["OnWindowActivate"] = None

            print(
                f"{timestamp()} {USER} openWindow workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} window id:{Wn.WindowNumber} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "openWindow",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "id": Wn.WindowNumber,
                "event_src_path": Wb.Path
            })

        def OnWindowDeactivate(self, Wb, Wn):
            self.seen_events["OnWindowDeactivate"] = None
            print(
                f"{timestamp()} {USER} closeWindow workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} window id:{Wn.WindowNumber} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "closeWindow",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "id": Wn.WindowNumber,
                "event_src_path": Wb.Path
            })

        def OnWindowResize(self, Wb, Wn):
            print(
                f"{timestamp()} {USER} resizeWindow workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} window id:{Wn.WindowNumber} size:{Wn.Width}x{Wn.Height} ")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "resizeWindow",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "id": Wn.WindowNumber,
                "event_src_path": Wb.Path,
                "window_size": f"{Wn.Width}x{Wn.Height}"
            })

        # ************
        # Workbook
        # ************

        def OnNewWorkbook(self, Wb):
            self.seen_events["OnNewWorkbook"] = None

            print(
                f"{timestamp()} {USER} newWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "newWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookOpen(self, Wb):
            print(
                f"{timestamp()} {USER} openWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "openWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookBeforeSave(self, Wb, SaveAsUI, Cancel):
            print(
                f"{timestamp()} {USER} saveWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path} saveAs dialog {SaveAsUI}")
            if SaveAsUI:
                description = "SaveAs dialog box displayed"
            else:
                description = "SaveAs dialog box not displayed"
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "saveWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path,
                "description": description
            })

        def OnWorkbookAddinInstall(self, Wb):
            print(
                f"{timestamp()} {USER} addinInstalledWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "addinInstalledWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookAddinUninstall(self, Wb):
            print(
                f"{timestamp()} {USER} addinUninstalledWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "addinUninstalledWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookAfterXmlImport(self, Wb, Map, Url, Result):
            print(
                f"{timestamp()} {USER} XMLImportWOrkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "XMLImportWOrkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookAfterXmlExport(self, Wb, Map, Url, Result):
            print(
                f"{timestamp()} {USER} XMLExportWOrkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "XMLExportWOrkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookBeforePrint(self, Wb, Cancel):
            print(
                f"{timestamp()} {USER} printWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "printWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookBeforeClose(self, Wb, Cancel):
            print(
                f"{timestamp()} {USER} closeWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "closeWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookActivate(self, Wb):
            print(
                f"{timestamp()} {USER} activateWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "activateWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookDeactivate(self, Wb):
            print(
                f"{timestamp()} {USER} deactivateWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "deactivateWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookModelChange(self, Wb, Changes):
            print(
                f"{timestamp()} {USER} modelChangeWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "modelChangeWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookNewChart(self, Wb, Ch):
            print(
                f"{timestamp()} {USER} newChartWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "newChartWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path,
                "title": Ch.Name
            })

        def OnAfterCalculate(self):
            print(
                f"{timestamp()} {USER} afterCalculate")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "afterCalculate",
            })

        # ************
        # Worksheet
        # ************

        def filterNoneRangeValues(self, values):
            # When a range of cells is selected, Target.Value is a Tuple of tuples containing the value of every
            # selected cell Target.Value = ((None, None, None, None), (None, 'prova', None, None)). I'm
            # interested only in cells with meaningful value, so I create a single list with all the tuples in
            # Target.Value (by chaining the tuples using chain.from_iterable(list)) obtaining [None, None, None,
            # None, None, 'prova', None, None] Now I remove the elements that are None by applying a filter
            # operator to the previous list
            if values:
                # return list(filter(lambda s: s is not None, list(chain.from_iterable(list(values)))))
                return [s for s in list(chain.from_iterable(list(values))) if s is not None]
            else:
                return ""

        def OnSheetActivate(self, Sh):
            # to get the list of active worksheet names, I cycle through the parent which is the workbook
            print(
                f"{timestamp()} {USER} MS-EXCEL selectWorksheet {Sh.Name} {Sh.Parent.Name} {self.getWorksheets(Sh, None)}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "selectWorksheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "worksheets": self.getWorksheets(Sh, None),
                "event_src_path": Sh.Parent.Path
            })

        def OnSheetBeforeDelete(self, Sh):
            print(
                f"{timestamp()} {USER} MS-EXCEL deleteWorksheet {Sh.Name} {Sh.Parent.Name} {self.getWorksheets(Sh, None)}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "deleteWorksheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "worksheets": self.getWorksheets(Sh, None)
            })

        def OnSheetBeforeDoubleClick(self, Sh, Target, Cancel):
            event_type = "doubleClickEmptyCell"
            value = ""
            if Target.Value:  # cell has value
                event_type = "doubleClickCellWithValue"
                value = Target.Value

            print(
                f"{timestamp()} {USER} MS-EXCEL {event_type} {Sh.Name} {Sh.Parent.Name} {Target.Address.replace('$', '')} {value}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": event_type,
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "cell_range": Target.Address.replace('$', ''),
                "cell_content": value
            })

        def OnSheetBeforeRightClick(self, Sh, Target, Cancel):
            event_type = "rightClickEmptyCell"
            value = ""
            if Target.Value:  # cell has value
                event_type = "rightClickCellWithValue"
                value = Target.Value
            print(
                f"{timestamp()} {USER} MS-EXCEL {event_type} {Sh.Name} {Sh.Parent.Name} {Target.Address.replace('$', '')} {value}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": event_type,
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "cell_range": Target.Address.replace('$', ''),
                "cell_content": value
            })

        def OnSheetCalculate(self, Sh):
            print(
                f"{timestamp()} {USER} MS-EXCEL sheetCalculate {Sh.Name} {Sh.Parent.Name} ")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "sheetCalculate",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
            })

        def OnSheetChange(self, Sh, Target):
            value = self.filterNoneRangeValues(Target.Value)
            print(
                f"{timestamp()} {USER} MS-EXCEL editCellSheet {Sh.Name} {Sh.Parent.Name} {Target.Address.replace('$', '')} {value}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "editCellSheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "cell_range": Target.Address.replace('$', ''),
                "cell_content": value
            })

        def OnSheetDeactivate(self, Sh):
            self.seen_events["OnSheetDeactivate"] = None
            print(
                f"{timestamp()} {USER} MS-EXCEL deselectWorksheet {Sh.Name} {Sh.Parent.Name} {self.getWorksheets(Sh, None)}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "deselectWorksheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "worksheets": self.getWorksheets(Sh, None),
                "event_src_path": Sh.Parent.Path
            })

        def OnSheetFollowHyperlink(self, Sh, Target):
            print(
                f"{timestamp()} {USER} MS-EXCEL followHiperlinkSheet {Sh.Name} {Sh.Parent.Name} {Target.Range.Address.replace('$', '')} {Target.Address}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "followHiperlinkSheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "cell_range": Target.Range.Address.replace('$', ''),
                "browser_url": Target.Address
            })

        def OnSheetPivotTableAfterValueChange(self, Sh, TargetPivotTable, TargetRange):
            print(
                f"{timestamp()} {USER} MS-EXCEL pivotTableValueChangeSheet {Sh.Name} {Sh.Parent.Name} {TargetRange.Address.replace('$', '')} {TargetRange.Value}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "pivotTableValueChangeSheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "cell_range": TargetRange.Address.replace('$', ''),
                "cell_content": TargetRange.Value if TargetRange.Value else ""
            })

        def OnSheetSelectionChange(self, Sh, Target):
            cells_selected = Target.Address.replace('$',
                                                    '')  # value returned is in the format $B$3:$D$3, I remove $ sign
            event_type = "getCell"
            value = Target.Value if Target.Value else ""
            rangeSelected = (':' in cells_selected)  # True if the user selected a range of cells
            # if a range of cells has been selected
            if rangeSelected:
                event_type = "getRange"
                # Returns values of selected cells removing empty cells
                value = self.filterNoneRangeValues(Target.Value)

            # If LOG_EVERY_CELL is False and a user selects a single cell the event is not logged
            if rangeSelected or LOG_EVERY_CELL:
                print(
                    f"{timestamp()} {USER} MS-EXCEL {event_type} {Sh.Name} {Sh.Parent.Name} {cells_selected} {value}")
                session.post(SERVER_ADDR, json={
                    "timestamp": timestamp(),
                    "user": USER,
                    "category": "MSOffice",
                    "application": "Microsoft Excel",
                    "event_type": event_type,
                    "workbook": Sh.Parent.Name,
                    "current_worksheet": Sh.Name,
                    "cell_range": cells_selected,
                    "cell_content": value
                })

        def OnSheetTableUpdate(self, Sh, Target):
            print(f"{timestamp()} {USER} MS-EXCEL worksheetTableUpdated {Sh.Name} {Sh.Parent.Name} ")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Excel",
                "event_type": "worksheetTableUpdated",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
            })

    try:
        # needed for thread
        pythoncom.CoInitialize()

        # start new instance of Excel
        e = DispatchWithEvents("Excel.Application", ExcelEvents)
        # e.seen_events = {}
        e.Visible = 1  # open window

        if filename:
            # open existing workbook
            e.Workbooks.Open(filename)
        else:
            # create new empty workbook that contains worksheet
            e.Workbooks.Add()

        # sheet = e.Worksheets(1)

        runLoop(e)
        print("[officeEvents] Excel logging started")
        if not CheckSeenEvents(e, ["OnNewWorkbook", "OnWindowActivate"]):
            sys.exit(1)

    except Exception as e:
        exception = str(e)
        print(f"Failed to launch Excel: {exception}")
        #  https://stackoverflow.com/q/47608506/1440037
        if "win32com.gen_py" in exception:
            #  https://stackoverflow.com/a/54422675/1440037  Deleting the gen_py output directory and re-running the
            # script should fix the issue find the corrupted directory to remove in gen_py path using regex (
            # directory is in the form 'win32com.gen_py.00020813-0000-0000-C000-000000000046x0x1x9) I should have a
            # string like '00020813-0000-0000-C000-000000000046x0x1x9'
            dirToRemove = findall(r"'(.*?)'", exception)[0].split('.')[-1]
            if not dirToRemove:
                # if regex failed use default folder
                dirToRemove = '00020813-0000-0000-C000-000000000046x0x1x9'
            pathToRemove = path.join(__gen_path__, dirToRemove)
            print(f"Trying to fix the error, deleting {pathToRemove}")
            rmtree(pathToRemove, ignore_errors=True)
            if not path.exists(pathToRemove):
                print("The error should now be fixed, try to execute the program again.")


def wordEvents(filename=None):
    # ************
    # Application object events
    # https://docs.microsoft.com/en-us/office/vba/api/word.application
    # ************
    class WordEvents:

        def __init__(self):
            self.seen_events = {}
            self.Visible = 1

        # ************
        # Window
        # ************

        def OnWindowActivate(self, Doc, Wn):
            self.seen_events["OnWindowActivate"] = None
            print(
                f"{timestamp()} {USER} activateWindow")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Word",
                "event_type": "activateWindow",
            })

        def OnWindowDeactivate(self, Doc, Wn):
                self.seen_events["OnWindowDeactivate"] = None
                self.seen_events["OnWindowActivate"] = None
                print(
                    f"{timestamp()} {USER} deactivateWindow")
                session.post(SERVER_ADDR, json={
                    "timestamp": timestamp(),
                    "user": USER,
                    "category": "MSOffice",
                    "application": "Microsoft Word",
                    "event_type": "deactivateWindow",
                })

        def OnWindowBeforeDoubleClick(self, Sel, Cancel):
            # https://docs.microsoft.com/en-us/office/vba/api/word.selection#properties
                print(
                    f"{timestamp()} {USER} doubleClickWindow")
                session.post(SERVER_ADDR, json={
                    "timestamp": timestamp(),
                    "user": USER,
                    "category": "MSOffice",
                    "application": "Microsoft Word",
                    "event_type": "doubleClickWindow",
                })

        def OnWindowBeforeRightClick(self, Sel, Cancel):
            print(f"{timestamp()} {USER} rightClickWindow")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Word",
                "event_type": "rightClickWindow",
            })

        # Too much spam
        # def OnWindowSelectionChange(self, Sel):
        #     print(f"{timestamp()} {USER} selectionChangeWindow")
        #     session.post(SERVER_ADDR, json={
        #         "timestamp": timestamp(),
        #         "user": USER,
        #         "category": "MSOffice",
        #         "application": "Microsoft Word",
        #         "event_type": "selectionChangeWindow",
        #     })

        # ************
        # Document
        # ************

        def OnNewDocument(self, Doc):
            self.seen_events["OnNewDocument"] = None
            print(f"{timestamp()} {USER} newDocument")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Word",
                "event_type": "newDocument",
            })

        def OnDocumentOpen(self, Doc):
            print(f"{timestamp()} {USER} openDocument")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Word",
                "event_type": "openDocument",
            })

        def OnDocumentChange(self):
            self.seen_events["OnDocumentChange"] = None
            print(f"{timestamp()} {USER} changeDocument")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Word",
                "event_type": "changeDocument",
            })

        def OnDocumentBeforeSave(self, Doc, SaveAsUI, Cancel):
            print(f"{timestamp()} {USER} saveDocument")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Word",
                "event_type": "saveDocument",
            })

        def OnDocumentBeforePrint(self, Doc, Cancel):
            print(f"{timestamp()} {USER} printDocument")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Word",
                "event_type": "printDocument",
            })

        def OnQuit(self):
            self.seen_events["OnQuit"] = None

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


def powerpointEvents(filename=None):
    # ************
    # Application object events
    # https://docs.microsoft.com/en-us/office/vba/api/powerpoint.application
    # ************
    class powerpointEvents:
        def __init__(self):
            self.seen_events = None
            self.Visible = 1
            self.presentationSlides = dict()

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
            print(f"{timestamp()} {USER} Powerpoint activateWindow {Pres.Name} {Pres.Path} ")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "activateWindow",
                "title": Pres.Name,
                "event_src_path": Pres.Path,
            })

        def OnWindowDeactivate(self, Pres, Wn):
            print(f"{timestamp()} {USER} Powerpoint activateWindow {Pres.Name} {Pres.Path} ")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "activateWindow",
                "title": Pres.Name,
                "event_src_path": Pres.Path,
            })

        def OnWindowBeforeRightClick(self, Sel, Cancel):
            print(Sel.SlideRange)
            print(Sel.TextRange)
            print(f"{timestamp()} {USER} Powerpoint rightClickPresentation ")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "rightClickPresentation",
            })

        def OnWindowBeforeDoubleClick(self, Sel, Cancel):
            print(Sel.SlideRange)
            print(Sel.TextRange)
            print(f"{timestamp()} {USER} Powerpoint doubleClickPresentation ")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "doubleClickPresentation",
            })

        # ************
        # Presentation
        # ************

        def OnNewPresentation(self, Pres):
            self.presentationSlides.clear()
            print(f"{timestamp()} {USER} Powerpoint newPresentation {Pres.Name} {Pres.Path}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "newPresentation",
                "title": Pres.Name,
                "event_src_path": Pres.Path,
            })

        def OnPresentationNewSlide(self, Sld):
            self.addSlide(Sld)
            print(f"{timestamp()} {USER} Powerpoint newPresentation {Sld.Name} {Sld.SlideNumber} {self.getSlides()}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "newPresentation",
                "title": Sld.Name,
                "id": Sld.SlideNumber,
                "slides": self.getSlides()
            })

        def OnPresentationBeforeClose(self, Pres, Cancel):
            print(f"{timestamp()} {USER} Powerpoint closePresentation {Pres.Name} {self.getSlides()}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "closePresentation",
                "title": Pres.Name,
                "event_src_path": Pres.Path,
                "slides": self.getSlides()
            })
            self.presentationSlides.clear()

        def OnPresentationBeforeSave(self, Pres, Cancel):
            print(f"{timestamp()} {USER} Powerpoint savePresentation {Pres.Name} {self.getSlides()}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "savePresentation",
                "title": Pres.Name,
                "event_src_path": Pres.Path,
                "slides": self.getSlides()
            })

        def OnAfterPresentationOpen(self, Pres):
            self.presentationSlides.clear()
            print(f"{timestamp()} {USER} Powerpoint openPresentation {Pres.Name} {self.getSlides()}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "openPresentation",
                "title": Pres.Name,
                "event_src_path": Pres.Path,
                "slides": self.getSlides()
            })

        def OnAfterShapeSizeChange(self, shp):
            self.presentationSlides.clear()
            print(f"{timestamp()} {USER} Powerpoint shapeSizeChangePresentation {shp.Type} ")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "shapeSizeChangePresentation",
                "description": shp.Type
            })

        def OnPresentationPrint(self, Pres):
            print(f"{timestamp()} {USER} Powerpoint openPresentation {Pres.Name} {self.getSlides()}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "openPresentation",
                "title": Pres.Name,
                "event_src_path": Pres.Path,
                "slides": self.getSlides()
            })

        # Wn is a slideshowview https://docs.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview
        def OnSlideShowBegin(self, Wn):
            print(f"{timestamp()} {USER} Powerpoint slideshowBegin ")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "slideshowBegin",
                "title": Wn.SlideShowName,
                "description": Wn.State, # https://docs.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.state
                "newZoomFactor": Wn.Zoom,
                "slides": Wn.Slide.Name
            })

        def OnSlideShowOnNext(self, Wn):
            print(f"{timestamp()} {USER} Powerpoint nextSlideshow ")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "nextSlideshow",
                "title": Wn.SlideShowName,
                "description": Wn.State,
                # https://docs.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.state
                "newZoomFactor": Wn.Zoom,
                "slides": Wn.Slide.Name
            })

        # https://docs.microsoft.com/en-us/office/vba/api/powerpoint.effect#properties
        def OnSlideShowNextClick(self, Wn, nEffect):
            print(f"{timestamp()} {USER} Powerpoint clickNextSlideshow ")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
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
            print(f"{timestamp()} {USER} Powerpoint previousSlideshow ")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "previousSlideshow",
                "title": Wn.SlideShowName,
                "description": Wn.State,
                # https://docs.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.state
                "newZoomFactor": Wn.Zoom,
                "slides": Wn.Slide.Name
            })

        def OnSlideShowEnd(self, Pres):
            print(f"{timestamp()} {USER} Powerpoint slideshowEnd {Pres.Name} {self.getSlides()}")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "slideshowEnd",
                "title": Pres.Name,
                "event_src_path": Pres.Path,
                "slides": self.getSlides()
            })

        def OnSlideSelectionChanged(self, SldRange):
            print(f"{timestamp()} {USER} Powerpoint SlideSelectionChanged")
            session.post(SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "MSOffice",
                "application": "Microsoft Powerpoint",
                "event_type": "SlideSelectionChanged",
            })


    try:
        # needed for thread
        # pythoncom.CoInitialize()

        # start new instance of Excel
        e = DispatchWithEvents("powerpoint.Application", powerpointEvents)

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

def outlookEvents():
    # https://stackoverflow.com/questions/49695160/how-to-continuously-monitor-a-new-mail-in-outlook-and-unread-mails-of-a-specific
    class outlookEvents:
        def OnDocumentChange(self):
            self.seen_events["OnDocumentChange"] = None
            print("{} {} documentChange".format(timestamp(), getuser()))

        # def OnNewDocument(self):
        #     self.seen_events["OnDocumentChange"] = None
        #     print("{} {} newDocument".format(currentTimestamp(),getuser()))
        def OnWindowActivate(self, doc, wn):
            self.seen_events["OnWindowActivate"] = None
            print("{} {} outlookOpened".format(timestamp(), getuser()))

        def OnDocumentBeforeSave(self, *args):
            print("{} {} documentSaved".format(timestamp(), getuser()))

        def OnDocumentBeforePrint(self, *args):
            print("{} {} documentPrinted".format(timestamp(), getuser()))

        def OnQuit(self):
            self.seen_events["OnQuit"] = None
            # stopEvent.set() #Set the internal flag to true. All threads waiting for it to become true are awakened

        def __init__(self):
            # First action to do when using the class in the DispatchWithEvents
            inbox = self.Application.GetNamespace("MAPI").GetDefaultFolder(6)
            messages = inbox.Items
            # Check for unread emails when starting the event
            for message in messages:
                if message.UnRead:
                    # Or whatever code you wish to execute.
                    print(message.Subject)

        def OnQuit(self):
            # To stop PumpMessages() when Outlook Quit
            # Note: Not sure it works when disconnecting!!
            ctypes.windll.user32.PostQuitMessage(0)

        def OnNewMailEx(self, receivedItemsIDs):
            # RecrivedItemIDs is a collection of mail IDs separated by a ",".
            # You know, sometimes more than 1 mail is received at the same moment.
            for ID in receivedItemsIDs.split(","):
                mail = self.Session.GetItemFromID(ID)
                subject = mail.Subject
                print(subject)
                try:
                    command = re.search(r"%(.*?)%", subject).group(1)
                    print(command)  # Or whatever code you wish to execute.
                except:
                    pass

    o = DispatchWithEvents("outlook.Application", outlookEvents)
    o.seen_events = {}
    o.Visible = 1
    inbox = o.GetNamespace("MAPI").GetDefaultFolder(6)
    # o.Presentations.Add()

    runLoop(o)
    if not CheckSeenEvents(o, ["OnDocumentChange", "OnWindowActivate"]):
        sys.exit(1)


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
