# https://stackoverflow.com/questions/18599339/python-watchdog-monitoring-file-for-changes

from time import sleep
from datetime import datetime
from getpass import getuser #user id
from os.path import expanduser
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
        if any(s in event.src_path for s in ['AppData','.pylint', '.ini', '.DS_Store']): #exclude folders
            return
        else:
            if event.event_type == "moved":
                print(f"{datetime.now()} {getuser()} OS-System {event.event_type} {event.src_path} {event.dest_path}")
                return
            print(f"{datetime.now()} {getuser()} OS-System {event.event_type} {event.src_path}")

def monitorProcessesWin():
    pass

def monitorProcessesUnix():
    pass

if __name__ == "__main__":
    my_event_handler = MyHandler()
    path = expanduser("~") #user home folder
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=True)
    my_observer.start()
    print("Logger started...")
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
    my_observer.join()


