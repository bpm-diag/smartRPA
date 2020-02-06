// Chrome APIs
// https://developer.chrome.com/extensions/api_index


// ********************
// Tabs events 
// https://developer.chrome.com/extensions/tabs
// ********************

var tabTitles = new Map();
var tabUrls = new Map();

// Fired when a tab is created.
// https://developer.chrome.com/extensions/tabs#event-onCreated
chrome.tabs.onCreated.addListener( (tab) => {
    console.log("Tab created")
    chrome.tabs.query({ 'active': true, 'lastFocusedWindow': true }, (tabs) => {
        try{
            buildAndSendEventLog("newTab", tabs)
        } catch(error){
            console.log("Platform not supported");
            console.log(error.message);
        }
    })
});


// Fired when a tab is moved within a window 
// https://developer.chrome.com/extensions/tabs#event-onMoved
chrome.tabs.onMoved.addListener( (tabId, moveInfo) => {
    console.log("Tab moved")
    chrome.tabs.query({ 'active': true, 'lastFocusedWindow': true }, (tabs) => {
        try{
            buildAndSendEventLog("moveTab", tabs, moveInfo)
        } catch(error){
            console.log("Platform not supported");
            console.log(error.message);
        }
    });
});


// Fired when a tab is attached to a window; for example, because it was moved between windows.
// https://developer.chrome.com/extensions/tabs#event-onAttached
chrome.tabs.onAttached.addListener( (attachInfo) => {
    console.log("Tab attached")
    chrome.tabs.query({ 'active': true, 'lastFocusedWindow': true }, (tabs) => {
        try{
            buildAndSendEventLog("attachTab", tabs)
        } catch(error){
            console.log("Platform not supported");
            console.log(error.message);
        }
    });
});


// Fired when a tab is detached from a window; for example, because it was moved between windows.
// https://developer.chrome.com/extensions/tabs#event-onDetached
chrome.tabs.onDetached.addListener( (detachInfo) => {
    console.log("Tab detached")
    chrome.tabs.query({ 'active': true, 'lastFocusedWindow': true }, (tabs) => {
        try{
            buildAndSendEventLog("detachTab", tabs)
        } catch(error){
            console.log("Platform not supported");
            console.log(error.message);
        }
    });
});


// Fires when the active tab in a window changes.
// https://developer.chrome.com/extensions/tabs#event-onActivated
chrome.tabs.onActivated.addListener( (activeInfo) => {
    console.log("Tab activated")
    // get active tab https://developer.chrome.com/extensions/tabs#method-query
    chrome.tabs.query({ 'active': true, 'lastFocusedWindow': true }, (tabs) => {
        try{
            if (!tabs[0].url.includes("newtab")) {
                buildAndSendEventLog("selectTab", tabs)
            }
        } catch(error){
            console.log("Platform not supported");
            console.log(error.message);
        }
    });
});


// Fired when a tab is closed.
// https://developer.chrome.com/extensions/tabs#event-onRemoved
chrome.tabs.onRemoved.addListener( (tabId, removeInfo) => {
    console.log("Tab removed")
    // https://developer.chrome.com/extensions/tabs#method-query
    chrome.tabs.query({ 'lastFocusedWindow': true }, (tabs) => {
        try{
            let tabsID = new Array();
            for(i = 0; i < tabs.length; i++)
                tabsID.push(tabs[i].id);
            
            let originalTabs = Array.from(tabTitles.keys());
            
            for(i = 0; i < originalTabs.length; i++){				
                if(!tabsID.includes(originalTabs[i])){
                    removedTab = [{
                        url: tabUrls.get(originalTabs[i]),
                        title: tabTitles.get(originalTabs[i]),
                        id: originalTabs[i]
                    }]
                    buildAndSendEventLog("closeTab", removedTab)
                    break;
                }
            }
            
        } catch(err){
            console.log("Platform not supported");
            console.log(error.message);
        }
    });
});


// Fired when a tab is zoomed.
// https://developer.chrome.com/extensions/tabs#event-onZoomChange
chrome.tabs.onZoomChange.addListener( (ZoomChangeInfo) => {
    console.log("Tab zoomed")
    chrome.tabs.query({ 'active': true, 'lastFocusedWindow': true }, (tabs) => {
        try{
            console.log(ZoomChangeInfo);
            buildAndSendEventLog("zoomTab", tabs, ZoomChangeInfo)
        } catch(error){
            console.log("Platform not supported");
            console.log(error.message);
        }
    });
});


