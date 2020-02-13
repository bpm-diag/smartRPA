from sys import path
path.append('../')  # this way main file is visible from this file
import pyperclip
from time import sleep
from datetime import datetime
from getpass import getuser  # user id
from requests import post
from utils import consumerServer
from utils import utils

# constantly monitors clipboard for changes
def logClipboard():
    recent_value = ""
    while 1:
        temp_value = pyperclip.paste()
        if temp_value != recent_value:
            recent_value = temp_value
            print(f"{datetime.now()} {getuser()} OS-Clipboard copy {recent_value}")
            post(consumerServer.SERVER_ADDR, json={
                "timestamp": utils.timestamp(),
                "user": getuser(),
                "category": "OS-Clipboard",
                "application": "Clipboard",
                "event_type": "copy",
                "clipboard_content": recent_value
            })
        sleep(0.2)

