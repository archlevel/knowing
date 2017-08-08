<!DOCTYPE html>
<html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
</head>
<body style="margin:0;padding:0;">
<div style="width:600px;height:220px;">
  <div style="width:600px;height:200px;" id="div_chart"></div>
  <div style="width:600px;height:20px;line-height:20px;font-size:14px;text-align:center;">
    慢查询趋势线
  </div>
</div>
<script type="text/javascript" src="/assets/js/amcharts.js"></script>
<script type="text/javascript">
var chart_data = {{! data }};
AmCharts.ready(function() {

    var chart = new AmCharts.AmSerialChart();
    chart.dataProvider = chart_data;
    chart.categoryField = "date";
    chart.marginTop = 0;

    var categoryAxis = chart.categoryAxis;
    categoryAxis.gridColor = "#000000";
    categoryAxis.axisColor = "#555555";
    categoryAxis.gridAlpha = 0;

    var slow_queryAxis = new AmCharts.ValueAxis();
    slow_queryAxis.title = "慢查询数";
    slow_queryAxis.gridAlpha = 0.05;
    slow_queryAxis.axisAlpha = 0;
    slow_queryAxis.inside = true;
    chart.addValueAxis(slow_queryAxis);

    var rewr_queryAxis = new AmCharts.ValueAxis();
    rewr_queryAxis.title = "总查询数";
    rewr_queryAxis.gridAlpha = 0;
    rewr_queryAxis.position = "right";
    rewr_queryAxis.inside = true;
    rewr_queryAxis.axisAlpha = 0;
    chart.addValueAxis(rewr_queryAxis);

    var slow_queryGraph = new AmCharts.AmGraph();
    slow_queryGraph.valueField = "slow";
    slow_queryGraph.type = "line";
    slow_queryGraph.valueAxis = slow_queryAxis;
    slow_queryGraph.lineColor = "#CC0000";
    slow_queryGraph.balloonText = "慢查询：[[value]]";
    slow_queryGraph.lineThickness = 1;
    slow_queryGraph.bullet = "square";
    slow_queryGraph.bulletSize = 6;
    chart.addGraph(slow_queryGraph);

    var rewr_queryGraph = new AmCharts.AmGraph();
    rewr_queryGraph.valueField = "query";
    rewr_queryGraph.type = "column";
    rewr_queryGraph.fillAlphas = 0.1;
    rewr_queryGraph.valueAxis = rewr_queryAxis;
    rewr_queryGraph.balloonText = "总查询：[[value]]";
    rewr_queryGraph.lineColor = "#000000";
    rewr_queryGraph.lineAlpha = 0;
    chart.addGraph(rewr_queryGraph);

    var chartCursor = new AmCharts.ChartCursor();
    chartCursor.zoomable = false;
    chartCursor.cursorAlpha = 0;
    chart.addChartCursor(chartCursor);

    chart.write('div_chart');
});
</script>
</body>
</html>
