import requests
import configparser
import json
import sys
import os.path

libdir = os.path.dirname(__file__)
sys.path.append(os.path.split(libdir)[0])

from auth import auth

config = configparser.ConfigParser()
config.read('config.ini')
apiKey = config['AUTH']['ApiKey']
apiSecret = config['AUTH']['ApiSecret']

if __name__ == '__main__':
    data = {
        'message': {
            'to': '01092119647',#119라던가
            'from': '01092119647',#"인증받은 번호만 됩니다"
            'text': 'test'#여기에 주소랑 입력하면 될거같습니다
        }
    }
    res = requests.post(config['SERVER']['URI'] + 'send', headers=auth.get_headers(apiKey, apiSecret), json=data)
    print(json.dumps(json.loads(res.text), indent=2, ensure_ascii=False))
