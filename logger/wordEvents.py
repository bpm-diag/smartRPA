# https://sigma-coding.com/tag/win32com-events/
# If it does not work, kill excel from task manager and re-open in

import win32com.client
import pythoncom
from datetime import datetime
from getpass import getuser #user id
from sys import exit

class ApplicationEvents: # define an event inside of our application
    
    # https://docs.microsoft.com/en-us/office/vba/api/excel.application.sheetactivate
    def OnSheetActivate(self, *args):
        print(f"{datetime.now()} {getuser()} MS-EXCEL sheet activated")


class WorkbookEvents: # define an event inside of our Workbook
    
    # https://docs.microsoft.com/en-us/office/vba/api/excel.workbook.sheetselectionchange
    def OnSheetSelectionChange(self, *args):
        #print(args) #sheet
        range_of_cells_selected = args[1].Address
        print(f"{datetime.now()} {getuser()} MS-EXCEL range selected {range_of_cells_selected}")
        #args[0].Range('A1').Value = 'You selected cell ' + str(args[1].Address)

def excelEvents():
    # Get the active instance of Excel, the program must be running
    xl = win32com.client.GetActiveObject('Excel.Application')
    #xl = win32com.client.Dispatch("Excel.Application")
    #xl.Visible=1
    # assign our event to the Excel Application Object
    xl_events = win32com.client.WithEvents(xl, ApplicationEvents)

    # grab the workbook
    xl_workbook = xl.Workbooks('Book1')
    # assign events to Workbook
    xl_workbook_events = win32com.client.WithEvents(xl_workbook, WorkbookEvents)

    # while True:
    #     pythoncom.PumpWaitingMessages() #display the message
    
    # define initalizer
    keepOpen = True
    # while there are messages keep displaying them, and also as long as the Excel App is still open
    while keepOpen:
        # display the message
        pythoncom.PumpWaitingMessages()
        try:
            # if the workbook count does not equal zero we can assume Excel is open
            if xl.Workbooks.Count != 0:
                keepOpen = True
            # otherwise close the application and exit the script
            else:
                keepOpen = False
                xl = None 
                exit()
        except:
            # if there is an error close excel and exit the script
            keepOpen = False
            xl = None
            exit()

if __name__ == "__main__":
    excelEvents()
    