# from keras.utils import np_utils
import random
import numpy as np
import pandas as pd 
import tensorflow as tf
import os
# from keras.preprocessing import sequence
import math
import json

frame_num = 123
# category = ['0', '가스', '가시', '감금', '감전', '개', '경찰', '기절', '끓는물', '누수', '누전', '도둑']
# category = ['0', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
# category = [
#  '0',
#  '0',
#  '1',
#  '10',
#  '1000',
#  '10000',
#  '16',
#  '2',
#  '28',
#  '3',
#  '4',
#  '5',
#  '6',
#  '7',
#  '8',
#  '9',
#  '95',
#  '가스',
#  '가시',
#  '감금',
#  '감전',
#  '강',
#  '강풍',
#  '개',
#  '거실',
#  '결박',
#  '경운기',
#  '경찰',
#  '기절',
#  '끓는물',
#  '누수',
#  '누전',
#  '도둑',
#  '앞집',
#  '어지러움',
#  '의사',
#  '인대',
#  '침수']

category = ['0', '0', '1', '10', '1000', '10000','16','2','28','3','4','5','6','7','8','9','경찰','기절','끓는물','누수','누전','도둑','시작','앞집','어지러움']

def get_distance(row):
    left = row[0:42]
    right = row[42:]
    dlist = []
    for i in range(0, len(left), 2):
        for j in range(i+2, len(left), 2):
            x1 = left[i]
            x2 = left[i+1]
            y1 = left[j]
            y2 = left[j+1]
            dlist.append(math.hypot(x2-x1, y2-y1))
    for i in range(0, len(right), 2):
        for j in range(i+2, len(right), 2):
            x1 = right[i]
            x2 = right[j]
            y1 = right[i+1]
            y2 = right[j+1]
            dlist.append(math.hypot(x2-x1, y2-y1))
    return dlist

def pred_word(keypoints):

    ex = np.array(keypoints).reshape(-1, 84)
    distance_list = []
    for row in range(len(ex)):
        distance_list.extend(get_distance(ex[row].tolist()))

    train_frame_len = frame_num * 420
    input_frame_len = len(distance_list)
    print(input_frame_len)
    if input_frame_len <= train_frame_len:
        # 0으로 padding
        distance_list = [0]*(train_frame_len-input_frame_len) + distance_list
    else:
        distance_list = distance_list[:train_frame_len]
    print(len(distance_list)/420)

    distance_list = np.array(distance_list).reshape(1, -1, 420)
    # print(distance_list.shape)

    model = tf.keras.models.load_model('201216_LSTM_89.h5') 
    # model = tf.keras.models.load_model('201215_LSTM_210_92.h5') 
    prediction = model.predict(distance_list)
    idx = np.argmax(prediction)

    # print(prediction)
    # print(category[idx])
    return category[idx]

if __name__ == '__main__':
    print('predict.py', len(arow))  