$(document).ready(function() {
	var lastHeaderImg = '';

	function currentDataTimeout() {
		var dom = document.domain;
		var port = location.port;
		$.getJSON('http://'+dom+':'+port+'/data?name=currentData', function (lastJson) {
			if (lastHeaderImg != lastJson['headerImg']) {
				document.getElementById("header").style.backgroundImage = "url('" + lastJson['headerImg'] + "')";
				lastHeaderImg = lastJson['headerImg'];
			}

			data = lastJson['data'];
			for (var key in data) {
				$('#' + key).html(data[key]);
			}

			var nextUpdate = (lastJson['nextUpdate'] >= 0) ? lastJson['nextUpdate']*1000 : 180000
			setTimeout(function(){
            		currentDataTimeout();
        	}, nextUpdate);
		});
	};

	currentDataTimeout();
});