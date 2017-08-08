<div class="row-fluid">
  <div id="custom_container" class="span12 awesome-box content-box container">

    <ul class="nav nav-tabs">
      <li
      % if active_subtab == 'follow':
      class="active"
      % end
      ><a href="/custom/follow">我的订阅</a></li>
      <li
      % if active_subtab == 'profile':
      class="active"
      % end
      ><a href="/custom/profile">我的信息</a></li>
    </ul>

    <div class="tab-content">
      <div class="tab-pane active">
      % include
      </div>
    </div> <!-- .tab-content -->

  </div>
</div>

% rebase layout user=user, active_tab='custom'
