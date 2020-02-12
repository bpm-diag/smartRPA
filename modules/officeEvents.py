import time
import sys
import types
from datetime import datetime
from getpass import getuser  # user id
from string import ascii_uppercase
from re import findall
from os import path
from shutil import rmtree
from platform import system
from requests import post
sys.path.append('../')  # this way main file is visible from this file
from utils import consumerServer

if system() == "Windows":
    from win32com.client import DispatchWithEvents, Dispatch, DispatchEx
    import pythoncom
    from win32com import __gen_path__


def excelEvents():
    class ExcelEvents:
        def setApplication(self, application):
            self.application = application

        def OnNewWorkbook(self, wb):
            # if type(wb) != types.InstanceType:
            #    raise (RuntimeError, "The transformer doesnt appear to have translated this for us!")
            self.seen_events["OnNewWorkbook"] = None

        def OnWindowActivate(self, wb, wn):
            # if type(wb) != types.InstanceType or type(wn) != types.InstanceType:
            #    raise (RuntimeError, "The transformer doesnt appear to have translated this for us!")
            self.seen_events["OnWindowActivate"] = None
            print(f"{datetime.now()} {getuser()} windowActive")
            post(consumerServer.SERVER_ADDR, json={
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3],
                "user": getuser(),
                "category": "MS-OFFICE",
                "application": "Microsoft Excel",
                "event_type": "windowActive",
            })

        def OnWindowDeactivate(self, wb, wn):
            self.seen_events["OnWindowDeactivate"] = None

        def OnSheetDeactivate(self, sh):
            self.seen_events["OnSheetDeactivate"] = None

        def OnSheetBeforeDoubleClick(self, Sh, Target, Cancel):
            # This function is a vo id, so the result ends up in
            # the only ByRef - Cancel.
            if Target is not None or Target != 'None':
                print("{} {} doubleClickCellWithValue {}".format(
                    datetime.now(), getuser(), Target))
            else:
                print("{} {} doubleClickEmptyCell".format(
                    datetime.now(), getuser()))
            return 1

    class WorkbookEvents:

        def OnActivate(self):
            print("{} {} workbookActive".format(datetime.now(), getuser()))

        def OnBeforeRightClick(self, Target, Cancel):
            # print ("It's a Worksheet Event")
            print(
                "{} {} MS-EXCEL workbookRightClick {}".format(datetime.now(), getuser(), Target))

        # https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetactivate
        def OnSheetActivate(self, Sh):
            print(f"{datetime.now()} {getuser()} MS-EXCEL selectWorksheet {Sh.Name}")

        #  https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetchange
        def OnSheetChange(self, Sh, Target):
            # dictionary to convert numbers in letters
            d = dict(zip(range(1, 27), ascii_uppercase))
            letter = d.get(Target.Column) if d.get(
                Target.Column) != None else Target.Column  # Target.Column is the columnt number, I want to convert it to letter as shown in excel
            print("{} {} MS-EXCEL editCellSheet {} {}".format(datetime.now(), getuser(), f"{letter}{Target.Row}",
                                                              Target.Value))

        # https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetselectionchange
        def OnSheetSelectionChange(self, Sh, Target):
            cells_selected = Target.Address.replace('$',
                                                    '')  # value returned is in the format $B$3:$D$3, I remove $ sign
            value = Target.Value if Target.Value != None else ""
            if ':' in cells_selected:  # range of cells selected
                print(
                    f"{datetime.now()} {getuser()} MS-EXCEL getRange {cells_selected}")
            else:  # single cell selected
                print(
                    f"{datetime.now()} {getuser()} MS-EXCEL getCell {cells_selected} {value}")
            # args[0].Range('A1').Value = 'You selected cell ' + str(args[1].Address)

        def OnBeforeSave(self, *args):
            print("{} {} MS-EXCEL workbookSaved".format(datetime.now(), getuser()))

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
        #     datetime.now(), getuser(), e.StandardFont))
        # print("{} {} workbookFontSize {}".format(
        #     datetime.now(), getuser(), e.StandardFontSize))
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
            print("{} {} documentChange".format(datetime.now(), getuser()))

        # def OnNewDocument(self):
        #     self.seen_events["OnDocumentChange"] = None
        #     print("{} {} newDocument".format(datetime.now(),getuser()))
        def OnWindowActivate(self, doc, wn):
            self.seen_events["OnWindowActivate"] = None
            print("{} {} wordOpened".format(datetime.now(), getuser()))

        def OnDocumentBeforeSave(self, *args):
            print("{} {} documentSaved".format(datetime.now(), getuser()))

        def OnDocumentBeforePrint(self, *args):
            print("{} {} documentPrinted".format(datetime.now(), getuser()))

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
            print("{} {} documentChange".format(datetime.now(), getuser()))

        # def OnNewDocument(self):
        #     self.seen_events["OnDocumentChange"] = None
        #     print("{} {} newDocument".format(datetime.now(),getuser()))
        def OnWindowActivate(self, doc, wn):
            self.seen_events["OnWindowActivate"] = None
            print("{} {} powerpointOpened".format(datetime.now(), getuser()))

        def OnDocumentBeforeSave(self, *args):
            print("{} {} documentSaved".format(datetime.now(), getuser()))

        def OnDocumentBeforePrint(self, *args):
            print("{} {} documentPrinted".format(datetime.now(), getuser()))

        def OnQuit(self):
            self.seen_events["OnQuit"] = None
            # stopEvent.set() #Set the internal flag to true. All threads waiting for it to become true are awakened

        def OnPresentationNewSlide(self, Sld):
            print(Sld)
            print("{} {} MS-POWERPOINT newSlideAdded".format(datetime.now(), getuser()))

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
            print("{} {} documentChange".format(datetime.now(), getuser()))

        # def OnNewDocument(self):
        #     self.seen_events["OnDocumentChange"] = None
        #     print("{} {} newDocument".format(datetime.now(),getuser()))
        def OnWindowActivate(self, doc, wn):
            self.seen_events["OnWindowActivate"] = None
            print("{} {} outlookOpened".format(datetime.now(), getuser()))

        def OnDocumentBeforeSave(self, *args):
            print("{} {} documentSaved".format(datetime.now(), getuser()))

        def OnDocumentBeforePrint(self, *args):
            print("{} {} documentPrinted".format(datetime.now(), getuser()))

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
