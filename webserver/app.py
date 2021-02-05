import ssl
import math
import pickle
import pandas as pd
from sys import stdout
import logging
from flask import Flask, render_template, jsonify
import requests
from flask_socketio import SocketIO, emit
import cv2, base64
import numpy as np
import mediapipe as mp
import datetime
import feedparser
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import configparser
import json
import sys
import os.path
import os
import flask
from auth2 import auth
import boto3
import http.client, urllib

CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

libdir = os.path.dirname(__file__)
sys.path.append(os.path.split(libdir)[0])
apiKey = 'NCSLIPZ9VIPR1W3N'
apiSecret = 'O6RMZCI4WYHO5DZKYBCBTEBRQHVMRYKL'

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(stdout))
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
socketio = SocketIO(app)
app.secret_key = '0000'


global prediction_global
prediction_flag=0


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

# vector의 column 만들기
indicators = ['MAV', 'RMS', 'VAR', 'SSI', 'MAX', 'MIN']
ncols = []
for i in range(len(hands_dist)):
    for j in range(len(indicators)):
        ncols.append(hands_dist[i]+'_'+indicators[j])
print(len(ncols))

with open('201211_SVM_features.txt') as f:
    features = f.read().split(',')
features = [f for f in features][:-1]

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
    # apiKey = 'ed1bf3c638a2675545a28dcb6354c23c'
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
    # print(json)

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
    global prediction_global
    prediction_global = 999
    global prediction_flag
    prediction_flag = 1

    return {'title': title, 'icon': icon, 'temperature': temperature, 'desc': desc, 'temperatureHigh': temperatureHigh,
            'temperatureLow': temperatureLow, 'week_summary': week_summary,
            'time0': time[0], 'time0_hightemp': time_hightemp[0], 'time0_lowtemp': time_lowtemp[0], 'time0_icon': time_icon[0],
            'time1': time[1], 'time1_hightemp': time_hightemp[1], 'time1_lowtemp': time_lowtemp[1], 'time1_icon': time_icon[1],
            'time2': time[2], 'time2_hightemp': time_hightemp[2], 'time2_lowtemp': time_lowtemp[2], 'time2_icon': time_icon[2],
            'time3': time[3], 'time3_hightemp': time_hightemp[3], 'time3_lowtemp': time_lowtemp[3], 'time3_icon': time_icon[3],
            'time4': time[4], 'time4_hightemp': time_hightemp[4], 'time4_lowtemp': time_lowtemp[4], 'time4_icon': time_icon[4],
            'time5': time[5], 'time5_hightemp': time_hightemp[5], 'time5_lowtemp': time_lowtemp[5], 'time5_icon': time_icon[5]}


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


@socketio.on('input image', namespace='/test')
def test_message(input):
    # image = input
    # image = cv2.imdecode(np.frombuffer(base64.b64decode(image.split(',')[1]), np.uint8), cv2.IMREAD_COLOR)
    camera = cv2.VideoCapture("http://192.168.0.133:8090/?action=stream")
    success, image = camera.read()
    df=[]
    # while True:
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
            host = 'https://a2cgafwgqe.execute-api.us-east-1.amazonaws.com/'
            url = 'zzignal/sign'
            parm= {
                "sign": keypoint
            }
            response = requests.get(host+url, params=parm)
            print('lambda', response)

            for data_point in hand_landmarks.landmark:
                #                     nset = (data_point.x, data_point.y)
                #                     arow = arow.append(nset)

                arow.append(data_point.x)
                arow.append(data_point.y)
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # # multi_handedness
        handed = len(results.multi_handedness)
        #             print(results.multi_handedness)
        if handed == 1:
            hd = results.multi_handedness[0].classification[0].label.split('\r')[0]
            if hd == 'Left':
                arow = arow + [0] * 42
            else:
                arow = [0] * 42 + arow
        #             df = df.append(pd.Series(arow, index=df.columns), ignore_index=True)
        #             print(arow)

        #             print(len(arow))
        df.extend(arow)

        ex = pd.DataFrame(np.array(df).reshape(-1, 84), columns=hands_list)
        ex = ex[rhands]
        #     print(len(ex))
        # if len(ex) == 0:
        # continue
        # print(file)
        ex[distcol] = ex.apply(lambda row: get_distance(row), axis=1)
        # if len(ex) >= 100:
        sldf = pd.DataFrame()
        sldf = sldf.append(pd.Series(get_vector(ex), index=ncols), ignore_index=True)
        sldf = sldf[features]
        # print("ex : " , len(ex))
        # print("sldf : ", len(sldf))
        # print(loaded_model.predict(sldf))
        prediction = loaded_model.predict(sldf)
        global prediction_global
        prediction_global = int(prediction)
        print(prediction_global)

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
    return render_template('index.html')


