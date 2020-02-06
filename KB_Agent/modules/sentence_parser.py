# -*- coding:utf-8 -*-
import requests
import json

# statement로부터 분석기(추후 FrameNet 추가)
def Frame_Interpreter(text,target='all'):
	
	#Kor_FrameNet
	targetURL = "http://wisekb.kaist.ac.kr:1107/FRDF"
	headers = {'Content-Type': 'application/json; charset=utf-8'}
	requestJson = {
		"text": text,
		"result_format": "textae"
	}
	response = requests.post(targetURL, data=json.dumps(requestJson), headers=headers)
	#print("[responseCode] " + str(response.status_code))
	#print(response.json())
	result_json = response.json()
	v_frame = []

	for frame in result_json:
		lu = frame['lu']
		pos = lu.split('.')[1]
		if target=='all':
			v_frame.append(frame)
		else:
			if pos == target:
				v_frame.append(frame)

	return v_frame

def Entity_Linking(text):
	# Entity Linking 사용
	targetURL = "http://wisekb.kaist.ac.kr:6120/entity_linking_plain/"
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
	#print("[responseCode] " + str(response.status_code))

	entities = response.json()[0]['entities']

	return entities
