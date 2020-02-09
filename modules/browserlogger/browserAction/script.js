// document.getElementById('myHeading').style.color = 'red'

document.addEventListener('DOMContentLoaded', function () {
    // Check if server is reachable
    $.ajax({
        url: "http://127.0.0.1:4444/",
        type: "HEAD",
        timeout:1000,
        statusCode: {
            200: function (response) {
                console.log('Server online');
                $("#server_status").text('Logging server running')
                $("#server_status").css('color', 'greenyellow');
            },
            400: function (response) {
                console.log('Server offline 400');
                $("#server_status").text('Logging server not running')
            },
            0: function (response) {
                console.log('Server offline 0');
                $("#server_status").text('Logging server not running')
            }              
        }
    })
    
});
