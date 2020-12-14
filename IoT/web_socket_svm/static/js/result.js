function result() {

	req = $.ajax({
		url : '/result',
		type : 'POST',
		data : {}
	});

	req.done(function(data) {
		var desc = data.result;
		if(desc==0){
		    $('#contents').load("/start");
		}
		else if(desc==1){
		    $('#contents').load("/weather")
		}

	});

}

setInterval(result, 5000);