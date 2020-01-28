# https://docs.microsoft.com/en-us/windows/win32/api/
from time import sleep
from datetime import datetime
from getpass import getuser #user id
from os.path import expanduser #user folder
from os import listdir
from sys import platform #detect running os
from sys import exit
from threading import Thread
import csv
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
import pythoncom #for win32 thread
import win32com.client #access running programs, part of pywin32
from winregistry import WinRegistry as Reg #access registry
#pywin32 for folder changes api
import win32file 
import win32event
import win32con

RECENT_ITEMS_PATH = expanduser("~")+"\\AppData\\Roaming\\Microsoft\\Windows\\Recent"

# https://pythonhosted.org/watchdog/api.html#event-handler-classes
# https://stackoverflow.com/questions/18599339/python-watchdog-monitoring-file-for-changes
class MyHandler(RegexMatchingEventHandler):
    def __init__(self):
      super(MyHandler, self).__init__(ignore_regexes=['^[.]{1}.*', '.*/[.]{1}.*', '.*\\[.]{1}.*']) #ignore hidden files

    def on_any_event(self, event):
        if any(s in event.src_path for s in ['AppData','.pylint', '.ini', '.DS_Store', 'node_modules']): #exclude folders
            return
        else:
            if event.event_type == "moved": #destination path is available
                print(f"{datetime.now()} {getuser()} OS-System {event.event_type} {event.src_path} {event.dest_path}")
                return
            elif event.event_type == "modified": #avoid spam
                return
            else: #created,deleted
                print(f"{datetime.now()} {getuser()} OS-System {event.event_type} {event.src_path}")

# monitor file changes
def watchFolder():
    my_event_handler = MyHandler()
    path = expanduser("~") #user home folder
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=True)
    my_observer.start()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()

# Detects programs opened and closed
def logProcessesWin(): 
    #https://stackoverflow.com/a/1187338
    pythoncom.CoInitialize()
    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")

    programs_to_ignore = ["sppsvc.exe", "WMIC.exe", "git.exe" ,"BackgroundTransferHost.exe", "backgroundTaskHost.exe", "MusNotification.exe", "usocoreworker.exe", "GoogleUpdate.exe"]

    # create initial set of running processes
    colItems = objSWbemServices.ExecQuery("Select * from Win32_Process") #access windows sql database of currently running process (also used by task manager)
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
                    if pathList: #path to program is known
                        path=pathList[0].ExecutablePath # check if path exists
                        print(f"{datetime.now()} {getuser()} AppOpen {app} {path}")
                    else: 
                        print(f"{datetime.now()} {getuser()} AppOpen {app}")
            
            new_programs_len = len(new_programs)
        if len(closed_programs): #set is not empty
            for app in closed_programs:
                if app in open_programs: 
                    open_programs.remove(app)
                    pathList = list(filter(lambda prog: prog.Name == app, colItems)) #find the given program in the list of running processes and take its path
                    if pathList: #path to program is known
                        path=pathList[0].ExecutablePath # check if path exists
                        print(f"{datetime.now()} {getuser()} AppClose {app} {path}")
                    else: 
                        print(f"{datetime.now()} {getuser()} AppClose {app}")

# return list of programs uninstalled by user
def findUninstall():
    #HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Uninstall
    #HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall
    reg = Reg() #https://github.com/shpaker/winregistry#usage
    path = r'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall'
    keys = reg.read_key(path)['keys']
    uninstalls=[]
    for k in keys:
        values = reg.read_key(path+'\\'+k)['values']
        dn=list(filter(lambda x: x['value'] == 'DisplayName', values))
        if len(dn):
            displayName= dn[0].get('data')
            uninstalls.append(displayName)
    print(uninstalls)

#http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html#use_findfirstchange 
def watchRecentsFolder():
    change_handle = win32file.FindFirstChangeNotification ( #sets up a handle for watching file changes
    RECENT_ITEMS_PATH, #path to watch
    0, #boolean indicating whether the directories underneath the one specified are to be watched
    win32con.FILE_NOTIFY_CHANGE_FILE_NAME #list of flags as to what kind of changes to watch for https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-findfirstchangenotificationa#parameters
    )
    # Loop forever, listing any file changes. The WaitFor... will
    #  time out every half a second allowing for keyboard interrupts
    #  to terminate the loop.
    try:
        old_path_contents = dict ([(f, None) for f in listdir (RECENT_ITEMS_PATH)])
        while 1:
            result = win32event.WaitForSingleObject(change_handle, 500)
            # If the WaitFor... returned because of a notification (as
            #  opposed to timing out or some error) then look for the
            #  changes in the directory contents.
            if result == win32con.WAIT_OBJECT_0:
                new_path_contents = dict ([(f, None) for f in listdir (RECENT_ITEMS_PATH)])
                added = [f for f in new_path_contents if not f in old_path_contents]
                #deleted = [f for f in old_path_contents if not f in new_path_contents]
                if added: 
                    #print ("Added: ", ", ".join (added))
                    print(f"{datetime.now()} {getuser()} OS-System OpenFile/Folder {added[0][:-4]}") #remove extension
                #if deleted: print ("Deleted: ", ", ".join (deleted))
                old_path_contents = new_path_contents
                win32file.FindNextChangeNotification (change_handle)
    finally:
        win32file.FindCloseChangeNotification (change_handle)

if __name__ == "__main__":
    print("Logger started...")
    try:
        t1=Thread(target=watchFolder)
        t2=Thread(target=logProcessesWin)
        t3=Thread(target=watchRecentsFolder)
        #daemon threads are closed when main ends
        t1.daemon = True
        t2.daemon = True
        t3.daemon = True  
        t1.start()
        t2.start()
        t3.start()
        while 1: #keep main active
            #sleep(1)
            pass
    except (KeyboardInterrupt, SystemExit):
        print("Closing threads...")
        exit(0)

