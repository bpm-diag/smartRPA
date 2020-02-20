
/* global console, document, Excel, Office */

Office.onReady(info => {
    if (info.host === Office.HostType.Excel) {
        document.getElementById("sideload-msg").style.display = "none";
        document.getElementById("app-body").style.display = "flex";
        handleCheckbox();

        // https://docs.microsoft.com/en-us/office/dev/add-ins/excel/excel-add-ins-events#events-in-excel
        Excel.run(function(context) {
            let sheets = context.workbook.worksheets;
            sheets.onActivated.add(handleEvent);
            sheets.onAdded.add(handleEvent);
            sheets.onDeleted.add(handleEvent);
            return context.sync().then(function() {
                let worksheet = sheets.getActiveWorksheet();
                worksheet.onChanged.add(handleEvent);
                worksheet.onSelectionChanged.add(handleEvent);
                worksheet.onCalculated.add(handleEvent);
                worksheet.onFormatChanged.add(handleEvent);
                worksheet.onColumnSorted.add(handleEvent);
                worksheet.onRowSorted.add(handleEvent);
            });
        }).catch(error => console.log(error));

    }
});

function handleCheckbox(){
    $('#logging_checkbox').click(function() {
        if ($(this).is(':checked')) {
            $('#checkboxLabel').text("Logging enabled")
        } else {
            $('#checkboxLabel').text("Logging disabled")
        }
    });
}

function handleEvent(event){
    return Excel.run(function(context) {
        let worksheet = context.workbook.worksheets.getActiveWorksheet().load("name");
        let workbook_name = context.workbook.load("name");
        let range = context.workbook.worksheets
            .getActiveWorksheet()
            .getRange(event.address)
            .load(["address", "values", "name"]);

        return context.sync().then(function() {

            let eventLog = {
                timestamp: moment().format("YYYY-MM-DD HH:mm:ss:SSS"),
                category: "MSOffice",
                application: "Microsoft Excel (MacOS)",
                event_type: event.type,
                workbook: workbook_name._N,
                current_worksheet: worksheet.name,
                id: event.address
        };

            if (event.type === "WorksheetSelectionChanged" || event.type === "WorksheetChanged") {
                // When I select cells I get an array of arrays containing all the values of the cells,
                // like [["", "", ""],["", "test", ""], ["", "test", ""]]
                // I want to get only the non empty strings so I merge all the arrays into one uning concat
                // and remove the empty strings using filter
                let cell_content = [].concat.apply([], range.values).filter(cell => cell);
                let eventType = "editCell";
                if (event.address.includes(":"))
                    eventType = "editRange";
                eventLog.event_type = eventType;
                eventLog.cell_content = JSON.stringify(cell_content);
            }

            post(eventLog);
        });
    }).catch(error => console.log(error));
}

async function post(req) {
    if ($("#logging_checkbox").prop("checked")) {
        console.log(JSON.stringify(req));
        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:4444",
            crossDomain: true,
            contentType: "application/json",
            data: JSON.stringify(req),
            success: function(responseData, status, xhr) {
                console.log(`Request Successful`);
                // console.log(`Request Successful ${JSON.stringify(responseData)}`);
            },
            error: function(request, status, error) {
                console.log(
                    `Request failed ${JSON.stringify(request)}. Status: ${status}. Error: ${error}`
                );
            }
        });
    } else {
        console.log("Logging Disabled");
    }
}