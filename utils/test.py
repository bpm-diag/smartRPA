# message
def showDialog():
    import win32ui
    import win32con
    dialog = win32ui.MessageBox("Message", "Title", win32con.MB_YESNOCANCEL)
    if dialog == win32con.IDYES:
        win32ui.MessageBox("You pressed 'Yes'")

#showDialog()

# prints all events from windows event log:
def winEventLog(): #Windows Management Instrumentation (WMI)
    import win32com.client

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




import queue
import os
import threading

# q = queue.Queue()

# def producer():
#     for i in range(100):
#         QUEUE.put(f'{threading.current_thread().name}-{i}')


# def consumer():
#     with open('out.txt', 'w+') as fp:
#         while True:
#             item = q.get()
#             if item is None:
#                 break
#             fp.write(item + os.linesep)


# worker = [threading.Thread(target=producer) for _ in range(2)]
# [i.start() for i in worker]

# master = threading.Thread(target=consumer)
# master.start()

# [i.join() for i in worker]
# writer.QUEUE.put(None)
# master.join()




from kafka import KafkaConsumer,KafkaProducer
from time import sleep

def producer():
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    producer.send('csv_logs', b'Hello, World!')
    producer.send('csv_logs', key=b'message-two', value=b'This is Kafka-Python')

    for e in range(1000):
        data = e
        producer.send('csv_logs', value=data)
        sleep(5)

import csv
from datetime import datetime

import pyperclip
from time import sleep
from datetime import datetime
from getpass import getuser  # user id
from requests import post
def logClipboard():
    recent_value = ""
    while True:
        tmp_value = pyperclip.paste()
        if tmp_value != recent_value:
            recent_value = tmp_value
            print(recent_value)
        sleep(0.2)

logClipboard()