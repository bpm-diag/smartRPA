// ********************
// Utilities
// ********************

function post(eventLog) {
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:4444/",
        crossDomain: true,
        contentType: "application/json",
        data: JSON.stringify(eventLog),
        success: function(responseData, status, xhr) {
            console.log("Request Successful! ") // + JSON.stringify(responseData));
        },
        error: function(request, status, error) {
            console.log("Request Failed " + error);
        }
    });
}

function getBrowser() {
    if (typeof chrome !== "undefined") {
        if (typeof browser !== "undefined") return "Firefox";
        else return "Chrome";
    }
}

// function log(eventLog) {
//     let storage = (localStorage.getItem("log_browser") || {}) == "true";
// }

function sendToBackgroundForPost(eventLog) {
    chrome.runtime.sendMessage({
        contentScriptQuery: "postData",
        data: eventLog
    });
}

function checkServerStatus(){
    $.ajax({
        url: "http://127.0.0.1:4444/serverstatus",
        type: "GET",
        timeout: 1000
    })
        .done(function(data, textStatus, jqXHR) {
            console.log("HTTP Request Succeeded: " + jqXHR.status);
            if (
                (getBrowser() == "Chrome" && data.log_chrome) ||
                (getBrowser() == "Firefox" && data.log_firefox)
            ) {
                // server running and browser logging enabled by user
                loggingON();
            } else {
                // server running but browser logging NOT enabled by user
                loggingONOFF();
            }
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            // server NOT running
            loggingOFF();
        })
        .always(function() {
            /* ... */
        });
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
