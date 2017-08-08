<form action="" method="post" class="form-horizontal">

  % if msg[0]:
  <div
  % if msg[1]:
  class="alert alert-error"
  % else:
  class="alert alert-success"
  % end
  >
    <button type="button" class="close" data-dismiss="alert">&times;</button>
    <strong>
    % if msg[1]:
    错误！
    % end
    </strong>
    {{ msg[0] }}
  </div>
  % end

  <div class="control-group">
    <label class="control-label">用户名：</label>
    <div class="controls">
      <input type="text" value="{{ forms['username'] }}" readonly="readonly">
    </div>
  </div>
  <div class="control-group">
    <label class="control-label">姓名：</label>
    <div class="controls">
      <input type="text" value="{{ forms['truename'] }}" readonly="readonly">
    </div>
  </div>
  <div class="control-group">
    <label class="control-label">接警邮箱：</label>
    <div class="controls">
      <textarea name="email" rows="5">{{ forms['email'] }}</textarea><br>
      <i class="icon-info-sign"></i> <font color="gray">可输入多个邮箱，以换行分隔。</font>
    </div>
  </div>
  <div class="control-group">
    <div class="controls">
      <input type="submit" value="保存" class="btn btn-primary">
      <input type="reset" value="重置" class="btn" onclick="return confirm('确定要重置吗？');">
    </div>
  </div>
</form>

% rebase custom/layout user=user, active_subtab='profile'