@app.route("/result", methods=['POST'])
def result():
    global prediction_global
    global prediction_flag
    return jsonify({'result': prediction_global, 'flag':prediction_flag})


@app.route('/start')
def start():
    # global prediction_global
    # prediction_global = 999
    return render_template('start.html')


@app.route('/weather')
def weather():
    return render_template('weather.html')


@app.route("/update_weather", methods=['POST'])
def update_weather():
    currentWeather = get_weather()
    return jsonify({'result' : 'success', 'currentWeather': currentWeather})


@app.route('/news')
def news():
    urls = (
        "http://fs.jtbc.joins.com/RSS/newsflash.xml"  # 속보
    )
    rss_dic = []
    news_dic = []
    parse_rss = feedparser.parse(urls)
    for p in parse_rss.entries:
        rss_dic.append({'title': p.title, 'link': p.link})
    for i in range(5):
        news_dic.append(rss_dic[i])

    return render_template('news.html', news=news_dic)

################### 캘린더 시작 ##############################
@app.route('/calender')
def calender():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    calendar_id = 'primary'  # 사용할 캘린더 ID
    today = datetime.date.today().isoformat()
    time_min = today + 'T00:00:00+09:00'  # 일정을 조회할 최소 날짜
    time_max = '2020-12-31' + 'T23:59:59+09:00'  # 일정을 조회할 최대 날짜
    max_results = 30  # 일정을 조회할 최대 개수
    is_single_events = True  # 반복 일정의 여부
    orderby = 'startTime'  # 일정 정렬

    # 오늘 일정 가져오기
    events_result = service.events().list(calendarId=calendar_id,
                                          timeMin=time_min,
                                          timeMax=time_max,
                                          maxResults=max_results,
                                          singleEvents=is_single_events,
                                          orderBy=orderby).execute()
    flask.session['credentials'] = credentials_to_dict(credentials)

    print(service)
    print(events_result)
    return flask.jsonify(**events_result)


@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES
    )

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/ouath2callback')
def oauth2callback():
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state
    )
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('test_api_request'))


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
###################### 캘린더 끝 ######################################


def send_message():
    data = {
        'message': {
            'to': '01092119647',  # 119라던가 보낼번호
            'from': '01092119647',  # "인증받은 번호만 됩니다"
            'text': 'test'  # 여기에 주소랑 입력하면 될거같습니다
        }
    }
    res = requests.post('https://api.solapi.com/messages/v4/' + 'send', headers=auth.get_headers(apiKey, apiSecret),
                        json=data)

    print(json.dumps(json.loads(res.text), indent=2, ensure_ascii=False))
    print(res)
    return res


@app.route('/report')
def report_accident():
    result = send_message()
    print(result)

    if(result.status_code==200):
        result2 = "신고하였습니다"
    else:
        result2 = "신고에 실패하였습니다."
    return jsonify({'result' : result2})
    # pass

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    # ssl_context.load_cert_chain(certfile='newcert.pem', keyfile='newkey.pem', password='secret')

    # socketio.run(app, host='0.0.0.0', ssl_context=ssl_context)
    socketio.run(app, host='0.0.0.0')
