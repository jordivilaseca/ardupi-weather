$(document).ready(function() {
	var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
	socket.on('currentDataUpdate', function (data) {
		for (var key in data) {
			$('#' + key).html(data[key]);
		}
	});
});