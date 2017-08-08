<div class="row-fluid">
  <div id="monitor-container" class="span12 awesome-box content-box container">
    <ul class="nav nav-tabs" id="monitor-tab">
      % for item in lv1_list:
      <li
      % if item['id'] == cate1['id']:
      class="active"
      % end
      ><a href="/{{ tab }}/{{ item['id'] }}">{{ item['name'] }}</a></li>
      % end

      <li class="pull-right"><a href="/monitoring/{{ cate1['id'] }}/{{ cate2['id'] }}">监控模式</a></li>

      % if auth.is_role('sa'):
      <li class="pull-right"><a href="/admin/chart/new/{{ cate2['id'] }}">添加图表</a></li>
      % end
    </ul>

    <div class="tab-content">
      <div class="tab-pane active">

        <ul class="nav nav-pills">
          % for item in lv2_list:
            <li
            % if cate2['id'] == item['id']:
            class="active"
            % end
            ><a href="/{{ tab }}/{{ cate1['id'] }}/{{ item['id'] }}">{{ item['name'] }}</a></li>
          % end

          % if cate1['id'] == anjuke_cid:
            <li><a href="/monitor/haopan/1">好盘竞价</a></li>
            <li><a href="/monitor/haopan/2">好盘定价</a></li>
          % end

          % if get('ops_list'):
          % for item in ops_list[1].values():
            <li><a href="/monitor/suite/{{ item['id'] }}">{{ item['name'] }}</a></li>
          % end
          % end

        </ul>

        <div class="chartlist">
          % if chart_list:
          <ul id="monitor_charts">
            % for item in chart_list:
            <li>
              <div class="title">{{ item['name'] }}</div>
              <a href="/chart/{{ item['id'] }}" target="_blank">
              <img data-original="/graph/haopan/list/{{ item['id'] }}?_={{ millitime }}" src="/assets/img/transparent.gif">
              </a>
            </li>
            % end
          </ul>
          % else:
          <i class="icon-exclamation-sign"></i> 没有找到图表
          % end
        </div>

      </div>
    </div>
  </div>
</div>

<script type="text/javascript" src="/assets/js/jquery.lazyload.min.js"></script>
<script type="text/javascript" src="/assets/js/monitor.js"></script>
<script type="text/javascript">
var haopan = new Monitor({
});
</script>

%rebase layout user=user, active_tab=tab

