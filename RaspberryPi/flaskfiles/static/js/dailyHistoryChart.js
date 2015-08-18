$(document).ready(function() {

	Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });

	$(dhChart_id).highcharts('StockChart', {

		chart : {
			height: dhHeight
        },

        rangeSelector: {

                buttons: [{
                    type: 'month',
                    count: 1,
                    text: '1mo'
                }, {
                    type: 'year',
                    count: 1,
                    text: '1y'
                }, {
                    type: 'all',
                    text: 'All'
                }],
                selected: 1
        },

        title: {text: dhChart_name},
        xAxis: {type: 'datetime'},
        yAxis: dhYAxis,
        series: dhSeries
    });
});