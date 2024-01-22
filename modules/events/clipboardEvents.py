# ****************************** #
# CSV logging Server
# Receives events from all the threads and writes them in a single csv file
# ****************************** #

from sys import path
path.append('../../')  # this way main file is visible from this file
import pyperclip
from time import sleep
from modules import consumerServer, supervision
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
            screenshot = takeScreenshot()
            recent_value = temp_value
            print(f"{timestamp()} {USER} Clipboard copy {recent_value}")
            json_string={
                "timestamp": timestamp(),
                "user": USER,
                "category": "Clipboard",
                "application": "Clipboard",
                "event_type": "copy",
                "clipboard_content": recent_value,
                "screenshot": screenshot
            }
            # Get supervision feature if active, otherwise returns None value
            answer =  supervision.getResponse(json_string)
            json_string["event_relevance"] = answer

            # Post result to the consumer server, 
            # json=json_string is necessary, if only json_string the result at the server would be "None"
            session.post(consumerServer.SERVER_ADDR, json=json_string) 
        sleep(0.2)

