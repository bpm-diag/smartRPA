from flask import Flask, request, jsonify
from datetime import datetime
import csv
import json

SERVER_ADDR = 'http://localhost:4444'

app = Flask(__name__)
app.logger.disabled = True
filename = "" #will be set by mainLogger when program is run

@app.route('/')
def index():
    return "Server working, send a post with json data."

# https://stackoverflow.com/a/35614301
@app.route('/', methods=['POST'])
def writeLog():
    content = request.json
    #fields = ['timeStamp', 'userID', 'targetApp', 'eventType', 'url', 'content', 'target.workbookName', 'target.sheetName','target.id','target.className','target.tagName', 'target.type', 'target.name', 'target.value', 'target.innerText', 'target.checked', 'target.href', 'target.option', 'target.title', 'target.innerHTML']
    with open(filename, 'a') as out_file:
        f = csv.writer(out_file)
        # f.writerow(["datetime", "user", "application","event_type","event_src_path","event_dest_path"])
        f.writerow([
                content.get('datetime'),
                content.get("user"),
                content.get("application"),
                content.get("event_type"),
                content.get("event_src_path"),
                content.get("event_dest_path"),
                ])
    return content


def runServer():
    app.run(port=4444, debug=False, use_reloader=False)

#for debug
# if __name__ == '__main__':
#         app.run(port=4444, debug=True, use_reloader=True)
