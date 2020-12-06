from sys import path
path.append('../../')  # this way main file is visible from this file
from pynput import mouse
import utils.utils
from modules import consumerServer
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
                utils.utils.session.post(consumerServer.SERVER_ADDR, json={
                    "timestamp": utils.utils.timestamp(),
                    "user": utils.utils.USER,
                    "category": "MouseClick",
                    "application": "OperatingSystem",
                    "event_type": "click",
                    "mouse_coord": coord
                })
        except Exception:
            pass

    # Collect events until released
    with mouse.Listener(on_click=_on_click) as listener:
        listener.join()
