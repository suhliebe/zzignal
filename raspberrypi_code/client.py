import socket
import time
import threading
import RPi.GPIO as GPIO
from imutils.video import VideoStream
import imagezmq
import paho.mqtt.client as mqtt
import pigpio

from time import sleep

### 실행전 sudo pigpiod 꼭 실행하기
### 그리고 끄기전 꼭 sudo killall pigpiod 실행하기
# 설치가 끝나셨으면 사용법은 pigpio의 데몬을 실행해 주어야합니다.
# pigpio의 데몬이 로우레벨언어로 하드웨어 동작과 연산을 나눠주는 역할을 하는놈이지 않을까 싶네요.


count = 0
ms = 0
pi = pigpio.pi()
nowAngle = 75
pi.set_servo_pulsewidth(18, 1350)
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	#client.subscribe("$SYS/#")
	client.subscribe("hand") #구독 "nodemcu"

def on_message(client, userdata, message):
  global nowAngle
  global count
  global ms
  point = float(str(message.payload.decode("utf-8")))
  print(point)
  if int(point) > 65:
    nowAngle += 2
  elif int(point) < 35:
    nowAngle -= 2
  set_servo_pos()
  count = 0
  ms = 0

def start_timer():
    global count
    global ms 
    ms += 1
    count = ms / 10
    if(count%1 == 0):
        print(count)
    timer = threading.Timer(0.1,start_timer)
    timer.start()

    if(count>10):
        print("no MAN")
        serching_man()
        
def serching_man():
    global count
    global nowAngle
    if (int(count/10))%2 == 1:
        nowAngle = 150/100*(ms%100 + 1) 
    else:
        nowAngle = 150/100*(100-(ms%100 + 1)) 
    set_servo_pos()
    
def set_servo_pos():
  global nowAngle
  if nowAngle > 150:
    nowAngle = 150
  elif nowAngle < 0:
    nowAngle = 0

  #각도(degree)를 duty로 변경
  duty = 600 + (nowAngle*10)
  # duty 값 출력
  print("Degree: {} to {}(Duty)".format(nowAngle, duty))

  #변경된 duty값을 서보 pwm에 적용
  pi.set_servo_pulsewidth(18, duty)

client = mqtt.Client() #client A 오브젝트 생성
client.on_connect = on_connect #콜백설정
client.on_message = on_message #콜백설정
#client.connect("192.168.219.106", 1883, 60)#집
client.connect("192.168.0.133", 1883, 60)#학원

#sender = imagezmq.ImageSender(connect_to='tcp://192.168.219.100:5555')#집
# sender = imagezmq.ImageSender(connect_to='tcp://192.168.0.14:5555')#학원

# rpi_name = socket.gethostname() # send RPi hostname with each image

# picam = VideoStream(usePiCamera=True).start()
# time.sleep(2.0)  # allow camera sensor to warm up
client.loop_stop()
start_timer()
while True:  # send images as stream until Ctrl-C
  # image = picam.read()
  # sender.send_image(rpi_name, image)
  client.loop_start()
