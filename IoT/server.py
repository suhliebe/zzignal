import cv2
import imagezmq
import mediapipe as mp
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	#client.subscribe("$SYS/#")
	client.subscribe("hand") #구독 "nodemcu"

def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload)) #토픽과 메세지를 출력한다.

client = mqtt.Client() #client 오브젝트 생성
client.on_connect = on_connect #콜백설정
client.on_message = on_message #콜백설정

client.connect("192.168.219.106", 1883, 60) #라즈베리파이3 MQTT 브로커에 연결

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

image_hub = imagezmq.ImageHub()

while True:
    keypoint=0
    a = 0
    rpi_name, image = image_hub.recv_image()
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    image.flags.writeable = False
    results = hands.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    #print(results.multi_hand_landmarks)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for a in range(21):
                keypoint+=hand_landmarks.landmark[a].x
            idx=0
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.imwrite('C:/workspace/pratice/web_server/tmp/img.png', cv2.flip(image, 1))
        keypoint = (keypoint*100)/a
        print(keypoint)
        client.publish("hand", keypoint)
    cv2.imshow(rpi_name, image)
    if cv2.waitKey(1) == ord('q'):
        break

    

    image_hub.send_reply(b'OK')