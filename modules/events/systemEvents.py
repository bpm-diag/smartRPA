# ****************************** #
# System events
# Files/Folders, Clipboard, programs, hotkeys, usb
# https://docs.microsoft.com/en-us/windows/win32/api/
# ****************************** #

from sys import path

path.append('../../')  # this way main file is visible from this file
import keyboard
import pyperclip
from time import sleep
import os
from threading import Thread
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
from modules import consumerServer
from utils.utils import *
import psutil
import pynput

mouse = pynput.mouse.Controller()

if WINDOWS:
    import pythoncom  # for win32 thread
    import win32com.client  # access running programs, part of pywin32
    import win32file
    import win32event
    import win32con
    import wmi
    from win32com.shell import shell, shellcon

if MAC:
    import applescript
    import fsevents

programs_to_ignore = ["sppsvc.exe", "WMIC.exe", "git.exe", "BackgroundTransferHost.exe", "backgroundTaskHost.exe",
                      "MusNotification.exe", "usocoreworker.exe", "GoogleUpdate.exe", "plugin_host.exe",
                      "LocalBridge.exe", "SearchProtocolHost.exe", "SearchFilterHost.exe", "splwow64.exe",
                      "printfilterpipelinesvc.exe", "smartscreen.exe", "HxTsr.exe", "GoogleCrashHandler.exe",
                      "WmiApSrv.exe", "ChromeNativeMessaging.exe", "chromenativemessaging.exe", "wmiapsrv.exe",
                      "software_reporter_tool.exe", "chrome.exe", "OUTLOOK.EXE", "WMIADAP.exe", "audiodg.exe",
                      "OfficeC2RClient.exe", "FileCoAuth.exe", "setup.exe", "MicrosoftEdgeUpdate.exe", "MpCmdRun.exe",
                      "cmd.exe", "WmiPrvSE.exe", "AppHostRegistrationVerifier.exe", "SgrmBroker.exe"]


def watchFolder():
    """
    monitor file/folder changes on windows using system APIs

    https://pythonhosted.org/watchdog/api.html#event-handler-classes

    :return: file/folder changes event
    """
    class WatchFilesHandler(RegexMatchingEventHandler):
        def __init__(self):
            # ignore hidden files
            super(WatchFilesHandler, self).__init__(ignore_regexes=['^[.]{1}.*', '.*/[.]{1}.*', '.*\\[.]{1}.*'])

        def on_any_event(self, event):
            if any(s in event.src_path for s in
                   ['AppData', '.pylint', '.ini', '.DS_Store', 'node_modules', '.TMP', '.wine']):  # exclude folders
                return
            else:
                if event.event_type == "moved":  # destination path is available
                    print(
                        f"{timestamp()} {USER} OperatingSystem {event.event_type} {event.src_path} {event.dest_path}")
                    session.post(consumerServer.SERVER_ADDR, json={
                        "timestamp": timestamp(),
                        "user": USER,
                        "category": "OperatingSystem",
                        "application": "Finder" if MAC else "Explorer",
                        "event_type": event.event_type,
                        "event_src_path": event.src_path,
                        "event_dest_path": event.dest_path,
                        "mouse_coord": mouse.position
                    })
                    # return
                elif event.event_type == "modified":  # avoid spam
                    return
                else:  # created, deleted
                    # do not log temporary windows files
                    if "~$" not in event.src_path:
                        print(
                            f"{timestamp()} {USER} OperatingSystem {event.event_type} {event.src_path}")
                        session.post(consumerServer.SERVER_ADDR, json={
                            "timestamp": timestamp(),
                            "user": USER,
                            "category": "OperatingSystem",
                            "application": "Finder" if MAC else "Explorer",
                            "event_type": event.event_type,
                            "event_src_path": event.src_path,
                            "mouse_coord": mouse.position
                        })

    print("[systemEvents] Files/Folder logging started")

    my_observer = Observer()
    my_observer.schedule(WatchFilesHandler(), HOME_FOLDER, recursive=True)
    my_observer.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()


