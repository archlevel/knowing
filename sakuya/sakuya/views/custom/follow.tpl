% if chart_list:
<table class="table table-hover">
  % for item in chart_list:
  <tr>
    <td width="20"><i class="icon-picture"></i></td>
    <td><a href="/chart/{{ item['id'] }}">{{ item['name'] }}</a></td>
    <td width="100">
      <label for="cb_recv_warning_{{ item['id'] }}" class="checkbox inline no-padding">
        <input type="checkbox" id="cb_recv_warning_{{ item['id'] }}" chart_id="{{ item['id'] }}"
        % if item['recv_warning']:
        checked="checked"
        % end
        >
        接收全部报警
      </label>
    <td width="75"><input type="button" value="取消订阅" class="btn btn-info btn-small" chart_id="{{ item['id'] }}"></td>
  </tr>
  % end
</table>
% else:
<p><i class="icon-exclamation-sign"></i> 您还没有订阅任何内容。</p>
% end

<script type="text/javascript">
$(':button[chart_id]').click(function() {
    var btn = $(this),
        action = $(this).is('.btn-success') ? 'follow' : 'unfollow',
        cbWarning = $(':checkbox[chart_id="' + $(this).attr('chart_id') + '"]');

    var data = {
        _r:Math.random()
    };
    $.getJSON('/chart/' + action + '/' + btn.attr('chart_id'),data, function(response) {
        if (response.status == 'ok') {
            if (action == 'follow') {
                btn.removeClass('btn-success').addClass('btn-info').val('取消订阅');
                cbWarning.removeAttr('checked').parent().show();
            } else {
                btn.removeClass('btn-info').addClass('btn-success').val('订阅图表');
                cbWarning.parent().hide();
            }
        } else {
            alert(response.msg);
        }
    });

});
$(':checkbox[chart_id]').click(function() {
    var data = {
        chart_id: $(this).attr('chart_id'),
        recv_rules: $(this).is(':checked') ? 'all' : '',
        _r:Math.random()
    };
    $.getJSON('/chart/recv_warning', data, function(response) {
        if (response.status != 'ok') {
            alert(response.msg);
        }
    });
});
</script>

% rebase custom/layout user=user, active_subtab='follow'
