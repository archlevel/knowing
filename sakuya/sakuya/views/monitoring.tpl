<!DOCTYPE html>
<!--
welcome to the source of
 _  __                    _
| |/ /_ __   _____      _(_)_ __   __ _
| ' /| '_ \ / _ \ \ /\ / / | '_ \ / _` |
| . \| | | | (_) \ V  V /| | | | | (_| |
|_|\_\_| |_|\___/ \_/\_/ |_|_| |_|\__, |
                                  |___/
page
-->
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <title>监控模式 - Knowing</title>
    <link href="/assets/css/screen.css" rel="stylesheet">
    <link href="/assets/css/bootstrap.min.css" rel="stylesheet">
    <link href="/assets/css/sakuya.css" rel="stylesheet">
    <script type="text/javascript" charset="utf-8" src="/assets/js/jquery-1.8.1.min.js"></script>
    <script type="text/javascript" charset="utf-8" src="/assets/js/bootstrap.min.js"></script>
  </head>

  <body style="padding: 0">
    <div class="container" id="">

<div class="row-fluid">
  <div id="monitoring-container" class="span12 awesome-box content-box container">
    <ul id="ul_charts"></ul>
  </div>
</div>

<div style="position:fixed;right:15px;top:10px;">
  <a href="/"><i class="icon-home"></i> 返回首页</a>
</div>

<script type="text/javascript" src="/assets/js/jquery.lazyload.min.js"></script>
<script type="text/javascript" src="/assets/js/monitoring.js"></script>
<script type="text/javascript">

var monitoring = new Monitoring({'cate':'{{! cate }}'});
</script>

    </div>
  </body>
</html>

<!-- codename: sakuya; styled by AleiPhoenix (A.K.A. AReverie) -->
