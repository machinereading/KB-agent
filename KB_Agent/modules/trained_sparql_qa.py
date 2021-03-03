import sys
import modules_constant
import socket
import sentence_parser
from keras.models import load_model
import gensim
import json
import numpy as np

def jsonload(fname, encoding="utf-8"):
    with open(fname, encoding=encoding) as f:
        j = json.load(f)

    return j

KB_AGENT_PATH = modules_constant.KB_AGENT_PATH
data_path = KB_AGENT_PATH + 'KB_Agent/modules/sparql_qa_model/'
# print(KB_AGENT_PATH + 'KB_Agent/modules/sparql_qa_model/')
# sys.path.append(KB_AGENT_PATH + 'KB_Agent/modules/sparql_qa_model/')

w2v = gensim.models.Word2Vec.load(data_path + 'ko.bin')
label_dict = jsonload(data_path + 'label.json')
label_to_uri = jsonload(data_path + 'property_uri.json')
idx_to_label = {}
for label, idx in label_dict.items():
    idx_to_label[idx] = label
model = load_model(data_path + 'sparql_qa_model')


def getETRI(text):
    # host = '143.248.135.60'
    # port = 33222
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


def get_embedding(word, w2v):
    if word in w2v.wv:
        vector = w2v.wv[word]
    else:
        vector = False

    return vector


def property_prediction_from_sentence(sentence):
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

    input_embed = np.zeros([1, modules_constant.MAX_SEQ_LEN, modules_constant.WORD_VEC_SIZE], np.float32)
    for j in range(len(morp_split)):
        embedding = get_embedding(morp_split[j], w2v)
        if embedding is False:
            continue
        if j >= modules_constant.MAX_SEQ_LEN:
            break
        input_embed[0][j] = embedding

    result_y = model.predict(input_embed)
    label_idx = result_y.argmax()
    label = idx_to_label[label_idx]
    score = result_y.max()

    # yhat = model.predict_classes(input_embed)
    # label = idx_to_label[yhat[0]]


    return label_to_uri[label], score


if __name__ == "__main__":
    question = '김연아는 어느나라 사람인가요?'
    print(property_prediction_from_sentence(question))
