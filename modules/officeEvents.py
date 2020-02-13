import sys
sys.path.append('../')  # this way main file is visible from this file
from getpass import getuser  # user id
from re import findall
from os import path
from shutil import rmtree
from itertools import chain
from utils import consumerServer
from utils.utils import timestamp, session, WINDOWS

if WINDOWS:
    from win32com.client import DispatchWithEvents, Dispatch, DispatchEx
    import pythoncom
    from win32com import __gen_path__
    import ctypes


def excelEvents():

    # This variable controls OnSheetSelectionChange, if True an actions is logged every time a cell is selected. It's
    # resource expensive, so it's possible to turn it off by setting variable to False
    LOG_EVERY_CELL = True

    # ************
    # Application object events
    # https://docs.microsoft.com/en-us/office/vba/api/excel.application(object)
    # ************
    class ExcelEvents:
        def setApplication(self, application):
            self.application = application

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

            print(f"{timestamp()} {getuser()} openWindow workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} window id:{Wn.WindowNumber} path: {Wb.Path}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
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
            self.seen_events["OnWindowDeactivate"] = None
            print(
                f"{timestamp()} {getuser()} closeWindow workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} window id:{Wn.WindowNumber} path: {Wb.Path}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
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
            print(
                f"{timestamp()} {getuser()} resizeWindow workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} window id:{Wn.WindowNumber} size:{Wn.Width}x{Wn.Height} ")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
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
                f"{timestamp()} {getuser()} newWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "newWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookBeforeSave(self, Wb, SaveAsUI, Cancel):
            print(f"{timestamp()} {getuser()} saveWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path} saveAs dialog {SaveAsUI}")
            if SaveAsUI: description = "SaveAs dialog box displayed"
            else: description = "SaveAs dialog box not displayed"
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "saveWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path,
                "description": description
            })

        def OnWorkbookAddinInstall(self, Wb):
            print(f"{timestamp()} {getuser()} addinInstalledWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "addinInstalledWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookAddinUninstall(self, Wb):
            print(f"{timestamp()} {getuser()} addinUninstalledWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "addinUninstalledWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookAfterXmlImport(self, Wb, Map, Url, Result):
            print(f"{timestamp()} {getuser()} XMLImportWOrkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "XMLImportWOrkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookAfterXmlExport(self, Wb, Map, Url, Result):
            print(f"{timestamp()} {getuser()} XMLExportWOrkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "XMLExportWOrkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookBeforePrint(self, Wb, Cancel):
            print(f"{timestamp()} {getuser()} printWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "printWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
            })

        def OnWorkbookBeforeClose(self, Wb, Cancel):
            print(f"{timestamp()} {getuser()} closeWorkbook workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "closeWorkbook",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": self.getWorksheets(None, Wb),
                "event_src_path": Wb.Path
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
                return list(filter(lambda s: s is not None, list(chain.from_iterable(list(values)))))
            else:
                return ""

        def OnSheetActivate(self, Sh):
            # to get the list of active worksheet names, I cycle through the parent which is the workbook
            print(f"{timestamp()} {getuser()} MS-EXCEL selectWorksheet {Sh.Name} {Sh.Parent.Name} {self.getWorksheets(Sh, None)}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "selectWorksheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "worksheets": self.getWorksheets(Sh, None),
                "event_src_path": Sh.Parent.Path
            })

        def OnSheetBeforeDelete(self, Sh):
            print(
                f"{timestamp()} {getuser()} MS-EXCEL deleteWorksheet {Sh.Name} {Sh.Parent.Name} {self.getWorksheets(Sh, None)}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "deleteWorksheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "worksheets": self.getWorksheets(Sh, None)
            })

        def OnSheetBeforeDoubleClick(self, Sh, Target, Cancel):
            event_type = "doubleClickEmptyCell"
            value = ""
            if Target.Value: # cell has value
                event_type = "doubleClickCellWithValue"
                value = Target.Value

            print(f"{timestamp()} {getuser()} MS-EXCEL {event_type} {Sh.Name} {Sh.Parent.Name} {Target.Address.replace('$', '')} {value}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": event_type,
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "cell_range":  Target.Address.replace('$', ''),
                "cell_content": value
            })

        def OnSheetBeforeRightClick(self, Sh, Target, Cancel):
            event_type = "rightClickEmptyCell"
            value = ""
            if Target.Value: # cell has value
                event_type = "rightClickCellWithValue"
                value = Target.Value
            print(f"{timestamp()} {getuser()} MS-EXCEL {event_type} {Sh.Name} {Sh.Parent.Name} {Target.Address.replace('$', '')} {value}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": event_type,
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "cell_range": Target.Address.replace('$', ''),
                "cell_content": value
            })

        def OnSheetCalculate(self, Sh):
            print(
                f"{timestamp()} {getuser()} MS-EXCEL sheetCalculate {Sh.Name} {Sh.Parent.Name} ")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "sheetCalculate",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
            })

        def OnSheetChange(self, Sh, Target):
            value = self.filterNoneRangeValues(Target.Value)
            print(
                f"{timestamp()} {getuser()} MS-EXCEL editCellSheet {Sh.Name} {Sh.Parent.Name} {Target.Address.replace('$','')} { value }")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "editCellSheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "cell_range": Target.Address.replace('$', ''),
                "cell_content":  value
            })

        def OnSheetDeactivate(self, Sh):
            self.seen_events["OnSheetDeactivate"] = None
            print(
                f"{timestamp()} {getuser()} MS-EXCEL deselectWorksheet {Sh.Name} {Sh.Parent.Name} {self.getWorksheets(Sh, None)}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "deselectWorksheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "worksheets": self.getWorksheets(Sh, None),
                "event_src_path": Sh.Parent.Path
            })

        def OnSheetFollowHyperlink(self, Sh, Target):
            print(
                f"{timestamp()} {getuser()} MS-EXCEL followHiperlinkSheet {Sh.Name} {Sh.Parent.Name} {Target.Range.Address.replace('$', '')} {Target.Address}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "followHiperlinkSheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "cell_range": Target.Range.Address.replace('$', ''),
                "browser_url":  Target.Address
            })

        def OnSheetPivotTableAfterValueChange(self, Sh, TargetPivotTable, TargetRange):
            print(
                f"{timestamp()} {getuser()} MS-EXCEL pivotTableValueChangeSheet {Sh.Name} {Sh.Parent.Name} {TargetRange.Address.replace('$', '')} {TargetRange.Value}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "pivotTableValueChangeSheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "cell_range": TargetRange.Address.replace('$', ''),
                "cell_content":  TargetRange.Value if TargetRange.Value else ""
            })

        def OnSheetSelectionChange(self, Sh, Target):
            cells_selected = Target.Address.replace('$','')  # value returned is in the format $B$3:$D$3, I remove $ sign
            event_type = "getCell"
            value = Target.Value if Target.Value else ""
            rangeSelected = (':' in cells_selected) # True if the user selected a range of cells
            # if a range of cells has been selected
            if rangeSelected:
                event_type = "getRange"
                # Returns values of selected cells removing empty cells
                value = self.filterNoneRangeValues(Target.Value)

            # If LOG_EVERY_CELL is False and a user selects a single cell the event is not logged
            if rangeSelected or LOG_EVERY_CELL:
                print(f"{timestamp()} {getuser()} MS-EXCEL {event_type} {Sh.Name} {Sh.Parent.Name} {cells_selected} {value}")
                session.post(consumerServer.SERVER_ADDR, json={
                    "timestamp": timestamp(),
                    "user": getuser(),
                    "category": "MicrosoftOffice",
                    "application": "Microsoft Excel",
                    "event_type": event_type,
                    "workbook": Sh.Parent.Name,
                    "current_worksheet": Sh.Name,
                    "cell_range": cells_selected,
                    "cell_content": value
                })

        def OnSheetTableUpdate(self, Sh, Target):
            print(f"{timestamp()} {getuser()} MS-EXCEL worksheetTableUpdated {Sh.Name} {Sh.Parent.Name} ")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": getuser(),
                "category": "MicrosoftOffice",
                "application": "Microsoft Excel",
                "event_type": "worksheetTableUpdated",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
            })

    class WorkbookEvents:

        # def OnActivate(self):
        #     print("{} {} workbookActive".format(timestamp(), getuser()))

        # def OnBeforeRightClick(self, Target, Cancel):
        #     # print ("It's a Worksheet Event")
        #     print(
        #         "{} {} MS-EXCEL workbookRightClick {}".format(timestamp(), getuser(), Target))

        # https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetactivate
        # def OnSheetActivate(self, Sh):
        #     print(f"{timestamp()} {getuser()} MS-EXCEL selectWorksheet {Sh.Name}")

        #  https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetchange

            # args[0].Range('A1').Value = 'You selected cell ' + str(args[1].Address)

        # def OnBeforeSave(self, *args):
        #     print("{} {} MS-EXCEL workbookSaved".format(timestamp(), getuser()))
        pass

    class WorksheetEvents:
        def OnActivate(self):
            print("worksheet OnActivate")
        # def OnChange(self, Target):
        #     print(Target.Row)
        #     print(Target.Column)
        #     print(Target.Value)
        #     print("onchange {}".format(Target))

    try:
        # pythoncom.CoInitialize()  # needed for thread
        e = DispatchWithEvents("Excel.Application", ExcelEvents)
        e.seen_events = {}
        e.Visible = 1  # open window
        book = e.Workbooks.Add()  # create workbook that contains sheet
        # book = DispatchWithEvents(book, WorkbookEvents)
        # print("Book activated", book)
        # sheet = e.Worksheets(1)
        # sheet = DispatchWithEvents(sheet, WorksheetEvents)
        # print("{} {} workbookFont {}".format(
        #     currentTimestamp(), getuser(), e.StandardFont))
        # print("{} {} workbookFontSize {}".format(
        #     currentTimestamp(), getuser(), e.StandardFontSize))
        runLoop(e)
        if not CheckSeenEvents(e, ["OnNewWorkbook", "OnWindowActivate"]):
            sys.exit(1)
    except Exception as e:
        exception = str(e)
        print(f"Failed to launch Excel: {exception}")
        # https://stackoverflow.com/q/47608506/1440037
        if "win32com.gen_py" in exception:
            # https://stackoverflow.com/a/54422675/1440037
            # Deleting the gen_py output directory and re-running the script should fix the issue
            # find the corrupted directory to remove in gen_py path using regex (directory is in the form 'win32com.gen_py.00020813-0000-0000-C000-000000000046x0x1x9)
            # I should have a string like '00020813-0000-0000-C000-000000000046x0x1x9'
            dirToRemove = findall(r"'(.*?)'", exception)[0].split('.')[-1]
            if not dirToRemove:
                # if regex failed use default folder
                dirToRemove = '00020813-0000-0000-C000-000000000046x0x1x9'
            pathToRemove = path.join(__gen_path__, dirToRemove)
            print(f"Trying to fix the error, deleting {pathToRemove}")
            rmtree(pathToRemove, ignore_errors=True)
            if not path.exists(pathToRemove):
                print("The error should now be fixed, try to execute the program again.")


