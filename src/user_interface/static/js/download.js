function generateSigma() {
    const file_uuid = $('#file_uuid').data().name;
    const filename = $('#filename').data().name;
    console.log(file_uuid)
    const table = document.getElementById("t_ioc");
    console.log(table);

    let iocList = [];
    var inputs = document.getElementsByClassName("ioc_checkbox");
    for(var i = 0; i < inputs.length; i++) {
        if(inputs[i].checked) {
            iocList.push(inputs[i].value)
        }
    }

    // for (let i=1; i<table.rows.length; i++) {
    //     currentRow = table.rows[i];
    //     if (currentRow.cells[currentRow.cells.length-2].children[0].checked) {
    //         rowValue = currentRow.cells[currentRow.cells.length-1].value;
    //         iocList.push(currentRow.cells[currentRow.cells.length-1].innerHTML);
    //     }
    // }
    // console.log(iocList)
    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(e) {
          if (xhr.readyState == 4) {
             window.location.replace("download-file?file_uuid=" + file_uuid + "&report_name=" + filename)
              // console.log("DONE")
          }
        };
    xhr.open("POST", "/update-sigma");
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({"ioc_uuids": iocList, "file_uuid": file_uuid, "filename": filename}));
}