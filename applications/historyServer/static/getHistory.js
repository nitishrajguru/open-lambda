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
  var time = [];
  var network_sent = [];
  var network_recv = [];
  for (var i = 0, len = rows.length; i < len; i++) {
    var temp_time = [];
    var temp_network_sent = [];
    var temp_network_recv = [];
    row = rows[i];
    // X-axis
    temp_time.push(row.ID);
    temp_network_sent.push(row.ID);
    temp_network_recv.push(row.ID);
    // Y-axis
    temp_time.push(row.time_taken);
    temp_network_sent.push(row.sent_bytes);
    temp_network_recv.push(row.receive_bytes);
    // Append it to the data set.
    time.push(temp_time);
    network_sent.push(temp_network_sent);
    network_recv.push(temp_network_recv);
  }
  // Plot the graphs.
  console.log(network_sent)
  console.log(network_recv)
  $.plot('#timeGraph', [ { label : "Completion time(seconds)", data: time } ], { xaxis: {
    axisLabel : "Time Period",
    axisLabelUseCanvas : true,
    mode: "time",
    timeformat: "%h:%M"
  }, yaxis : {
     axisLabel : "Completion time(secs)",
     axisLabelUseCanvas : true
  },
     series : {
     points : { show : true }
  }})
  $.plot('#networkGraph', [{label : "Sent(bytes)", data : network_sent}, {label : "Receive(bytes)", data : network_recv}], { xaxis: {
    axisLabel : "Time Period",
    axisLabelUseCanvas : true,
    mode: "time",
    timeformat: "%h:%M"
  }, yaxis : {
     axisLabel : "Data(bytes)",
     axisLabelUseCanvas : true
  },
     series : {
     points : { show : true }
  }})
}


function getHistory() {
var data = {"op":"history", "selLambda": id, "lambdaID" : "profile"};
lambda_post(data, function(data){
    if ("error" in data) {
      html_error = data.error.replace(/\n/g, '<br/>');
      $("#comments").html("Error: <br/><br/>" + html_error + "<br/><br/>Consider refreshing.")
    } else {
      console.log(data.result);
      populateDetails(data.result.details);
      //populateDBInternals(data.result.DB);
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
      getHistory();
    })
    .fail(function( jqxhr, textStatus, error ) {
      $("#comments").html("Error: " + error + ".  Consider refreshing.")
    })
}
$(document).ready(function() {
  main();
});
