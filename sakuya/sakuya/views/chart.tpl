<div class="row-fluid">
  <div id="monitor-container" class="span12 awesome-box content-box container">
    <div class="tab-content">
      <div class="tab-pane active" id="chart">
        <div id="chart-info-container">

          % if breadcrumbs:
          <ul class="breadcrumb" style="margin-bottom:0;">
            % for item in breadcrumbs:
            <li>
            <a href="{{ item['link'] }}">{{ item['name'] }}</a>
            % if item['link'] != breadcrumbs[-1]['link']:
            <span class="divider">/</span>
            % end
            </li>
            % end
          </ul>
          % end

          <div id="chart-title">
            <h3>{{ title }}
             %if user is not None:
              % if not is_haopan:
              <input type="button" value="认领" class="btn pull-right" id="btn_ack" style="margin-left: 10px;">
              % end

              % if following:
              <input type="button" value="取消订阅" class="btn btn-info pull-right" id="btn_follow" style="margin-left: 10px;">
              % else:
              <input type="button" value="订阅图表" class="btn btn-success pull-right" id="btn_follow" style="margin-left: 10px;">
              % end

              % if is_admin:
              % if status:
              <input type="button" value="隐藏图表" vstatus="0" class="btn btn-info pull-right" id="btn_hide" >
              % else:
              <input type="button" value="取消隐藏" vstatus="1" class="btn btn-success pull-right" id="btn_hide">
              % end
              % end

             % end
            <a href="#chart-info" class="pull-right warning-tips"
            % if not following:
            style="display: none;"
            % end
            >请到下方订阅报警规则</a>
            </h3>
            <form class="form-inline">
              日期： <input type="text" class="input-small" value="{{ dt_range[0] }}" id="dt_date">&nbsp;&nbsp;&nbsp;&nbsp;
              范围： <input type="text" class="input-small" value="{{ dt_range[0] }}" id="dt_start">
              - <input type="text" class="input-small" value="{{ dt_range[0] }}" id="dt_end">&nbsp;&nbsp;&nbsp;&nbsp;

              <div class="btn-group">
                  <input type="button" class="btn" id="btn_reset" value="提交">
                  <input type="button" class="btn" id="btn_refresh" value="刷新">
              </div>&nbsp;&nbsp;&nbsp;&nbsp;

              <div class="btn-group" id="btngrp_date_range">
                <input type="button" class="btn" dt_date="{{ dt_range[0] }}" value="今天">
                <input type="button" class="btn" dt_date="{{ dt_range[-1] }}" value="昨天">
                <input type="button" class="btn" dt_start="{{ dt_range[-2] }}" value="近3天">
                <input type="button" class="btn" dt_start="{{ dt_range[-6] }}" value="近7天">
                <input type="button" class="btn" dt_start="{{ dt_range[-14] }}" value="近15天">
                <input type="button" class="btn" dt_start="{{ dt_range[-29] }}" value="近30天">
              </div>&nbsp;&nbsp;&nbsp;&nbsp;

              <label for="cb_daily" class="checkbox">
                <input type="checkbox" id="cb_daily"> 日趋线
              </label>
            </form>
          </div>

          <div class="main-chart" id="div_main_chart"></div>

          <div id="chart-option-container">
            <ul class="nav nav-tabs" id="chart-tab">
              <li class="active" ><a href="#chart-info" data-toggle="tab">信息</a></li>
              <li><a href="#chart-data" data-toggle="tab">数据</a></li>
              <li><a href="#chart-settings" data-toggle="tab">配置</a></li>
              % if defined('warning_logs'):
              <li><a href="#warning-logs" data-toggle="tab">报警日志</a></li>
              % end
            </ul>
            <div class="tab-content">
              <div class="tab-pane active" id="chart-info">
                <table class="table">
                  <tr><th width="100" style="text-align: right;">图表名称：</th><td>{{ title }}</td></tr>
                  <tr>
                    % if defined('storm_info'):
                    <th style="text-align: right;">Storm：</th>
                    <td>
                        数据源：{{ storm_info['datasource'] }}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        类型：{{ storm_info['rule_type'] }}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        % if 'field' in storm_info:
                          字段：{{ storm_info['field'] }}
                        % end
                        <br>
                        过滤条件：
                        <table id="storm_filters">
                          % for item in storm_info['filters']:
                          <tr>
                            <th>&nbsp;&nbsp;&nbsp;&nbsp;字段：</th>
                            <td>{{ item['field'] }}</td>
                            <th>操作符：</th>
                            <td>
                              {{ item['operator'] }}
                              % if item['negative']:
                              （取反）
                              % end
                            </td>
                            <th>内容：</th>
                            <td width="400">{{ item['content'] }}</td>
                          </tr>
                          % end
                        </table>
                    </td>
                    % else:
                    <th style="text-align: right;">WebAPI：</th>
                    <td>
                      curl -d "tid={{ id }}&dt=2012-10-24 18:12&data=100" http://10.10.3.43:9075/api/add-data
                      % if defined('api_ip') and defined('api_ts'):
                      <br>最近调用：IP {{ api_ip }}, 时间 {{ api_ts }}
                      % end
                    </td>
                    % end
                  </tr>
                  <tr><th style="text-align: right;">报警规则：</th><td>
                    % if defined('alert_info'):
                      <table class="table table-condensed table-alert-rules">
                      % for alert_item in alert_info:
                      <tr>
                        <td rel="popover" data-content="{{ alert_item['subscriber'] }}" style="cursor:pointer;">
                        {{ alert_item['duration_start'] }}～{{ alert_item['duration_end'] }},
                        % if alert_item['type'] == 'HWM':
                          上限模式,
                          警告 {{ alert_item['hwm_warning'] }},
                          崩溃 {{ alert_item['hwm_critical'] }},
                        % elif alert_item['type'] == 'LWM':
                          下限模式,
                          警告 {{ alert_item['lwm_warning'] }},
                          崩溃 {{ alert_item['lwm_critical'] }},
                        % elif alert_item['type'] == 'RANGE':
                          范围模式,
                          警告 -{{ alert_item['lwm_warning'] }}%～{{ alert_item['hwm_warning'] }}%,
                          崩溃 -{{ alert_item['lwm_critical'] }}%～{{ alert_item['hwm_critical'] }}%,
                        % else:
                          未知报警模式
                        % end
                        延迟 {{ alert_item['latency'] }} 分钟,
                        间隔 {{ alert_item['interval'] }} 分钟
                        </td>
                        <td class="align-right" width="100">
                        <label for="alert_item_id_{{ alert_item['id'] }}"
                        % if not following:
                        style="display: none;"
                        % end
                        >
                        <input type="checkbox" value="{{ alert_item['id'] }}" id="alert_item_id_{{ alert_item['id'] }}"
                        % if following and recv_warning:
                          % if recv_rules == 'all':
                          checked="checked" disabled="disabled"
                          % elif alert_item['id'] in recv_rules:
                          checked="checked"
                          % end
                        % end
                        > 接收报警
                        </label>
                        </td>
                        % if alert_item == alert_info[0]:
                        <td rowspan="{{ len(alert_info) }}" class="align-right valign-center" width="250">
                          <label for="alert_item_all"
                          % if not following:
                          style="display: none;"
                          % end
                          >
                          <input type="checkbox" value="all" id="alert_item_all"
                          % if following and recv_warning and recv_rules == 'all':
                          checked="checked"
                          % end
                          > 全部接收（包括日后新增的规则）
                          </label>
                        </td>
                        % end
                      </tr>
                      % end
                      </table>
                    % else:
                    关闭
                    % end
                  </td></tr>
                  <tr><th style="text-align: right;">创建时间：</th><td>{{ owner }} 创建于 {{ createtime }}</td></tr>
                </table>
              </div>

              <div class="tab-pane" id="chart-data">
              <table class="table table-condensed">
                <tr>
                  <th>编号</th>
                  <th>日期</th>
                  <th>小时</th>
                  <th>分钟</th>
                </tr>
              </table>
              </div>

              <div class="tab-pane" id="chart-settings">
              <table class="table" id="tbl_chart_settings">
              <tr>
                <th width="100">调整图表：</th>
                <td>
                  下限：<input type="text" id="ylim_min" class="input input-small">&nbsp;&nbsp;&nbsp;
                  上限：<input type="text" id="ylim_max" class="input input-small">
                  <input type="button" class="btn" value="刷新" id="btn_ylim">
                </td>
              </tr>
              % if editable:
              <tr>
                <th>管理员操作：</th>
                <td>
                  <a href="/admin/chart/edit/{{ id }}" class="btn">修改</a>
                  % if deletable:
                  <a href="/admin/chart/edit/{{ id }}?copy=1" class="btn">复制</a>
                  <a href="/admin/chart/delete/{{ id }}" class="btn" onclick="return confirm('确认要删除吗？');">删除</a>
                  % end
                </td>
              </tr>
              % end
              </table>
              </div>

              % if defined('warning_logs'):
              <div class="tab-pane" id="warning-logs">
                <table class="table table-condensed table-hover">
                <tr>
                  <th width="100">编号</th>
                  <th width="100">级别</th>
                  <th>内容</th>
                  <th width="150">时间</th>
                </tr>
                % for item in warning_logs:
                  <tr>
                    <td>{{ item['id'] }}</td>
                    <td>
                      % if item['level'] == 'critical':
                      <label class="label label-important" style="width: 40px; text-align: center;">严重</label>
                      % else:
                      <label class="label label-warning" style="width: 40px; text-align: center;">警告</label>
                      % end
                    </td>
                    <td>{{ item['content'] }}</td>
                    <td>{{ item['time'] }}</td>
                  </tr>
                % end
                </table>
              </div>
              % end

            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="modal hide" id="dlg_detail">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3></h3>
  </div>
  <div class="modal-body">
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">关闭</a>
  </div>
