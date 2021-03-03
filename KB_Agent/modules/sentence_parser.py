# -*- coding:utf-8 -*-
import requests
import json


# statement로부터 분석기(추후 FrameNet 추가)
def Frame_Interpreter(text, target='all'):
    # Kor_FrameNet
    targetURL = "http://143.248.135.188:1107/frameBERT"
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    requestJson = {
        "text": text,
        "result_format": "textae"
    }
    response = requests.post(targetURL, data=json.dumps(requestJson), headers=headers)
    # print("[responseCode] " + str(response.status_code))
    # print(response.json())
    result_json = response.json()
    v_frame = []
    print(result_json)
    for frame in result_json:
        lu = frame['lu']
        pos = lu.split('.')[1]
        if target == 'all':
            v_frame.append(frame)
        else:
            if pos == target:
                v_frame.append(frame)

    return v_frame


def Entity_Linking(text):
    # Entity Linking 사용
    targetURL = "http://elvis.kaist.ac.kr:15151/entity_linking_plain/"
    # targetURL = "http://wisekb.kaist.ac.kr:6120/entity_linking_plain/"
    requestJson = {
        "content": text
    }
    '''
			headers={
				"Accept": "application/json, text/plain, */*",
				"Content-Type": "application/json; charset = utf-8"
			},
	'''
    response = requests.post(targetURL, data=requestJson)
    # print("[responseCode] " + str(response.status_code))
    print('entity_linking response:', response)
    try:
        if 'entities' not in response.json()[0]:
            return []
        entities = response.json()[0]['entities']
    except Exception as e:
        print('error: ', e)
        return []
    return entities


def relation_extraction(text):
    targetURL = "http://elvis.kaist.ac.kr:15251"
    requestJson = {
        "text": text
    }

    response = requests.post(targetURL, json=requestJson)
    # print("[responseCode] " + str(response.status_code))

    result = response.json()

    return result


def knowledge_validation(triple):
    print('validation_start')
    input_triple=[triple[0].split('/')[-1], triple[1].split('/')[-1], triple[2].split('/')[-1]]
    targetURL = "http://143.248.135.194:7701/check_B"

    response = requests.post(targetURL, json=input_triple)
    result = response.json()
    print('validation_end')
    return result


if __name__ == "__main__":
    # question = ' [김연아] 의 국가는 무엇인가요, [대한민국] 인가요.'
    # print(relation_extraction(question))
    #print(knowledge_validation(["들국화_(밴드)", "bandMember", "전인권"]))
    print(Entity_Linking('김연아는 어때'))
