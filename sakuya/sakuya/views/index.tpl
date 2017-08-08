<div class="row-fluid index-container">
  <div class="span12 front-stats">
  欢迎使用 Knowing 实时业务监控系统，
  目前系统中共有 <span>{{ stats['charts'] }}</span> 张图表，
  <span>{{ stats['users'] }}</span> 位用户，
  共 <span>{{ stats['follows'] }}</span> 次订阅。
  </div>
</div>

<div class="row-fluid index-container">

  <div class="span8 awesome-box content-box" style="padding: 2px;">
    <div id="homepage-slide" class="carousel slide">
      <div class="carousel-inner">
        <div class="active item">
          <h2>“鱼眼”到“先知”</h2>
          <p>从Pyfisheyes到Knowing，不止名字及外观的转变</p>
          <p>新的设计理念，新的后端计算系统</p>
        </div>
        <div class="item">
          <h2>你的监控你做主</h2>
          <p>灵活添加你的监控，轻松设定你的报警</p>
          <p>关注你所关注的数据和异常</p>
        </div>
        <div class="item">
          <h2>强大的实时计算</h2>
          <p>Storm -- 开源实时Hadoop</p>
          <p>分布式的，容错的实时计算系统</p>
          <p>全部展现给你最新鲜及时的数据，方便你第一时间定位问题</p>
        </div>
        <div class="item">
          <h2>更多数据</h2>
          <p>涉及业务，运维，速度，安全</p>
          <p>你想要的，这里都有……</p>
        </div>
      </div>
      <a class="carousel-control left" href="#homepage-slide" data-slide="prev">&lsaquo;</a>
      <a class="carousel-control right" href="#homepage-slide" data-slide="next">&rsaquo;</a>
    </div>
  </div>

  <div class="span4 awesome-box content-box" id="personal-stuff">

  % if user is None:

  <h3 class="home-title">请登录</h3>

  <form class="form-horizontal" method="post" action="{{ login_info['url'] }}/login.php">

  <input type="hidden" name="code" value="{{ login_info['code'] }}">
  <input type="hidden" name="client_secret" value="{{ login_info['client_secret'] }}">
  <input type="hidden" name="grant_type" value="{{ login_info['grant_type'] }}">
  <input type="hidden" name="client_id" value="{{ login_info['client_id'] }}">

  <div class="control-group" style="margin-top: 58px;">
    <label class="control-label" for="inputEmail" style="width: 100px;">用户名：</label>
    <div class="controls" style="margin-left: 120px;">
      <input type="text" id="inputEmail" placeholder="域帐号" name="username">
    </div>
  </div>
  <div class="control-group">
    <label class="control-label" for="inputPassword" style="width: 100px;">密码：</label>
    <div class="controls" style="margin-left: 120px;">
      <input type="password" id="inputPassword" placeholder="密码" name="password">
    </div>
  </div>
  <div class="control-group">
    <div class="controls" style="margin-left: 120px;">
      <button type="submit" class="btn">登录</button>
    </div>
  </div>
  </form>

  % else:

  <div class="more pull-right"><a href="/custom">更多 &gt;&gt;</a></div>
  <ul class="nav nav-tabs">
    <li class="active"><a href="#my-follows" data-toggle="tab">我的订阅</a></li>
    <li><a href="#my-charts" data-toggle="tab">我的图表</a></li>
  </ul>

  <div class="tab-content">
    <div class="tab-pane active" id="my-follows">
      % if my_follows:
        <ul class="chart-list">
        % for item in my_follows:
        <li>
          <i class="icon-picture pull-left"></i>
          <a href="/chart/{{ item['id'] }}">{{ item['name'] }}</a>
        </li>
        % end
        </ul>
      % else:
        <div class="tip">
        你还没有在Knowing中订阅图表。
        </div>
      % end
    </div>
    <div class="tab-pane" id="my-charts">
      % if my_charts:
        <ul class="chart-list">
        % for item in my_charts:
        <li>
          <i class="icon-picture pull-left"></i>
          <a href="/chart/{{ item['id'] }}">{{ item['name'] }}</a>
        </li>
        % end
        </ul>
      % else:
        <div class="tip">
        你还没有在Knowing中创建图表，请<a href="mailto:dl-tech-ops@anjuke.com">联系运维团队</a>。
        </div>
      % end
    </div>
  </div>

  % end

  </div>

</div>

<div class="row-fluid index-container">

  <div class="span4 awesome-box content-box" style="margin-bottom: 50px;">
  <div class="more pull-right"><a href="/monitor">更多 &gt;&gt;</a></div>
  <h3 class="home-title">监控</h3>
  <ul class="monitor-list">
    % for item in top_monitor:
    <li>
      <span class="badge pull-right" title="{{ item['num'] }}次订阅">{{ item['num'] }}</span>
      <i class="icon-picture pull-left"></i>
      <a href="/chart/{{ item['id'] }}">{{ item['name'] }}</a>
    </li>
    % end
  </ul>
  </div>

  <div class="span4 awesome-box content-box">
  <div class="more pull-right"><a href="/speed">更多 &gt;&gt;</a></div>
  <h3 class="home-title">速度</h3>
  <ul class="monitor-list">
    % for item in top_speed:
    <li>
      <span class="badge pull-right" title="{{ item['num'] }}次订阅">{{ item['num'] }}</span>
      <i class="icon-picture pull-left"></i>
      <a href="/chart/{{ item['id'] }}">{{ item['name'] }}</a>
    </li>
    % end
  </ul>
  </div>

  <div id="latest-warnings" class="span4 awesome-box content-box">
    <div class="more pull-right"><a href="/alert">更多 &gt;&gt;</a></div>
    <h3 class="home-title">最新报警</h3>

    <ul>
      %for item in events:
      <li>
        <span class="pull-right time">{{ item['time'] }}</span>
        <span class="pull-left leading"
        % if item['type'] == 'Critical':
        style="background-color:#B94A48;"
        % else:
        style="background-color:#F89406;"
        % end
        >&nbsp;</span>
        <a href="/chart/{{ item['cid'] }}" target="_blank" class="title" title="{{item['info']}}">{{item['info']}}</a>
      </li>
      %end
    </ul>
  </div>

</div>

%rebase layout user=user, active_tab='index'
