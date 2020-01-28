
document.addEventListener('DOMContentLoaded', function () {
    console.log("started: " + $("#record").prop("checked"))

    // var storage = JSON.parse(localStorage.getItem('checkboxValue') || {});
    var storage = (localStorage.getItem('checkboxValue') || {}) == 'true';



    console.log("storage:" + storage);

    if (storage === true ){
        $("#record").prop("checked",true);
        console.log("was true "+$("#record").prop("checked")); 
    } else{
        console.log("was false "+$("#record").prop("checked")); 
        $("#record").prop("checked",false);
    }

    // $("#record").prop("checked", true);

    $("#record").on("change", function () {
        value = this.checked;
        console.log("clicked " + value)
        localStorage.setItem('checkboxValue', value);
        console.log("storage updated: "+localStorage.getItem('checkboxValue'));
        //alert("Hello! I am an alert box!!");
    });



});








