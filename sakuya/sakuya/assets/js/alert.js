;

var solve_event = function () {
  var regex = /\d+/
  var m = $(this).attr("href").match(regex)
  if (m) {
    var event_id = m[0]
    $.ajax({
      "url": "/ajax/events/solve",
      "type": "POST",
      "data": {"event_id": event_id},
      "success": solve_callback,
      "fail": solve_callback_fail
    })
  }
  return false
}

var solve_callback = function (data) {
  if (data['status'] == "ok") {
    $("#status-" + data['event_id']).removeClass('label-important')
    $("#status-" + data['event_id']).addClass('label-success')
    $("#status-" + data['event_id']).text("已解决")
    $("#solve-" + data['event_id']).attr("disabled", true)
  }
}

var solve_callback_fail = function () {
  alert("event solving failed!")
}

var alert_startup = function () {
  $(".solve-btn").bind("click", solve_event)
}

$(alert_startup)

;

(function() {

    $('select[name="level"], select[name="status"]').change(function() {
        $('#frm_filter').submit();
    });

    $('a[page]').click(function() {
        $(':hidden[name="page"]').val($(this).attr('page'));
        $('#frm_filter').submit();
    });

})();
