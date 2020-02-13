import sys
sys.path.append('../')  # this way main file is visible from this file
from datetime import datetime
from getpass import getuser  # user id
from string import ascii_uppercase
from re import findall
from os import path
from shutil import rmtree
from requests import post
from utils import consumerServer
from utils import utils

if utils.WINDOWS:
    from win32com.client import DispatchWithEvents, Dispatch, DispatchEx
    import pythoncom
    from win32com import __gen_path__


def excelEvents():
    # https://docs.microsoft.com/en-us/office/vba/api/excel.application(object)
    class ExcelEvents:
        def setApplication(self, application):
            self.application = application

        # ************
        # Workbooks
        # ************

        def OnNewWorkbook(self, wb):
            self.seen_events["OnNewWorkbook"] = None

            print(
                f"{utils.timestamp()} {getuser()} newWorkbook workbook: {wb.Name} Worksheet:{wb.ActiveSheet.Name} path: {wb.Path}")
            post(consumerServer.SERVER_ADDR, json={
                "timestamp": utils.timestamp(),
                "user": getuser(),
                "category": "MS-OFFICE",
                "application": "Microsoft Excel",
                "event_type": "newWorkbook",
                "workbook": wb.Name,
                "current_worksheet": wb.ActiveSheet.Name,
                "worksheets": list(map(lambda sh: sh.Name, wb.Worksheets)),
                "event_src_path": wb.Path
            })

        def OnWindowActivate(self, wb, wn):
            self.seen_events["OnWindowActivate"] = None

            print(f"{utils.timestamp()} {getuser()} openWindow workbook: {wb.Name} Worksheet:{wb.ActiveSheet.Name} window id:{wn.WindowNumber} path: {wb.Path}")
            post(consumerServer.SERVER_ADDR, json={
                "timestamp": utils.timestamp(),
                "user": getuser(),
                "category": "MS-OFFICE",
                "application": "Microsoft Excel",
                "event_type": "openWindow",
                "workbook": wb.Name,
                "current_worksheet": wb.ActiveSheet.Name,
                "worksheets": list(map(lambda sh: sh.Name, wb.Worksheets)),
                "id": wn.WindowNumber,
                "event_src_path": wb.Path
            })

        def OnWindowDeactivate(self, wb, wn):
            self.seen_events["OnWindowDeactivate"] = None
            print(
                f"{utils.timestamp()} {getuser()} closeWindow workbook: {wb.Name} Worksheet:{wb.ActiveSheet.Name} window id:{wn.WindowNumber} path: {wb.Path}")
            post(consumerServer.SERVER_ADDR, json={
                "timestamp": utils.timestamp(),
                "user": getuser(),
                "category": "MS-OFFICE",
                "application": "Microsoft Excel",
                "event_type": "closeWindow",
                "workbook": wb.Name,
                "current_worksheet": wb.ActiveSheet.Name,
                "worksheets": list(map(lambda sh: sh.Name, wb.Worksheets)),
                "id": wn.WindowNumber,
                "event_src_path": wb.Path
            })

        def OnWorkbookBeforeSave(self, Wb, SaveAsUI, Cancel):
            print(f"{utils.timestamp()} {getuser()} openWindow workbook: {Wb.Name} Worksheet:{Wb.ActiveSheet.Name} path: {Wb.Path}")
            post(consumerServer.SERVER_ADDR, json={
                "timestamp": utils.timestamp(),
                "user": getuser(),
                "category": "MS-OFFICE",
                "application": "Microsoft Excel",
                "event_type": "openWindow",
                "workbook": Wb.Name,
                "current_worksheet": Wb.ActiveSheet.Name,
                "worksheets": list(map(lambda sh: sh.Name, Wb.Worksheets)),
                "id": wn.WindowNumber,
                "event_src_path": wb.Path
            })

        # ************
        # Worksheets
        # ************

        def getWorksheets(self, Sh):
            return list(map(lambda sh: sh.Name, Sh.Parent.Worksheets))

        def OnSheetActivate(self, Sh):
            # to get the list of active worksheet names, I cycle through the parent which is the workbook
            print(f"{utils.timestamp()} {getuser()} MS-EXCEL selectWorksheet {Sh.Name} {Sh.Parent.Name} {self.getWorksheets(Sh)}")
            post(consumerServer.SERVER_ADDR, json={
                "timestamp": utils.timestamp(),
                "user": getuser(),
                "category": "MS-OFFICE",
                "application": "Microsoft Excel",
                "event_type": "selectWorksheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "worksheets": self.getWorksheets(Sh),
                "event_src_path": Sh.Parent.Path
            })

        def OnSheetDeactivate(self, Sh):
            self.seen_events["OnSheetDeactivate"] = None
            print(
                f"{utils.timestamp()} {getuser()} MS-EXCEL deselectWorksheet {Sh.Name} {Sh.Parent.Name} {self.getWorksheets(Sh)}")
            post(consumerServer.SERVER_ADDR, json={
                "timestamp": utils.timestamp(),
                "user": getuser(),
                "category": "MS-OFFICE",
                "application": "Microsoft Excel",
                "event_type": "deselectWorksheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "worksheets": self.getWorksheets(Sh),
                "event_src_path": Sh.Parent.Path
            })

        def OnSheetBeforeDelete(self, Sh):
            print(
                f"{utils.timestamp()} {getuser()} MS-EXCEL deleteWorksheet {Sh.Name} {Sh.Parent.Name} {self.getWorksheets(Sh)}")
            post(consumerServer.SERVER_ADDR, json={
                "timestamp": utils.timestamp(),
                "user": getuser(),
                "category": "MS-OFFICE",
                "application": "Microsoft Excel",
                "event_type": "deleteWorksheet",
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "worksheets": self.getWorksheets(Sh)
            })

        def OnSheetBeforeDoubleClick(self, Sh, Target, Cancel):
            event_type = "doubleClickEmptyCell"
            value = ""
            if Target.Value: # cell has value
                event_type = "doubleClickCellWithValue"
                value = Target.Value

            print(f"{utils.timestamp()} {getuser()} MS-EXCEL {event_type} {Sh.Name} {Sh.Parent.Name} {Target.Address.replace('$', '')} {value}")
            post(consumerServer.SERVER_ADDR, json={
                "timestamp": utils.timestamp(),
                "user": getuser(),
                "category": "MS-OFFICE",
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
            print(f"{utils.timestamp()} {getuser()} MS-EXCEL {event_type} {Sh.Name} {Sh.Parent.Name} {Target.Address.replace('$', '')} {value}")
            post(consumerServer.SERVER_ADDR, json={
                "timestamp": utils.timestamp(),
                "user": getuser(),
                "category": "MS-OFFICE",
                "application": "Microsoft Excel",
                "event_type": event_type,
                "workbook": Sh.Parent.Name,
                "current_worksheet": Sh.Name,
                "cell_range": Target.Address.replace('$', ''),
                "cell_content": value
            })


    class WorkbookEvents:

        # def OnActivate(self):
        #     print("{} {} workbookActive".format(utils.timestamp(), getuser()))

        # def OnBeforeRightClick(self, Target, Cancel):
        #     # print ("It's a Worksheet Event")
        #     print(
        #         "{} {} MS-EXCEL workbookRightClick {}".format(utils.timestamp(), getuser(), Target))

        # https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetactivate
        # def OnSheetActivate(self, Sh):
        #     print(f"{utils.timestamp()} {getuser()} MS-EXCEL selectWorksheet {Sh.Name}")

        #  https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetchange
        def OnSheetChange(self, Sh, Target):
            # dictionary to convert numbers in letters
            d = dict(zip(range(1, 27), ascii_uppercase))
            letter = d.get(Target.Column) if d.get(
                Target.Column) != None else Target.Column  # Target.Column is the columnt number, I want to convert it to letter as shown in excel
            print("{} {} MS-EXCEL editCellSheet {} {}".format(utils.timestamp(), getuser(), f"{letter}{Target.Row}", Target.Value))

        # https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetselectionchange
        def OnSheetSelectionChange(self, Sh, Target):
            cells_selected = Target.Address.replace('$','')  # value returned is in the format $B$3:$D$3, I remove $ sign
            value = Target.Value if Target.Value != None else ""
            if ':' in cells_selected:  # range of cells selected
                print(
                    f"{utils.timestamp()} {getuser()} MS-EXCEL getRange {cells_selected}")
            else:  # single cell selected
                print(
                    f"{utils.timestamp()} {getuser()} MS-EXCEL getCell {cells_selected} {value}")
            # args[0].Range('A1').Value = 'You selected cell ' + str(args[1].Address)

        def OnBeforeSave(self, *args):
            print("{} {} MS-EXCEL workbookSaved".format(utils.timestamp(), getuser()))

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
        sheet = e.Worksheets(1)
        # sheet = DispatchWithEvents(sheet, WorksheetEvents)
        # print("{} {} workbookFont {}".format(
        #     utils.currentTimestamp(), getuser(), e.StandardFont))
        # print("{} {} workbookFontSize {}".format(
        #     utils.currentTimestamp(), getuser(), e.StandardFontSize))
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
            print("{} {} documentChange".format(utils.timestamp(), getuser()))

        # def OnNewDocument(self):
        #     self.seen_events["OnDocumentChange"] = None
        #     print("{} {} newDocument".format(utils.currentTimestamp(),getuser()))
        def OnWindowActivate(self, doc, wn):
            self.seen_events["OnWindowActivate"] = None
            print("{} {} wordOpened".format(utils.timestamp(), getuser()))

        def OnDocumentBeforeSave(self, *args):
            print("{} {} documentSaved".format(utils.timestamp(), getuser()))

        def OnDocumentBeforePrint(self, *args):
            print("{} {} documentPrinted".format(utils.timestamp(), getuser()))

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
            print("{} {} documentChange".format(utils.timestamp(), getuser()))

        # def OnNewDocument(self):
        #     self.seen_events["OnDocumentChange"] = None
        #     print("{} {} newDocument".format(utils.currentTimestamp(),getuser()))
        def OnWindowActivate(self, doc, wn):
            self.seen_events["OnWindowActivate"] = None
            print("{} {} powerpointOpened".format(utils.timestamp(), getuser()))

        def OnDocumentBeforeSave(self, *args):
            print("{} {} documentSaved".format(utils.timestamp(), getuser()))

        def OnDocumentBeforePrint(self, *args):
            print("{} {} documentPrinted".format(utils.timestamp(), getuser()))

        def OnQuit(self):
            self.seen_events["OnQuit"] = None
            # stopEvent.set() #Set the internal flag to true. All threads waiting for it to become true are awakened

        def OnPresentationNewSlide(self, Sld):
            print(Sld)
            print("{} {} MS-POWERPOINT newSlideAdded".format(utils.timestamp(), getuser()))

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
            print("{} {} documentChange".format(utils.timestamp(), getuser()))

        # def OnNewDocument(self):
        #     self.seen_events["OnDocumentChange"] = None
        #     print("{} {} newDocument".format(utils.currentTimestamp(),getuser()))
        def OnWindowActivate(self, doc, wn):
            self.seen_events["OnWindowActivate"] = None
            print("{} {} outlookOpened".format(utils.timestamp(), getuser()))

        def OnDocumentBeforeSave(self, *args):
            print("{} {} documentSaved".format(utils.timestamp(), getuser()))

        def OnDocumentBeforePrint(self, *args):
            print("{} {} documentPrinted".format(utils.timestamp(), getuser()))

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
    if not CheckSeenEvents(p, ["OnDocumentChange", "OnWindowActivate"]):
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
