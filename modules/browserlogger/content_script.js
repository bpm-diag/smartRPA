// A content script is “a JavaScript file that runs in the context of web pages.” This means that a content script can interact with web pages that the browser visits.
// https://developer.chrome.com/extensions/content_scripts


// https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/onpaste
document.body.onpaste = (event) => {
    console.log("paste");
    let paste = (event.clipboardData || window.clipboardData).getData('text/plain');
    let eventLog = { 
        timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
        category: "Browser",
        application: getBrowser(),
        event_type: "paste",
        clipboard_content: paste,
        browser_url: document.URL
    };
    console.log(JSON.stringify(eventLog));
    post(eventLog);
};

// https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/onclick
document.body.onclick = (event) => {
    console.log("click");
    console.log(JSON.stringify(event));
    
    let eventLog = { 
        timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
        category: "Browser",
        application: getBrowser(),
        event_type: "paste",
        browser_url: document.URL
    };
    console.log(JSON.stringify(eventLog));
    post(eventLog);
};


// // https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/onchange
// document.body.onchange = (e) => {
//     console.log("change");
//     let eventLog = { 
//         timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
//         category: "Browser",
//         application: getBrowser(),
//         event_type: "edit",
//         browser_url: document.URL
//     };
//     console.log(JSON.stringify(eventLog));
//     post(eventLog);
// };

// //
// document.body.onkeypress = (e) => {
//     console.log("paste");
//     let eventLog = { 
//         timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
//         category: "Browser",
//         application: getBrowser(),
//         event_type: "paste",
//         clipboard_content: e.clipboardData.getData('text/plain'),
//         browser_url: document.URL
//     };
//     console.log(JSON.stringify(eventLog));
//     post(eventLog);
// };


