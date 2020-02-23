# ****************************** #
# CSV logging Server
# Receives events from all the threads and writes them in a single csv file
# ****************************** #

from os import environ
from flask import Flask, request, jsonify
from csv import writer
from logging import getLogger
from utils.utils import USER

# server port
PORT = 4444
SERVER_ADDR = f'http://localhost:{PORT}'

app = Flask(__name__)

# disable server log
app.logger.disabled = True
getLogger('werkzeug').disabled = True
environ['WERKZEUG_RUN_MAIN'] = 'true'

# will be set by mainLogger when program is run
filename = ""
LOG_CHROME = False
LOG_FIREFOX = False
LOG_EDGE = False
LOG_OPERA = False

# Header to use for the csv logging file, written by main when file is first created
HEADER = [
    "timestamp", "user", "category", "application", "event_type", "event_src_path", "event_dest_path",
    "clipboard_content",
    "workbook", "current_worksheet", "worksheets", "sheets", "cell_content", "cell_range", "window_size",
    "slides", "effect",
    "id", "title", "description", "browser_url", "eventQual", "tab_moved_from_index", "tab_moved_to_index",
    "newZoomFactor", "oldZoomFactor", "tab_pinned", "tab_audible", "tab_muted", "window_ingognito", "file_size",
    "tag_category", "tag_type", "tag_name", "tag_title", "tag_value", "tag_checked", "tag_html", "tag_href",
    "tag_innerText", "tag_option"
]


@app.route('/')
def index():
    return "Server working, send post with json data."


@app.route('/', methods=['POST'])
def writeLog():
    content = request.json

    print(f"\nPOST received with content: {content}\n")

    # check if user enabled browser logging
    application = content.get("application")
    if (application == "Chrome" and not LOG_CHROME) or \
            (application == "Firefox" and not LOG_FIREFOX) or \
            (application == "Edge" and not LOG_EDGE) or \
            (application == "Opera" and not LOG_OPERA):
        print(f"{application} logging disabled by user.")
        return content

    # create row to write on csv: take the value of each column in HEADER if it exists and append it to the list
    # row = list(map(lambda col: content.get(col), HEADER))
    row = list()

    for col in HEADER:
        # add current user to browser logs (because browser extension can't determine current user for security reasons)
        if not content.get("user"):
            content["user"] = USER

        # convert events to camelCase (already done by browser extension)
        # content["event_type"] = stringcase.camelcase(content["event_type"])

        row.append(content.get(col))

    with open(filename, 'a', newline='') as out_file:
        f = writer(out_file)
        f.writerow(row)

    # empty the list for next use
    row.clear()

    return content


# get server status, for browser extension
@app.route('/serverstatus', methods=['GET'])
def getServerStatus():
    return jsonify(log_chrome=LOG_CHROME, log_firefox=LOG_FIREFOX, log_edge=LOG_EDGE, log_opera=LOG_OPERA)


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
        print(f"Could not start logging server, port {PORT} is already in use.")


if __name__ == "__main__":
    app.run(port=PORT, debug=True, use_reloader=True)
