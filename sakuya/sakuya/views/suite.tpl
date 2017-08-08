<div class="row-fluid">
  <div id="monitor-container" class="span12 awesome-box content-box container">

    <ul class="nav nav-tabs" id="monitor-tab">
      % for item in pri_list[1].values():
      <li
      % if item['id'] == pri_cate[1]['id']:
      class="active"
      % end
      ><a href="/monitor/{{ item['id'] }}">{{ item['name'] }}</a></li>
      % end
    </ul>

    <div class="tab-content">
      <div class="tab-pane active">

        <ul class="nav nav-pills">
          % for item in pri_list[2].values():
            <li><a href="/monitor/{{ pri_cate[1]['id'] }}/{{ item['id'] }}">{{ item['name'] }}</a></li>
          % end

          % if len(sec_list) > 1 and sec_list[1]:
          % for item in sec_list[1].values():
            <li
            % if item['id'] == sec_cate[1]['id']:
            class="active"
            % end
            ><a href="/monitor/suite/{{ item['id'] }}">{{ item['name'] }}</a></li>
          % end
          % end
        </ul>

        <ul class="suite-category well nav nav-list">
        % if len(sec_list) > 2 and sec_list[2]:
        % for item2 in sec_list[2].values():

          % if item2['id'] == sec_cate[2]['id']:
          <li>
            <a href="/monitor/suite/{{ sec_cate[1]['id'] }}/{{ item2['id'] }}"><i class="icon-folder-open"></i> {{ item2['name'] }}</a>
          </li>
            % if len(sec_list) > 3 and sec_list[3]:
            % for item3 in sec_list[3].values():
              <li
              % if item3['id'] == sec_cate[3]['id']:
              class="active"
              % end
              >
                <a href="/monitor/suite/{{ sec_cate[1]['id'] }}/{{ item2['id'] }}/{{ item3['id'] }}"><i class="icon-blank"></i> {{ item3['name'] }}</a>
              </li>
            % end
            % end
          % else:
          <li>
            <a href="/monitor/suite/{{ sec_cate[1]['id'] }}/{{ item2['id'] }}"><i class="icon-folder-close"></i> {{ item2['name'] }}</a>
          </li>
          % end

        % end
        % end
        </ul>

        <div class="suite-charts">

          <!--<div class="suite-chart-item">
            <div class="button-group">
              <input type="button" value="今天" class="btn btn-small"><br>
              <input type="button" value="昨天" class="btn btn-small"><br>
              <input type="button" value="近3天" class="btn btn-small"><br>
              <input type="button" value="近7天" class="btn btn-small"><br>
              <input type="button" value="近15天" class="btn btn-small"><br>
              <input type="button" value="详情" class="btn btn-small">
            </div>
            <div id="chart_1" style="width:850px;height:320px;"></div>
          </div>-->

        </div>

      </div>
    </div>

  </div>
</div>

<div class="modal hide fade" id="dlg_detail">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3></h3>
  </div>
  <div class="modal-body">
    <div id="chart_detail" style="width:500px;height:300px;"></div>
  </div>
</div>

<script type="text/javascript" src="/assets/js/highcharts.js"></script>
<script type="text/javascript" src="/assets/js/suite.js"></script>
<script type="text/javascript">
new Suite({
    charts: {{! js_charts }},
    curDate: '{{ cur_date }}',
    hasDetail: {{ 'true' if has_detail else 'false' }}
});
</script>

% rebase layout user=user, active_tab='monitor'
