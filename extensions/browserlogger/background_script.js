// Chrome APIs
// https://developer.chrome.com/extensions/api_index

// ********************
// Bookmarks events
// https://developer.chrome.com/extensions/bookmarks
// ********************

// Fired when a bookmark or folder is created.
// https://developer.chrome.com/extensions/windows#event-onCreated
chrome.bookmarks.onCreated.addListener((id, bookmark) => {
    // console.log("Bookmark created");
    // https://developer.chrome.com/extensions/bookmarks#type-BookmarkTreeNode
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "newBookmark",
        browser_url: bookmark.url,
        title: bookmark.title
    };

    logAndPost(eventLog);
});

// Fired when a bookmark or folder is removed.
// https://developer.chrome.com/extensions/windows#event-onRemoved
chrome.bookmarks.onRemoved.addListener((id, removeInfo) => {
    // console.log("Bookmark removed");
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "removeBookmark",
        browser_url: removeInfo.node.url
    };

    logAndPost(eventLog);
});

// Fired when a bookmark or folder is changed.
// https://developer.chrome.com/extensions/windows#event-onChanged
chrome.bookmarks.onChanged.addListener((id, changeInfo) => {
    // console.log("Bookmark changed");
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "modifyBookmark",
        browser_url: changeInfo.url,
        title: changeInfo.title
    };

    logAndPost(eventLog);
});

// Fired when a bookmark or folder is moved.
// https://developer.chrome.com/extensions/windows#event-onMoved
chrome.bookmarks.onMoved.addListener((id, moveInfo) => {
    // console.log("Bookmark moved");
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "moveBookmark"
    };

    logAndPost(eventLog);
});

// // Fired when a bookmark or folder is moved.
// // https://developer.chrome.com/extensions/windows#event-onMoved
// chrome.bookmarks.onImportBegan.addListener( () => {
//     console.log("Bookmark imported");
//     let eventLog = {
//         timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
//         category: "Browser",
//         application: getBrowser(),
//         event_type: "importBookmark",
//     };
//     console.log(eventLog);
//     post(eventLog);
// });

// ********************
// Download events
// https://developer.chrome.com/extensions/downloads#event-onCreated
// ********************

// This event fires with the DownloadItem object when a download begins.
// https://developer.chrome.com/extensions/downloads#event-onCreated
chrome.downloads.onCreated.addListener(downloadItem => {
    // console.log("Download started");
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "startDownload",
        browser_url: downloadItem.url,
        title: downloadItem.filename,
        file_size: downloadItem.totalBytes
    };

    logAndPost(eventLog);
});

// Fires with the downloadId when a download is erased from history.
// https://developer.chrome.com/extensions/downloads#event-onErased
chrome.downloads.onErased.addListener(downloadId => {
    // console.log("Download erased");
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "erasedDownload",
        id: downloadId
    };

    logAndPost(eventLog);
});

// ********************
// History events (too much spam)
// https://developer.chrome.com/extensions/history#event-onVisited
// ********************

// chrome.history.onVisited.addListener( (result) => {
//     console.log("History changed");
//     let eventLog = {
//         timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
//         category: "Browser",
//         application: getBrowser(),
//         event_type: "changeHistory",
//         browser_url: result.url,
//     };
//     console.log(eventLog);
//     post(eventLog);
// });

// ********************
// Extension Management events
// https://developer.chrome.com/extensions/management
// ********************

// Fired when an app or extension has been installed.
// https://developer.chrome.com/extensions/management#event-onInstalled
chrome.management.onInstalled.addListener(info => {
    // console.log("Extension installed");
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "installBrowserExtension",
        id: info.id,
        title: info.name,
        description: info.description
    };

    logAndPost(eventLog);
});

// Fired when an app or extension has been uninstalled.
// https://developer.chrome.com/extensions/management#event-onUninstalled
chrome.management.onUninstalled.addListener(id => {
    // console.log("Extension uninstalled");
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "uninstallBrowserExtension",
        id: id
    };

    logAndPost(eventLog);
});

// Fired when an app or extension has been enabled.
// https://developer.chrome.com/extensions/management#event-onEnabled
chrome.management.onEnabled.addListener(info => {
    // console.log("Extension enabled");
    console.log(info);
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "enableBrowserExtension",
        id: info.id,
        title: info.name,
        description: info.description
    };

    logAndPost(eventLog);
});

// Fired when an app or extension has been disabled.
// https://developer.chrome.com/extensions/management#event-onDisabled
chrome.management.onDisabled.addListener(info => {
    // console.log("Extension disabled");
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "disableBrowserExtension",
        id: info.id,
        title: info.name,
        description: info.description
    };

    logAndPost(eventLog);
});

// ********************
// Notification events
// https://developer.chrome.com/extensions/management
// ********************

// The notification closed, either by the system or by user action.
// https://developer.chrome.com/extensions/notifications#event-onClosed
chrome.notifications.onClosed.addListener((notificationId, byUser) => {
    // console.log("Notification closed");
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "closedNotification",
        id: notificationId
    };

    logAndPost(eventLog);
});

