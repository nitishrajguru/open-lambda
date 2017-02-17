var id;
var config;

function lambda_post(data, callback) {
  var url = config['url']
  $.ajax({
    type: "POST",
    url: url,
    contentType: "application/json; charset=utf-8",
    data: JSON.stringify(data),
    dataType: "json",
    success: callback,
    failure: function(error) {
      $("#comments").html("Error: " + error + ".  Consider refreshing.")
    }
  });
}


function populateDetails(rows) {
      for (var i = 0, len = rows.length; i < len; i++) {
        row = rows[i];
        var table = document.getElementById("networkTable");
        var newRow = table.insertRow(1);
        var readCell = newRow.insertCell(0);
        var writeCell = newRow.insertCell(1);
        readCell.innerHTML = row.sent_bytes;
        writeCell.innerHTML = row.receive_bytes;
        table = document.getElementById("ioTable");
        newRow = table.insertRow(1);
        readCell = newRow.insertCell(0);
        writeCell = newRow.insertCell(1);
        readCell.innerHTML = row.read_bytes;
        writeCell.innerHTML = row.write_bytes;
        table = document.getElementById("descTable");
        newRow = table.insertRow(1);
        var firstCell = newRow.insertCell(0);
        var secondCell = newRow.insertCell(1);
        firstCell.innerHTML = row.cpu_util + "%";
        secondCell.innerHTML = row.mem_active;
        //tsCell.innerHTML = '<a href="www.google.com">' + row.ts + '</a>';
        /*var link = document.createElement("a");
        link.setAttribute("href", "details.html?id=" + row.ID);
        var linkText = document.createTextNode(row.ID);
        link.appendChild(linkText);
        tsCell.appendChild(link);
        timeCell.innerHTML = row.time_taken;*/
      }
}

function populateLambdaInternals(rows) {
  var table = document.getElementById("lambdaTable");
  for (var i = 0, len = rows.length; i < len; i++) {
    row = rows[i];
    var newRow = table.insertRow(i + 1);
    var tsCell = newRow.insertCell(0);
    var timeCell = newRow.insertCell(1);
    var lamCell = newRow.insertCell(2);
    var link = document.createElement("a");
    link.setAttribute("href", "details.html?id=" + row.ID);
    var linkText = document.createTextNode(row.ID);
    link.appendChild(linkText);
    tsCell.appendChild(link);
    timeCell.innerHTML = row.time_taken;
    lamCell.innerHTML = row.lambdaID;    
  }
}

function populateDBInternals(rows) {
  var table = document.getElementById("dbTable");
  for (var i = 0, len = rows.length; i < len; i++) {
    row = rows[i];
    var newRow = table.insertRow(i + 1);
    var timeCell = newRow.insertCell(0);
    var readCell = newRow.insertCell(1);
    var writeCell = newRow.insertCell(2);
    timeCell.innerHTML = row.time_taken; 
    readCell.innerHTML = row.end_read_bytes - row.start_read_bytes;
    writeCell.innerHTML = row.end_write_bytes - row.start_write_bytes;       
  }
}

function getDetails() {
var data = {"op":"details", "id": id, "lambdaID" : "profile"};
lambda_post(data, function(data){
    if ("error" in data) {
      html_error = data.error.replace(/\n/g, '<br/>');
      $("#comments").html("Error: <br/><br/>" + html_error + "<br/><br/>Consider refreshing.")
    } else {
      console.log(data.result);
      populateDetails(data.result.details);
      populateLambdaInternals(data.result.lambda);
      populateDBInternals(data.result.DB);
    }
  });
}

function main() {
  var parameters = location.search.substring(1).split("&");
  var temp = parameters[0].split("=");
  id = unescape(temp[1]);
  $.getJSON('config.json')
    .done(function(data) {
      config = data;
      getDetails();
    })
    .fail(function( jqxhr, textStatus, error ) {
      $("#comments").html("Error: " + error + ".  Consider refreshing.")
    })
}

$(document).ready(function() {
  main();
});