def watchFolderMac():
    """
    monitor file/folder changes on mac using system APIs

    :return: file/folder changes event
    """
    from _fsevents import (
        loop,
        stop,
        schedule,
        unschedule,
        CF_POLLIN,
        CF_POLLOUT,
        FS_IGNORESELF,
        FS_FILEEVENTS,
        FS_ITEMCREATED,
        FS_ITEMREMOVED,
        FS_ITEMINODEMETAMOD,
        FS_ITEMRENAMED,
        FS_ITEMMODIFIED,
        FS_ITEMFINDERINFOMOD,
        FS_ITEMCHANGEOWNER,
        FS_ITEMXATTRMOD,
        FS_ITEMISFILE,
        FS_ITEMISDIR,
        FS_ITEMISSYMLINK,
        FS_EVENTIDSINCENOW,
        FS_FLAGEVENTIDSWRAPPED,
        FS_FLAGNONE,
        FS_FLAGHISTORYDONE,
        FS_FLAGROOTCHANGED,
        FS_FLAGKERNELDROPPED,
        FS_FLAGUNMOUNT,
        FS_FLAGMOUNT,
        FS_FLAGUSERDROPPED,
        FS_FLAGMUSTSCANSUBDIRS,
        FS_CFLAGFILEEVENTS,
        FS_CFLAGNONE,
        FS_CFLAGIGNORESELF,
        FS_CFLAGUSECFTYPES,
        FS_CFLAGNODEFER,
        FS_CFLAGWATCHROOT,
    )

    stringmap = {
        FS_FLAGMUSTSCANSUBDIRS: 'MustScanSubDirs',
        FS_FLAGUSERDROPPED: 'UserDropped',
        FS_FLAGKERNELDROPPED: 'KernelDropped',
        FS_FLAGEVENTIDSWRAPPED: 'EventIDsWrapped',
        FS_FLAGHISTORYDONE: 'HistoryDone',
        FS_FLAGROOTCHANGED: 'RootChanged',
        FS_FLAGMOUNT: 'Mount',
        FS_FLAGUNMOUNT: 'Unmount',
        # Flags when creating the stream.
        FS_ITEMCREATED: 'created',
        FS_ITEMREMOVED: 'deleted',
        FS_ITEMINODEMETAMOD: 'ItemInodeMetaMod',
        FS_ITEMRENAMED: 'moved',
        FS_ITEMMODIFIED: 'modified',
        FS_ITEMFINDERINFOMOD: 'ItemFinderInfoMod',
        FS_ITEMCHANGEOWNER: 'ItemChangedOwner',
        FS_ITEMXATTRMOD: 'ItemXAttrMod',
        FS_ITEMISFILE: 'ItemIsFile',
        FS_ITEMISDIR: 'ItemIsDir',
        FS_ITEMISSYMLINK: 'ItemIsSymlink'
    }

    def _maskToString(mask):
        vals = []
        for k, s in list(stringmap.items()):
            if mask & k:
                vals.append(s)
        return vals

    # I need to save events already logged for each path otherwise the callback is called in loop after every event
    logged = dict()

    def callback(file_event):
        path = file_event.name
        event_type = _maskToString(file_event.mask)[0]
        # this callback is called endlessly by the stream but I want to log the event only once. To fix this I create
        # a dictionary with the file_path as key and the event_type occurred as value. In this way I log an event for
        # the same path only once. Every time, the event type for a specific path is updated. The dictionary is like
        # {'/Users/marco/Desktop/test.txt': 'ItemCreated'}
        # insert key and value in dictionary the first time if doesn't exist
        if path not in logged.keys(): logged[path] = ""
        # ~ means temporary file
        if event_type != "UserDropped" and event_type not in logged.get(path) and "~" not in file_event.name:
            logged[path] = event_type
            # file_extension = os.path.splitext(path)[1]
            print(f"{timestamp()} {USER} OperatingSystem {event_type} {file_event.name}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "OperatingSystem",
                "application": "Finder" if MAC else "Explorer",
                "event_type": event_type,
                "event_src_path": file_event.name,
                "mouse_coord": mouse.position
            })

    print("[systemEvents] Files/Folder logging started")
    observer = fsevents.Observer()
    # Streams can observe any number of paths so I have to pass each path manually. In windows version I just pass
    # the HOME directory and it recursively observes all other folders but this does not work on macOS. Moreover the
    # home directory itself can't be observed.
    stream = fsevents.Stream(callback,
                             DESKTOP, DOCUMENTS, DOWNLOADS,
                             file_events=True)
    observer.start()
    observer.schedule(stream)


