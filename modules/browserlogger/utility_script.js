// ********************
// Utilities
// ********************

// detect which browser is running the extension
function getBrowser() {
    // if (typeof chrome !== "undefined") {
    //     if (typeof browser !== "undefined") return "Firefox";
    //     else return "Chrome";
    // }
    if (window.navigator.userAgent.indexOf("Firefox") > -1)
        return "Firefox";
    else if (window.navigator.userAgent.indexOf("Edge/") > -1)
        return "Edge";
    else if (window.navigator.userAgent.indexOf("Edg/") > -1)
        return "EdgeChromium";
    else if (window.navigator.userAgent.indexOf("Safari") > -1 && window.navigator.userAgent.indexOf('Chrome') == -1)
        return "Safari";
    else if (window.navigator.userAgent.indexOf("MSIE ") > -1 || !!navigator.userAgent.match(/Trident.*rv\:11\./))
        return "InternetExplorer";
    else if (window.navigator.userAgent.indexOf("Chrome") > -1)
        return "Chrome";
}

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
        timeout: 500
    })
        .done(function(data, textStatus, jqXHR) {
            console.log("Logging server running: " + jqXHR.status);
            if (
                (getBrowser() === "Chrome" && data.log_chrome) ||
                (getBrowser() === "Firefox" && data.log_firefox) ||
                (getBrowser().includes("Edge") && data.log_edge)
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
    // setExtensionBadge("ON")
    chrome.storage.local.set({ log_browser: true });
    console.log("logging enabled");
}

// server running but browser logging NOT enabled by user
function loggingONOFF() {
    $("#server_status").text(
        `Logging server running but ${getBrowser()} logging disabled`
    );
    $("#server_status").css("color", "orange");
    // setExtensionBadge("ONOFF")
    chrome.storage.local.set({ log_browser: false });
    console.log("logging disabled");
}

// server NOT running
function loggingOFF() {
    console.log("HTTP Request Failed, server offline");
    $("#server_status").text("Logging server not running");
    // setExtensionBadge("OFF")
    chrome.storage.local.set({ log_browser: false });
    console.log("logging disabled");
}

function setExtensionBadge(status) {
    chrome.browserAction.setBadgeText({ text: status });
    if (status == "ON")
        chrome.browserAction.setBadgeBackgroundColor({ color: "green" });
    else if (status == "ONOFF")
        chrome.browserAction.setBadgeBackgroundColor({ color: "orange" });
    else if (status == "OFF")
        chrome.browserAction.setBadgeBackgroundColor({ color: "red" });
}

// if user is using dark mode, change extension icon to white so it is visible in dark toolbar, used by background script
function setupIconColor(){
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        chrome.browserAction.setIcon({
            path: {
                "16": "icons/icon-16-dark.png",
                "32": "icons/icon-32-dark.png",
                "48": "icons/icon-48-dark.png",
                "128": "icons/icon-128-dark.png"
            }
        });
    }
}