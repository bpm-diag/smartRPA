# https://docs.microsoft.com/en-us/windows/win32/api/
from sys import path

path.append('../')  # this way main file is visible from this file
from time import sleep
from datetime import datetime
from getpass import getuser  # user id
from os.path import expanduser  # user folder
from os import listdir
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
from utils import consumerServer
from utils.utils import timestamp, session, WINDOWS, MAC, LINUX, DESKTOP, HOME_FOLDER

if WINDOWS:
    import pythoncom  # for win32 thread
    import win32com.client  # access running programs, part of pywin32
    from winregistry import WinRegistry as Reg  # access registry
    # pywin32 for folder changes api
    import win32file
    import win32event
    import win32con


#  monitor file changes
def watchFolder():
    #  https://pythonhosted.org/watchdog/api.html#event-handler-classes
    # https://stackoverflow.com/a/18599427
    class WatchFilesHandler(RegexMatchingEventHandler):
        def __init__(self):
            super(WatchFilesHandler, self).__init__(
                ignore_regexes=['^[.]{1}.*', '.*/[.]{1}.*', '.*\\[.]{1}.*'])  # ignore hidden files

        def on_any_event(self, event):
            if any(s in event.src_path for s in
                   ['AppData', '.pylint', '.ini', '.DS_Store', 'node_modules', '.TMP', '.wine']):  # exclude folders
                return
            else:
                if event.event_type == "moved":  # destination path is available
                    print(
                        f"{datetime.now()} {USER} OS-System {event.event_type} {event.src_path} {event.dest_path}")
                    session.post(consumerServer.SERVER_ADDR, json={
                        "timestamp": timestamp(),
                        "user": USER,
                        "category": "OS-System",
                        "application": "Explorer" if WINDOWS else "Finder",
                        "event_type": event.event_type,
                        "event_src_path": event.src_path,
                        "event_dest_path": event.dest_path
                    })
                    # return
                elif event.event_type == "modified":  # avoid spam
                    return
                else:  # created,deleted
                    print(
                        f"{datetime.now()} {USER} OS-System {event.event_type} {event.src_path}")
                    session.post(consumerServer.SERVER_ADDR, json={
                        "timestamp": timestamp(),
                        "user": USER,
                        "category": "OS-System",
                        "application": "Explorer" if WINDOWS else "Finder",
                        "event_type": event.event_type,
                        "event_src_path": event.src_path
                    })
                    # return

    my_event_handler = WatchFilesHandler()

    if WINDOWS:
        path = HOME_FOLDER
    else:
        # on osx script does not run recursively on home folder https://github.com/gorakhargosh/watchdog/issues/401
        path = DESKTOP

    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=True)
    my_observer.start()
    print("[systemEvents] Files/Folder logging started")
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()


#  Detects programs opened and closed
def logProcessesWin():
    # needed for thread http://timgolden.me.uk/pywin32-docs/pythoncom__CoInitialize_meth.html
    pythoncom.CoInitialize()
    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer, "root\cimv2")

    programs_to_ignore = ["sppsvc.exe", "WMIC.exe", "git.exe", "BackgroundTransferHost.exe", "backgroundTaskHost.exe",
                          "MusNotification.exe", "usocoreworker.exe", "GoogleUpdate.exe", "plugin_host.exe",
                          "LocalBridge.exe", "SearchProtocolHost.exe"]

    # create initial set of running processes using Windows Management Instrumentation (WMI)
    colItems = objSWbemServices.ExecQuery(
        "Select * from Win32_Process")  # access windows sql database of currently running process (also used by task manager) https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process
    running = []  # set of running programs
    for objItem in colItems:
        if objItem.Name not in running and objItem.Name not in programs_to_ignore:
            running.append(objItem.Name)

    new_programs = set()  # needed later to initialize 'closed' set
    new_programs_len = 0  # needed later to check if 'new_programs' set changes
    # maitain set of open programs so I don't have duplicates when logging events
    open_programs = []
    while True:
        sleep(1)  # seconds

        started = []  # set of programs started after the script is executed
        colItems = objSWbemServices.ExecQuery("Select * from Win32_Process")
        for objItem in colItems:
            if objItem.Name not in started and objItem.Name not in programs_to_ignore:
                started.append(objItem.Name)

        closed = new_programs

        new_programs = set(started) - set(
            running)  # check the difference between the new set and the original to find new processes
        # find programs that are not in new_programs set anymore so they have been closed
        closed_programs = closed - new_programs

        if len(new_programs) != new_programs_len:  # set is changed
            for app in new_programs:
                if app not in open_programs:
                    open_programs.append(app)
                    pathList = list(filter(lambda prog: prog.Name == app,
                                           colItems))  # find the given program in the list of running processes and take its path
                    path = pathList[0].ExecutablePath if pathList[0].ExecutablePath else ""
                    print(f"{datetime.now()} {USER} AppOpen {app} {path}")
                    post(consumerServer.SERVER_ADDR, json={
                        "timestamp": timestamp(),
                        "user": USER,
                        "category": "OS-System",
                        "application": app,
                        "event_type": "AppOpen",
                        "event_src_path": path
                    })
            new_programs_len = len(new_programs)

        if len(closed_programs):  # set is not empty
            for app in closed_programs:
                if app in open_programs:
                    open_programs.remove(app)
                    pathList = list(filter(lambda prog: prog.Name == app,
                                           colItems))  # find the given program in the list of running processes and take its path
                    path = pathList[0].ExecutablePath if pathList[0].ExecutablePath else ""
                    print(f"{datetime.now()} {USER} Appclose {app} {path}")
                    post(consumerServer.SERVER_ADDR, json={
                        "timestamp": timestamp(),
                        "user": USER,
                        "category": "OS-System",
                        "application": app,
                        "event_type": "Appclose",
                        "event_src_path": path
                    })


