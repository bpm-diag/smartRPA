# ****************************** #
# CSV logging Server
# Receives events from all the threads and writes them in a single csv file
# ****************************** #

from os import environ
from flask import Flask, request, jsonify
import csv
from logging import getLogger
import utils.config
import utils.utils
# import utils.GUI

# server port
PORT = 4444
SERVER_ADDR = f'http://localhost:{PORT}'

# The following variables are set by main during execution
log_filepath = str()
log_chrome = False
log_firefox = False
log_edge = False
log_opera = False

app = Flask(__name__)

# disable server log
app.logger.disabled = True
getLogger('werkzeug').disabled = True
environ['WERKZEUG_RUN_MAIN'] = 'true'


# Header to use for the csv logging file, written by main when file is first created
HEADER = [
    "timestamp", "user", "category", "application", "event_type", "event_src_path", "event_dest_path",
    "clipboard_content", "mouse_coord",
    "workbook", "current_worksheet", "worksheets", "sheets", "cell_content", "cell_range", "cell_range_number", "window_size",
    "slides", "effect", "hotkey",
    "id", "title", "description", "browser_url", "eventQual", "tab_moved_from_index", "tab_moved_to_index",
    "newZoomFactor", "oldZoomFactor", "tab_pinned", "tab_audible", "tab_muted", "window_ingognito", "file_size",
    "tag_category", "tag_type", "tag_name", "tag_title", "tag_value", "tag_checked", "tag_html", "tag_href",
    "tag_innerText", "tag_option", "tag_attributes", "xpath", "xpath_full"
]


@app.route('/')
def index():
    return "Server working, send post with json data."


@app.route('/', methods=['POST'])
def writeLog():
    """
    route where json event is received and processed.

    JSON event includes metadata about the event, such as the timestamp, category, application, concept:name
    and other information depending on the event type.

    All this data is appended to the csv event log.
    """
    content = request.json

    print(f"\nPOST received with content: {content}\n")

    # check if user enabled browser logging
    application = content.get("application")
    if (application == "Chrome" and not log_chrome) or \
            (application == "Firefox" and not log_firefox) or \
            (application == "Edge" and not log_edge) or \
            (application == "Opera" and not log_opera):
        print(f"{application} logging disabled by user.")
        return content

    # create row to write on csv: take the value of each column in HEADER if it exists and append it to the list
    # row = list(map(lambda col: content.get(col), HEADER))
    row = list()

    for col in HEADER:
        # add current user to browser logs (because browser extension can't determine current user)
        if not content.get("user"):
            content["user"] = utils.utils.USER
        if content.get("cell_content"):
            content["cell_content"] = content["cell_content"].strip('"')

        # convert events to camelCase (already done by browser extension)
        # content["event_type"] = stringcase.camelcase(content["event_type"])

        row.append(content.get(col))

    with open(log_filepath, 'a', newline='', encoding='utf-8-sig') as out_file:
        f = csv.writer(out_file)
        f.writerow(row)

    # empty the list for next use
    row.clear()

    return content


@app.route('/serverstatus', methods=['GET'])
def getServerStatus():
    """
    Get server status for browser extension.

    Returns status of each browser checkbox in GUI.

    :return: true if browser checkbox in GUI is active
    """
    return jsonify(log_chrome=log_chrome,
                   log_firefox=log_firefox,
                   log_edge=log_edge,
                   log_opera=log_opera)



@app.after_request
def add_headers(response):
    """
    Enable CORS, for browser extension

    https://stackoverflow.com/a/35306327
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response


def runServer(status_queue):
    """
    start server thread, executed by mainLogger

    :param status_queue: queue to print messages in GUI
    """
    if not utils.utils.isPortInUse(PORT):
        status_queue.put("[Server] Logging server started")
        app.run(port=PORT, debug=False, use_reloader=False)
    else:
        status_queue.put(f"[Server] Could not start logging server because port {PORT} is already in use.")


if __name__ == "__main__":
    app.run(port=PORT, debug=True, use_reloader=True)
