from sys import path
path.append('../')  # this way main file is visible from this file
from pynput import mouse
from utils.utils import timestamp, USER, session, getActiveWindowInfo
from utils import consumerServer


def logMouse():
    print("[Mouse] Mouse logging started...")

    def _on_click(x, y, button, pressed):
        try:
            if 'Excel' in getActiveWindowInfo('name') and pressed:
                coord = f"{x},{y}"
                print(f"{timestamp()} {USER} OperatingSystem click {coord}")
                session.post(consumerServer.SERVER_ADDR, json={
                    "timestamp": timestamp(),
                    "user": USER,
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
