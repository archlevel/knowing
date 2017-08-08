<div class="navbar navbar-inverse navbar-fixed-top" id="topbar">
  <div class="navbar-inner">
    <div class="container" style="width: 1270px;">
      <a class="brand" href="/"><span class="knowing-heading">Knowing</span></a>

      <div id="header_warn" class="pull-left ok" rel="tooltip"></div>

      <ul class="nav">

        <li
        %if active_tab == 'index':
        class="active"
        %end
        ><a href="/">首页</a></li>
        <li
        %if active_tab == 'monitor':
        class="active"
        %end
        ><a href="/monitor">监控</a></li>
        <li
        %if active_tab == 'alert':
        class="active"
        %end
        ><a href="/alert">报警</a></li>
        <li
        % if active_tab == 'speed':
        class="active"
        % end
        ><a href="/speed">速度</a></li>
        <li
        % if active_tab == 'security':
        class="active"
        % end
        ><a href="/security">安全</a></li>
        <li
        % if active_tab == 'search':
        class="active"
        % end
        ><a href="/search">搜索</a></li>
        <li
        %if active_tab == 'custom':
        class="active"
        %end
        ><a href="/custom">个人中心</a></li>
<li><a href="http://zabbix10.corp.anjuke.com" target="_blank">zabbix10</a></li>
<li><a href="http://zabbix20.corp.anjuke.com" target="_blank">zabbix20</a></li>
      </ul>

      <ul id="account-info" class="nav pull-right">

        <li>
          <form class="navbar-form pull-right" action="/search" method="get" id="nav-search">
          <input type="text" class="input-medium search-query" placeholder="请输入图表标题关键字" name="kw">
          </form>
        </li>

        %if user is None:
        <li><a href="/login">登录</a></li>
        %else:
        <li><a href="/custom/profile">你好，{{user['truename']}}！</a></li>
        <li><a href="/admin">管理</a></li>
        <li><a href="/logout">注销</a></li>
        %end
      </ul>

    </div>
  </div>
</div>

<div id="header_warn_content" style="display: none;"></div>
