#!/usr/bin/env python3
import sys
from keras.layers import Bidirectional, Dense, LSTM
from keras.models import Sequential, load_model
import socket
import gensim
import json
import numpy as np

sys.path.insert(0, './resources')
import constant


def jsonload(fname, encoding="utf-8"):
    with open(fname, encoding=encoding) as f:
        j = json.load(f)

    return j


def get_embedding(word, w2v):
    if word in w2v.wv:
        vector = w2v.wv[word]
    else:
        vector = False

    return vector


def get_data(data_file_name, label_dic, w2v):

    data_dict = jsonload(data_file_name)
    input_embed = np.zeros([len(data_dict), constant.MAX_SEQ_LEN, constant.WORD_VEC_SIZE], np.float32)
    targets = np.zeros([len(data_dict), constant.LABEL_NUM], np.float32)

    for i in range(len(data_dict)):

        for j in range(len(data_dict[i]['morp_split'])):
            embedding = get_embedding(data_dict[i]['morp_split'][j], w2v)
            if embedding is False:
                continue
            if j >= constant.MAX_SEQ_LEN:
                break
            input_embed[i][j] = embedding

    for i in range(len(data_dict)):
        idx = label_dic[data_dict[i]['property']]
        targets[i][idx] = 1
    return input_embed, targets


def getETRI(text):
    host = '143.248.135.146'
    port = 44444

    ADDR = (host, port)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        clientSocket.connect(ADDR)
    except Exception as e:
        print(e)
        return None
    try:
        clientSocket.sendall(str.encode(text))
        buffer = bytearray()
        while True:
            data = clientSocket.recv(1024)
            if not data:
                break
            buffer.extend(data)
        result = json.loads(buffer.decode(encoding='utf-8'))
        return result

    except Exception as e:
        print(e)
        return None


def test_model(w2v, label_dict):
    model = load_model('test_model')
    x, y = get_data(constant.FILE_ROOT + '_test_qa.json', label_dict, w2v)
    yhat = model.predict_classes(x)
    print(yhat)
    print(yhat.shape)

    count = 0
    for idx in range(len(y)):
        if y[idx][yhat[idx]] == 1:
            count += 1
    print(len(y))
    print(count)



def property_prediction_from_sentence(sentence, w2v, idx_to_label, model, label_to_uri):
    morp_split = []
    etri_result = getETRI(sentence)
    try:
        for s in etri_result['sentence']:
            for morp in s['morp']:
                morp_split.append(morp['lemma'])
    except:
        print(sentence)
        print(etri_result)
        return 'error'

    input_embed = np.zeros([1, constant.MAX_SEQ_LEN, constant.WORD_VEC_SIZE], np.float32)
    for j in range(len(morp_split)):
        embedding = get_embedding(morp_split[j], w2v)
        if embedding is False:
            continue
        if j >= constant.MAX_SEQ_LEN:
            break
        input_embed[0][j] = embedding

    yhat = model.predict_classes(input_embed)
    label = idx_to_label[yhat[0]]

    return label_to_uri[label]

if __name__ == '__main__':
    w2v = gensim.models.Word2Vec.load(constant.FILE_ROOT + '/ko.bin')
    label_dict = jsonload(constant.FILE_ROOT + 'label.json')
    label_to_uri = jsonload(constant.FILE_ROOT + 'property_uri.json')
    idx_to_label = {}
    for label, idx in label_dict.items():
        idx_to_label[idx] = label
    model = load_model('test_model')

    print(property_prediction_from_sentence('김연아는 어느나라 사람인가요?', w2v, idx_to_label, model, label_to_uri))

    #test_model(w2v, label_dict)
    sys.exit()


    print('data loading')
    train_x, train_y = get_data(constant.FILE_ROOT + '_train_qa.json', label_dict, w2v)
    dev_x, dev_y = get_data(constant.FILE_ROOT + '_dev_qa.json', label_dict, w2v)
    print('data loading complete')

    model = Sequential()
    model.add(Bidirectional(LSTM(128,
                                 dropout=0.2,
                                 recurrent_dropout=0.2,
                                 input_shape=(constant.MAX_SEQ_LEN, constant.WORD_VEC_SIZE))))
    model.add(Dense(256, activation='relu'))
    model.add(Dense(constant.LABEL_NUM, activation='softmax'))


    model.compile(loss="categorical_crossentropy", metric=['accuracy'], optimizer="rmsprop")
    model.fit(train_x, train_y, epochs=5, batch_size=32)
    model.summary()
    model.save('test_model')
    result = model.predict(dev_x)

    print('result:', result.shape)
    result = model.evaluate(dev_x, dev_y)
    print('result:', result)

