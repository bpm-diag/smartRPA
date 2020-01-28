// failed clipboard monitor
// const clipboardy = require('clipboardy');
// const clipMonit = require('clipboard-monitor');
 
// //initialize & optionally set the interval with which to monitor the clipboard
// var monitor = clipMonit(); // deaults to 500ms
// var initialize = false; 

// //'copy. event is fired every time data is copied to the clipboard
// monitor.on('copy', function (data) {
//     if (initialize == true ) {
//     //do something with the data
//     console.log("Copy event: "+data);
// } else { initialize = true;}
// });




// // Attempt at Copy/paste loader
// var copyElement = document.createElement('input');      
// copyElement.setAttribute('type', 'text');   
// copyElement.setAttribute('value',' ' );  
// document.body.appendChild(copyElement);   

// // Add copy button
// var btn = document.createElement("button");
// btn.textContent = "copy";
// document.body.appendChild(btn)
// btn.addEventListener('click', function(event) {
//   var copyText = document.querySelector('input');
//   copyText.select();
//     document.execCommand('copy');
// });



// Office.context.document.getSelectedDataAsync(Office.CoercionType.Text, function (asyncResult) {
//     if (asyncResult.status == Office.AsyncResultStatus.Failed) {
//         write('Action failed. Error: ' + asyncResult.error.message);
//     }
//     else {
//         write('Selected data: ' + asyncResult.value);
//     }
// });


// // Function that writes to a div with id='message' on the page.
// function write(message){
//     OfficeHelpers.UI.notify(`The selected data is `+message);
//     //document.getElementById('message').innerText += message; 
// }




////

// var clipboard = new ClipboardJS('.btn');
// clipboard.on('success', function (e) {
//     OfficeHelpers.UI.notify("Cliboard Success " + e);
//     console.log(e);
// });
// clipboard.on('error', function (e) {
//     console.log(e);
// });

// function listenClipboard() {
//     var new_clip = getClipboard();
//     if (new_clip !== clipboard) {
//         clipboard = new_clip;
//         //handleClipboardChange(clipboard);
//         console.log("The Clipboard has changed!")
//     }
//     setTimeout(listenClipboard, 100);
// }