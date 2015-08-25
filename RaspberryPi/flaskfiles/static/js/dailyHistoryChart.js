$(document).ready(function() {

	Highcharts.setOptions({
		global: {
			useUTC: false
		}
	});

	$.getJSON('http://' + document.domain + ':' + location.port + '/data/dailyHistory.json', function (data) {
		var entries = data['data']
		var showAVG = data['showAVG']
		var showMINMAX = data['showMINMAX']
		for(var i = 0; i < entries.length; i++){
			var timestamp = entries[i][0]
			var values = entries[i][1]
			var numSerie = 0
			for (var j = 0; j < values.length; j += 3) {
				if (showAVG) {
					dhSeries[numSerie]['data'].push([timestamp, values[j+2]])
					numSerie++
				}
				if (showMINMAX) {
					dhSeries[numSerie]['data'].push([timestamp, values[j], values[j+1]])
					numSerie++
				}
			};
		}

		$(dhChart_id).highcharts('StockChart', {

			chart : {
				height: dhHeight
			},

			rangeSelector: {

				buttons: [{
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
				selected: 0
			},

			xAxis: {type: 'datetime'},
			yAxis: dhYAxis,
			series: dhSeries
		});
	});
});