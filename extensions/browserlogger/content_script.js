// A content script is “a JavaScript file that runs in the context of web pages.” This means that a content script can interact with web pages that the browser visits.
// https://developer.chrome.com/extensions/content_scripts
// https://developer.mozilla.org/en-US/docs/Web/API

// ********************
// HTML elements events
// https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement
// ********************

// Paste
// https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/onpaste
document.body.onpaste = e => {
    // console.log("paste");
    let event = e || window.event;
    let paste = (event.clipboardData || window.clipboardData).getData(
        "text/plain"
    );
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "paste",
        clipboard_content: paste,
        browser_url: document.URL
    };
    // // console.log(JSON.stringify(eventLog));
    sendToBackgroundForPost(eventLog);
};

// ********************
// Window events
// https://developer.mozilla.org/en-US/docs/Web/API/WindowEventHandlers
// ********************

// The print event is raised before the print dialog window is opened.
// https://developer.mozilla.org/en-US/docs/Web/API/WindowEventHandlers/onbeforeprint
window.onbeforeprint = e => {
    // console.log("print");
    let event = e || window.event;
    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "print",
        browser_url: document.URL
    };
    // console.log(JSON.stringify(eventLog));
    sendToBackgroundForPost(eventLog);
};

// Fired when the fragment identifier of the URL has changed (the part of the URL beginning with and following the # symbol).
// https://developer.mozilla.org/en-US/docs/Web/API/WindowEventHandlers/onhashchange
window.onhashchange = e => {
    // console.log("url hash change");

    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "urlHashChange",
        browser_url: document.URL,
        tag_href: location.hash
    };
    // console.log(JSON.stringify(eventLog));
    sendToBackgroundForPost(eventLog);
};

// ********************
// Global events
// https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/// ********************

// Context menu (right click)
// https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/oncontextmenu
document.body.oncontextmenu = e => {
    // console.log("context menu");
    let event = e || window.event;
    let target = event.target;

    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "contextMenu",
        browser_url: document.URL,
        xpath: getXPath(target),
        xpath_full: getXPathFull(target)
    };
    // console.log(JSON.stringify(eventLog));
    sendToBackgroundForPost(eventLog);
};

// Click
// https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/onclick
document.body.onclick = e => {
    // console.log("click");

    let event = e || window.event;
    let target = event.target;
    let tag = target.tagName;
    let type = target.type;
    let click_coord = `${event.screenX},${event.screenY}`; // relative to browser
    let url = document.URL;
    let html = target.innerHTML;
    let innerText = target.innerText.substring(0,80) || "";
    let tag_value = target.value;
    let parent_title = target.parentNode.title  || "";
    let title = target.title;
    let attributes = getTargetAttributes(target) || {};
    attributes.parentNodeTitle = parent_title;

    // Set this variable to true if you want to log clicks on text elements like paragraphs, headers, div, span
    const LOG_TEXT_ELEMENTS = false;
    if (
        LOG_TEXT_ELEMENTS &&
        (tag == "DIV" ||
            tag == "H1" ||
            tag == "H2" ||
            tag == "H3" ||
            tag == "H4" ||
            tag == "H5" ||
            tag == "H6" ||
            tag == "P" ||
            tag == "SPAN" ||
            tag == "CODE" ||
            tag == "YT-FORMATTED-STRING" ||
            tag == "FIELDSET" ||
            tag == "BODY")
    )
        return 0;

    // already handled by onchange
    if (tag == "OPTION") return 0;

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

    // remove html if clicking on youtube
    if (url.includes("youtube")) html = "";

    // support for gmail
    if (url.includes("mail.google.com")){
        // gmail new message body
        tag_value = document.querySelector(".Am.Al.editable").innerText
    }
    if (url.includes("https://dl.acm.org/")) {
        if (target.className === "icon-section_arrow_d"){
            eventType = "clickLink";
            title = parent_title;
            innerText = parent_title;
        }
    }

    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: eventType,
        browser_url: url,
        mouse_coord: click_coord,
        id: target.id,
        tag_category: tag,
        tag_type: type,
        tag_name: target.name,
        tag_title: title,
        tag_value: tag_value,
        tag_html: html.substring(0,50) || "", //take only the first 50 characters otherwise it's too long
        tag_href: target.href || "",
        tag_innerText: innerText, //take only the first 80 characters otherwise it's too long
        tag_option: target.option,
        tag_attributes: attributes,
        xpath: getXPath(target),
        xpath_full: getXPathFull(target),
    };

    if (type === "checkbox" || type === "radio") {
        eventLog.tag_checked = target.checked;
    }

    // console.log(JSON.stringify(eventLog));
    // sendToBackgroundForPost(eventLog);
    sendToBackgroundForPost(eventLog);
};