</div>

% if user is not None and not is_haopan:
<div class="modal hide fade" id="dlg_ack">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>图表认领</h3>
  </div>
  <div class="modal-body">
    <div class="alert alert-info">
      <strong>什么是图表认领？</strong> 该功能主要提供给各事业部，将你们所关心的图表移动到正确的栏目，并将图表所有者修改为自己，以便设置报警规则。
    </div>
    <form class="form-horizontal">
      <div class="control-group">
        <label class="control-label">一级栏目：</label>
        <div class="controls">
          <select name="cl2">
            % for item in cl2s:
            <option value="{{ item[0] }}"
            % if cur_cl2 == item[0]:
            selected="selected"
            % end
            >{{ item[1] }}</option>
            % end
          </select>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">二级栏目：</label>
        <div class="controls">
          <select name="cl3" class="input-medium">
            <option value="">新建栏目</option>
            % for item in cl3s[cur_cl2]:
            <option value="{{ item[0] }}"
            % if cur_cl3 == item[0]:
            selected="selected"
            % end
            >{{ item[1] }}</option>
            % end
          </select>
          <input type="text" class="input-medium" style="display: none;" name="cl3_new">
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">认领人：</label>
        <div class="controls">
          <input type="text" value="{{ user['truename'] }}" readonly="readonly" class="input-small" placeholder="栏目名称">
        </div>
      </div>
    </form>
  </div>
  <div class="modal-footer">
    <a href="javascript:void(0);" class="btn btn-primary" id="btn_ack_submit">确定</a>
    <a href="javascript:void(0);" class="btn" data-dismiss="modal">关闭</a>
  </div>
