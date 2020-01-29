# https://win32com.goermezer.de/microsoft/ms-office/events-in-microsoft-word-and-excel.html
from win32com.client import DispatchWithEvents, Dispatch
import msvcrt, pythoncom
import time, sys
import types

from datetime import datetime
from getpass import getuser #user id

import threading
stopEvent = threading.Event()

def TestExcel():
    class ExcelEvents:
        def OnNewWorkbook(self, wb):
            #if type(wb) != types.InstanceType:
            #    raise (RuntimeError, "The transformer doesnt appear to have translated this for us!")
            self.seen_events["OnNewWorkbook"] = None
        def OnWindowActivate(self, wb, wn):
            #if type(wb) != types.InstanceType or type(wn) != types.InstanceType:
            #    raise (RuntimeError, "The transformer doesnt appear to have translated this for us!")
            self.seen_events["OnWindowActivate"] = None
        def OnWindowDeactivate(self, wb, wn):
            self.seen_events["OnWindowDeactivate"] = None
        def OnSheetDeactivate(self, sh):
            self.seen_events["OnSheetDeactivate"] = None
        def OnSheetBeforeDoubleClick(self, Sh, Target, Cancel):
            if Target.Column % 2 == 0:
                print ("You can double-click there...")
            else:
                print ("You can not double-click there...")
            # This function is a void, so the result ends up in
            # the only ByRef - Cancel.
                return 1

    class WorkbookEvents:
        def OnActivate(self):
            print ("workbook OnActivate")
        def OnBeforeRightClick(self, Target, Cancel):
            print ("It's a Worksheet Event")
        # https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetactivate
        def OnSheetActivate(self, *args):
            activated_sheet = args[0].Name
            print("{} {} selectWorksheet {}".format(datetime.now(),getuser(),activated_sheet))
            #print(f"{datetime.now()} {getuser()} MS-EXCEL selectWorksheet {activated_sheet}")
        # https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetselectionchange
        def OnSheetSelectionChange(self, *args): 
            cells_selected = args[1].Address.replace('$','') #value returned is in the format $B$3:$D$3, I remove $ sign
            if ':' in cells_selected: #range of cells selected
                print("{} {} getRange {}".format(datetime.now(),getuser(),cells_selected))
                #print(f"{datetime.now()} {getuser()} MS-EXCEL getRange {cells_selected}")
            else: #single cell selected
                print("{} {} getCells {}".format(datetime.now(),getuser(),cells_selected))
                #print(f"{datetime.now()} {getuser()} MS-EXCEL getCell {cells_selected}")
            #args[0].Range('A1').Value = 'You selected cell ' + str(args[1].Address)
        def OnSheetChange(self, *args):
            print(args[0])
            print(args[1])

    e = DispatchWithEvents("Excel.Application", ExcelEvents)
    e.seen_events = {}
    e.Visible=1
    book = e.Workbooks.Add()
    book = DispatchWithEvents(book, WorkbookEvents)
    print ("Have book", book)
#    sheet = e.Worksheets(1)
#    sheet = DispatchWithEvents(sheet, WorksheetEvents)

    #print ("Double-click in a few of the Excel cells...")
    #print ("Press any key when finished with Excel, or wait 10 seconds...")
    if not _WaitForFinish(e):
        e.Quit()
    if not _CheckSeenEvents(e, ["OnNewWorkbook", "OnWindowActivate"]):
        sys.exit(1)

def TestWord():
    class WordEvents:
        def OnDocumentChange(self):
            self.seen_events["OnDocumentChange"] = None
        def OnWindowActivate(self, doc, wn):
            self.seen_events["OnWindowActivate"] = None
        def OnQuit(self):
            self.seen_events["OnQuit"] = None
            stopEvent.set()

    w = DispatchWithEvents("Word.Application", WordEvents)
    w.seen_events = {}
    w.Visible = 1
    w.Documents.Add()
    print ("Press any key when finished with Word, or wait 10 seconds...")
    if not _WaitForFinish(w):
        w.Quit()
    if not _CheckSeenEvents(w, ["OnDocumentChange", "OnWindowActivate"]):
        sys.exit(1)

def _WaitForFinish(ob):
    while 1:
        if msvcrt.kbhit():
            msvcrt.getch()
            break
        pythoncom.PumpWaitingMessages()
        stopEvent.wait(.2)
        if stopEvent.isSet():
            stopEvent.clear()
            break
        try:
            if not ob.Visible:
                # Gone invisible - we need to pretend we timed
                # out, so the app is quit.
                return 0
        except pythoncom.com_error:
            # Excel is busy (eg, editing the cell) - ignore
            pass
    return 1

def _CheckSeenEvents(o, events):
    rc = 1
    for e in events:
        if not o.seen_events.has_key(e):
            print ("ERROR: Expected event did not trigger", e)
            rc = 0
    return rc

def test():
    import sys
    if "noword" not in sys.argv[1:]:
        TestWord()
    if "noexcel" not in sys.argv[1:]:
        TestExcel()
    print ("Word and Excel event tests passed.")

if __name__=='__main__':
    test()
