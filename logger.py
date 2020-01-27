# https://stackoverflow.com/questions/18599339/python-watchdog-monitoring-file-for-changes

from time import sleep
from datetime import datetime
from getpass import getuser #user id
from os.path import expanduser
from sys import platform
from sys import exit
import csv
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
import win32com.client

# https://pythonhosted.org/watchdog/api.html#event-handler-classes
class MyHandler(RegexMatchingEventHandler):
    def __init__(self):
      super(MyHandler, self).__init__(ignore_regexes=['^[.]{1}.*', '.*/[.]{1}.*', '.*\\[.]{1}.*']) #ignore hidden files
    # def on_modified(self, event):
    #     pass
    # def on_created(self, event):
    #     pass
    # def on_deleted(self, event):
    #     pass
    # def on_moved(self, event):
    #     pass
    def on_any_event(self, event):
        if any(s in event.src_path for s in ['AppData','.pylint', '.ini', '.DS_Store', 'node_modules']): #exclude folders
            return
        else:
            if event.event_type == "moved":
                print(f"{datetime.now()} {getuser()} OS-System {event.event_type} {event.src_path} {event.dest_path}")
                return
            elif event.event_type == "modified":
                return
            else:
                print(f"{datetime.now()} {getuser()} OS-System {event.event_type} {event.src_path}")

def logProcessesWin(): 
    #https://stackoverflow.com/a/1187338
    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")

    programs_to_ignore = ["sppsvc.exe", "WMIC.exe", "git.exe" ,"BackgroundTransferHost.exe", "backgroundTaskHost.exe", "MusNotification.exe", "usocoreworker.exe", "GoogleUpdate.exe"]

    # create initial set of running processes
    colItems = objSWbemServices.ExecQuery("Select * from Win32_Process")
    running=[] #set of running programs
    for objItem in colItems:
        if objItem.Name not in running and objItem.Name not in programs_to_ignore:
            running.append(objItem.Name)
    
    new_programs = set() #needed later to initialize 'closed' set
    new_programs_len = 0 #needed later to check if 'new_programs' set changes
    open_programs = [] #maitain set of open programs so I don't have duplicates when logging events
    while True:
        sleep(1) #seconds
        
        started = [] #set of programs started after the script is executed
        colItems = objSWbemServices.ExecQuery("Select * from Win32_Process")
        for objItem in colItems:
            if objItem.Name not in started and objItem.Name not in programs_to_ignore: 
                started.append(objItem.Name) 
        
        closed = new_programs
        
        new_programs = set(started) - set(running) # check the difference between the new set and the original to find new processes
        closed_programs = closed - new_programs #find programs that are not in new_programs set anymore so they have been closed

        if len(new_programs) != new_programs_len: #set is changed
            for app in new_programs:
                if app not in open_programs: 
                    open_programs.append(app)
                    pathList = list(filter(lambda prog: prog.Name == app, colItems)) #find the given program in the list of running processes and take its path
                    if pathList: path=pathList[0].ExecutablePath # check if path exists
                    print(f"{datetime.now()} {getuser()} AppOpen {app} {path}")
            
            new_programs_len = len(new_programs)
        if len(closed_programs): #set is not empty
            for app in closed_programs:
                if app in open_programs: 
                    open_programs.remove(app)
                    pathList = list(filter(lambda prog: prog.Name == app, colItems)) #find the given program in the list of running processes and take its path
                    if pathList: path=pathList[0].ExecutablePath # check if path exists
                    print(f"{datetime.now()} {getuser()} AppClose {app} {path}")


def monitorProcessesUnix():
    while True:
        sleep(1)

if __name__ == "__main__":
    
    my_event_handler = MyHandler()
    path = expanduser("~") #user home folder
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=True)
    my_observer.start()
    
    print("Logger started...")
    
    try:
        # while True:
        #     sleep(1)
        if platform == "linux" or platform == "linux2": # linux
            monitorProcessesUnix()
        elif platform == "darwin": # OS X
            monitorProcessesUnix()
        elif platform == "win32": #windows
            logProcessesWin()
    
    except KeyboardInterrupt:
        my_observer.stop()
    
    my_observer.join()
    
    


