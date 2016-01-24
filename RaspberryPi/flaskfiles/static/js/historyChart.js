$(document).ready(function() {

	$.getJSON('http://' + document.domain + ':' + location.port + '/data?name=history', function (json) {

		var entries = json['data']
		for(var i = 0; i < entries.length; i++){
			var timestamp = entries[i][0]
			var values = entries[i][1]
			for (var j = 0; j < values.length; j++) {
				hSeries[j]['data'].push([timestamp, values[j]])
			};
		}

		$(hChart_id).highcharts('StockChart', {
			chart : {
				height: hHeight
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

			yAxis: hYAxis,
			series: hSeries
		});

		function historyTimeout() {
			var dom = document.domain;
			var port = location.port;
			var chart = $(hChart_id).highcharts();
			var series = chart.series;
			$.getJSON('http://'+dom+':'+port+'/data?name=history&limit=last', function (lastJson) {
				if (lastJson['nextUpdate'] >= 0) {
					var data = lastJson['data'][0];
					for (var i = 0; i < series.length-1; i++) {
						series[i].addPoint([data[0], data[1][i]], false, true);
					}
					chart.redraw();

					setTimeout(function(){
						historyTimeout();
					}, lastJson['nextUpdate']*1000);
				} else {
					setTimeout(function(){
						historyTimeout();
					}, 1800000);
				}
			});
		};

		var nextUpdate = (json['nextUpdate'] > 0) ? json['nextUpdate']*1000 : 1800000;
		setTimeout(function(){
			historyTimeout();
		}, nextUpdate);
	});
});