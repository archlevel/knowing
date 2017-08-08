<ul class="breadcrumb">
    % for item in breadcrumbs:
    <li
    % if item['active']:
    class="active"
    % end
    >
    % if item['active']:
    {{ item['name'] }}
    % else:
    <a href="{{ item['link'] }}">{{ item['name'] }}</a> <span class="divider">/</span>
    % end
    </li>
    % end
    <li class="pull-right">
    % if get('cid'):
    <input type="button" value="新建图表" class="btn btn-primary btn-small" onclick="window.location = '/admin/chart/new/{{ cid }}';">
    % else:
    <input type="button" value="新建图表" class="btn btn-primary btn-small" onclick="window.location = '/admin/chart/new';">
    % end
    </li>
</ul>
