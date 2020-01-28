# https://sigma-coding.com/tag/win32com-events/

import win32
import win32com.client as win32
import pythoncom

class ApplicationEvents:
    # define an event inside of our application
    def OnSheetActivate(self, *args):
        print('You Activated a new sheet.')

class WorkbookEvents:
    # define an event inside of our Workbook
    def OnSheetSelectionChange(self, *args):
        #print the arguments
        print(args)
        print(args[1].Address)
        args[0].Range('A1').Value = 'You selected cell ' + str(args[1].Address)

if __name__ == "__main__":
    # Get the active instance of Excel
    xl = win32.GetActiveObject('Excel.Application')
    #xl = win32.Dispatch("Excel.Application")
    print(xl)
    # assign our event to the Excel Application Object
    xl_events = win32.WithEvents(xl, ApplicationEvents)

    while True:
        pythoncom.PumpWaitingMessages()