// Fired when a tab is updated.
// // https://developer.chrome.com/extensions/tabs#event-onUpdated
chrome.tabs.onUpdated.addListener( (tabId, changeInfo, tab) => {
    console.log("tab updated")
    chrome.tabs.query({ 'active': true, 'lastFocusedWindow': true }, (tabs) => {
        try{
            if (changeInfo.pinned != undefined) {
                buildAndSendEventLog("pinnedTab", tabs, changeInfo)
            }
            if (changeInfo.audible != undefined) {
                buildAndSendEventLog("audibleTab", tabs, changeInfo)
            }
            if (changeInfo.mutedInfo != undefined) {
                buildAndSendEventLog("mutedTab", tabs, changeInfo)
            }
        } catch(error){
            console.log("Platform not supported");
            console.log(error.message);
        }
    });
})


// Fired when a tab is highlighted.
// https://developer.chrome.com/extensions/tabs#event-onHighlighted
// chrome.tabs.onHighlighted.addListener( (highlightInfo) => {
//     console.log("highlighted tab changed")
//     chrome.tabs.query({ 'active': true, 'lastFocusedWindow': true }, (tabs) => {
//         try{
//             buildAndSendEventLog("highlightTab", tabs, highlightInfo)
//         } catch(error){
//             console.log("Platform not supported");
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
chrome.webNavigation.onCommitted.addListener( (details) => {
    console.log("onCommit")
    
    let eventLog = { 
        timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1).slice(0, -1),
        category: "Browser",
        application: getBrowser(),
        event_type: details.transitionType,
        browser_url: details.url,
        eventQual: JSON.stringify(details.transitionQualifiers)
    };
    
    if (details.transitionType != "auto_subframe") { //different from any nested iframes that are automatically loaded by their parent.
        
        // Cause of the navigation
        // https://developer.chrome.com/extensions/webNavigation#type-TransitionType
        if(eventLog.eventType == "typed" || 
        eventLog.eventType == "auto_bookmark" || 
        eventLog.eventType == "generated" || 
        eventLog.eventQual.includes("forward_back") ){
            eventLog.eventType = "navigateTo";			
        }
        if(!eventLog.browser_url.includes("newtab") && eventLog.eventType != "link"){
            console.log(eventLog);
            post(eventLog);
        }
        
        chrome.tabs.query({'active': true, 'lastFocusedWindow': true }, (tabs) => {
            try{
                let tabUrl = tabs[0].url;
                let tabTitle = tabs[0].title;
                let tabId = tabs[0].id;
                tabTitles.set(tabId, tabTitle);
                tabUrls.set(tabId, tabUrl);
            }	
            catch(error){
                console.log("Platform not supported");
                console.log(error.message);
            }			
        });
        
    }
});


// ********************
// window events 
// https://developer.chrome.com/extensions/windows
// ********************


// Fired when a window is created.
// https://developer.chrome.com/extensions/windows#event-onCreated
chrome.windows.onCreated.addListener( (window) => {
    console.log("Window opened");
    // https://developer.chrome.com/extensions/windows#type-Window
    let eventLog = { 
        timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
        category: "Browser",
        application: getBrowser(),
        event_type: "newWindow",
        window_ingognito: window.incognito,
        title: window.title
    };
    console.log(eventLog);
    post(eventLog);
});


// Fired when a window is removed (closed).
// https://developer.chrome.com/extensions/windows#event-onRemoved
chrome.windows.onRemoved.addListener( (windowId) => {
    console.log("Window closed");
    let eventLog = { 
        timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
        category: "Browser",
        application: getBrowser(),
        event_type: "closeWindow",
    };
    console.log(eventLog);
    post(eventLog);
});


// Fired when the currently focused window changes.
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
// Bookmarks events 
// https://developer.chrome.com/extensions/bookmarks
// ********************


