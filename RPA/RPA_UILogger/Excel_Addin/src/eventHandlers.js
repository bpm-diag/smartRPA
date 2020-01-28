function handleChange(event) {
    return Excel.run(function (context) {
        var range = context.workbook.worksheets.getActiveWorksheet().getRange(event.address);
        range.load(['address', 'values']);
        return context.sync()
            .then(function () {
                //var timestamp = Date.now();
                console.log("Change type of event: " + event.changeType);
                console.log("Address of event: " + event.address);
                console.log("Content of range: " + range.values);
                //console.log("Timestamp " = timestamp);
                postRest("Excel", event.changeType, event.address, range.values);
                //console.log("Source of event: " + event.source);
                OfficeHelpers.UI.notify("Change type of event: " + event.changeType + " Address of event: " + event.address + " Value: ");
            });
    }).catch(errorHandle)
}

function handleSelectionChange(event) {
    return Excel.run(function (context) {
        var range = context.workbook.worksheets.getActiveWorksheet().getRange(event.address);
        range.load(['address', 'values']);
        return context.sync()
            .then(function () {
                console.log("Change type of event: Selection Changed");
                console.log("Address of event: " + event.address);
                console.log("Content of range: " + range.values);
                postRest("Excel", "SelectionChanged", event.address, range.values);
                //console.log("Source of event: " + event.source);
                OfficeHelpers.UI.notify("Change type of event: " + event.changeType + " Address of event: " + event.address + " Value: ");
            });
    }).catch(errorHandle)
}

//generic error handler function
function errorHandle(error) {
    console.log("Error: " + error);
    if (error instanceof OfficeExtension.Error) {
        console.log("Debug info: " + JSON.stringify(error.debugInfo));
        OfficeHelpers.UI.notify("Debug info: " + JSON.stringify(error.debugInfo));
    }
}