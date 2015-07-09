$(document).ready(function() {
    $(chart_id).highcharts('StockChart', {
        rangeSelector: rangeSelector,
        chart: chart,
        title: title,
        xAxis: xAxis,
        yAxis: yAxis,
        series: series
    });
});