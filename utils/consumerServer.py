from os import environ
from flask import Flask, request, jsonify
from csv import writer
from logging import getLogger

SERVER_ADDR = 'http://localhost:4444'

app = Flask(__name__)

# disable server log
app.logger.disabled = True
getLogger('werkzeug').disabled = True
environ['WERKZEUG_RUN_MAIN'] = 'true'


# will be set by mainLogger when program is run
filename = ""  
log_chrome = False
log_firefox = False

header = ["timestamp", "user", "category", "application", "event_type", "event_src_path", "event_dest_path", "clipboard_content", "browser_url", "eventQual", "id", "title", "description", "tab_moved_from_index", "tab_moved_to_index",
          "newZoomFactor", "oldZoomFactor", "tab_pinned", "tab_audible", "tab_muted", "window_ingognito", "file_size", "tag_category", "tag_type", "tag_name", "tag_title", "tag_value", "tag_checked", "tag_html", "tag_href", "tag_innerText", "tag_option"]
# fields = ['timeStamp', 'userID', 'targetApp', 'eventType', 'url', 'content', 'target.workbookName',
# 'target.sheetName','target.id','target.className','target.tagName', 'target.type', 'target.name',
# 'target.value', 'target.innerText', 'target.checked', 'target.href', 'target.option', 'target.title',
# 'target.innerHTML']


@app.route('/')
def index():
    return "Server working, send a post with json data."


@app.route('/', methods=['POST'])
def writeLog():
    content = request.json

    print(f"POST received with content: {content}\n")

    # check if user enabled browser logging
    if (content.get("application") == "Chrome" and not log_chrome):
        print("Chrome logging disabled by user.")
        return content
    if (content.get("application") == "Firefox" and not log_firefox):
        print("Firefox logging disabled by user.")
        return content

    # create row to write on csv. take the value of each column in header if it exists and append it to the lsit
    row = list(map(lambda col: content.get(col), header))

    with open(filename, 'a') as out_file:
        f = writer(out_file)
        f.writerow(row)

    # empty the list for next use
    row.clear()

    return content


# get server status for extension
@app.route('/serverstatus', methods=['GET'])
def getServerStatus():
    return jsonify(log_chrome=log_chrome, log_firefox=log_firefox)


# Enable CORS
# https://stackoverflow.com/a/35306327
@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    return response


def runServer():
    print("Consumer server started...")
    app.run(port=4444, debug=False, use_reloader=False)

# if __name__ == "__main__":
#     app.run(port=4444, debug=True, use_reloader=True)
