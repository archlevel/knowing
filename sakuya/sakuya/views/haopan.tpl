<div class="row-fluid">
  <div id="haopan-container" class="span12 awesome-box content-box container">
    <ul class="nav nav-tabs" id="monitor-tab">
      % for item in lv1_list:
      <li
      % if item['id'] == anjuke_cid:
      class="active"
      % end
      ><a href="/monitor/{{ item['id'] }}">{{ item['name'] }}</a></li>
      % end
    </ul>

    <div class="tab-content">
      <div class="tab-pane active">

        <ul class="nav nav-pills">
          % for item in lv2_list:
            <li><a href="/monitor/{{ cate1['id'] }}/{{ item['id'] }}">{{ item['name'] }}</a></li>
          % end

          % if cate1['id'] == anjuke_cid:
            <li
            % if prod == 1:
            class="active"
            % end
            ><a href="/monitor/haopan/1">好盘竞价</a></li>
            <li
            % if prod == 2:
            class="active"
            % end
            ><a href="/monitor/haopan/2">好盘定价</a></li>
          % end
        </ul>

        <div class="haopan-panel">

          <div class="well">
            <table cellpadding="0" cellspacing="0">
            <tr>
              <th>图表：</th>
              <td>
                  <ul class="nav nav-pills custom" id="flt_charts">
                  <li class="active"><a href="javascript:void(0);" fltid="1">曝光量</a></li>
                  <li class="active"><a href="javascript:void(0);" fltid="2">点击量</a></li>
                  <li class="active"><a href="javascript:void(0);" fltid="4">扣费量</a></li>
                  </ul>
              </td>
            </tr>
            <tr>
              <th width="70">城市：</th>
              <td>
                  <ul class="nav nav-pills custom" id="flt_cities">
                  <li class="active"><a href="javascript:void(0);" fltid="sum">汇总</a></li>
                  <li><a href="javascript:void(0);" fltid="all">全部</a></li>
                  % for item in cities:
                  <li><a href="javascript:void(0);" fltid="{{ item[0] }}">{{ item[1] }}</a></li>
                  % end
                  </ul>
              </td>
            </tr>
            <tr>
              <th>渠道：</th>
              <td>
                  <ul class="nav nav-pills custom" id="flt_channels">
                  <li class="active"><a href="javascript:void(0);" fltid="sum">汇总</a></li>
                  <li><a href="javascript:void(0);" fltid="all">全部</a></li>
                  % for item in channels:
                  <li><a href="javascript:void(0);" fltid="{{ item[0] }}">{{ item[1] }}</a></li>
                  % end
                  </ul>
              </td>
            </tr>
            <tr>
              <th>展示点：</th>
              <td>
                  <ul class="nav nav-pills custom" id="flt_entries">
                  <li class="active"><a href="javascript:void(0);" fltid="sum">汇总</a></li>
                  <li>
                    <select class="input-medium" style="height: 26px; font-size: 12px;" id="sel_entries">
                      <option value="">添加展示点</option>
                      % for item in entries:
                      <option value="{{ item[0] }}">{{ item[1] }}</option>
                      % end
                    </select>
                  </li>
                  </ul>
              </td>
            </tr>
            </table>
          </div>

          <ul id="haopan_charts"></ul>

        </div>
      </div>
    </div>
  </div>
</div>

<script type="text/javascript" src="/assets/js/jquery.lazyload.min.js"></script>
<script type="text/javascript" src="/assets/js/haopan.js"></script>
<script type="text/javascript">
var haopan = new Haopan({
    prod: {{ prod }}
});
</script>

%rebase layout user=user, active_tab='monitor'