# return list of programs uninstalled by user


def findUninstall():
    # HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Uninstall
    # HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall
    reg = Reg()  # https://github.com/shpaker/winregistry#usage
    path = r'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall'
    keys = reg.read_key(path)['keys']
    uninstalls = []
    for k in keys:
        values = reg.read_key(path + '\\' + k)['values']
        dn = list(filter(lambda x: x['value'] == 'DisplayName', values))
        if len(dn):
            displayName = dn[0].get('data')
            uninstalls.append(displayName)
    print(uninstalls)


def watchRecentsFolderWin():
    RECENT_ITEMS_PATH = expanduser(
        "~") + "\\AppData\\Roaming\\Microsoft\\Windows\\Recent"
    change_handle = win32file.FindFirstChangeNotification(  # sets up a handle for watching file changes
        RECENT_ITEMS_PATH,  # path to watch
        0,  # boolean indicating whether the directories underneath the one specified are to be watched
        win32con.FILE_NOTIFY_CHANGE_FILE_NAME
        # list of flags as to what kind of changes to watch for https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-findfirstchangenotificationa#parameters
    )
    # Loop forever, listing any file changes. The WaitFor... will
    #  time out every half a second allowing for keyboard interrupts
    #  to terminate the loop.
    try:
        old_path_contents = dict([(f, None)
                                  for f in listdir(RECENT_ITEMS_PATH)])
        while 1:
            result = win32event.WaitForSingleObject(change_handle, 500)
            # If the WaitFor... returned because of a notification (as
            #  opposed to timing out or some error) then look for the
            #  changes in the directory contents.
            if result == win32con.WAIT_OBJECT_0:
                new_path_contents = dict([(f, None)
                                          for f in listdir(RECENT_ITEMS_PATH)])
                added = [
                    f for f in new_path_contents if not f in old_path_contents]
                # deleted = [f for f in old_path_contents if not f in new_path_contents]
                if added:
                    # print ("Added: ", ", ".join (added))
                    # remove extension
                    print(
                        f"{datetime.now()} {USER} OS-System OpenFile/Folder {added[0][:-4]}")
                    post(consumerServer.SERVER_ADDR, json={
                        "timestamp": timestamp(),
                        "user": USER,
                        "category": "OS-System",
                        "application": "Explorer" if WINDOWS else "Finder",
                        "event_type": "OpenFile/Folder",
                        "event_src_path": added[0][:-4]
                    })
                # if deleted: print ("Deleted: ", ", ".join (deleted))
                old_path_contents = new_path_contents
                win32file.FindNextChangeNotification(change_handle)
    finally:
        win32file.FindCloseChangeNotification(change_handle)


def detectSelectedFilesInExplorer():
    # look in the makepy output for IE for the 'CLSIDToClassMap' dictionary, and find the entry for 'ShellWindows'
    clsid = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'
    ShellWindows = win32com.client.Dispatch(clsid)

    # a busy state can be detected:
    # while ShellWindows[0].Busy == False:
    # go in for-loop here

    for i in range(ShellWindows.Count):
        print(ShellWindows[i].LocationURL)
        for j in range(ShellWindows[i].Document.SelectedItems().Count):
            path = ShellWindows[i].Document.SelectedItems().Item(j).Path
            print(f"Selected {path} in Windows Explorer")

    # Be careful: Internet Explorer uses also the same CLSID. You should implement a detection!


def GetUserShellFolders():
    # Routine to grab all the Windows Shell Folder locations from the registry.  If successful, returns dictionary
    # of shell folder locations indexed on Windows keyword for each; otherwise, returns an empty dictionary.
    import winreg
    return_dict = {}

    # First open the registry hive
    try:
        Hive = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    except WindowsError:
        print("Can't connect to registry hive HKEY_CURRENT_USER.")
        return return_dict

    # Then open the registry key where Windows stores the Shell Folder locations
    try:
        Key = winreg.OpenKey(
            Hive, "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
    except WindowsError:
        print("Can't open registry key Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders.")
        winreg.CloseKey(Hive)
        return return_dict

    # Nothing failed above, so enumerate through all the Shell Folder values and return in a dictionary
    # This relies on error at end of
    try:
        # i = 0
        # while 1:
        for i in range(0, winreg.QueryInfoKey(Key)[1]):
            name, value, val_type = winreg.EnumValue(Key, i)
            return_dict[name] = value
            i += 1
        winreg.CloseKey(Key)  # Only use with for loop
        winreg.CloseKey(Hive)  # Only use with for loop
        return return_dict  # Only use with for loop
    except WindowsError:
        # In case of failure before read completed, don't return partial results
        winreg.CloseKey(Key)
        winreg.CloseKey(Hive)
        return {}


# This script watches for activity at the installed printers and writes a logfile. It shows how much a user has printed on wich printer (works also with network printers).
def printerLogger():
    import wmi
    c = wmi.WMI()

    print_job_watcher = c.watch_for(
        notification_type="Creation",
        wmi_class="Win32_PrintJob",
        delay_secs=1
    )
    while 1:
        pj = print_job_watcher()
        print(
            f"{datetime.now()} {pj.Owner} OS-System printSubmitted {pj.Name} {pj.TotalPages}")