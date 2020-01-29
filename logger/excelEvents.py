# https://sigma-coding.com/tag/win32com-events/
# If it does not work, kill excel from task manager and re-open in

import win32com.client
import pythoncom
from datetime import datetime
from getpass import getuser #user id
from sys import exit
import time

class ExcelApplicationEvents: # define an event inside of our application
    
    # https://docs.microsoft.com/en-us/office/vba/api/excel.application.sheetactivate
    def OnSheetActivate(self, *args):
        activated_sheet = args[0].Name
        print(f"{datetime.now()} {getuser()} MS-EXCEL selectWorksheet {activated_sheet}")

    # https://docs.microsoft.com/en-us/office/vba/api/excel.application.workbookactivate
    #def OnWorkbookActivate(self, *args):
    #    print(f"{datetime.now()} {getuser()} MS-EXCEL selectWorksheet {args[0]}")



class WorkbookEvents: # define an event inside of our Workbook
    
    # https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetactivate
    def OnSheetActivate(self, *args):
        activated_sheet = args[0].Name
        print(f"{datetime.now()} {getuser()} MS-EXCEL selectWorksheet {activated_sheet}")

    # https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetselectionchange
    def OnSheetSelectionChange(self, *args): 
        cells_selected = args[1].Address.replace('$','') #value returned is in the format $B$3:$D$3, I remove $ sign
        if ':' in cells_selected: #range of cells selected
            print(f"{datetime.now()} {getuser()} MS-EXCEL getRange {cells_selected}")
        else: #single cell selected
            print(f"{datetime.now()} {getuser()} MS-EXCEL getCell {cells_selected}")
        #args[0].Range('A1').Value = 'You selected cell ' + str(args[1].Address)

def excelEvents():
    # Get the active instance of Excel, the program must be running
    #xl = win32com.client.GetActiveObject('Excel.Application')
    xl = win32com.client.gencache.EnsureDispatch('Excel.Application') #has ready property https://docs.microsoft.com/en-us/office/vba/api/excel.application.ready
    #gencache.EnsureModule('{0EA692EE-BB50-4E3C-AEF0-356D91732725}', 0, 1, 1) #for onenote https://stackoverflow.com/a/16325552
    #mod = gencache.EnsureModule("{00020813-0000-0000-C000-000000000046}", 9, 1, 0)
    #xl = win32com.client.Dispatch("Excel.Application")
    #xl.Visible=1
    # assign our event to the Excel Application Object
    xl_events = win32com.client.WithEvents(xl, ExcelApplicationEvents)

    # grab the workbook
    #xl_workbook = xl.Workbooks('Book1')
    # assign events to Workbook
    #xl_workbook_events = win32com.client.WithEvents(xl_workbook, WorkbookEvents)

    # define initalizer
    keepOpen = True
    # while there are messages keep displaying them, and also as long as the Excel App is still open
    while keepOpen:
        
        if (xl.Ready):
        # display the message
            pythoncom.PumpWaitingMessages()
        else:
            time.sleep(1)
        
        try:
            # if the workbook count does not equal zero we can assume Excel is open
            if xl.Workbooks.Count != 0:
                keepOpen = True
            # otherwise close the application and exit the script
            else:
                keepOpen = False
                xl = None 
                exit()
        except Exception as e:
            print(e)
            # if there is an error close excel and exit the script
            keepOpen = False
            xl = None
            exit()

if __name__ == "__main__":
    excelEvents()
    