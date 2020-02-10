// ********************
// Utilities 
// ********************

function post(eventLog) {
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:4444/",
        crossDomain: true,
        contentType: 'application/json',
        data: JSON.stringify(eventLog),
        success: function (responseData, status, xhr) {
            console.log("Request Successful!" + responseData);
        },
        error: function (request, status, error) {
            console.log("Request Failed!");
        }
    });
}

function getBrowser() {
    if (typeof chrome !== "undefined") {
        if (typeof browser !== "undefined") 
        return "Firefox";
        else 
        return "Chrome";
    }
}

function log(data){
    let storage = (localStorage.getItem('checkboxValue') || {}) == 'true';
}

function loggingON() {
    $("#server_status").text("Logging server running");
    $("#server_status").css("color", "greenyellow");
    chrome.browserAction.setBadgeText({ text: "ON" });
    chrome.browserAction.setBadgeBackgroundColor({
        color: "green"
    });
}

function loggingONOFF() {
    $("#server_status").text(
        `Logging server running but ${getBrowser()} logging disabled`
    );
    $("#server_status").css("color", "orange");
    chrome.browserAction.setBadgeText({ text: "OFF" });
    chrome.browserAction.setBadgeBackgroundColor({
        color: "orange"
    });
}

function loggingOFF() {
    console.log("HTTP Request Failed, server offline");
    $("#server_status").text("Logging server not running");
    chrome.browserAction.setBadgeText({ text: "OFF" });
    chrome.browserAction.setBadgeBackgroundColor({ color: "red" });
}
