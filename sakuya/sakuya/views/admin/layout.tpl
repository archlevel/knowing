<div class="row-fluid">
  <div id="admin-container" class="span12 awesome-box content-box container">

    <ul class="nav nav-tabs" id="admin-tab">
      <li
      % if active_subtab == 'category':
      class="active"
      % end
      ><a href="/admin/category">栏目管理</a></li>
    </ul>

    <div class="tab-content">
      <div class="tab-pane active">
      % include
      </div>
    </div> <!-- .tab-content -->

  </div>
</div>

% rebase layout user=user, active_tab='admin', styles=get('styles')