</div>
% end

% def styles():
<link href="/assets/js/smoothness/jquery-ui-1.9.1.custom.min.css" rel="stylesheet">
% end
<script type="text/javascript" src="/assets/js/jquery-ui-1.9.1.custom.min.js"></script>
<script type="text/javascript" src="/assets/js/jquery.ui.datepicker-zh-CN.min.js"></script>
<script type="text/javascript" src="/assets/js/highcharts.js"></script>
<script type="text/javascript" src="/assets/js/chart_view.js"></script>
<script type="text/javascript">
new ChartView({
  % if is_haopan and id2:
  series: [
      [{{ id }},   0, '{{ t1_title }}', '#4572A7'],
      [{{ id2 }},  0, '{{ t2_title }}', '#89A54E'],
      [{{ id }},  -7, '{{ t3_title }}', 'gray'],
      [{{ id2 }}, -7, '{{ t4_title }}', 'silver']
  ],
  % else:
  series: [
      [{{ id }},  0, '当日', '#4572A7'],
      [{{ id }}, -7, '上周', 'gray'],
  ],
  % end
  curDate: '{{ dt_range[0] }}',
  cl3s: {{! cl3s_json }},
  chartId: {{ id }}
});
</script>

% rebase layout user=user, active_tab=active_tab, styles=styles