def logProcessesWin():
    """
    Detects programs opened and closed on windows.

    Works by querying list of open programs every 0.5 seconds and determining if something has been added or removed to that list.

    :return: programOpen/programClose event
    """
    print("[systemEvents] WIN Processes logging started")

    def _logProcessData(app, event):
        try:
            exe = [p.exe() for p in psutil.process_iter() if p.name() == app]
        except (PermissionError, psutil.AccessDenied):
            exe = []
        path = exe[0] if exe else ""
        print(f"{timestamp()} {USER} {event} {app} {path}")
        session.post(consumerServer.SERVER_ADDR, json={
            "timestamp": timestamp(),
            "user": USER,
            "category": "OperatingSystem",
            "application": app,
            "event_type": event,
            "event_src_path": path,
            "mouse_coord": mouse.position
        })

    new_programs = set()  # needed later to initialize 'closed' set
    new_programs_len = 0  # needed later to check if 'new_programs' set changes
    open_programs = []  # maintain set of open programs so I don't have duplicates when logging events

    running = [p.name() for p in psutil.process_iter() if p.name() not in programs_to_ignore]

    while 1:
        started = [p.name() for p in psutil.process_iter() if p.name() not in programs_to_ignore]

        closed = new_programs
        # check the difference between the new set and the original to find new processes
        new_programs = set(started) - set(running)
        # find programs that are not in new_programs set anymore so they have been closed
        closed_programs = closed - new_programs

        if len(new_programs) != new_programs_len:  # set is changed
            for app in new_programs:
                if app not in open_programs:
                    open_programs.append(app)
                    _logProcessData(app, "programOpen")
            new_programs_len = len(new_programs)

        if len(closed_programs):  # set is not empty
            for app in closed_programs:
                if app in open_programs:
                    open_programs.remove(app)
                    _logProcessData(app, "programClose")

        sleep(0.5)  # seconds


def watchRecentsFilesWin():
    """
    Log files and folders recently opened on Windows

    :return: openFile/openFolder event
    """
    ACTIONS = {
        1: "Created",
        2: "Deleted",
        3: "Updated",
        4: "Renamed to something",
        5: "Renamed from something"
    }

    def _watch_path(path_to_watch, include_subdirectories=False):
        FILE_LIST_DIRECTORY = 0x0001
        hDir = win32file.CreateFile(
            path_to_watch,
            FILE_LIST_DIRECTORY,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS,
            None
        )
        while 1:
            results = win32file.ReadDirectoryChangesW(
                hDir,
                1024,
                include_subdirectories,
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_SIZE |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY,
                None,
                None
            )
            for action, file in results:
                full_filename = os.path.join(path_to_watch, file)
                if not os.path.exists(full_filename):
                    file_type = "<deleted>"
                elif os.path.isdir(full_filename):
                    file_type = 'folder'
                else:
                    file_type = 'file'
                yield (file_type, full_filename, ACTIONS.get(action, "Unknown"))

    class Watcher(Thread):

        def __init__(self, path_to_watch, results_queue, **kwds):
            Thread.__init__(self, **kwds)
            self.setDaemon(True)
            self.path_to_watch = path_to_watch
            self.results_queue = results_queue
            self.start()

        def run(self):
            for result in _watch_path(self.path_to_watch):
                self.results_queue.put(result)

    # return full path of shortcut lnk
    def _shortcut_target(filename):
        pythoncom.CoInitialize()
        link = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink,
            None,
            pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IShellLink
        )
        link.QueryInterface(pythoncom.IID_IPersistFile).Load(filename)
        name, _ = link.GetPath(shell.SLGP_UNCPRIORITY)
        return name

    files_changed = Queue()
    Watcher(RECENT_ITEMS_PATH_WIN, files_changed)

    print("[systemEvents] Recent files/folders logging started")

    while 1:
        try:
            file_type, filename, action = files_changed.get_nowait()
            if action == "Created":
                lnk_target = _shortcut_target(filename)
                file_extension = os.path.splitext(lnk_target)[1]
                if file_extension:
                    eventType = "openFile"
                else:
                    eventType = "openFolder"

                print(f"{timestamp()} {USER} OperatingSystem {eventType} {lnk_target}")
                session.post(consumerServer.SERVER_ADDR, json={
                    "timestamp": timestamp(),
                    "user": USER,
                    "category": "OperatingSystem",
                    "application": "Finder" if MAC else "Explorer",
                    "event_type": eventType,
                    "event_src_path": lnk_target,
                    "mouse_coord": mouse.position
                })

        except Exception:
            pass

        sleep(1)


