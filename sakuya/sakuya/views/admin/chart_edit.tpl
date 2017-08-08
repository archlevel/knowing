<h3 id="h3_chart_edit_title">
% if get('editing'):
编辑图表
% else:
新建图表
% end
</h3><hr>

% if defined('error_msg'):
<div class="alert alert-error">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>错误！</strong> {{ error_msg }}
</div>
% end

<form class="form-horizontal"
% if get('editing'):
action="/admin/chart/update/{{ id }}"
% else:
action="/admin/chart/add"
% end
method="post">
  <div class="control-group">
    <label class="control-label">名称：</label>
    <div class="controls">
      <input type="text" placeholder="名称" name="name" value="{{ forms['name'] }}"
      % if warn_only or is_haopan:
      readonly="readonly"
      % end
      >
    </div>
  </div>
  <div class="control-group"
  % if warn_only or is_haopan:
  style="display: none;"
  % end
  >
    <label class="control-label">所属栏目：</label>
    <div class="controls">
      <select name="cid">
      <option value="">请选择</option>
      % for item in categories:
      <option value="{{ item[0] }}"
      % if str(item[0]) == str(forms['cid']):
      selected="selected"
      % end
      >{{ item[1] }}</option>
      % end
      </select>
    </div>
  </div>
  <div class="control-group">
    <label class="control-label">创建人：</label>
    <div class="controls">
      <input type="text" name="owner_name" value="{{ forms['owner_name'] }}"
      % if warn_only or is_haopan:
      readonly="readonly"
      % end
      >
      <input type="hidden" name="owner" value="{{ forms['owner'] }}" display_value="{{ forms['owner_name'] }}">
    </div>
  </div>
  <div class="control-group">
    <label class="control-label">开启报警：</label>
    <div class="controls">
      <label for="alert_enable_yes" class="radio inline"><input type="radio" name="alert_enable" value="1" id="alert_enable_yes"
      % if forms['alert_enable']:
      checked="checked"
      % end
      > 是</label>
      <label for="alert_enable_no" class="radio inline"><input type="radio" name="alert_enable" value="0" id="alert_enable_no"
      % if not forms['alert_enable']:
      checked="checked"
      % end
      > 否</label>
    </div>
  </div>
  <div class="control-group">
    <label class="control-label">报警规则：</label>
    <div class="controls">
      <ul id="ul_warning_rules">
      <li>
        <input type="button" value="添加" class="btn oprule" id="btn_add_warning_rule">
      </li>
      </ul>
    </div>
  </div>
  <div class="control-group"
  % if warn_only or is_haopan:
  style="display:none;"
  % end
  >
    <label class="control-label">使用Storm：</label>
    <div class="controls">
      <label for="use_storm_yes" class="radio inline"><input type="radio" name="use_storm" value="1" id="use_storm_yes"
      % if forms['rule']:
      checked="checked"
      % end
      > 是</label>
      <label for="use_storm_no" class="radio inline"><input type="radio" name="use_storm" value="0" id="use_storm_no"
      % if not forms['rule']:
      checked="checked"
      % end
      > 否</label>
    </div>
  </div>
  <div class="control-group" id="cg_storm_datasource" style="display: none;">
    <label class="control-label">数据源：</label>
    <div class="controls">
      <select name="storm_datasource">
      <option value="">请选择</option>
      % for k in storm['datasources'].keys():
      <option value="{{ k }}">{{ k }}</option>
      % end
      </select>
    </div>
  </div>
  <div class="control-group" id="cg_storm_rule_type" style="display: none;">
    <label class="control-label">类型：</label>
    <div class="controls">
      <select name="storm_rule_type">
      <option value="">请选择</option>
      % for k, v in storm['rule_types'].iteritems():
      <option value="{{ k }}">{{ v[0] }}</option>
      % end
      </select>
    </div>
  </div>
  <div class="control-group" id="cg_storm_field" style="display: none;">
    <label class="control-label">字段：</label>
    <div class="controls">
      <select name="storm_field" disabled="disabled">
      <option value="">请选择</option>
      </select>
    </div>
  </div>
  <div class="control-group" id="cg_storm_filters" style="display: none;">
    <label class="control-label">过滤条件：</label>
    <div class="controls">
      <ul id="ul_storm_filters">
      <li>
          <input type="button" value="添加" class="btn opfilter" id="btn_add_filter">
      </li>
      </ul>
    </div>
  </div>
  <div class="control-group" id="cg_storm_misc" style="display: none;">
    <label class="control-label">其它：</label>
    <div class="controls">
      <label for="storm_logging" class="checkbox inline">
        <input type="checkbox" id="storm_logging" name="storm_logging" value="1">
        保存符合过滤条件的记录。
      </label>
    </div>
  </div>
  <div class="control-group">
    <div class="controls">
      <input type="submit" value="提交" class="btn btn-primary" id="btn_submit">&nbsp;&nbsp;&nbsp;
      % if forms['cid']:
      <a href="/admin/category/{{ forms['cid'] }}" class="btn">取消</a>
      % else:
      <a href="/admin/category" class="btn" class="btn">取消</a>
      % end
    </div>
  </div>
