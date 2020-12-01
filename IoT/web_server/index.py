#face_detect_webserver.py


from flask import Flask, render_template, Response
import cv2
import numpy as np
import time
import datetime
import sys
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

app = Flask(__name__)

@app.route('/')
def index():
    """Video streaming home page."""
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    templateData = {
            'title':'Image Streaming',
            'time': timeString
            }
    return render_template('index.html', **templateData)

def gen_frames():
    # camera = cv2.VideoCapture("http://192.168.0.7:8090/?action=stream")
    camera = cv2.VideoCapture("http://124.52.90.20:8090/?action=stream")
    time.sleep(0.2)
    lastTime = time.time()*1000.0

    while True:
        ret, image = camera.read()
        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                idx = 0
                # cv2.imwrite('C:/workspace/mediapipe/img/img_raw_image' + str(idx) + '.png', cv2.flip(image, 1))
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # cv2.imshow("Frame", image)
        # key = cv2.waitKey(1) & 0xFF
     # if the `q` key was pressed, break from the loop
     #    if key == ord("q"):
     #        break
   
        ret, buffer = cv2.imencode('.jpg', image)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
       
 
@app.route('/video_feed')

def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0')       