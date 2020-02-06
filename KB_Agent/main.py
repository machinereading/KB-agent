# -*- coding:utf-8 -*-

import sys
import os
import json
sys.path.append('../DB_linker/')
import DB_Linker as db_linker
import datetime
from modules import sentence_parser
from modules import entity_summarization

frame_info_path = './data/frame_info_full.json'
prior_property_path = './data/prior_property.json'

# class_dict = {'level_1': ['Disease', 'Event', 'Food', 'Place', 'Species', 'Work'],
# 				'level_2': ['Sport', 'Organisation', 'Person', 'PopulatedPlace', 'Film', 'MusicalWork'],
# 				'level_3': ['FictionalCharacter', 'Company', 'SportsTeam', 'Artist', 'Athlete', 'Scientist', 'Writer',
# 							  'SportsEvent', 'Settlement'],
# 				'level_4': ['College', 'University', 'School', 'MusicalArtist', 'Station']}
class_dict = {'level_1': ['Agent', 'Place'],
				'level_2': ['Person', 'Organisation', 'PopulatedPlace'],
				'level_3': ['EducationalInstitution', 'Settlement', 'Artist'],
				'level_4': ['College', 'University', 'Actor', 'City', 'Town']}

class kb_agent:

	user_name = None
	user_id = None
	pre_system_dialog_act = None
	frame_info = None
	frame_log_id = None
	question_argument = None
	prior_property = None
	lu = None
	question_triple = None
	empty_argument_list = []
	entity_question_triple_list = []

	def __init__(self,user_name):
		if self.user_login(user_name) == False:
			self.user_id = db_linker.AddNewUser(user_name)

		f = open(frame_info_path,'r',encoding='utf-8')
		self.frame_info = json.load(f)
		f.close()

		f = open(prior_property_path,'r',encoding='utf-8')
		self.prior_property = json.load(f)
		f.close()
	def user_login(self, user_name):
		self.user_name = user_name
		users = db_linker.LookUpUsers()

		for user in users:
			if user['user_name'] == user_name:
				self.user_id = user['user_id']
				return True
		return False
	def save_frame_info(self, frames, utterance_id):
		datalist = []
		datadict = {
		'utterance_id' : utterance_id,
		'lu' : frames[-1]['lu'],
		'frame' : frames[-1]['frame']
		}
		datalist.append(datadict)
		frame_log_id = db_linker.InsertDataToTable('FRAME_LOG',datalist)

		
		for denotation in frames[-1]['denotations']:
			datalist = []
			datadict = {
			'frame_log_id' : frame_log_id,
			'object' : denotation['obj'],
			'role' : denotation['role']
			}
			datalist.append(datadict)
			denotation_log_id = db_linker.InsertDataToTable('FRAME_DENOTATION',datalist)
			for span in denotation['token_span']:
				datalist = []
				datadict = {
				'denotation_log_id' : denotation_log_id,
				'token_span' : span
				}
				datalist.append(datadict)
				span_id = db_linker.InsertDataToTable('FRAME_DENOTATION_SPAN',datalist)

		return frame_log_id

	def get_frame_core_empty_argument(self, frames):
		frame = frames[-1]['frame']
		core_argument_list = []
		for argument_info in self.frame_info[frame]['arguments']:
			if argument_info['coreType'] == 'Core':
				core_argument_list.append(argument_info['fe'])
		
		denotation_argument_list = []
		for denotation in frames[-1]['denotations']:
			if denotation['role'] == 'ARGUMENT':
				denotation_argument_list.append(denotation['obj'])

		empty_argument_list = []
		for argument in core_argument_list:
			if argument not in denotation_argument_list:
				empty_argument_list.append(argument)

		return empty_argument_list

	def sparql_dialog(self, sentence):
		return 'sparql_answer'

	def get_sparql_similarity(self, sentence):

		return 0

	def frame_argument_question(self, frames):
		question_argument = self.empty_argument_list.pop()
		self.question_argument = question_argument
		question = self.lu +'의 ' +question_argument + '는 무엇인가요?'
		return question

	def save_frame_answer(self, frames, utterance_id):
		for denotation in frames[-1]['denotations']:
			datalist = []
			if denotation['role'] == 'TARGET':
				datadict = {
				'frame_log_id' : self.frame_log_id,
				'utterance_id' : utterance_id,
				'object' : self.question_argument,
				'role' : 'ARGUMENT'
				}
				datalist.append(datadict)
				frame_answered_denotation_id = db_linker.InsertDataToTable('FRAME_ANSWERED_DENOTATION',datalist)
				for span in denotation['token_span']:
					datalist = []
					datadict = {
					'frame_answered_denotation_id' : frame_answered_denotation_id,
					'token_span' : span
					}
					datalist.append(datadict)
					span_id = db_linker.InsertDataToTable('FRAME_ANSWERED_DENOTATION_SPAN',datalist)

			return denotation['text']
	def react_frame_answer(self, sentence, utterance_id):
		frames = sentence_parser.Frame_Interpreter(sentence,target='n')

			## 대답에서 frame을 잡지 못한 경우
		if len(frames)>0:
			obj = self.save_frame_answer(frames, utterance_id)
			answer = self.question_argument + '는 ' + obj +' 이군요 '
			answer = answer + '감사합니다.'

			## 질문이 더 남은 경우
			if len(self.empty_argument_list) > 0:
				self.pre_system_dialog_act = 'frame_question'
				answer = answer + ' ' +self.frame_argument_question(frames)

			## 질문이 더 남지 않은 경우
			else:
				self.pre_system_dialog_act = None

			## 대답에서 frame을 잡지 못한 경우
		else:
			answer = '죄송한데, 잘 이해를 못했어요. 다시 알려주세요.'

		return answer

	def nlg_with_triple(self,triple_list, dialogAct):
		answer = ''

		if dialogAct == 'Knowledge_inform':
			for triple in triple_list:
				if str(type(triple)) == "<class 'str'>":
					s, p, o = triple.split('\t')
				else:
					s, p, o = triple
				s = s.split('/')[-1].rstrip('>')
				p = p.split('/')[-1].rstrip('>')
				if 'http://kbox' in o:
					o = o.split('/')[-1].rstrip('>')
				temp = s+'의 '+p+'는 '+o+'에요.'
				if 'wiki' in temp or 'abstract' in temp:
					continue
				answer = answer + temp + '\n'

		return answer
	def get_entity_type(self, entities):
		entity_list = []
		
		for entity_type in entities[0]['type']:
			if 'http://dbpedia.org/ontology/' in entity_type:
				entity_list.append(entity_type.split('/')[-1])

		for entity_type in class_dict['level_4']:
			if entity_type in entity_list:
				return entity_type
		
		for entity_type in class_dict['level_3']:
			if entity_type in entity_list:
				return entity_type

		for entity_type in class_dict['level_2']:
			if entity_type in entity_list:
				return entity_type

		for entity_type in class_dict['level_1']:
			if entity_type in entity_list:
				return entity_type

		return None
	def Knowledge_check(self, triple, user_id=None):
		s, p, o = triple
		s = '<' + s + '>'
		p = '<' + p + '>'
		target = o

		result_query = 'ASK'
		if user_id:
			result_query = result_query + ' where { graph <http://kbox.kaist.ac.kr/username/' + user_id + '> { ' + s + ' ' + p + ' ' + o + ' } }'
		else:
			result_query = result_query + ' where { ' + s + ' ' + p + ' ' + o + ' }'

		return result_query

	def get_entity_question_list(self, entities, entity_type):
		question_property_list = self.prior_property[entity_type]
		question_num = 0
		question_list = []
		for candidate_property in question_property_list:
			if question_num == 3:
				break
			userdb_query = self.Knowledge_check([entities[0]['uri'], candidate_property, '?o'], self.user_name)
			masterdb_query = self.Knowledge_check([entities[0]['uri'], candidate_property, '?o'])
			
			masterdb_result = db_linker.QueryToMasterKB(masterdb_query)
			userdb_result = db_linker.QueryToUserKB(userdb_query)
			
			if masterdb_result['boolean'] == False and userdb_result['boolean'] == False:
				question_list.append([entities[0]['uri'],candidate_property,'?o'])
				question_num += 1

		return question_list

	def triple_question_generation(self, triple):
		s, p, o = triple
		s = s.split('/')[-1].rstrip('>')
		p = p.split('/')[-1].rstrip('>')
		question = s+'의 '+p+'를 알려주세요.'
		return question

	def save_knowledge(self, triple, utterance_id):
		db_linker.InsertKnowledgeToUserKB(self.user_name,triple)
		s, p, o = triple[0]
		s = s.split('/')[-1].rstrip('>')
		p = p.split('/')[-1].rstrip('>')
		o = o.split('/')[-1].rstrip('>')
		datalist = []
		datadict = {
		'utterance_id' : utterance_id,
		'subject' : s,
		'property' : p,
		'object' : o
		}
		datalist.append(datadict)
		db_linker.InsertDataToTable('USERKB_LOG', datalist)

	def dialog_policy(self,sentence, utterance_id):

		## 이전에 시스템이 비어있는 frame argument에 대해 질문을 한 경우
		## 사용자는 질문에 대한 대답을 했다고 가정.
		if self.pre_system_dialog_act =='frame_question':
			return self.react_frame_answer(sentence, utterance_id)
		elif self.pre_system_dialog_act == 'entity_question':

			entities = sentence_parser.Entity_Linking(sentence)
			answer = ''
			if len(entities) >0:
				entity = entities[-1]['uri']
				self.save_knowledge([[self.question_triple[0],self.question_triple[1],entity]], utterance_id)
				answer += self.nlg_with_triple([[self.question_triple[0],self.question_triple[1],entity]],'Knowledge_inform')
			else:
				answer = '무슨말씀이신지 잘 모르겠어요. 넘어갈게요!\n'

			if len(self.entity_question_triple_list) > 0:
				self.question_triple = self.entity_question_triple_list.pop(0)
				answer = answer + self.triple_question_generation(self.question_triple)
			else:
				self.pre_system_dialog_act = None
				answer += '감사합니다.'

			return answer
		## 아무런 상태가 아닌 경우 ( 초기 상태 )
		else:
			## SPARQL 쿼리로 변환 가능한 질문인 경우
			if self.get_sparql_similarity(sentence)>0.9:
				return self.sparql_answer(sentence)

			frames = sentence_parser.Frame_Interpreter(sentence,target='v')

			## frame이 잡힌경우
			if len(frames)>0:
				self.frame_log_id = self.save_frame_info(frames, utterance_id)
				self.lu = frames[-1]['lu']
				self.empty_argument_list = self.get_frame_core_empty_argument(frames)

				## frame이 잡혔고, 비어있는 core element가 존재하는 경우	
				if len(self.empty_argument_list) > 0:
					self.pre_system_dialog_act = 'frame_question'
					return self.frame_argument_question(frames)

			entities = sentence_parser.Entity_Linking(sentence)
			## entity가 잡힌 경우
			if len(entities)>0:
				answer = ''
				## Entity summarization을 통해 정보 제공
				summarized_triples = entity_summarization.ES(entities[0]['text'])
				answer = self.nlg_with_triple(summarized_triples, 'Knowledge_inform')


				entity_type = self.get_entity_type(entities)

				##entity type이 잡혀서 질문 목록 생성
				if entity_type is not None:			
					self.entity_question_triple_list = self.get_entity_question_list(entities,entity_type)

				## 질문 목록에 대해 질문 시작
				if len(self.entity_question_triple_list) > 0:
					answer = answer + entities[0]['text']+'에 대해서 물어보고 싶은게 있어요.\n'
					self.question_triple = self.entity_question_triple_list.pop(0)
					answer = answer + self.triple_question_generation(self.question_triple)
					self.pre_system_dialog_act = 'entity_question'

				return answer

		## 어디에서도 처리하지 못한 경우
		return '죄송해요, 제가 이해할 수 있는 말이 아닙니다.'
		

	

	def chat(self, sentence, utterance_id):

		system_utterance = self.dialog_policy(sentence, utterance_id)
		return system_utterance

	def save_utterance(self, sentence, speaker):
		datalist=[]
		now = datetime.datetime.now()
		nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
		datadict = {
		'utterance' : sentence,
		'date_time' : nowDatetime,
		'speaker' : speaker,
		'user_id' : self.user_id
		}
		datalist.append(datadict)
		#print(datalist)
		return db_linker.InsertDataToTable('DIALOG',datalist)


global_command = ['stop']


if __name__ == "__main__":

	print('사용자 이름을 입력해주세요.')
	user_name = input()

	chat_bot = kb_agent(user_name)

	print(user_name+'님 안녕하세요.')

	while True:
		user_utterance = input()
		utterance_id = chat_bot.save_utterance(user_utterance,'user')

		if user_utterance in global_command:
			break

		system_utterance = chat_bot.chat(user_utterance,utterance_id)
		chat_bot.save_utterance(system_utterance,'system')
		print(system_utterance)


	
