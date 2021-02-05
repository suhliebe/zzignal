import numpy as np
import tensorflow as tf


def pred_number(arow):
    print('========arow.shape', arow.shape)
    arow2 = arow.reshape(1, -1, 210)
    print('=========arow2.shape', arow2.shape)

    # model = tf.keras.models.load_model('201214_LSTM_55_210_1.h5')
    model = tf.keras.models.load_model('201214_LSTM_210_92.h5')
    prediction = model.predict(arow2)

    print(prediction)
    for i in range(len(prediction)):
        idx = np.argmax(prediction[i])
        print('idx-1', idx-1)
        # category = pd.read_csv('category.csv')
        # res = category['sign_word'][category['sign_id'] == int(idx).values[0]
        # print('res', res)
    # return idx-1


if __name__ == '__main__':
    print('predict.py', len(arow))  