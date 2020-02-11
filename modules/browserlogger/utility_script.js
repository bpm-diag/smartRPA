// ********************
// Utilities
// ********************

// post request to server sending logging data
function post(eventLog) {
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:4444/",
        crossDomain: true,
        contentType: "application/json",
        data: JSON.stringify(eventLog),
        success: function(responseData, status, xhr) {
            console.log("Log sent to server "); // + JSON.stringify(responseData));
        },
        error: function(request, status, error) {
            console.log("Request Failed " + error);
        }
    });
}

// detect which browser is running the extension
function getBrowser() {
    if (typeof chrome !== "undefined") {
        if (typeof browser !== "undefined") return "Firefox";
        else return "Chrome";
    }
}

// log data only if server is running
// https://developer.chrome.com/apps/storage
function logAndPost(eventLog) {
    chrome.storage.local.get(["log_browser"], result => {
        let log_browser = result.log_browser || false;
        if (log_browser) {
            console.log(eventLog);
            post(eventLog);
        }
    });
}

// Used by content_script to pass data to background_script to make post request,
// It is not possible anymore to do it directly from content_script due to security reasons
// https://www.chromium.org/Home/chromium-security/extension-content-script-fetches
function sendToBackgroundForPost(eventLog) {
    chrome.runtime.sendMessage({
        contentScriptQuery: "postData",
        data: eventLog
    });
}

// check if server is online and update extension status
// used by extension script.js when clicking the icon, background script on extension startup and on installed
function checkServerStatus() {
    $.ajax({
        url: "http://127.0.0.1:4444/serverstatus",
        type: "GET",
        timeout: 1000
    })
        .done(function(data, textStatus, jqXHR) {
            console.log("Logging server running: " + jqXHR.status);
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
            console.log("Logging server off");
            // server NOT running
            loggingOFF();
        })
        .always(function() {
            /* ... */
        });
}

// server running and browser logging enabled by user
function loggingON() {
    // set extension page text and color
    $("#server_status").text("Logging server running");
    $("#server_status").css("color", "greenyellow");
    // set extension badge
    // chrome.browserAction.setBadgeText({ text: "ON" });
    // chrome.browserAction.setBadgeBackgroundColor({ color: "green" });
    // save logging status in localstorage
    chrome.storage.local.set({ log_browser: true });
    console.log("logging enabled");
}

// server running but browser logging NOT enabled by user
function loggingONOFF() {
    $("#server_status").text(
        `Logging server running but ${getBrowser()} logging disabled`
    );
    $("#server_status").css("color", "orange");
    // chrome.browserAction.setBadgeText({ text: "OFF" });
    // chrome.browserAction.setBadgeBackgroundColor({ color: "orange" });
    chrome.storage.local.set({ log_browser: false });
    console.log("logging disabled");
}

// server NOT running
function loggingOFF() {
    console.log("HTTP Request Failed, server offline");
    $("#server_status").text("Logging server not running");
    // chrome.browserAction.setBadgeText({ text: "OFF" });
    // chrome.browserAction.setBadgeBackgroundColor({ color: "red" });
    chrome.storage.local.set({ log_browser: false });
    console.log("logging disabled");
}
