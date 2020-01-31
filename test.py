# message
def showDialog():
    import win32ui
    import win32con
    dialog = win32ui.MessageBox("Message", "Title", win32con.MB_YESNOCANCEL)
    if dialog == win32con.IDYES:
        win32ui.MessageBox("You pressed 'Yes'")

showDialog()

import win32com.client

# prints all events from windows event log:
def winEventLog(): #Windows Management Instrumentation (WMI)
    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
    colItems = objSWbemServices.ExecQuery("Select * from Win32_NTLogEvent") #https://docs.microsoft.com/en-us/previous-versions/windows/desktop/eventlogprov/win32-ntlogevent
    for objItem in colItems:
        print ("Category: ", objItem.Category)
        print ("Category String: ", objItem.CategoryString)
        print ("Computer Name: ", objItem.ComputerName)
        z = objItem.Data
        if z is None:
            a = 1
        else:
            for x in z:
                print ("Data: ", x)
        print ("Event Code: ", objItem.EventCode)
        print ("Event Identifier: ", objItem.EventIdentifier)
        print ("Event Type: ", objItem.EventType)
        z = objItem.InsertionStrings
        if z is None:
            a = 1
        else:
            for x in z:
                print( "Insertion Strings: ", x)
        print ("Logfile: ", objItem.Logfile)
        print( "Message: ", objItem.Message)
        print ("Record Number: ", objItem.RecordNumber)
        print ("Source Name: ", objItem.SourceName)
        print ("Time Generated: ", objItem.TimeGenerated)
        print ("Time Written: ", objItem.TimeWritten)
        print ("Type: ", objItem.Type)
        print ("User: ", objItem.User )
        break


#winEventLog()