def detectSelectionWindowsExplorer():
    """
    Log currently selected files in windows explorer

    Every 0.8 seconds it queries File explorer to check for selection.

    :return: selectedFile/selectedFolder event
    """
    print("[systemEvents] detectSelectionWindowsExplorer logging started")
    # used for threads
    pythoncom.CoInitialize()
    # look in the makepy output for IE for the 'CLSIDToClassMap' dictionary, and find the entry for 'ShellWindows'
    CLSID = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'
    ShellWindows = win32com.client.Dispatch(CLSID)
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
                            # file_extension = os.path.splitext(path)[1]
                            if os.path.isfile(path):
                                eventType = "selectedFile"
                            else:
                                eventType = "selectedFolder"
                            print(f"{timestamp()} {USER} OperatingSystem {eventType} {path}")
                            session.post(consumerServer.SERVER_ADDR, json={
                                "timestamp": timestamp(),
                                "user": USER,
                                "category": "OperatingSystem",
                                "application": "Explorer",
                                "event_type": eventType,
                                "event_src_path": path,
                                "mouse_coord": mouse.position
                            })
        except Exception as e:
            # print(e)
            continue
        sleep(0.8)


def logHotkeys():
    """
    Log hotkeys using 'keyboard' python package.

    All supported hotkeys are store in 'keys_to_detect' dictionary.

    Once a supported hotkey is detected, a new thread is started to handle the event.

    :return: hotkeys event
    """
    print("[systemEvents] Hotkey logging started...")
    # https://www.hongkiat.com/blog/100-keyboard-shortcuts-windows/
    keys_to_detect = {
        'alt+d': 'Select address bar',
        'alt+F4': 'Close window',
        'alt+esc': 'Cycle through windows',
        'alt+tab': 'Cycle through open apps',
        'alt+enter': 'Display item properties',
        'alt+space+n': 'Minimise window',
        'alt+space+x': 'Maximise window',
        'ctrl+a': 'Select all',
        # 'ctrl+c': 'Copy', # handled by clipboardEvents
        'ctrl+d': 'Delete selected item',
        'ctrl+e': 'Select search box',
        'ctrl+f': 'Find',
        'ctrl+h': 'Find and replace',
        'ctrl+n': 'New',
        'ctrl+r': 'Refresh',
        'ctrl+s': 'Save',
        'ctrl+p': 'Print',
        # 'ctrl+v': 'Paste',
        'ctrl+w': 'Close window',
        'ctrl+x': 'Cut',
        'ctrl+y': 'Undo',
        'ctrl+z': 'Redo',
        'ctrl+shift+t': 'Reopen closed tab',
        'win+tab': 'Cycle through apps',
        'win+d': 'Show/Hide desktop',
        'win+e': 'Open explorer',
        'win+f': 'Search for files',
        'win+i': 'Open settings',
        'win+m': 'Minimize all windows',
        'win+p': 'Choose presentation display mode',
        'win+r': 'Run',
        'F1': 'Help',
        'F2': 'Rename',
        'F3': 'Search',
        'F5': 'Refresh',
    }

    def handleH(hotkey):
        window_name = getActiveWindowName()
        try:
            appName = window_name.split('-')[-1].strip()
        except Exception:
            appName = "Keyboard"
        meaning = keys_to_detect.get(hotkey)
        event_type = "hotkey"
        clipboard_content = ""
        if hotkey == "ctrl+x":
            event_type = "cut"
            clipboard_content = pyperclip.paste()
        if hotkey == "ctrl+h" and 'chrome' in appName.lower():
            meaning = "Show history"
        print(f"{timestamp()} {USER} OperatingSystem {event_type} {hotkey.upper()} {meaning} {clipboard_content}")
        session.post(consumerServer.SERVER_ADDR, json={
            "timestamp": timestamp(),
            "user": USER,
            "category": "OperatingSystem",
            "application": appName,
            "event_type": event_type,
            "title": window_name,
            "hotkey": hotkey.upper(),
            "description": meaning,
            "clipboard_content": clipboard_content,
            "mouse_coord": mouse.position
        })

    def handleHotkey(key):
        t = Thread(target=handleH, args=[key])
        t.start()
        t.join()

    for key in keys_to_detect.keys():
        keyboard.add_hotkey(key, handleHotkey, args=[key])

    keyboard.wait()