// Fired when a bookmark or folder is created.
// https://developer.chrome.com/extensions/windows#event-onCreated
chrome.bookmarks.onCreated.addListener( (id, bookmark) => {
    console.log("Bookmark created");
    
    // https://developer.chrome.com/extensions/bookmarks#type-BookmarkTreeNode
    let eventLog = { 
        timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
        category: "Browser",
        application: getBrowser(),
        event_type: "newBookmark",
        browser_url: bookmark.url,
        title: bookmark.title
    };
    console.log(eventLog);
    post(eventLog);
});


// Fired when a bookmark or folder is removed. 
// https://developer.chrome.com/extensions/windows#event-onRemoved
chrome.bookmarks.onRemoved.addListener( (id, removeInfo) => {
    console.log("Bookmark removed");
    let eventLog = { 
        timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
        category: "Browser",
        application: getBrowser(),
        event_type: "removeBookmark",
        browser_url: removeInfo.node.url,
    };
    console.log(eventLog);
    post(eventLog);
});


// Fired when a bookmark or folder is changed. 
// https://developer.chrome.com/extensions/windows#event-onChanged
chrome.bookmarks.onChanged.addListener( (id, changeInfo) => {
    console.log("Bookmark changed");
    let eventLog = { 
        timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
        category: "Browser",
        application: getBrowser(),
        event_type: "modifyBookmark",
        browser_url: changeInfo.url,
        title: changeInfo.title
    };
    console.log(eventLog);
    post(eventLog);
});


// Fired when a bookmark or folder is moved. 
// https://developer.chrome.com/extensions/windows#event-onMoved
chrome.bookmarks.onMoved.addListener( (id, moveInfo) => {
    console.log("Bookmark moved");
    let eventLog = { 
        timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
        category: "Browser",
        application: getBrowser(),
        event_type: "moveBookmark",
    };
    console.log(eventLog);
    post(eventLog);
});


// Fired when a bookmark or folder is moved. 
// https://developer.chrome.com/extensions/windows#event-onMoved
chrome.bookmarks.onImportBegan.addListener( () => {
    console.log("Bookmark imported");
    let eventLog = { 
        timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
        category: "Browser",
        application: getBrowser(),
        event_type: "importBookmark",
    };
    console.log(eventLog);
    post(eventLog);
});


// ********************
// Utilities 
// ********************


// Prepares JSON log and makes POST request to server for tabs events
function buildAndSendEventLog(eventType, tabs, info){
    let tabUrl = tabs[0].url;
    let tabTitle = tabs[0].title;
    let tabId = tabs[0].id;
    
    let eventLog = { 
        timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
        category: "Browser",
        application: getBrowser(),
        event_type: eventType,
        browser_url: tabUrl,
        tab_id: tabId,
        title: tabTitle
    };
    
    if (eventType == "moveTab") {
        eventLog.tab_moved_from_index = info.fromIndex
        eventLog.tab_moved_to_index = info.toIndex
    } else if (eventType == "newTab") {
        tabTitles.set(tabId, tabTitle);
        tabUrls.set(tabId, tabUrl);
    } else if (eventType == "closeTab"){
        tabUrls.delete(tabId);
        tabTitles.delete(tabId);
    } else if (eventType == "zoomTab"){
        eventLog.newZoomFactor = info.newZoomFactor
        eventLog.oldZoomFactor = info.oldZoomFactor
    } else if (eventType == "pinnedTab") {
        eventLog.pinned = info.pinned
    } else if (eventType == "audibleTab") {
        eventLog.audible = info.audible
    } else if (eventType == "mutedTab") {
        eventLog.muted = info.mutedInfo.muted
    }
    
    console.log(eventLog);
    post(eventLog);
}


function post(eventLog) {
    return true
    // var storage = (localStorage.getItem('checkboxValue') || {}) == 'true';
    // if (storage === true) {
    // console.log("Recording Enabled")
    
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
            console.log("Request Failed! " + JSON.stringify(request) + 'Status ' + status + "Error msg: " + error);
        }
    });
    
    // } else {
    //     console.log("Recording Disabled");
    // }
}

function getBrowser() {
    if (typeof chrome !== "undefined") {
        if (typeof browser !== "undefined") 
        return "Firefox";
        else 
        return "Chrome";
    }
}