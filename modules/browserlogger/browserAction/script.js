// document.getElementById('myHeading').style.color = 'red'

document.addEventListener("DOMContentLoaded", function() {
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
});