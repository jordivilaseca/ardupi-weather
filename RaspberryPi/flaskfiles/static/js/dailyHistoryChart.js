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
                    type: 'minute',
                    count: 30,
                    text: '30mi'
                }, {
                    type: 'hour',
                    count: 5,
                    text: '5h'
                }, {
                    type: 'day',
                    count: 1,
                    text: '1d'
                }, {
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
                selected: 2
        },

        title: {text: dhChart_name},
        xAxis: {type: 'datetime'},
        yAxis: dhYAxis,
        series: dhSeries
    });
});