# https://win32com.goermezer.de/microsoft/ms-office/events-in-microsoft-word-and-excel.html
from win32com.client import DispatchWithEvents, Dispatch
import msvcrt, pythoncom
import time, sys
import types

from datetime import datetime
from getpass import getuser #user id

import threading
stopEvent = threading.Event()

def excelEvents():
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
            # This function is a void, so the result ends up in
            # the only ByRef - Cancel.
            if Target is not None or Target != 'None': print("{} {} doubleClickCellWithValue {}".format(datetime.now(),getuser(), Target ))
            else: print("{} {} doubleClickEmptyCell".format(datetime.now(),getuser()))
            return 1

    class WorkbookEvents:
        def OnActivate(self):
            print ("workbook OnActivate")
        def OnBeforeRightClick(self, Target, Cancel):
            print ("It's a Worksheet Event")
        # https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetactivate
        def OnSheetActivate(self, *args):
            print("{} {} selectWorksheet {}".format(datetime.now(),getuser(),args[0].Name))
            #print(f"{datetime.now()} {getuser()} MS-EXCEL selectWorksheet {activated_sheet}")
        # https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetchange
        def OnSheetChange(self, *args):
            print("{} {} editCell {}".format(datetime.now(),getuser(),args[1]))
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
        def OnBeforeSave(self, *args):
                print("{} {} wbSaved".format(datetime.now(),getuser()))

    class WorksheetEvents:
        def OnActivate(self):
            print ("worksheet OnActivate")

    e = DispatchWithEvents("Excel.Application", ExcelEvents)
    e.seen_events = {}
    e.Visible=1
    book = e.Workbooks.Add()
    book = DispatchWithEvents(book, WorkbookEvents)
    print ("Book activated", book)
    sheet = e.Worksheets(1)
    sheet = DispatchWithEvents(sheet, WorksheetEvents)

    if not _WaitForFinish(e):
        e.Quit()
    if not _CheckSeenEvents(e, ["OnNewWorkbook", "OnWindowActivate"]):
        sys.exit(1)

def wordEvents():
    
    class WordEvents:
        def OnDocumentChange(self):
            self.seen_events["OnDocumentChange"] = None
        def OnWindowActivate(self, doc, wn):
            self.seen_events["OnWindowActivate"] = None
        def OnQuit(self):
            self.seen_events["OnQuit"] = None
            stopEvent.set() #Set the internal flag to true. All threads waiting for it to become true are awakened

    w = DispatchWithEvents("Word.Application", WordEvents)
    w.seen_events = {}
    w.Visible = 1
    w.Documents.Add()
    #print ("Press any key when finished with Word, or wait 10 seconds...")
    if not _WaitForFinish(w):
        w.Quit()
    if not _CheckSeenEvents(w, ["OnDocumentChange", "OnWindowActivate"]):
        sys.exit(1)

def _WaitForFinish(ob):
    while 1:
        # if msvcrt.kbhit(): #Return true if a keypress is waiting to be read
        #     msvcrt.getch() #Read a keypress and return the resulting character. Nothing is echoed to the console. This call will block if a keypress is not already available, but will not wait for Enter to be pressed.
        #     break
        pythoncom.PumpWaitingMessages()
        # stopEvent.wait(.2) # https://docs.python.org/2/library/threading.html#event-objects
        # if stopEvent.isSet():
        #     stopEvent.clear()
        #     break
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
        wordEvents()
    if "noexcel" not in sys.argv[1:]:
        excelEvents()
    print ("Word and Excel event tests passed.")

if __name__=='__main__':
    test()
