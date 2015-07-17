$(document).ready(function() {

	Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });

	$(chart_id).highcharts('StockChart', {

		chart : {
			height: height,
            events : {
                load : function () {
				    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
				    var series = this.series;
				    var chart = $(chart_id).highcharts()
				    socket.on('sample', function (sample) {
				    	for (var i = 0; i < series.length-1; i++) {
    						series[i].addPoint([sample[0], sample[1][i]], false, true);
    					}
    					chart.redraw()
				    });
                }
            }
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
                selected: 1
        },

        title: {text: chart_name},
        xAxis: {categories: ['Time']},
        yAxis: yAxis,
        series: series
    });
});