</form>

<div class="modal hide fade" id="dlg_warning_rule">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>添加报警规则</h3>
  </div>
  <div class="modal-body">
    <form class="form-horizontal">
      <div class="control-group">
        <label class="control-label">时间范围：</label>
        <div class="controls">
          <input type="text" id="txt_warn_duration_start" class="input-small">
          <input type="text" id="txt_warn_duration_end" class="input-small">
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">报警模式：</label>
        <div class="controls">
          <label for="rb_wt_hwm" class="radio inline">
            <input type="radio" name="warn_type" value="HWM" id="rb_wt_hwm" checked="checked">
            上限
          </label>
          <label for="rb_wt_lwm" class="radio inline">
            <input type="radio" name="warn_type" value="LWM" id="rb_wt_lwm">
            下限
          </label>
          <label for="rb_wt_range" class="radio inline">
            <input type="radio" name="warn_type" value="RANGE" id="rb_wt_range">
            范围
          </label>
        </div>
      </div>
      <div class="control-group" id="cg_warn_hwm">
        <label class="control-label">上限警告/崩溃：</label>
        <div class="controls">
          <input type="text" id="txt_warn_hwm_warning" class="input-small">
          <input type="text" id="txt_warn_hwm_critical" class="input-small">
          <span id="spn_warn_hwm"></span>
        </div>
      </div>
      <div class="control-group" id="cg_warn_lwm" style="display:none;">
        <label class="control-label">下限警告/崩溃：</label>
        <div class="controls">
          <input type="text" id="txt_warn_lwm_warning" class="input-small">
          <input type="text" id="txt_warn_lwm_critical" class="input-small">
          <span id="spn_warn_lwm"></span>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">延迟时间：</label>
        <div class="controls">
          <input type="text" id="txt_warn_latency" class="input-small"> 分钟
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">报警间隔：</label>
        <div class="controls">
          <input type="text" id="txt_warn_interval" class="input-small"> 分钟
        </div>
      </div>
    </form>
  </div>
  <div class="modal-footer">
    <a href="javascript:void(0);" class="btn btn-primary" id="btn_warn_ok">确定</a>
    <a href="javascript:void(0);" class="btn" data-dismiss="modal">取消</a>
  </div>
</div>

% def styles():
<link href="/assets/js/smoothness/jquery-ui-1.9.1.custom.min.css" rel="stylesheet">
<link href="/assets/js/smoothness/jquery-ui-timepicker-addon.css" rel="stylesheet">
% end
<script type="text/javascript" src="/assets/js/jquery-ui-1.9.1.custom.min.js"></script>
<script type="text/javascript" src="/assets/js/jquery.ui.datepicker-zh-CN.min.js"></script>
<script type="text/javascript" src="/assets/js/jquery-ui-timepicker-addon.js"></script>
<script type="text/javascript" src="/assets/js/jquery-ui-timepicker-zh-CN.js"></script>
<script type="text/javascript" src="/assets/js/chart_edit.js"></script>
<script type="text/javascript">
var chartEdit = new ChartEdit({
    storm: {{! storm_json }},
    users: {{! users_json}}
});
% if forms['rule']:
    % if not warn_only:
        $('#use_storm_yes').click();
    % end
    $('select[name="storm_datasource"]').val('{{ forms['rule']['datasource'] }}').change();
    $('select[name="storm_rule_type"]').val('{{ forms['rule']['rule_type'] }}').change();
    % if forms['rule']['field']:
        $('select[name="storm_field"]').val('{{ forms['rule']['field'] }}');
    % end
    % for filter in forms['rule']['filters']:
        chartEdit.addFilter({{! filter }});
    % end
    % if forms['rule']['logging']:
      $(':checkbox[name="storm_logging"]').attr('checked', 'checked');
    % end
% end

% for rule in forms['warn']:
    chartEdit.addWarningRule({{! rule }});
% end
</script>

% rebase admin/layout user=user, active_subtab='category', styles=styles
