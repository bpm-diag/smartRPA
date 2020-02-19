# ****************************** #
# System events
# Files/Folders, Clipboard, programs, hotkeys, usb
# https://docs.microsoft.com/en-us/windows/win32/api/
# ****************************** #

from sys import path
path.append('../')  # this way main file is visible from this file
import keyboard
import pyperclip
from time import sleep
from os import listdir
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
from utils import consumerServer
from utils.utils import *

if WINDOWS:
    import pythoncom  # for win32 thread
    import win32com.client  # access running programs, part of pywin32
    from winregistry import WinRegistry as Reg  # access registry
    # pywin32 for folder changes api
    import win32file
    import win32event
    import win32con

if MAC:
    import applescript


#  monitor file/folder changes
def watchFolder():
    #  https://pythonhosted.org/watchdog/api.html#event-handler-classes
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


#  detects programs opened and closed
def logProcessesWin():
    print("[systemEvents] WIN Processes logging started")
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
                    if pathList:
                        path = pathList[0].ExecutablePath
                    else:
                        continue
                    print(f"{datetime.now()} {USER} AppOpen {app} {path}")
                    session.post(consumerServer.SERVER_ADDR, json={
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
                    if pathList:
                        path = pathList[0].ExecutablePath
                    else:
                        continue
                    print(f"{datetime.now()} {USER} Appclose {app} {path}")
                    session.post(consumerServer.SERVER_ADDR, json={
                        "timestamp": timestamp(),
                        "user": USER,
                        "category": "OS-System",
                        "application": app,
                        "event_type": "Appclose",
                        "event_src_path": path
                    })


# logs recently opened files and folders
def watchRecentsFolderWin():
    print("[systemEvents] Recent files/folders logging started")

    RECENT_ITEMS_PATH = expanduser(
        "~") + "\\AppData\\Roaming\\Microsoft\\Windows\\Recent"
    change_handle = win32file.FindFirstChangeNotification(  # sets up a handle for watching file changes
        RECENT_ITEMS_PATH,  # path to watch
        0,  # boolean indicating whether the directories underneath the one specified are to be watched
        win32con.FILE_NOTIFY_CHANGE_FILE_NAME
        # list of flags as to what kind of changes to watch for
        # https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-findfirstchangenotificationa#parameters
    )
    # Loop forever, listing any file changes. The WaitFor... will time out every half a second allowing for keyboard
    # interrupts to terminate the loop.
    try:
        old_path_contents = dict([(f, None) for f in listdir(RECENT_ITEMS_PATH)])
        while 1:
            result = win32event.WaitForSingleObject(change_handle, 500)
            # If the WaitFor... returned because of a notification (as
            #  opposed to timing out or some error) then look for the
            #  changes in the directory contents.
            if result == win32con.WAIT_OBJECT_0:
                new_path_contents = dict([(f, None) for f in listdir(RECENT_ITEMS_PATH)])
                added = [f for f in new_path_contents if not f in old_path_contents]
                deleted = [f for f in old_path_contents if not f in new_path_contents]
                if added:
                    # [:-4] to remove extension
                    print(
                        f"{datetime.now()} {USER} OS-System OpenFile/Folder {added[0][:-4]}")
                    session.post(consumerServer.SERVER_ADDR, json={
                        "timestamp": timestamp(),
                        "user": USER,
                        "category": "OS-System",
                        "application": "Explorer" if WINDOWS else "Finder",
                        "event_type": "OpenFile/Folder",
                        "event_src_path": added[0][:-4]
                    })
                # if deleted:
                #     print ("Deleted")
                old_path_contents = new_path_contents
                win32file.FindNextChangeNotification(change_handle)
    finally:
        win32file.FindCloseChangeNotification(change_handle)


# logs currently selected files in windows explorer
def detectSelectedFilesInExplorer():
    print("[systemEvents] detectSelectedFiles logging started")
    # used for threads
    pythoncom.CoInitialize()
    # look in the makepy output for IE for the 'CLSIDToClassMap' dictionary, and find the entry for 'ShellWindows'
    clsid = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'
    ShellWindows = win32com.client.Dispatch(clsid)
    # contains selected files. Used dictionary instead of list because I have to keep track of selected files for
    # each window in explorer, so the dictionary key is the window id and the value is a list of all selected files
    selected = dict()
    while 1:
        try:
            for i in range(ShellWindows.Count):
                # add key to dictionary
                if not selected.get(i):
                    selected[i] = []
                # explorerPath = ShellWindows[i].LocationURL
                selectedItems = ShellWindows[i].Document.SelectedItems()
                if selectedItems.Count < 1:
                    selected.pop(i)
                    continue
                else:
                    for j in range(selectedItems.Count):
                        path = selectedItems.Item(j).Path
                        if path != [] and path not in selected.get(i):
                            selected[i].append(path)
                            print(f"{datetime.now()} {USER} OS-System fileSelected {path}")
                            session.post(consumerServer.SERVER_ADDR, json={
                                "timestamp": timestamp(),
                                "user": USER,
                                "category": "OS-System",
                                "application": "Explorer",
                                "event_type": "fileSelected",
                                "event_src_path": path
                            })
        except Exception as e:
            print(e)
        sleep(0.5)


# logs hotkeys
def logHotkeys():
    print("[systemEvents] Hotkey logging started...")

    # https://www.hongkiat.com/blog/100-keyboard-shortcuts-windows/
    keys_to_detect = {
        'alt+d': 'Select address bar',
        'alt+F4': 'Close item',
        'alt+space+n': 'Minimise window',
        'alt+space+x': 'Maximise window',
        'ctrl+a': 'Select all',
        # 'ctrl+c': 'Copy',
        'ctrl+e': 'Select search box',
        'ctrl+f': 'Find',
        'ctrl+h': 'Find and replace',
        'ctrl+n': 'New',
        'ctrl+r': 'Refresh',
        'ctrl+s': 'Save',
        'ctrl+p': 'Print',
        'ctrl+v': 'Paste',
        'ctrl+w': 'Close window',
        'ctrl+x': 'Cut',
        'ctrl+y': 'Undo',
        'ctrl+z': 'Redo',
        'ctrl+shift+t': 'Reopen closed tab',
        'win+tab': 'Cycle through apps',
        'F2': 'Rename',
        'F5': 'Refresh',
    }

    def handleHotkey(hotkey):
        meaning = keys_to_detect.get(hotkey)
        event_type = "pressHotkey"
        clipboard_content = ""
        application = "Keyboard"
        # handle paste
        if hotkey == "ctrl+v":
            event_type = "Paste"
            clipboard_content = pyperclip.paste()
            application = "Clipboard"
        print(f"{datetime.now()} {USER} OS-System {event_type} {hotkey.upper()} {meaning} {clipboard_content}")
        session.post(consumerServer.SERVER_ADDR, json={
            "timestamp": timestamp(),
            "user": USER,
            "category": "OS-System",
            "application": application,
            "event_type": event_type,
            "title": hotkey.upper(),
            "description": meaning,
            "clipboard_content": clipboard_content
        })

    for key in keys_to_detect.keys():
        keyboard.add_hotkey(key, handleHotkey, args=[key])

    keyboard.wait()


# logs insertion and removal of usb drives
def logUSBDrives():
    def _queryWinDrives():
        pythoncom.CoInitialize()
        strComputer = "."
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(strComputer, "root\cimv2")

        # 1. Win32_DiskDrive
        colItems = objSWbemServices.ExecQuery("SELECT * FROM Win32_DiskDrive WHERE InterfaceType = \"USB\"")
        if len(colItems) > 0:
            DiskDrive_DeviceID = colItems[0].DeviceID.replace('\\', '').replace('.', '')
            DiskDrive_Caption = colItems[0].Caption

            # 2. Win32_DiskDriveToDiskPartition
            colItems = objSWbemServices.ExecQuery("SELECT * from Win32_DiskDriveToDiskPartition")
            for objItem in colItems:
                if DiskDrive_DeviceID in str(objItem.Antecedent):
                    DiskPartition_DeviceID = objItem.Dependent.split('=')[1].replace('"', '')

            # 3. Win32_LogicalDiskToPartition
            colItems = objSWbemServices.ExecQuery("SELECT * from Win32_LogicalDiskToPartition")
            for objItem in colItems:
                if DiskPartition_DeviceID in str(objItem.Antecedent):
                    LogicalDisk_DeviceID = objItem.Dependent.split('=')[1].replace('"', '')
                    return LogicalDisk_DeviceID, DiskDrive_Caption
        else:
            return None, None

    print("[systemEvents] USB drives logging started...")
    drive_list = dict()
    while 1:
        LogicalDisk_DeviceID, DiskDrive_Caption = _queryWinDrives()
        # if there is at least one usb drive insterted
        if LogicalDisk_DeviceID and DiskDrive_Caption:
            id = LogicalDisk_DeviceID[:-1]
            if id not in drive_list.keys():
                drive_list[id] = DiskDrive_Caption
                print(f"{datetime.now()} {USER} OS-System insertUSB {id} {DiskDrive_Caption}")
                session.post(consumerServer.SERVER_ADDR, json={
                    "timestamp": timestamp(),
                    "user": USER,
                    "category": "OS-System",
                    "application": "Explorer",
                    "event_type": "insertUSB",
                    "id": id,
                    "title": DiskDrive_Caption,
                })
        else:
            drive_list.clear()

        sleep(10)


# detects programs opened and closed on mac
def logProcessesMac():
    print("[systemEvents] MAC Processes logging started")
    running = applescript.tell.app("System Events", "name of every process where background only is false").out.split(
        ',')
    new_programs = set()  # needed later to initialize 'closed' set
    new_programs_len = 0
    open_programs = []
    while 1:
        started = applescript.tell.app("System Events",
                                       "name of every process where background only is false").out.split(',')
        closed = new_programs
        new_programs = set(started) - set(running)
        closed_programs = closed - new_programs
        if len(new_programs) != new_programs_len:  # set is changed
            for app in new_programs:
                if app not in open_programs:
                    open_programs.append(app)
                    print(f"{datetime.now()} {USER} AppOpen {app.strip()}.app")
                    session.post(consumerServer.SERVER_ADDR, json={
                        "timestamp": timestamp(),
                        "user": USER,
                        "category": "OS-System",
                        "application": app.strip(),
                        "event_type": "AppOpen",
                        "event_src_path": f"/Applications/{app.strip()}.app"
                    })
            new_programs_len = len(new_programs)

        if len(closed_programs):  # set is not empty
            for app in closed_programs:
                if app in open_programs:
                    open_programs.remove(app)
                    print(f"{datetime.now()} {USER} Appclose {app.strip()}")
                    session.post(consumerServer.SERVER_ADDR, json={
                        "timestamp": timestamp(),
                        "user": USER,
                        "category": "OS-System",
                        "application": app.strip(),
                        "event_type": "Appclose",
                        "event_src_path": f"/Applications/{app.strip()}"
                    })

        sleep(2)


# not included by main


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


# This script watches for activity at the installed printers and writes a logfile. It shows how much a user has
# printed on wich printer (works also with network printers).
def printerLogger():
    print("[systemEvents] Printer logging started")
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
