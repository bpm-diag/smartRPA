// A content script is “a JavaScript file that runs in the context of web pages.” This means that a content script can interact with web pages that the browser visits.
// https://developer.chrome.com/extensions/content_scripts
// https://developer.mozilla.org/en-US/docs/Web/API

// Click
// https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/onclick
document.body.onclick = e => {
    console.log("click");

    let event = e || window.event;
    let target = event.target;
    let tag = target.tagName;
    let type = target.type;
    let click_coord = `(${event.screenX}, ${event.screenY})`; // relative to browser

    // Set this variable if you want to log clicks on text elements like paragraphs, headers, div, span
    LOG_TEXT_ELEMENTS = false;
    if (
        !LOG_TEXT_ELEMENTS &&
        (tag == "DIV" ||
            tag == "H1" ||
            tag == "H2" ||
            tag == "H3" ||
            tag == "H4" ||
            tag == "H5" ||
            tag == "H6" ||
            tag == "P" ||
            tag == "SPAN" ||
            tag == "CODE")
    )
        return 0;

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
    } else if (tag == "SELECT" || tag == "OPTION") {
        eventType = "selectOptions";
    }

    let eventLog = {
        timestamp: moment().format("YYYY-MM-DD HH:mm:ss:SSS"),
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

// Paste
// https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/onpaste
document.body.onpaste = e => {
    console.log("paste");
    let event = e || window.event;
    let paste = (event.clipboardData || window.clipboardData).getData(
        "text/plain"
    );
    let eventLog = {
        timestamp: moment().format("YYYY-MM-DD HH:mm:ss:SSS"),
        category: "Browser",
        application: getBrowser(),
        event_type: "paste",
        clipboard_content: paste,
        browser_url: document.URL
    };
    console.log(JSON.stringify(eventLog));
    post(eventLog);
};

// Selection
document.body.onmouseup = e => {
    let selection = window.getSelection().toString();
    if (selection) {
        console.log("selection mouse up");
        let eventLog = {
            timestamp: moment().format("YYYY-MM-DD HH:mm:ss:SSS"),
            category: "Browser",
            application: getBrowser(),
            event_type: "selectText",
            browser_url: document.URL,
            tag_value: selection
        };
        console.log(JSON.stringify(eventLog));
        post(eventLog);
    }
};

// Submit form
document.body.onsubmit = e => {
    console.log("submit");
    let eventLog = {
        timestamp: moment().format("YYYY-MM-DD HH:mm:ss:SSS"),
        category: "Browser",
        application: getBrowser(),
        event_type: "submit",
        browser_url: document.URL
    };
    console.log(JSON.stringify(eventLog));
    post(eventLog);
};

// Context menu (right click)
// https://developer.mozilla.org/en-US/docs/Web/API/Element/contextmenu_event
document.body.oncontextmenu = e => {
    console.log("context menu");
    let eventLog = {
        timestamp: moment().format("YYYY-MM-DD HH:mm:ss:SSS"),
        category: "Browser",
        application: getBrowser(),
        event_type: "contextMenu",
        browser_url: document.URL
    };
    console.log(JSON.stringify(eventLog));
    post(eventLog);
};

// Change, fired for <input>, <select>, and <textarea> elements when an alteration to the element's value is committed by the user
// https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/onchange
document.body.onchange = e => {
    console.log("changeField");

    let event = e || window.event;
    let target = event.target;
    let tag = target.tagName;
    let type = target.type;

    // already handled by click event
    if (type == "checkbox" || type == "radio") {
        return 0;
    }

    let eventLog = {
        timestamp: moment().format("YYYY-MM-DD HH:mm:ss:SSS"),
        category: "Browser",
        application: getBrowser(),
        event_type: "changeField",
        browser_url: document.URL,
        tag_category: tag,
        tag_type: type,
        tag_name: target.name,
        tag_value: target.value
    };
    console.log(JSON.stringify(eventLog));
    post(eventLog);
};

// The focus event fires when an element has received focus. 
// https://developer.mozilla.org/en-US/docs/Web/API/Element/focus_event
document.body.ondblclick = e => {
    console.log("double click");
    let eventLog = {
        timestamp: moment().format("YYYY-MM-DD HH:mm:ss:SSS"),
        category: "Browser",
        application: getBrowser(),
        event_type: "doubleClick",
        browser_url: document.URL
    };
    console.log(JSON.stringify(eventLog));
    post(eventLog);
};

// The drag event is fired every few hundred milliseconds as an element or text selection is being dragged by the user.
// https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API
document.body.ondragstart = e => {
    console.log("drag");
    let event = e || window.event;

    let eventLog = {
        timestamp: moment().format("YYYY-MM-DD HH:mm:ss:SSS"),
        category: "Browser",
        application: getBrowser(),
        event_type: "dragElement",
        browser_url: document.URL,
        tag_value: event.dataTransfer.getData("text/plain")
    };
    console.log(JSON.stringify(eventLog));
    post(eventLog);
};

// too much spam
// document.body.oninput = e => {
//     console.log("input");
//     let eventLog = {
//         timestamp: moment().format("YYYY-MM-DD HH:mm:ss:SSS"),
//         category: "Browser",
//         application: getBrowser(),
//         event_type: "inputField",
//         browser_url: document.URL
//     };
//     console.log(JSON.stringify(eventLog));
//     post(eventLog);
// };

// too much spam
// document.body.onkeypress = (e) => {
//     console.log("keypress");
//     let eventLog = {
//         timestamp: moment().format('YYYY-MM-DD HH:mm:ss:SSS'),
//         category: "Browser",
//         application: getBrowser(),
//         event_type: "keypress",
//         browser_url: document.URL
//     };
//     console.log(JSON.stringify(eventLog));
//     post(eventLog);
// };
