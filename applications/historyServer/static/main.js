var config;
var global = 0.0;
var timeout;

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

function updates(ts) {
  console.log(ts)
  var data = {"op":"updates", "id": ts, "lambdaID" : "profile"};
  lambda_post(data, function(data){
    if ("error" in data) {
      html_error = data.error.replace(/\n/g, '<br/>');
      $("#comments").html("Error: <br/><br/>" + html_error + "<br/><br/>Consider refreshing.")
    } else {
      var ts = global;
      var table = document.getElementById("jobTable");
      for (var i = 0, len = data.result.length; i < len; i++) {
	row = data.result[i];
	if (row.ID > ts) {
	  ts = row.ID;
	}
        var newRow = table.insertRow(1);
        var tsCell = newRow.insertCell(0);
        var timeCell = newRow.insertCell(1);
        var lamCell = newRow.insertCell(2);

        var link = document.createElement("a");
        link.setAttribute("href", "details.html?id=" + row.ID);
        var linkText = document.createTextNode(row.ID);
        link.appendChild(linkText);
        tsCell.appendChild(link);
        timeCell.innerHTML = row.time_taken;
        link = document.createElement("a");
        link.setAttribute("href", "history.html?id=" + row.lambdaID);
        linkText = document.createTextNode(row.lambdaID);
        link.appendChild(linkText);
        lamCell.appendChild(link);
      }
      global = ts;
    }
  });
}

function main() {
  $.getJSON('config.json')
    .done(function(data) {
      config = data;

      // setup handlers
      //$("#submit").click(updates(0));
      //updates(0);
      updates(global);
      timeout = window.setInterval(function() { updates(global); }, 5000);
    })
    .fail(function( jqxhr, textStatus, error ) {
      $("#comments").html("Error: " + error + ".  Consider refreshing.")
    })
}

$(document).ready(function() {
  main();
});

