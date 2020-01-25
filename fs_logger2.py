# https://stackoverflow.com/questions/18599339/python-watchdog-monitoring-file-for-changes

import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):

    def on_modified(self, event):
        print(f'event type: {event.event_type}  path : {event.src_path}')

    def on_created(self, event):
        print(f"hey, {event.src_path} has been created!")

    def on_deleted(self, event):
        print(f"what the f**k! Someone deleted {event.src_path}!")

    def on_moved(self, event):
        print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")

if __name__ == "__main__":
    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True
    #my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler = MyHandler()

    path = "."
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)

    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
    my_observer.join()


