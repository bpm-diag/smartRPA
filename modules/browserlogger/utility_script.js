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