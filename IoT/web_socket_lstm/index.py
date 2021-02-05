#face_detect_webserver.py
import requests
import pickle
import os
import pandas as pd
import math
# import paho.mqtt.client as mqtt
import json
import urllib.request
from flask import Flask, render_template, Response, jsonify, redirect, url_for, make_response
import cv2
import numpy as np
import time
import datetime
import sys
import mediapipe as mp
from time import sleep
from predict import *

frame_num = 5

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	#client.subscribe("$SYS/#")
	client.subscribe("hand") #구독 "nodemcu"

def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload)) #토픽과 메세지를 출력한다.

# loaded_model = pickle.load(open('201211_SVM_number.pickle', 'rb'))
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
hands_dist = rhands+distcol

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

app = Flask(__name__)

def get_distance(row):
    right = row
    dlist = []
    for i in range(0, len(right), 2):
        for j in range(i+2, len(right), 2):
            x1 = right[i]
            x2 = right[j]
            y1 = right[i+1]
            y2 = right[j+1]
            dlist.append(math.hypot(x2-x1, y2-y1))
    return dlist


icon_lookup = {
	'clear-day': "assets/Sun.png",  # clear sky day
	'wind': "assets/Wind.png",   #wind
	'cloudy': "assets/Cloud.png",  # cloudy day
	'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
	'rain': "assets/Rain.png",  # rain day
	'snow': "assets/Snow.png",  # snow day
	'snow-thin': "assets/Snow.png",  # sleet day
	'fog': "assets/Haze.png",  # fog day
	'clear-night': "assets/Moon.png",  # clear sky night
	'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
	'thunderstorm': "assets/Storm.png",  # thunderstorm
	'tornado': "assets/Tornado.png",    # tornado
	'hail': "assets/Hail.png"  # hail
}

def get_weather():
    # apiKey = 'apiKey'
    # print("geting weather")
    # city = 'Seoul'
    # url = 'http://api.openweathermap.org/data/2.5/weather?q=' + city + '&mode=json&APPID=' + apiKey
    # data = urllib.request.urlopen(url).read()
    # j = json.loads(data)

    # Get json from dark skys api
    APIKEY = '6b4e2599041ea02b9f19e4e86ae23f59'
    LAT, LON =37.512828, 127.052707
    URL = 'https://api.darksky.net/forecast/{}/{},{}'.format(APIKEY, LAT, LON)
    # print(URL)
    r = requests.get(URL)
    json = r.json()
    # print(json.dumps(j, indent=4))
    print(json)

    temperatureHigh = json['daily']['data'][0]['temperatureHigh']
    temperatureLow = json['daily']['data'][0]['temperatureLow']
    week_summary = json['daily']['summary']
    # Get current and hourly data
    currently = json['currently']
    hourly = json['hourly']
    # print(hourly['data'])
    # Fetch important information for display
    title = currently['summary']
    icon = icon_lookup[currently['icon']]
    # temperature = int(round(currently['temperature']))
    temperature = int(round((currently['temperature']-32)*5/9))
    desc = hourly['summary'].rstrip('.')

    week = {0: "월요일", 1: "화요일", 2: "수요일", 3: "목요일", 4: "금요일", 5: "토요일", 6: "일요일"}

    time = [0,0,0,0,0,0]
    time_hightemp = [0,0,0,0,0,0]
    time_lowtemp = [0,0,0,0,0,0]
    time_icon = [0,0,0,0,0,0]
    for i in range(6):
        time[i] = week[datetime.datetime.fromtimestamp(json['daily']['data'][i+1]['time']).weekday()]
        # time[i]="월요일"
        time_hightemp[i] = int(round((json['daily']['data'][i+1]['temperatureHigh']-32)*5/9))
        time_lowtemp[i] = int(round((json['daily']['data'][i+1]['temperatureLow']-32)*5/9))
        time_icon[i] = json['daily']['data'][i+1]['icon']

    return {'title': title, 'icon': icon, 'temperature': temperature, 'desc': desc, 'temperatureHigh': temperatureHigh,
            'temperatureLow': temperatureLow, 'week_summary': week_summary,
            'time0': time[0], 'time0_hightemp': time_hightemp[0], 'time0_lowtemp': time_lowtemp[0], 'time0_icon': time_icon[0],
            'time1': time[1], 'time1_hightemp': time_hightemp[1], 'time1_lowtemp': time_lowtemp[1], 'time1_icon': time_icon[1],
            'time2': time[2], 'time2_hightemp': time_hightemp[2], 'time2_lowtemp': time_lowtemp[2], 'time2_icon': time_icon[2],
            'time3': time[3], 'time3_hightemp': time_hightemp[3], 'time3_lowtemp': time_lowtemp[3], 'time3_icon': time_icon[3],
            'time4': time[4], 'time4_hightemp': time_hightemp[4], 'time4_lowtemp': time_lowtemp[4], 'time4_icon': time_icon[4],
            'time5': time[5], 'time5_hightemp': time_hightemp[5], 'time5_lowtemp': time_lowtemp[5], 'time5_icon': time_icon[5]}


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

@app.route('/start')
def start():
    return render_template('start.html')


@app.route('/weather')
def weather():
    return render_template('weather.html')


@app.route("/update_weather", methods=['POST'])
def update_weather():
    currentWeather = get_weather()
    return jsonify({'result' : 'success', 'currentWeather' : currentWeather})


def gen_frames():
    # camera = cv2.VideoCapture("http://ip:port/?action=stream")
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    time.sleep(0.2)
    lastTime = time.time()*1000.0
    prediction = 0
    df = []
    distance_lst = []
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
        arow = []
        if results.multi_hand_landmarks:
            
            for hand_landmarks in results.multi_hand_landmarks:

                handed = len(results.multi_handedness)
                hd = results.multi_handedness[0].classification[0].label.split('\r')[0]
                #                     print(hd)
                if hd == "Right":
                    for data_point in hand_landmarks.landmark:
                        arow.append(data_point.x)
                        arow.append(data_point.y)
                distance = get_distance(arow)   
                if len(distance_lst) <= frame_num *210:
                    distance_lst.extend(distance)

                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        if len(distance_lst) >= frame_num *210:
            print('predict============= len(distance_lst)', len(distance_lst))
            prediction = pred_number(np.array(distance_lst))
            distance_lst = distance_lst[210:]
            # try:
            #     prediction = pred_number(np.array(distance_lst))
            #     distance_lst = distance_lst[210:]s
            # except:
            #     pass

        ret, buffer = cv2.imencode('.jpg', image)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
       
 
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    frame = gen_frames()
    print(frame)
    if frame == '0':
        return Response(frame, mimetype='text/xml')
    else:
        return Response(frame,
                        mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)