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

# server port
PORT = 4444
SERVER_ADDR = f'http://localhost:{PORT}'

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
    "slides", "effect",
    "id", "title", "description", "browser_url", "eventQual", "tab_moved_from_index", "tab_moved_to_index",
    "newZoomFactor", "oldZoomFactor", "tab_pinned", "tab_audible", "tab_muted", "window_ingognito", "file_size",
    "tag_category", "tag_type", "tag_name", "tag_title", "tag_value", "tag_checked", "tag_html", "tag_href",
    "tag_innerText", "tag_option", "xpath"
]


@app.route('/')
def index():
    return "Server working, send post with json data."


@app.route('/', methods=['POST'])
def writeLog():
    content = request.json

    print(f"\nPOST received with content: {content}\n")

    # check if user enabled browser logging
    config = utils.config.MyConfig.get_instance()
    application = content.get("application")
    if (application == "Chrome" and not config.log_chrome) or \
            (application == "Firefox" and not config.log_firefox) or \
            (application == "Edge" and not config.log_edge) or \
            (application == "Opera" and not config.log_opera):
        print(f"{application} logging disabled by user.")
        return content

    # create row to write on csv: take the value of each column in HEADER if it exists and append it to the list
    # row = list(map(lambda col: content.get(col), HEADER))
    row = list()

    for col in HEADER:
        # add current user to browser logs (because browser extension can't determine current user)
        if not content.get("user"):
            content["user"] = utils.utils.USER

        # convert events to camelCase (already done by browser extension)
        # content["event_type"] = stringcase.camelcase(content["event_type"])

        row.append(content.get(col))

    with open(utils.config.MyConfig.get_instance().log_filepath, 'a', newline='') as out_file:
        f = csv.writer(out_file)
        f.writerow(row)

    # empty the list for next use
    row.clear()

    return content


# get server status, for browser extension
@app.route('/serverstatus', methods=['GET'])
def getServerStatus():
    config = utils.config.MyConfig.get_instance()
    return jsonify(log_chrome=config.log_chrome,
                   log_firefox=config.log_firefox,
                   log_edge=config.log_edge,
                   log_opera=config.log_opera)


# Enable CORS, for browser extension
# https://stackoverflow.com/a/35306327
@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response


# check if port is available to start server
def isPortInUse(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


# start server thread, run by mainLogger
def runServer():
    if not isPortInUse(PORT):
        print("[Server] Logging server started...")
        app.run(port=PORT, debug=False, use_reloader=False)
    else:
        print(f"[Server] Could not start logging server, port {PORT} is already in use.")


if __name__ == "__main__":
    app.run(port=PORT, debug=True, use_reloader=True)