// The user clicked in a non-button area of the notification.
// https://developer.chrome.com/extensions/notifications#event-onClosed
chrome.notifications.onClicked.addListener(notificationId => {
    // console.log("Notification clicked");
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "clickedNotification",
        id: notificationId
    };

    logAndPost(eventLog);
});

// ********************
// Tabs events
// https://developer.chrome.com/extensions/tabs
// ********************

// Every new tab is added to this map so when a tab is closed I can get informations about it
let previousTabs = new Map();

// Fired when a tab is created.
// https://developer.chrome.com/extensions/tabs#event-onCreated
chrome.tabs.onCreated.addListener(tab => {
    // console.log("Tab created");
    try {
        buildAndSendEventLog("newTab", tab);
    } catch (error) {
        console.log(error.message);
    }
});

// Fired when a tab is moved within a window
// https://developer.chrome.com/extensions/tabs#event-onMoved
chrome.tabs.onMoved.addListener((tabId, moveInfo) => {
    // console.log("Tab moved");
    chrome.tabs.get(tabId, tab => {
        try {
            buildAndSendEventLog("moveTab", tab, moveInfo);
        } catch (error) {
            console.log(error.message);
        }
    });
});

// Fired when a tab is attached to a window; for example, because it was moved between windows.
// https://developer.chrome.com/extensions/tabs#event-onAttached
chrome.tabs.onAttached.addListener((tabId, attachInfo) => {
    // console.log("Tab attached");
    chrome.tabs.get(tabId, tab => {
        try {
            buildAndSendEventLog("attachTab", tab, attachInfo);
        } catch (error) {
            console.log(error.message);
        }
    });
});

// Fired when a tab is detached from a window; for example, because it was moved between windows.
// https://developer.chrome.com/extensions/tabs#event-onDetached
chrome.tabs.onDetached.addListener((tabId, detachInfo) => {
    // console.log("Tab detached");
    chrome.tabs.get(tabId, tab => {
        try {
            buildAndSendEventLog("detachTab", tab, detachInfo);
        } catch (error) {
            console.log(error.message);
        }
    });
});

// Fires when the active tab in a window changes.
// https://developer.chrome.com/extensions/tabs#event-onActivated
chrome.tabs.onActivated.addListener(activeInfo => {
    // console.log("Tab activated, selected");
    chrome.tabs.get(activeInfo.tabId, tab => {
        try {
            if (!tab.url.includes("newtab")) {
                buildAndSendEventLog("selectTab", tab, activeInfo);
            }
        } catch (error) {
            console.log(error.message);
        }
    });
});

// Fired when a tab is closed.
// https://developer.chrome.com/extensions/tabs#event-onRemoved
chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
    // console.log("Tab removed");
    try {
        buildAndSendEventLog("closeTab", previousTabs.get(tabId), removeInfo);
    } catch (error) {
        console.log(error.message);
    }
});

// Fired when a tab is zoomed.
// https://developer.chrome.com/extensions/tabs#event-onZoomChange
chrome.tabs.onZoomChange.addListener(ZoomChangeInfo => {
    // Check if zoom factor changes so page actually zoomed, otherwise chrome fires this even when new tab is created or selected
    if (ZoomChangeInfo.oldZoomFactor !== ZoomChangeInfo.newZoomFactor) {
        // console.log("Tab zoomed");
        chrome.tabs.get(ZoomChangeInfo.tabId, tab => {
            try {
                buildAndSendEventLog("zoomTab", tab, ZoomChangeInfo);
            } catch (error) {
                console.log(error.message);
            }
        });
    }
});

// Fired when a tab is updated.
// // https://developer.chrome.com/extensions/tabs#event-onUpdated
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // console.log("tab updated");
    try {
        if (changeInfo.pinned !== undefined) {
            if (changeInfo.pinned)
                buildAndSendEventLog("pinnedTab", tab, changeInfo);
            else
                buildAndSendEventLog("unpinnedTab", tab, changeInfo);
        }
        if (changeInfo.audible !== undefined) {
            buildAndSendEventLog("audibleTab", tab, changeInfo);
        }
        if (changeInfo.mutedInfo !== undefined) {
            if (changeInfo.mutedInfo.muted)
                buildAndSendEventLog("mutedTab", tab, changeInfo);
            else
                buildAndSendEventLog("unmutedTab", tab, changeInfo);
        }
    } catch (error) {
        console.log(error.message);
    }
});

// Fired when a tab is highlighted. (redundant)
// https://developer.chrome.com/extensions/tabs#event-onHighlighted
// chrome.tabs.onHighlighted.addListener( (highlightInfo) => {
//     console.log("highlighted tab changed")
//     chrome.tabs.query({ 'active': true, 'lastFocusedWindow': true }, (tabs) => {
//         try{
//             buildAndSendEventLog("highlightTab", tabs, highlightInfo)
//         } catch(error){
//
//             console.log(error.message);
//         }
//     });
// })

// ********************
// webNavigation events
// https://developer.chrome.com/extensions/webNavigation
// ********************

