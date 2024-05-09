from sys import path
path.append('../../')  # this way main file is visible from this file
from pynput import mouse
from utils.utils import *
from modules import consumerServer, supervision
from deprecated.sphinx import deprecated


@deprecated(version='1.1.0',
            reason="Not in use anymore.")
def logMouse():
    """
    Log mouse coordinates on click in excel
    """
    print("[Mouse] Mouse logging started...")

    def _on_click(x, y, button, pressed):
        try:
            if 'Excel' in utils.utils.getActiveWindowInfo('name') and pressed:
                coord = f"{x},{y}"
                print(f"{utils.utils.timestamp()} {utils.utils.USER} OperatingSystem click {coord}")
                screenshot = takeScreenshot()
                json_string={
                    "timestamp": utils.utils.timestamp(),
                    "user": utils.utils.USER,
                    "category": "MouseClick",
                    "application": "OperatingSystem",
                    "event_type": "click",
                    "mouse_coord": coord,
                    "screenshot": screenshot
                }
                # Get supervision feature if active, otherwise returns None value
                answer =  supervision.getResponse(json_string)
                json_string["event_relevance"] = answer
                utils.utils.session.post(consumerServer.SERVER_ADDR, json=json_string)
        except Exception:
            pass

    # Collect events until released
    with mouse.Listener(on_click=_on_click) as listener:
        listener.join()
