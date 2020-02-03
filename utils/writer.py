from queue import Queue
from threading import Thread
import csv 
from datetime import datetime 

QUEUE = Queue(1)

def safeWriter():
    class SafeWriter:
        def __init__(self, *args):
            self.filewriter = open(*args)
            self.queue = Queue()
            self.finished = False
            Thread(name = "SafeWriter", target=self.internal_writer).start()  

        def write(self, data):
            self.queue.put(data)

        def internal_writer(self):
            while not self.finished:
                try:
                    data = self.queue.get(True, 1)
                except Empty:
                    continue 
                self.filewriter.write(data)
                self.queue.task_done()

        def close(self):
            self.queue.join()
            self.finished = True
            self.filewriter.close()

    w = SafeWriter("filename", "w")
    w.write("can be used among multiple threads")
    w.close() #it is really important to close or the program would not end 


#https://stackoverflow.com/a/58307973
def syncThread(queue):
    dataFromThread1 = None 
    # filename = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")
    filename = "test.csv"
    with open(filename, 'a+', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL) 
        while True:  # Here - a sync Event May be used to get out of the Loop and Join Thread Nicely
            try:
                dataFromThread1 = queue.get(block=False)
            except Exception as ex:
                pass
            if dataFromThread1 is not None:
                writer.writerow(list(dataFromThread1))  # Here data will be written Into File.
                csvfile.flush()  # Important

def startWriter():
    tSync = Thread(target=syncThread, args=(QUEUE))
    tSync.daemon = True
    tSync.start()