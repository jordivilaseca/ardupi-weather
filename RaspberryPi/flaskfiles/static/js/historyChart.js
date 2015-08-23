$(document).ready(function() {

	Highcharts.setOptions({
		global: {
			useUTC: false
		}
	});

	$.getJSON('http://' + document.domain + ':' + location.port + '/data/history.json', function (data) {

		var entries = data['data']
		for(var i = 0; i < entries.length; i++){
			var timestamp = entries[i][0]
			var values = entries[i][1]
			for (var j = 0; j < values.length; j++) {
				hSeries[j]['data'].push([timestamp, values[j]])
			};
		}

		$(hChart_id).highcharts('StockChart', {
			chart : {
				height: hHeight,
				events : {
					load : function () {
						var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
						var series = this.series;
						var chart = $(hChart_id).highcharts()
						socket.on('historyUpdate', function (data) {
							for (var i = 0; i < series.length-1; i++) {
								series[i].addPoint([data[0], data[1][i]], false, true);
							}
							chart.redraw()
						});
					}
				}
			},

			rangeSelector: {

				buttons: [{
					type: 'hour',
					count: 5,
					text: '5h'
				}, {
					type: 'day',
					count: 1,
					text: '1d'
				}, {
					type: 'day',
					count: 7,
					text: '1w'
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

			title: {text: hChart_name},
			xAxis: {categories: ['Time']},
			yAxis: hYAxis,
			series: hSeries
		});
	});
});