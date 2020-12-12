import urllib.request
import json



def get_weather(city):
    apiKey = 'ed1bf3c638a2675545a28dcb6354c23c'
    print("geting weather")

    url = 'http://api.openweathermap.org/data/2.5/weather?q='+city+'&mode=json&APPID='+apiKey
    data = urllib.request.urlopen(url).read()
    j = json.loads(data)

    print(city+"is" +j['weather'][0]['main'])
    print("최고 기온은" + str(j['main']['temp_max']-273.15)+"도")
    print("최저 기온은" + str(j['main']['temp_min']-273.15)+"도")

get_weather('Seoul')