import win32com.client
from time import sleep
from datetime import datetime
from getpass import getuser #user id

#print (f"File location: {objItem.ExecutablePath}")

def monitorProcessesWin():
    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")

    # create initial set of running processes
    colItems = objSWbemServices.ExecQuery("Select * from Win32_Process")
    running=[]
    for objItem in colItems:
        if objItem not in running:
            running.append(objItem.Name)
    #print(set(running))

    while True:
        sleep(2) #seconds
        started = []
        colItems = objSWbemServices.ExecQuery("Select * from Win32_Process")
        for objItem in colItems:
            if objItem.Name not in started: 
                started.append(objItem.Name) 
        new = set(started) - set(running) # check the difference between the new set and the original to find new processes
        
        if len(new): #set is not empty
            print(f"{datetime.now()} {getuser()} AppLaunch {new}")

if __name__ == "__main__":
    monitorProcessesWin()