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
    <title>Knowing</title>
    <link href="/assets/css/screen.css" rel="stylesheet">
    <link href="/assets/css/bootstrap.min.css" rel="stylesheet">
    <!-- <link href="/assets/css/docs.css" rel="stylesheet"> -->
    <link href="/assets/css/sakuya.css" rel="stylesheet">
    % if get('styles'):
    % styles()
    % end
    <script type="text/javascript" charset="utf-8" src="/assets/js/jquery-1.8.1.min.js"></script>
    <script type="text/javascript" charset="utf-8" src="/assets/js/bootstrap.min.js"></script>
    <script type="text/javascript" charset="utf-8" src="/assets/js/sakuya.js"></script>
  </head>

  <body>
    %include header user=user, active_tab=active_tab
    <div class="container" id="">
    %include
    </div>
    %include footer
  </body>
</html>

<!-- codename: sakuya; styled by AleiPhoenix (A.K.A. AReverie) -->