def logPasteHotkey():
    """
    Paste hotkey is handled separately for performance reasons.
    Once the hotkey is detected, a thread is started to handle the event.

    :return: paste hotkey
    """
    def handleCB():
        # paste event in browser is handled separately so this should log only if I'm not in browser
        browsers = ["chrome", "edge", "firefox", "opera"]
        window_name = getActiveWindowName()
        if not (any(b in window_name.lower() for b in browsers)):
            clipboard_content = pyperclip.paste()
            try:
                appName = window_name.split('-')[-1].strip()
            except Exception:
                appName = "Clipboard"
            # remove milliseconds from timestamp so duplicated events are easier to remove
            ts = timestamp()[:-3] + '000'
            print(f"{ts} {USER} OperatingSystem paste CTRL+V Paste {clipboard_content}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": ts,
                "user": USER,
                "category": "OperatingSystem",
                "application": appName,
                "title": window_name,
                "event_type": 'paste',
                "description": 'Paste',
                "clipboard_content": clipboard_content
            })

    def handleHotkey():
        cb = Thread(target=handleCB)
        cb.start()
        cb.join()

    keyboard.add_hotkey('ctrl+v', handleHotkey)
    keyboard.wait()


def logUSBDrives():
    """
    logs insertion and removal of usb drives

    :return: insertUSB event
    """
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
                print(f"{timestamp()} {USER} OperatingSystem insertUSB {id} {DiskDrive_Caption}")
                session.post(consumerServer.SERVER_ADDR, json={
                    "timestamp": timestamp(),
                    "user": USER,
                    "category": "OperatingSystem",
                    "application": "Explorer",
                    "event_type": "insertUSB",
                    "id": id,
                    "title": DiskDrive_Caption,
                })
        else:
            drive_list.clear()

        sleep(10)


def logProcessesMac():
    """
    detects programs opened and closed on mac.

    Works by querying list of open programs every 2 seconds and determining if something has been added or removed to that list.

    :return:
    """
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
                    print(f"{timestamp()} {USER} programOpen {app.strip()}.app")
                    session.post(consumerServer.SERVER_ADDR, json={
                        "timestamp": timestamp(),
                        "user": USER,
                        "category": "OperatingSystem",
                        "application": app.strip(),
                        "event_type": "programOpen",
                        "event_src_path": f"/Applications/{app.strip()}.app",
                        "mouse_coord": mouse.position
                    })
            new_programs_len = len(new_programs)

        if len(closed_programs):  # set is not empty
            for app in closed_programs:
                if app in open_programs:
                    open_programs.remove(app)
                    print(f"{timestamp()} {USER} programClose {app.strip()}.app")
                    session.post(consumerServer.SERVER_ADDR, json={
                        "timestamp": timestamp(),
                        "user": USER,
                        "category": "OperatingSystem",
                        "application": app.strip(),
                        "event_type": "programClose",
                        "event_src_path": f"/Applications/{app.strip()}.app",
                        "mouse_coord": mouse.position
                    })

        sleep(2)


def printerLogger():
    """
    Watchfor activity at the installed printers (works also with network printers).

    :return: printSubmitted event
    """
    print("[systemEvents] Printer logging started")
    pythoncom.CoInitialize()
    c = wmi.WMI()
    print_job_watcher = c.watch_for(
        notification_type="Creation",
        wmi_class="Win32_PrintJob",
        delay_secs=1
    )
    while 1:
        pj = print_job_watcher()
        print(
            f"{timestamp()} {pj.Owner} OperatingSystem printSubmitted {pj.Name}")
        session.post(consumerServer.SERVER_ADDR, json={
            "timestamp": timestamp(),
            "user": USER,
            "category": "OperatingSystem",
            "application": "Printer",
            "event_type": "printSubmitted",
            "title": pj.Name
        })
