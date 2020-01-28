// communicate with background script via runtime.Port object using runtime.connect API.
var myPort = chrome.runtime.connect({ name: "port-from-cs" });

//list of event listeners

//copy/paste
document.body.oncopy = document.body.oncut = copy;
document.body.onpaste = paste;

// Mouse Events
document.body.onclick = mouseClick;
// Not in use
// document.body.onmouseover = moveMouse; 
// document.body.onmouseout= moveMouse;

//missing:
// highlight Text - doubleclick / click & drag
// dropdown selection

// Keyboard inputs
//document.body.onkeypress = keyPress;

//document.body.oninput = onInput; // works on every incremental change
document.body.onchange = onChange; // works at the end of change

// same as onclick but for keyboard tabbing
//document.body.onfocus = onSelect;

function paste(e) {
    var eventObj = { timeStamp: new Date(Date.now()) };
    var evt = window.event || e;
    eventObj.eventType = "paste";
	eventObj.url = document.URL;
    var target = buildTarget(evt);
	var regex = /\r\n$/g;
	eventObj.content = evt.clipboardData.getData('text/plain').replace(regex, '').replace(/\n/g,"\\n").replace(/\r/g,"\\r").replace(/\t/g,"\\t");
	eventObj.target = target;
    console.log("eventObj: " + JSON.stringify(eventObj));
    myPort.postMessage(eventObj);
}

function copy(e) {
    var eventObj = { timeStamp: new Date(Date.now()) };
    var evt = window.event || e;
    eventObj.eventType = evt.type;
	eventObj.url = document.URL;
    var target = buildTarget(evt);
    var copydata = document.getSelection();
    console.log("copypaste: " + copydata);
	var regex = /\r\n$/g;
	eventObj.content = copydata.toString().replace(regex, '').replace(/\n/g,"\\n").replace(/\r/g,"\\r").replace(/\t/g,"\\t");
	eventObj.target = target;
    myPort.postMessage(eventObj);
}

function keyPress(e) {
    var eventObj = { timeStamp: new Date(Date.now()) };
    eventObj.eventType = "pressKey";
	eventObj.url = document.URL;
    eventObj.target = targetNaming(e.target);
	console.log(JSON.stringify(eventObj));
}

// onChange procs every time there an element has finished changed
function onChange(e) {
    var eventObj = { timeStamp: new Date(Date.now()) };
    var evt = window.event || e;
    eventObj.eventType = "editField";
	eventObj.url = document.URL;
    var target = buildTarget(evt);
    eventObj.target = target;
	console.log("eventObj: " + JSON.stringify(eventObj));
    myPort.postMessage(eventObj);
}

// onInput procs every time there is a change to an element's value (procs for each key stroke)
function onInput(e) {
    var eventObj = { timeStamp: new Date(Date.now()) };
    var evt = window.event || e;
    eventObj.eventType = "fieldInput";
	eventObj.url = document.URL;
    var target = buildTarget(evt);
    eventObj.target = target;
    myPort.postMessage(eventObj);
}

function onSelect(e) {
    // var eventObj = {timeStamp:Date.now()};
    // var evt = window.event || e;
    // eventObj.eventType="Selection";
    // var target = buildTarget(evt);
    // eventObj.target = target;
    // console.log("eventObj: "+JSON.stringify(eventObj));
    console.log("onSelectFired");
}

