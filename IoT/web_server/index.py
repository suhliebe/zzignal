#face_detect_webserver.py

import pickle
import os
import pandas as pd
import math
import paho.mqtt.client as mqtt

from flask import Flask, render_template, Response
import cv2
import numpy as np
import time
import datetime
import sys
import mediapipe as mp

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	#client.subscribe("$SYS/#")
	client.subscribe("hand") #구독 "nodemcu"

def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload)) #토픽과 메세지를 출력한다.

client = mqtt.Client() #client 오브젝트 생성
client.on_connect = on_connect #콜백설정
client.on_message = on_message #콜백설정

client.connect("192.168.0.133", 1883, 60) #라즈베리파이3 MQTT 브로커에 연결


loaded_model = pickle.load(open('201211_SVM_number.pickle', 'rb'))
distcol = ['r_'+str(i)+'to'+str(j) for i in range(21) for j in range(i+1, 21)]
# print(len(distcol))

# 좌표 column 만들기
lhands = []
for i in range(21):
    lhands.append('xl_'+str(i))
    lhands.append('yl_'+str(i))
# lhands

rhands = []
for i in range(21):
    rhands.append('xr_'+str(i))
    rhands.append('yr_'+str(i))
# rhands

hands_list = lhands+rhands

# hands_dist = hands+distcol
hands_dist = rhands+distcol
print(len(hands_dist))
# print(hands_dist)

## vector의 column 만들기
indicators = ['MAV', 'RMS', 'VAR', 'SSI', 'MAX', 'MIN']
ncols = []
for i in range(len(hands_dist)):
    for j in range(len(indicators)):
        ncols.append(hands_dist[i]+'_'+indicators[j])
print(len(ncols))

with open('201211_SVM_features.txt') as f:
    features = f.read().split(',')
features = [f for f in features][:-1]




mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

app = Flask(__name__)

def get_distance(row):
    right = row
#     left = row[0:42]
#     right = row[42:]
    dlist = []
#     for i in range(0, len(left), 2):
#         for j in range(i+2, len(left), 2):
#             x1 = left[i]
#             x2 = left[i+1]
#             y1 = left[j]
#             y2 = left[j+1]
#             dlist.append(math.hypot(x2-x1, y2-y1))
    for i in range(0, len(right), 2):
        for j in range(i+2, len(right), 2):
            x1 = right[i]
            x2 = right[j]
            y1 = right[i+1]
            y2 = right[j+1]
            dlist.append(math.hypot(x2-x1, y2-y1))
#     print(len(dlist))

    return pd.Series(dlist)


def get_vector(data):
    columns = list(data.columns)

    vector = []  # this variable will contain all the features for a single class (1 csv file)
    # to loop over each sensor reading
    for item in columns:
        temp = list(data[item])  # data[item]: for each sensor

        # calculating MAV
        abs_val = list(map(abs, temp))
        MAV = np.mean(abs_val)
        vector.append(MAV)
        #         print('MAV', MAV)

        # calculating RMS
        RMS = np.sqrt(np.mean(np.array(temp) ** 2))
        vector.append(RMS)
        #         print('RMS', RMS)

        # calculate variance
        x_mean = np.mean(temp)
        dif = temp - x_mean
        VAR = np.mean(np.array(dif) ** 2)
        vector.append(VAR)
        #         print('VAR', VAR)

        # calculating ssi
        SSI = np.sum(np.array(temp) ** 2)
        vector.append(SSI)
        #         print('SSI', SSI)

        # calculating max
        MAX = max(temp)
        vector.append(MAX)
        #         print('MAX', MAX)

        # calculating min
        MIN = min(temp)
        vector.append(MIN)
    #         print('MIN', MIN)

    return vector



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
    camera = cv2.VideoCapture("http://192.168.0.133:8090/?action=stream")
    # camera = cv2.VideoCapture("http://124.52.90.20:8090/?action=stream")
    # cap = cv2.VideoCapture(0)
    time.sleep(0.2)
    lastTime = time.time()*1000.0
    df = []
    while True:
        success, image = camera.read()
        if not success:
            break        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        keypoint = 0
        a = 0

        image.flags.writeable = False
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        ########################################


        # if results.multi_hand_landmarks:
        #     for hand_landmarks in results.multi_hand_landmarks:
        #         idx = 0
        #         # cv2.imwrite('C:/workspace/mediapipe/img/img_raw_image' + str(idx) + '.png', cv2.flip(image, 1))
        #         mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        if results.multi_hand_landmarks:
            arow = []
            # multi_hand_landmarks
            for hand_landmarks in results.multi_hand_landmarks:
                #                 print(hand_landmarks)
                for a in range(21):
                    keypoint += hand_landmarks.landmark[a].x
                idx = 0
                keypoint = (keypoint * 100) / a
                client.publish("hand", keypoint)

                for data_point in hand_landmarks.landmark:
                    #                     nset = (data_point.x, data_point.y)
                    #                     arow = arow.append(nset)

                    arow.append(data_point.x)
                    arow.append(data_point.y)
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # # multi_handedness
            # handed = len(results.multi_handedness)
            # #             print(results.multi_handedness)
            # if handed == 1:
            #     hd = results.multi_handedness[0].classification[0].label.split('\r')[0]
            #     if hd == 'Left':
            #         arow = arow + [0] * 42
            #     else:
            #         arow = [0] * 42 + arow
            # #             df = df.append(pd.Series(arow, index=df.columns), ignore_index=True)
            # #             print(arow)
            #
            # #             print(len(arow))
            # df.extend(arow)
            #
            #
            #
            # ex = pd.DataFrame(np.array(df).reshape(-1, 84), columns=hands_list)
            # ex = ex[rhands]
            # #     print(len(ex))
            # # if len(ex) == 0:
            #     # continue
            # # print(file)
            # ex[distcol] = ex.apply(lambda row: get_distance(row), axis=1)
            # # if len(ex) >= 100:
            # sldf = pd.DataFrame()
            # sldf = sldf.append(pd.Series(get_vector(ex), index=ncols), ignore_index=True)
            # sldf = sldf[features]
            # print("ex : " , len(ex))
            # print("sldf : ", len(sldf))
            # print(loaded_model.predict(sldf))
            #
            # ex = ex.loc[1:,]
        # sign = loaded_model.predict(sldf)



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