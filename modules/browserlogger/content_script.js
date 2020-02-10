// A content script is “a JavaScript file that runs in the context of web pages.” This means that a content script can interact with web pages that the browser visits.
// https://developer.chrome.com/extensions/content_scripts

// https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/onpaste
document.body.onpaste = e => {
    console.log("paste");
    let event = e || window.event;
    let paste = (event.clipboardData || window.clipboardData).getData(
        "text/plain"
    );
    let eventLog = {
        timestamp: moment().format('YYYY-MM-DD HH:mm:ss:SSS'),
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
document.body.onclick = e => {
    console.log("click");
    let event = e || window.event;

    let click_coord = `(${event.clientX}, ${event.clientY})`; // relative to browser
    let target = event.target;
    let tag = target.tagName;
    let type = target.type;

    let eventType = "mouseClick";
    if (tag == "TEXTAREA" || tag == "INPUT") {
        if (type == "submit") eventType = "clickButton";
        else if (type == "checkbox") eventType = "clickCheckboxButton";
        else if (type == "radio") eventType = "clickRadioButton";
        else if (type == "text") eventType = "clickTextField";
    } else if (tag == "BUTTON") {
        eventType = "clickButton";
    } else if (target.href) {
        eventType = "clickLink";
    } else if (tag == "SELECT") {
        eventType = "selectOptions";
    }

    let eventLog = {
        timestamp: moment().format('YYYY-MM-DD HH:mm:ss:SSS'),
        category: "Browser",
        application: getBrowser(),
        event_type: eventType,
        browser_url: document.URL,
        tag_category: tag,
        tag_type: type,
        tag_name: target.name,
        tag_title: target.title,
        tag_value: target.value,
        tag_html: target.innerHTML,
        tag_href: target.href || "",
        tag_innerText: target.innerText,
        tag_option: target.option
    };

    if (type == "checkbox" || type == "radio") {
        eventLog.tag_checked = target.checked;
    }

    console.log(JSON.stringify(eventLog));
    post(eventLog);
};




document.body.onsubmit = event => {
    console.log("focus");

    let eventLog = {
        timestamp: moment().format('YYYY-MM-DD HH:mm:ss:SSS'),
        category: "Browser",
        application: getBrowser(),
        event_type: "submit",
        browser_url: document.URL
    };
    console.log(JSON.stringify(eventLog));
    post(eventLog);
};

document.body.oncontextmenu = event => {
    console.log("context menu");
    let eventLog = {
        timestamp: moment().format('YYYY-MM-DD HH:mm:ss:SSS'),
        category: "Browser",
        application: getBrowser(),
        event_type: "contextMenu",
        browser_url: document.URL
    };
    console.log(JSON.stringify(eventLog));
    post(eventLog);
};

// // https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/onchange
// document.body.onchange = event => {
//     console.log("change");

//     let eventLog = {
//         timestamp: new Date(Date.now())
//             .toISOString()
//             .replace("T", " ")
//             .slice(0, -1),
//         category: "Browser",
//         application: getBrowser(),
//         event_type: "edit",
//         browser_url: document.URL
//     };
//     console.log(JSON.stringify(eventLog));
//     post(eventLog);
// };

// document.body.onkeypress = (e) => {
//     console.log("keypress");
//     let eventLog = {
//         timestamp: new Date(Date.now()).toISOString().replace('T',' ').slice(0, -1),
//         category: "Browser",
//         application: getBrowser(),
//         event_type: "keypress",
//         browser_url: document.URL
//     };
//     console.log(JSON.stringify(eventLog));
//     post(eventLog);
// };
