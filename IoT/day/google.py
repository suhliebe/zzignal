#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#get_ipython().system('pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib')
#get_ipython().system('pip install requests')


# In[ ]:


##################################################
# 1. 인증
##################################################


# In[ ]:


# 1-1. 구글 API 인증
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
# 구글 OAuth 클라이언트 ID Json 파일
gcreds_filename = 'auth/gcredentials.json'

# 캘린더에서 사용할 권한
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None
if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

# 새로운 창에서 로그인 하시면 인증 정보를 얻게 됩니다.
if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(gcreds_filename, SCOPES)
            gcreds = flow.run_local_server()
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)




# In[ ]:
##################################################
# 2. 구글 캘린더 일정 가져오기
##################################################


# In[ ]:


# 기본 라이브러리 import
import datetime
import requests
import urllib
import json


# In[ ]:


# 구글 캘린더 API 서비스 객체 생성
from googleapiclient.discovery import build

service = build('calendar', 'v3', credentials=gcreds)

# 조회에 사용될 요청 변수 지정
calendar_id = 'primary'                   # 사용할 캘린더 ID
today = datetime.date.today().isoformat()
time_min = today + 'T00:00:00+09:00'      # 일정을 조회할 최소 날짜
time_max = today + 'T23:59:59+09:00'      # 일정을 조회할 최대 날짜
max_results = 1                           # 일정을 조회할 최대 개수
is_single_events = True                   # 반복 일정의 여부
orderby = 'startTime'                     # 일정 정렬

# 오늘 일정 가져오기
events_result = service.events().list(calendarId = calendar_id,
                                      timeMin = time_min,
                                      timeMax = time_max,
                                      maxResults = max_results,
                                      singleEvents = is_single_events,
                                      orderBy = orderby).execute()

events_result.get('items', [])
print(events_result)

# In[ ]:


##################################################
# 3. 일정 데이터 정제하기
##################################################
# 테스트를 위해 오늘 일정에서 한 개만 가져오겠습니다.
items = events_result.get('items')
item = items[0]

# 일정 제목
gsummary = item.get('summary')

# 일정 제목에서 [식사-국민대]에서 카테고리와 장소만 빼내옵니다.
gcategory, glocation = gsummary[gsummary.index('[')+1 : gsummary.index(']')].split('-')

# 해당 구글 캘린더 일정 연결 링크
gevent_url = item.get('htmlLink')

gaddress = item.get('location')
# 구글 주소를 정제합니다.
# ex) "국민대학교, 대한민국 서울특별시 성북구 정릉동 정릉로 77" => "대한민국 서울특별시 성북구 정릉동 정릉로 77"
if ',' in gaddress:
    gaddress = gaddress.split(',')[1].strip()

