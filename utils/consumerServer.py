from os import environ
from flask import Flask, request
from csv import writer
from logging import getLogger

SERVER_ADDR = 'http://localhost:4444'

app = Flask(__name__)

# disable server log
app.logger.disabled = True
getLogger('werkzeug').disabled = True
environ['WERKZEUG_RUN_MAIN'] = 'true'

filename = ""  # will be set by mainLogger when program is run

@app.route('/')
def index():
    return "Server working, send a post with json data."


#  https://stackoverflow.com/a/35614301
@app.route('/', methods=['POST'])
def writeLog():
    content = request.json
    # fields = ['timeStamp', 'userID', 'targetApp', 'eventType', 'url', 'content', 'target.workbookName',
    # 'target.sheetName','target.id','target.className','target.tagName', 'target.type', 'target.name',
    # 'target.value', 'target.innerText', 'target.checked', 'target.href', 'target.option', 'target.title',
    # 'target.innerHTML']
    print(f"POST received with content: {content}\n")
    with open(filename, 'a') as out_file:
        f = writer(out_file)
        f.writerow([
            content.get("timestamp"),
            content.get("user"),
            content.get("category"),
            content.get("application"),
            content.get("event_type"),
            content.get("event_src_path"),
            content.get("event_dest_path"),
            content.get("clipboard_content"),
            content.get("browser_url"),
            content.get("eventQual"),
            content.get("tab_id"),
            content.get("title"),
            content.get("tab_moved_from_index"),
            content.get("tab_moved_to_index"),
            content.get("newZoomFactor"),
            content.get("oldZoomFactor"),
            content.get("pinned"),
            content.get("audible"),
            content.get("muted"),
            content.get("window_ingognito"),
        ])
    # print(f"new line written in {filename}")
    return content

# Enable CORS
# https://stackoverflow.com/a/35306327
@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response

def runServer():
    print("Consumer server started...")
    app.run(port=4444, debug=False, use_reloader=False)

# if __name__ == "__main__":
#     app.run(port=4444, debug=True, use_reloader=True)