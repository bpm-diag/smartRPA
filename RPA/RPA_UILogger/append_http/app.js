var fs = require('fs'),
  express = require('express'),
  app = express(),
  bodyParser = require('body-parser'),
  http = require('http');

var os = require("os"); 
  
app.use(bodyParser.json());

//enable cors
app.use(function (req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

var port = 8080;
http.createServer(app).listen(port);

var userID = process.argv[2];
if(userID == null) {
  console.log("Please provide your username.");
  process.exit();
}

var timestamp = new Date(Date.now());
var filename = timestamp.getTime() + ".csv";

app.get('/', function (req, res) {
  res.header('Content-type', 'text/html');
  return res.end('<h1>Hello World!</h1>');
});

app.post('/', function (req, res) {
  var output = req.body;
  output.userID = userID;
  console.log(JSON.stringify(output));
  csvParse(output,res);
});

console.log('Server running at ' + port);
console.log("Action Logger now recording");

const clipMonit = require('./clipboard/clipmonit.js');

//initialize & optionally set the interval with which to monitor the clipboard
var monitor = clipMonit(1);
var initialize = false;

//'copy. event is fired every time data is copied to the clipboard
monitor.on('copy', function (data) {
  if (initialize == true && typeof data == "string" && data !== "Invalid Content") {
    //do something with the data
	var regex = /\r\n$/g;
	eventObj={timeStamp:new Date(Date.now()),targetApp:"OS-Clipboard",eventType:"copy",content: data.replace(regex,"").replace(/\n/g,"\\n").replace(/\r/g,"\\r").replace(/\t/g,"\\t")};
	console.log(eventObj);
    csvParse(eventObj,0);
    //  console.log(output);
  } else { initialize = true; }
});

function csvParse(data,res){
  const Json2csvParser = require('json2csv').Parser;
  const fields = ['timeStamp', 'userID', 'targetApp', 'eventType', 'url', 'content', 'target.workbookName', 'target.sheetName','target.id','target.className','target.tagName', 'target.type', 'target.name', 'target.value', 'target.innerText', 'target.checked', 'target.href', 'target.option', 'target.title', 'target.innerHTML'];
  var json2csvParser;
  
  if (!fs.existsSync(filename)) {
    json2csvParser = new Json2csvParser({ fields, header: true}); //withBOM: true, 
  } else {
    json2csvParser = new Json2csvParser({ fields, header: false}); //withBOM: true
  };

  var csv = json2csvParser.parse(data);
  //csv = csv.replace(/\n$/g, "");
  //csv = csv.replace(/\"|\n/g, "");
  //csv = csv.replace(/\n/g, "");
  
  //if(csv.charCodeAt(0) === 0xFEFF)
  //	  csv = csv.substr(1);
  
  // tried UTF-8, utf, ascii, base64, hex, utf16le, ucs2
  
  //csv = csv.replace(/\"/g,"");
  
  fs.appendFile(filename, csv + os.EOL, function (err) {
    if (err) throw err;
    if (res != 0){
    res.write("http appended");
    res.end();}
  });
}

/*
function csvParse(data,res){
  const Json2csvParser = require('json2csv').Parser;
  const fields = ['timeStamp', 'userID', 'targetApp', 'eventType', 'url', 'content', 'target.id','target.class','target.tagName', 'target.type', 'target.name', 'target.value', 'target.innerText', 'target.checked', 'target.href', 'target.option'];
  var json2csvParser;
  if (!fs.existsSync('logs.csv')) {
    json2csvParser = new Json2csvParser({ fields, header: true, withBOM: true });
  } else {
    json2csvParser = new Json2csvParser({ fields, header: false, withBOM: true });
  };
  var csv = json2csvParser.parse(data);
  fs.appendFile('logs.csv', csv + "\n", function (err) {
    if (err) throw err;
    if (res != 0){
    res.write("http appended");
    res.end();}
  });
}
*/