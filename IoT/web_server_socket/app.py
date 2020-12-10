from sys import stdout
import logging
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2, base64
import numpy as np
import mediapipe as mp
from camera import Camera
from makeup_artist import Makeup_artist


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)


app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(stdout))
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
socketio = SocketIO(app)
camera = Camera(Makeup_artist())


@socketio.on('input image', namespace='/test')
def test_message(input):
    image = input
    image = cv2.imdecode(np.frombuffer(base64.b64decode(image.split(',')[1]), np.uint8), cv2.IMREAD_COLOR)
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    image = cv2.imencode('.jpg', image)[1].tobytes()
    image = base64.b64encode(image).decode('utf-8')
    image = f"data:image/jpeg;base64,{image}"

    emit('out-image-event', {'image_data': image}, namespace='/test')
    #camera.enqueue_input(base64_to_pil_image(input))

@socketio.on('connect', namespace='/test')
def test_connect():
    app.logger.info("client connected")


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app)

# from sys import stdout
# from makeup_artist import Makeup_artist
# import logging
# from flask import Flask, render_template, Response
# from flask_socketio import SocketIO, emit
# from camera import Camera
# from utils import base64_to_pil_image, pil_image_to_base64
#
#
# app = Flask(__name__)
# app.logger.addHandler(logging.StreamHandler(stdout))
# app.config['SECRET_KEY'] = 'secret!'
# app.config['DEBUG'] = True
# socketio = SocketIO(app)
# camera = Camera(Makeup_artist())
#
#
# @socketio.on('input image', namespace='/test')
# def test_message(input):
#     input = input.split(",")[1]
#     camera.enqueue_input(input)
#     image_data = input # Do your magical Image processing here!!
#     #image_data = image_data.decode("utf-8")
#     image_data = "data:image/jpeg;base64," + image_data
#     print("OUTPUT " + image_data)
#     emit('out-image-event', {'image_data': image_data}, namespace='/test')
#     #camera.enqueue_input(base64_to_pil_image(input))
#
#
# @socketio.on('connect', namespace='/test')
# def test_connect():
#     app.logger.info("client connected")
#
#
# @app.route('/')
# def index():
#     """Video streaming home page."""
#     return render_template('index.html')
#
#
# def gen():
#     """Video streaming generator function."""
#
#     app.logger.info("starting to generate frames!")
#     while True:
#         frame = camera.get_frame() #pil_image_to_base64(camera.get_frame())
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#
#
# @app.route('/video_feed')
# def video_feed():
#     """Video streaming route. Put this in the src attribute of an img tag."""
#     return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
#
#
# if __name__ == '__main__':
#     socketio.run(app)