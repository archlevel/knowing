<!DOCTYPE html>
<html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
</head>
<body style="margin:0;padding:0;">
<div style="width:600px;height:220px;">
  <div style="width:600px;height:200px;" id="div_chart"></div>
  <div style="width:600px;height:20px;line-height:20px;font-size:14px;text-align:center;">
    日读写量趋势图
  </div>
</div>
<script type="text/javascript" src="/assets/js/amcharts.js"></script>
<script type="text/javascript">
var chart_data = {{! data }};
AmCharts.ready(function() {

    var chart = new AmCharts.AmSerialChart();
    chart.dataProvider = chart_data;
    chart.categoryField = "date";
    //chart.marginTop = 0;

    var categoryAxis = chart.categoryAxis;
    categoryAxis.gridColor = "#000000";
    categoryAxis.axisColor = "#555555";
    categoryAxis.gridAlpha = 0;

    var slow_queryAxis = new AmCharts.ValueAxis();
    slow_queryAxis.gridAlpha = 0.05;
    slow_queryAxis.axisAlpha = 0;
    //slow_queryAxis.inside = true;
    slow_queryAxis.unit = '亿';
    chart.addValueAxis(slow_queryAxis);

    var rewr_queryAxis = new AmCharts.ValueAxis();
    rewr_queryAxis.gridAlpha = 0;
    rewr_queryAxis.position = "right";
    //rewr_queryAxis.inside = true;
    rewr_queryAxis.unit = '亿';
    rewr_queryAxis.axisAlpha = 0;
    chart.addValueAxis(rewr_queryAxis);

    var slow_queryGraph = new AmCharts.AmGraph();
    slow_queryGraph.title = '查询';
    slow_queryGraph.valueField = "read";
    slow_queryGraph.type = "smoothedLine";
    slow_queryGraph.valueAxis = slow_queryAxis;
    slow_queryGraph.balloonText = "查询量：[[value]]亿";
    slow_queryGraph.lineColor = "#339900";
    slow_queryGraph.lineThickness = 2;
    chart.addGraph(slow_queryGraph);

    var rewr_queryGraph = new AmCharts.AmGraph();
    rewr_queryGraph.title = '更新';
    rewr_queryGraph.valueField = "write";
    rewr_queryGraph.type = "smoothedLine";
    rewr_queryGraph.valueAxis = rewr_queryAxis;
    rewr_queryGraph.balloonText = "更新量：[[value]]亿";
    rewr_queryGraph.lineColor = "#cc0000";
    rewr_queryGraph.lineThickness = 2;
    chart.addGraph(rewr_queryGraph);

    var chartCursor = new AmCharts.ChartCursor();
    chartCursor.zoomable = false;
    chartCursor.cursorAlpha = 0;
    chart.addChartCursor(chartCursor);

    var legend = new AmCharts.AmLegend();
    legend.position = "absolute";
    legend.markerSize = 7;
    legend.left = "125px";
    legend.top = "-15px";
    legend.valueText = '';
    chart.addLegend(legend);

    chart.write('div_chart');
});
</script>
</body>
</html>