// Selection
// https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/onmouseup
document.body.onmouseup = e => {
    let event = e || window.event;
    let target = event.target;
    let click_coord = `${event.screenX},${event.screenY}`; // relative to browser
    let selection = window.getSelection().toString();
    if (selection) {
        // console.log("selection mouse up");
        let eventLog = {
            timestamp: timestamp(),
            category: "Browser",
            application: getBrowser(),
            event_type: "selectText",
            browser_url: document.URL,
            mouse_coord: click_coord,
            tag_value: selection,
            xpath: getXPath(target),
            xpath_full: getXPathFull(target)
        };
        // console.log(JSON.stringify(eventLog));
        sendToBackgroundForPost(eventLog);
    }
};

// Submit form
// https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/onsubmit
document.body.onsubmit = e => {
    // console.log("submit");

    let event = e || window.event;
    let target = event.target;

    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "submit",
        browser_url: document.URL,
        xpath: getXPath(target),
        xpath_full: getXPathFull(target)
    };
    // console.log(JSON.stringify(eventLog));
    sendToBackgroundForPost(eventLog);
};

// Change, fired for <input>, <select>, and <textarea> elements when an alteration to the element's value is committed by the user
// https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/onchange
document.body.onchange = e => {
    // console.log("changeField");

    let event = e || window.event;
    let target = event.target;
    let tag = target.tagName;
    let type = target.type;

    // already handled by click event
    if (type == "checkbox" || type == "radio") {
        return 0;
    }

    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "changeField",
        browser_url: document.URL,
        tag_category: tag,
        tag_type: type,
        id: target.id,
        tag_name: target.name,
        tag_value: target.value,
        tag_attributes: getTargetAttributes(target) || "",
        xpath: getXPath(target),
        xpath_full: getXPathFull(target)
    };

    sendToBackgroundForPost(eventLog);
};

// The focus event fires when an element has received focus.
// https://developer.mozilla.org/en-US/docs/Web/API/Element/focus_event
document.body.ondblclick = e => {
    // console.log("double click");
    let event = e || window.event;
    let target = event.target;

    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "doubleClick",
        browser_url: document.URL,
        xpath: getXPath(target),
        xpath_full: getXPathFull(target)
    };
    // console.log(JSON.stringify(eventLog));
    sendToBackgroundForPost(eventLog);
};

// The drag event is fired every few hundred milliseconds as an element or text selection is being dragged by the user.
// https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API
document.body.ondragstart = e => {
    // console.log("drag");
    let event = e || window.event;
    let target = event.target;

    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "dragElement",
        browser_url: document.URL,
        tag_value: event.dataTransfer.getData("text/plain"),
        xpath: getXPath(target),
        xpath_full: getXPathFull(target)
    };
    // console.log(JSON.stringify(eventLog));
    sendToBackgroundForPost(eventLog);
};

// The cancel event fires when the user indicates a wish to dismiss a <dialog>
// https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/oncancel
document.body.oncancel = e => {
    // console.log("cancelDialog");
    let event = e || window.event;

    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "cancelDialog",
        browser_url: document.URL
    };
    // console.log(JSON.stringify(eventLog));
    sendToBackgroundForPost(eventLog);
};

// Fired when the element has transitioned into or out of full-screen mode.
// https://developer.mozilla.org/en-US/docs/Web/API/Element/onfullscreenchange
document.body.onfullscreenchange = e => {
    // console.log("fullscreen");

    let event = e || window.event;
    let target = event.target;
    let isFullscreen = document.fullscreenElement === target;
    console.log(target);
    console.log(isFullscreen);

    // document.fullscreenElement will point to the element that
    // is in fullscreen mode if there is one. If there isn't one,
    // the value of the property is null.
    if (document.fullscreenElement) {
        console.log(
            `Element: ${document.fullscreenElement.id} entered full-screen mode.`
        );
    } else {
        console.log("Leaving full-screen mode.");
    }

    let eventLog = {
        timestamp: timestamp(),
        category: "Browser",
        application: getBrowser(),
        event_type: "fullscreen",
        browser_url: document.URL,
        id: document.fullscreenElement.id || ""
    };
    // console.log(JSON.stringify(eventLog));
    sendToBackgroundForPost(eventLog);
};