def wordEvents():
    class WordEvents:
        def OnDocumentChange(self):
            self.seen_events["OnDocumentChange"] = None
            print("{} {} documentChange".format(timestamp(), getuser()))

        # def OnNewDocument(self):
        #     self.seen_events["OnDocumentChange"] = None
        #     print("{} {} newDocument".format(currentTimestamp(),getuser()))
        def OnWindowActivate(self, doc, wn):
            self.seen_events["OnWindowActivate"] = None
            print("{} {} wordOpened".format(timestamp(), getuser()))

        def OnDocumentBeforeSave(self, *args):
            print("{} {} documentSaved".format(timestamp(), getuser()))

        def OnDocumentBeforePrint(self, *args):
            print("{} {} documentPrinted".format(timestamp(), getuser()))

        def OnQuit(self):
            self.seen_events["OnQuit"] = None
            # stopEvent.set() #Set the internal flag to true. All threads waiting for it to become true are awakened

    pythoncom.CoInitialize()  # needed for thread
    w = DispatchWithEvents("Word.Application", WordEvents)
    w.seen_events = {}
    w.Visible = 1
    w.Documents.Add()

    runLoop(w)

    if not CheckSeenEvents(w, ["OnDocumentChange", "OnWindowActivate"]):
        sys.exit(1)


