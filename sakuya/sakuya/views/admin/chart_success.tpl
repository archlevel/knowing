% include admin/category_breadcrumbs breadcrumbs=breadcrumbs, cid=cid

<h3 id="h3_chart_edit_title">图表添加成功</h3><hr>

<p>您已成功添加图表，可以通过调用以下API添加数据：</p>
<pre>
curl -d "tid={{ id }}&dt=2012-10-24 18:12&data=100" \
 http://10.10.3.43:9075/api/add-data
</pre>
<p>
<strong>tid:</strong> 图表ID，即 <strong>{{ id }}</strong><br>
<strong>dt:</strong> 时间日期，格式为 <strong>%Y-%m-%d %H:%S</strong><br>
<strong>data:</strong> 数据，整型
</p>

% rebase admin/layout user=user, active_subtab='category'