function mouseClick(e) {
    //alert('test');
    console.log("MouseClick")
    var eventObj = { timeStamp: new Date(Date.now()), eventType: "mouseClick", url: document.URL };
    var evt = window.event || e;
    var dt1 = getDataT1Class(evt);
    console.log("DT1 OBJ: " + JSON.stringify(dt1));
    // if (window.location.href.indexOf("sharepoint") > -1) {
    //     return logOffice(eventObj)
    // }
    if (dt1 != null && dt1 != undefined && Object.keys(dt1).length > 0 && dt1 != {}) {
        // specific for student 1 application
        console.log(dt1);
        if (dt1.type != null || dt1.type != undefined) {
            if (dt1.type.toLowerCase() == "input" || dt1.type.toLowerCase() == "textarea") {
                if (dt1.type.toLowerCase() == "checkbox") {
                    eventObj["eventType"] = "clickCheckbox";
                } else {
                    eventObj["eventType"] = "clickTextField";
					console.log(JSON.stringify(eventObj));
                }
            } else if (dt1.type.toLowerCase() == "button") {
                eventObj["eventType"] = "clickButton";
            } else if (dt1.type.toLowerCase() == "select") {
                eventObj["eventType"] = "selectOptions";
            } else {
                eventObj["eventType"] = "mouseClick";
            }
        } else {
            eventObj["eventType"] = "mouseClick";
        }
        console.log("Event Obj is : " + JSON.stringify(eventObj));
        eventObj.target = dt1;

        // console.log(dt1);
        myPort.postMessage(eventObj);
    } else {
        var target = buildTarget(evt);
        eventObj.target = target;
        console.log("")
        console.log(target)
        if (target.tagName == "INPUT" || target.tagName == "BUTTON" || target.tagName == "A" || target.type == "submit" || target.href != null || target.tagName == "TEXTAREA") {
            if (target.tagName == "INPUT" || target.tagName == "TEXTAREA") {
                if (target.type == "checkbox")
                    eventObj["eventType"] = "clickCheckbox";
                else if (target.type == "submit")
		    eventObj["eventType"] = "clickButton";
		else
		    eventObj["eventType"] = "clickTextField";
                console.log(JSON.stringify(eventObj));
            } else if (target.tagName == "BUTTON") {
                eventObj["eventType"] = "clickButton";
            } else if (target.href != null) {
                eventObj["eventType"] = "clickLink";
            } else if (target.tagName == "SELECT") {
                eventObj["eventType"] = "selectOptions";
            } else {
                eventObj["eventType"] = "mouseClick";
            }
            myPort.postMessage(eventObj); // need to change this to make it generic
        }
    }
    console.log("eventObj: " + JSON.stringify(eventObj));
}

function logOffice(eventObj){
    alert("esplodo")
}

// build the target object
function buildTarget(mye) {
    var target = mye.target;
    var targetObj = {};
    
    if(target.tagName != "INPUT" && target.tagName != "BUTTON" && target.tagName != "A" && target.href == null)
        target = getParentElement(target);
	
    if (target.id != null && target.id != undefined && target.id != "") {
        targetObj.id = target.id;
    }
    if (target.tagName != null && target.tagName != undefined && target.tagName != "") {
        var tagName = target.tagName;
        targetObj.tagName = tagName;
        var username = "";
        if (target.className != null && target.className != undefined && target.className != "") {
            targetObj.className = target.className;
        }
        if (target.type != null && target.type != undefined && target.type != "") {
            targetObj.type = target.type;
        }
        if (target.name != null && target.name != undefined && target.name != "") {
            targetObj.name = target.name;
            username = target.name.toString();
            username = username.replace(/\s/g, "");
        }
		if (target.title != null && target.title != undefined && target.title != "") {
			targetObj.title = target.title;
		}
		if (target.innerHTML != null && target.innerHTML != undefined && target.innerHTML != ""){
			targetObj.innerHTML = target.innerHTML.replace(/\n/g,"\\n").replace(/\r/g,"\\r").replace(/\t/g,"\\t");
		}
        if (target.value != null && target.value != undefined) {
            // do not store passwords
            if (target.type.toLowerCase() == "password") {
                targetObj.value = "User Password";
            }
            //do not store user names
            else if (username.toLowerCase() == "username" || username.toLowerCase() == "user") {
                targetObj.value = "UserName"
            }
            else {
                targetObj.value = target.value.replace(/\n/g,"\\n").replace(/\r/g,"\\r").replace(/\t/g,"\\t");
            }
        }
        if (target.type == "checkbox" || target.type == "radio") {
            if (target.checked != null && target.checked != undefined) {
                targetObj.checked = target.checked;
            }
        }
        //Hrefs
	if (target.href != null && target.href != undefined && target.href != "") {
            targetObj.href = target.getAttribute("href");
        } else {
            var href = getParentLink(target);
            if (href != "") { // get the ultimate parent href if exists
                targetObj.href = href;
            }
        }
        // this section might be site specific, needs further testing
        if (target.innerText != null && target.innerText != undefined && target.innerText != "")
            targetObj.innerText = target.innerText.replace(/\n/g,"\\n").replace(/\r/g,"\\r").replace(/\t/g,"\\t");
    }
    if (target.option != null && target.option != undefined && target.option != "") {
        targetObj.option = target.option;
    }
	//targetObj.documentTitle = document.title;
	
    console.log("targetObj: "+JSON.stringify(targetObj));
    return targetObj;
}

