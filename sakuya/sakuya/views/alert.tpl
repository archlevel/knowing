<div class="row-fluid">
  <div id="monitor-container" class="span12 awesome-box content-box container">

    <form action="" method="get" class="form-inline" style="margin-bottom: 10px;" id="frm_filter">
      级别：
      <select name="level" class="input-medium">
        <option value="-1">全部</option>
        <option value="1"
        % if level == 1:
        selected="selected"
        % end
        >Warning</option>
        <option value="2"
        % if level == 2:
        selected="selected"
        % end
        >Critical</option>
      </select>&nbsp;&nbsp;&nbsp;&nbsp;
      状态：
      <select name="status" class="input-medium">
        <option value="-1">全部</option>
        <option value="0"
        % if status == 0:
        selected="selected"
        % end
        >未解决</option>
        <option value="1"
        % if status == 1:
        selected="selected"
        % end
        >已解决</option>
      </select>
      <input type="hidden" name="page" value="{{ page }}">
    </form>

    <table class="table table-hover">
      <tr>
        <th width="70">ID</th>
        <th width="70">级别</th>
        <th>信息</th>
        <th width="200">时间</th>
        <th width="150">状态</th>
        <th width="150">操作</th>
      </tr>
      % if events:
      % for e in events:
      <tr>
        <td>{{e['id']}}</td>
        % if e['level'] == 'warning':
        <td><span class="label label-warning">Warning</span></td>
        % elif e['level'] == 'critical':
        <td><span class="label label-important">Critical</span></td>
        % end
        <td><a href="/chart/{{e['cid']}}">{{e['message']}}</a></td>
        <td>{{e['time']}}</td>
        % if e['status'] == 0:
        <td><span class="label label-important" id="status-{{e['id']}}">未解决</span></td>
        <td>
          <a href="#solve-{{e['id']}}" id="solve-{{e['id']}}"class="btn btn-info solve-btn">解决</a>
        </td>
        % elif e['status'] == 1:
        <td><span class="label label-success" id="status-{{e['id']}}">已解决</span></td>
        <td>
          <a href="#solve-{{e['id']}}" id="solve-{{e['id']}}" class="btn btn-info" disabled="false" >解决</a>
        </td>
        % end
      </tr>
      % end
      % end
    </table>
    <a class="btn pull-left" href="javascript:void(0);" page="{{ prev_page }}">前一页</a>
    <a class="btn pull-right" href="javascript:void(0);" page="{{ next_page }}">后一页</a>
  </div> <!-- #monitor-container -->
</div> <!-- .row-fluid -->

<script type="text/javascript" src="/assets/js/alert.js"></script>

%rebase layout user=user, active_tab='alert'

