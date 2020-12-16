$(document).ready(function(){
  let namespace = "/test";
  let video = document.querySelector("#videoElement");
  let canvas = document.querySelector("#canvasElement");
  let ctx = canvas.getContext('2d');
  photo = document.getElementById('photo');
  var localMediaStream = null;

  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

  function sendSnapshot() {
    if (!localMediaStream) {
      return;
    }

    ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight, 0, 0, 300, 150);

    let dataURL = canvas.toDataURL('image/jpeg');
    socket.emit('input image', dataURL);

    socket.emit('output image')

    var img = new Image();
    socket.on('out-image-event',function(data){


    img.src = dataURL//data.image_data
    photo.setAttribute('src', data.image_data);

    });
  }
  function result() {
	req = $.ajax({
		url : '/result',
		type : 'POST',
		data : {}
	});

	req.done(function(data) {
		var desc = data.result;
		if(desc==0){
		    socket.off();
		    clearInterval(resultInterval);
		    clearInterval(sendInterval);
		    $('#contents').load("/start");
		}
		else if(desc==1){
		    socket.off();
		    clearInterval(resultInterval);
		    clearInterval(sendInterval);
		    $('#contents').load("/weather")
		}
		else if(desc==2){
		    socket.off();
		    clearInterval(resultInterval);
		    clearInterval(sendInterval);
		    $('#contents').load("/news")
		}
		else if(desc==999){
		    socket.off();
		    clearInterval(resultInterval);
		}

	});
}

  socket.on('connect', function() {
    console.log('Connected!');
  });

  var constraints = {
    video: {
      width: { min: 640 },
      height: { min: 480 }
    }
  };
  var resultInterval=setInterval(result, 5000);
  var sendInterval = setInterval(sendSnapshot, 50);

  navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
    video.srcObject = stream;
    localMediaStream = stream;
  }).catch(function(error) {
    console.log(error);
  });
});