function getParentElement(target){
	var parentElement = target;
	while(parentElement.tagName != "BODY"){
		if(parentElement.tagName == "BUTTON" || parentElement.tagName == "A" || (parentElement.href != null && parentElement.href != undefined && parentElement.href != ""))
			return parentElement;
		else
			parentElement = parentElement.parentNode;
	}
	return null;
}

function getParentLink(target) {
    var href = "";
    var test = true;
    while (test) {
        target = target.parentNode;
        if (target.href != null && target.href != undefined && target.href != "") {
            href = target.getAttribute("href");
            test = false;
        }
        if (target.tagName == "BODY") {
            test = false;
        }
    }
    return href;
}

function getChildrenElemements(target){
	var childrenElements = target.childNodes;
	return childrenElements;
}

function getDataT1Class(mye) {
    var test = true;
    var target = mye.target;
    var dt1 = {};
    var firstTagName = target.tagName;
    while (test) {
        var dataT1 = {};
        dataT1.ctrl = target.getAttribute("data-t1-control");
        dataT1.class = target.getAttribute("class");
        dataT1.type = target.getAttribute("data-t1-control-type");
        dataT1.id = target.getAttribute("id");
        dataT1.title = target.getAttribute("title");

        if (dataT1.ctrl != undefined && dataT1.ctrl != null && dataT1.ctrl != {}) {
            // console.log(target.getAttribute("data-t1-control-type"));
            var dt1ctrl = JSON.parse(dataT1.ctrl);
            dt1.class = dataT1.class;
            if (target.innerText != null && target.innerText != undefined && target.innerText != "") {
                dt1.innerText = target.innerText.replace(/\n/g,"\\n").replace(/\r/g,"\\r").replace(/\t/g,"\\t");
            }
            // test = false;
            if (dt1ctrl.LabelText != undefined) {
                dt1.innerText = dt1ctrl.LabelText.replace(/\n/g,"\\n").replace(/\r/g,"\\r").replace(/\t/g,"\\t");
            }
            if (dataT1.title != null && dataT1.title != undefined) {
                dt1.name = dataT1.title;
            }
            if (firstTagName != "" || firstTagName != null || firstTagName != undefined) {
                if (dataT1.type != undefined && dataT1.type != null) {
                    if (dataT1.type.toLowerCase() == "checkbox") {
                        //console.log("checkbox found");
                        dt1.type = "checkbox";
                        dataT1.class.includes(" checked") ? dt1.checked = true : dt1.checked = false;
                    } else {
                        dt1.type = firstTagName;
                    }
                }
            }
            test = false;
        } else {
            target = target.parentNode;
            if (firstTagName != "BUTTON" && firstTagName != "INPUT" && firstTagName != "TEXTAREA" && firstTagName != "CHECKBOX"
                && firstTagName != "SELECT") {
                firstTagName = target.tagName;
            }
            if (target.tagName == "BODY") {
                test = false;
            }

        }
    }

    return dt1;
}