def powerpointEvents():
    class powerpointEvents:
        def OnDocumentChange(self):
            self.seen_events["OnDocumentChange"] = None
            print("{} {} documentChange".format(timestamp(), getuser()))

        # def OnNewDocument(self):
        #     self.seen_events["OnDocumentChange"] = None
        #     print("{} {} newDocument".format(currentTimestamp(),getuser()))
        def OnWindowActivate(self, doc, wn):
            self.seen_events["OnWindowActivate"] = None
            print("{} {} powerpointOpened".format(timestamp(), getuser()))

        def OnDocumentBeforeSave(self, *args):
            print("{} {} documentSaved".format(timestamp(), getuser()))

        def OnDocumentBeforePrint(self, *args):
            print("{} {} documentPrinted".format(timestamp(), getuser()))

        def OnQuit(self):
            self.seen_events["OnQuit"] = None
            # stopEvent.set() #Set the internal flag to true. All threads waiting for it to become true are awakened

        def OnPresentationNewSlide(self, Sld):
            print(Sld)
            print("{} {} MS-POWERPOINT newSlideAdded".format(timestamp(), getuser()))

    pythoncom.CoInitialize()  # needed for thread
    p = DispatchWithEvents("powerpoint.Application", powerpointEvents)
    p.seen_events = {}
    p.Visible = 1
    p.Presentations.Add()

    runLoop(p)

    if not CheckSeenEvents(p, ["OnDocumentChange", "OnWindowActivate"]):
        sys.exit(1)


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
        # Excel is busy (eg, editing the cell) - ignore
        except pythoncom.com_error:
            pass
    return 1


def CheckSeenEvents(o, events):
    rc = 1
    for e in events:
        if not e in o.seen_events:
            print("ERROR: Expected event did not trigger", e)
            rc = 0
    return rc


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
