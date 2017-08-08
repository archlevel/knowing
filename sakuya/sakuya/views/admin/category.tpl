% include admin/category_breadcrumbs breadcrumbs=breadcrumbs, cid=(cat['id'] if not cat['isp'] else 0)

% if cat['isp']:

<table class="table table-hover">
    <tr>
        <th width="70">ID</th>
        <th width="350">名称</th>
        <th>子栏目数量</th>
        <th>图表数量</th>
        <th width="120">操作</th>
    </tr>
    % if category_list:
    % for item in category_list:
    <tr>
        <td>{{ item['id'] }}</td>
        <td><a href="/admin/category/{{ item['id'] }}">{{ item['name'] }}</a></td>
        <td>{{ item['num_subcategories'] }}</td>
        <td>{{ item['num_charts'] }}</td>
        <td>
            <input type="button" class="btn btn-small" value="编辑" edit_category="{{ item['id'] }}">
            <input type="button" value="删除"
            % if item['show_delete']:
            class="btn btn-small" delete_category="{{ item['id'] }}"
            % else:
            class="btn btn-small disabled"
            % end
            >
        </td>
    </tr>
    % end
    % else:
    <tr><td colspan="5">没有找到子栏目，请创建。</td></tr>
    % end
</table>

<form action="/admin/category/add/{{ cat['id'] }}" method="post" class="form-horizontal">
    <legend>新建栏目</legend>
    <div class="control-group">
        <label class="control-label">名称：</label>
        <div class="controls">
            <input type="text" placeholder="名称" name="name">
        </div>
    </div>
    <div class="control-group">
        <label class="control-label">是否为父栏目：</label>
        <div class="controls">
            <label for="isp_yes" class="radio"><input type="radio" name="isp" value="1" id="isp_yes" checked="checked"> 是，该栏目包含子栏目。</label>
            <label for="isp_no" class="radio"><input type="radio" name="isp" value="0" id="isp_no"> 否，该栏目仅包含图表。</label>
        </div>
    </div>
    <div class="control-group">
        <div class="controls">
            <input type="submit" value="提交" class="btn btn-primary" id="btn_submit">
        </div>
    </div>
</form>

<script type="text/javascript">
$('#btn_submit').click(function() {
    var txtName = $(':text[name="name"]');
    if (!txtName.val()) {
        alert('栏目名称不能为空。');
        txtName.focus();
        return false;
    }
});
$(':button[delete_category]').click(function() {
    if (!confirm('确定要删除这个栏目吗？')) {
        return false;
    }
    window.location = '/admin/category/delete/' + $(this).attr('delete_category');
});
$(':button[edit_category]').click(function() {
    var name = prompt('请输入新的栏目名称：');
    if (name) {
        var url = '/admin/category/edit/' + $(this).attr('edit_category'),
            data = {name: name};
        $.post(url, data, function(response) {
            if (response.status == 'ok') {
                window.location.reload();
            } else {
                alert(response.msg);
            }
        }, 'json');
    }
});
</script>

% else:

<table class="table table-hover">
<tr>
    <th width="70">ID</th>
    <th width="350">名称</th>
    <th>数据源</th>
    <th>订阅人数</th>
    <th width="160">操作</th>
</tr>
% if chart_list:
% for item in chart_list:
<tr>
    <td>{{ item['id'] }}</td>
    <td><a href="/chart/{{ item['id'] }}">{{ item['name'] }}</a></td>
    <td><span class="label label-{{ item['powered_by'][1] }}">{{ item['powered_by'][0] }}</span></td>
    <td>{{ item['num_followers'] }}</td>
    <td>
        <input type="button" class="btn btn-small" value="编辑" edit_chart="{{ item['id'] }}">
        <input type="button" class="btn btn-small" value="复制" copy_chart="{{ item['id'] }}">
        <input type="button" value="删除" class="btn btn-small" delete_chart="{{ item['id'] }}">
    </td>
</tr>
% end
% else:
<tr><td colspan="5">没有找到图表，请创建。</td></tr>
% end
</table>

<script type="text/javascript">
$(':button[edit_chart]').click(function() {
    window.location = '/admin/chart/edit/' + $(this).attr('edit_chart');
});
$(':button[copy_chart]').click(function() {
    window.location = '/admin/chart/edit/' + $(this).attr('copy_chart') + '?copy=1';
});
$(':button[delete_chart]').click(function() {
    if (!confirm('确定要删除这张图表吗？')) {
        return false;
    }
    window.location = '/admin/chart/delete/' + $(this).attr('delete_chart');
});
</script>

% end

% rebase admin/layout user=user, active_subtab='category'
