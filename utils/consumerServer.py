from os import environ
from flask import Flask, request, jsonify
import csv
import logging

SERVER_ADDR = 'http://localhost:4444'

app = Flask(__name__)

#disable flask logging
#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)
#log.disabled = True
app.logger.disabled = True
logging.getLogger('werkzeug').disabled = True
environ['WERKZEUG_RUN_MAIN'] = 'true'

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
        f.writerow([
                content.get('datetime'),
                content.get("user"),
                content.get("category"),
                content.get("application"),
                content.get("event_type"),
                content.get("event_src_path"),
                content.get("event_dest_path"),
                ])
    #print(f"new line written in {filename}")
    return content


def runServer():
    app.run(port=4444, debug=False, use_reloader=False)

#for debug
# if __name__ == '__main__':
#         app.run(port=4444, debug=True, use_reloader=True)
