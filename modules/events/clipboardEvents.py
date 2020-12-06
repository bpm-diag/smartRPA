# ****************************** #
# CSV logging Server
# Receives events from all the threads and writes them in a single csv file
# ****************************** #

from sys import path
path.append('../../')  # this way main file is visible from this file
import pyperclip
from time import sleep
from modules import consumerServer
from utils.utils import *


def logClipboard():
    """
    Constantly monitors clipboard for changes.
    Detects 'copy' event. 'paste' event is detected by systemEvents.handleHotkey

    :return: JSON containing clipboard event
    """
    print("[Clipboard] Clipboard logging started...")
    recent_value = pyperclip.paste()
    while 1:
        temp_value = pyperclip.paste()
        if temp_value != recent_value:
            recent_value = temp_value
            print(f"{timestamp()} {USER} Clipboard copy {recent_value}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "Clipboard",
                "application": "Clipboard",
                "event_type": "copy",
                "clipboard_content": recent_value
            })
        sleep(0.2)

