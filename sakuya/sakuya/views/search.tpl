<div class="row-fluid">
  <div id="search-container" class="span12 awesome-box content-box container">
    <div
    % if kw:
    class="form-searching"
    % else:
    class="form-not-searching"
    % end
    >
      <form class="form-search" action="" method="get">
        <div class="input-append">
          <input type="text" class="input-xlarge search-query" placeholder="请输入图表标题关键字" name="kw" value="{{ kw }}">
          <button type="submit" class="btn">搜索</button>
        </div>
      </form>
    </div>

    % if kw:
      % if chart_list:

        <div class="chartlist">
          <ul id="chart_list">
            % for item in chart_list:
            <li>
              <div class="title">{{ item['name'] }}</div>
              <a href="/chart/{{ item['id'] }}" target="_blank">
              <img data-original="/graph/haopan/list/{{ item['id'] }}?_={{ millitime }}" src="/assets/img/transparent.gif">
              </a>
            </li>
            % end
          </ul>
        </div>

      % else:
      <i class="icon-exclamation-sign"></i> 没有找到相关图表
      % end
    % end
  </div>
</div>

<script type="text/javascript" src="/assets/js/jquery.lazyload.min.js"></script>
<script type="text/javascript" src="/assets/js/search.js"></script>
<script type="text/javascript">
new Search({
});
</script>
%rebase layout user=user, active_tab='search'