// when enter is pressed on address bar. At least part of the document has been received from the server and the browser has decided to switch to the new document.
// https://developer.chrome.com/extensions/webNavigation#event-onCommitted
chrome.webNavigation.onCommitted.addListener(details => {
    // console.log("webNavigation commit");

    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: details.transitionType,
        browser_url: details.url,
    };

    // convert each transition qualifier to camelCase
    let eventQual = details.transitionQualifiers.map(x => toCamelCase(x));
    eventLog.eventQual = JSON.stringify(eventQual);

    // Cause of the navigation different from any nested iframes that are automatically loaded by their parent.
    // https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/webNavigation/TransitionType
    if (details.transitionType !== "auto_subframe") {
        if (
            eventLog.eventType === "typed" ||
            eventLog.eventType === "generated" ||
            eventLog.eventType === "auto_bookmark" ||
            eventLog.eventQual.includes("forward_back")
        ) {
            eventLog.eventType = "navigateTo";
        }
        eventLog.event_type = toCamelCase(eventLog.event_type);
        if (
            !eventLog.browser_url.includes("newtab") &&
            eventLog.eventType !== "link"
        ) {
            logAndPost(eventLog);
        }

    }
});

// ********************
// window events
// https://developer.chrome.com/extensions/windows
// ********************

// Fired when a window is created.
// https://developer.chrome.com/extensions/windows#event-onCreated
chrome.windows.onCreated.addListener(window => {
    // console.log("Window opened");

    // https://developer.chrome.com/extensions/windows#type-Window
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "newWindow",
        window_ingognito: window.incognito,
        title: window.title
    };

    logAndPost(eventLog);
});

// Fired when a window is removed (closed).
// https://developer.chrome.com/extensions/windows#event-onRemoved
chrome.windows.onRemoved.addListener(windowId => {
    // console.log("Window closed");
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "closeWindow"
    };

    logAndPost(eventLog);
});

// Fired when the currently focused window changes. (too much spam)
// https://developer.chrome.com/extensions/windows#event-onFocusChanged
// chrome.windows.onFocusChanged.addListener((windowId) => {
//     console.log("Window focus changed");
//     let eventLog = {
//         timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
//         category: "Browser",
//         application: getBrowser(),
//         event_type: "focusChangeWindow",
//     };
//     console.log(eventLog);
//     post(eventLog);
// });

// ********************
// runtime events
// https://developer.chrome.com/apps/runtime
// ********************

// check if server is running and add all active tabs in the array of previousTabs (useful for debugging)
// https://developer.chrome.com/apps/runtime#event-onInstalled
chrome.runtime.onInstalled.addListener(runtimeStartup);
chrome.runtime.onStartup.addListener(runtimeStartup);
function runtimeStartup() {
    // check if server is running
    checkServerStatus();
    // save all open tabs in map
    chrome.tabs.query({ windowType: "normal" }, tabs => {
        tabs.forEach(tab => {
            previousTabs.set(tab.id, tab);
        });
    });
    // use white extension color if browser is in dark mode
    setupIconColor();
}

// receive messages from content and send them to server.
// It is not possible anymore to do it directly from content_script due to security reasons
// https://www.chromium.org/Home/chromium-security/extension-content-script-fetches
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.contentScriptQuery == "postData") {
        logAndPost(request.data);
    }
});

// ********************
// alarm events
// https://developer.chrome.com/apps/alarms
// ********************

// set up an alarm that check server status every minute.
// If server is running update extension text and badge to ON, else update to OFF
// const alarm_interval = 0.5; //30 seconds
// chrome.alarms.create("checkServerStatus", {
//     delayInMinutes: alarm_interval,
//     periodInMinutes: alarm_interval
// });
// chrome.alarms.onAlarm.addListener(function(alarm) {
//     if (alarm.name === "checkServerStatus") {
//         checkServerStatus();
//     }
// });

// ********************
// Utilities
// ********************

// Prepares JSON log and makes POST request to server for tabs events
function buildAndSendEventLog(eventType, tab, info) {
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: eventType,
        browser_url: tab.url || tab.pendingUrl,
        id: tab.index,
        title: tab.title
    };

    if (eventType == "moveTab") {
        eventLog.tab_moved_from_index = info.fromIndex;
        eventLog.tab_moved_to_index = info.toIndex;
    } else if (eventType == "newTab") {
        previousTabs.set(tab.id, tab);
    } else if (eventType == "closeTab") {
        previousTabs.delete(tab.id);
    } else if (eventType == "zoomTab") {
        eventLog.newZoomFactor = info.newZoomFactor;
        eventLog.oldZoomFactor = info.oldZoomFactor;
    } else if (eventType == "pinnedTab" || eventType == "unpinnedTab") {
        eventLog.pinned = info.pinned;
    } else if (eventType == "audibleTab") {
        eventLog.audible = info.audible;
    } else if (eventType == "mutedTab" || eventType == "unmutedTab") {
        eventLog.muted = info.mutedInfo.muted;
    }

    logAndPost(eventLog);
}
