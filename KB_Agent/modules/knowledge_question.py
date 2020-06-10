import sentence_parser
import constant
import entity_summarization
import sys
import json

KB_AGENT_PATH = constant.KB_AGENT_PATH
sys.path.append(KB_AGENT_PATH + 'DB_linker/')
import DB_Linker as db_linker

prior_property_path = KB_AGENT_PATH + 'KB_Agent/data/prior_property.json'
entity_summarized_path = KB_AGENT_PATH + 'KB_Agent/data/entity_summarized.json'
class_dict = {'level_1': ['Agent', 'Place'],
			  'level_2': ['Person', 'Organisation', 'PopulatedPlace'],
			  'level_3': ['EducationalInstitution', 'Settlement', 'Artist'],
			  'level_4': ['College', 'University', 'Actor', 'City', 'Town']}
f = open(prior_property_path, 'r', encoding='utf-8')
prior_property = json.load(f)
f.close()

f = open(entity_summarized_path, 'r', encoding='utf-8')
entity_summarized = json.load(f)
f.close()

def nlg_with_triple(triple_list, dialogAct):
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
			temp = s + '의 ' + p + '는 ' + o + '에요.'
			if 'wiki' in temp or 'abstract' in temp:
				continue
			answer = answer + temp + '\n'

	return answer


def get_entity_type(entities):
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


def Knowledge_check(triple, user_id=None):
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


def get_entity_question_list(user_name ,entities, entity_type):
	question_property_list = prior_property[entity_type]
	question_num = 0
	question_list = []
	for candidate_property in question_property_list:
		if question_num == 3:
			break
		userdb_query = Knowledge_check([entities[0]['uri'], candidate_property, '?o'], user_name)
		masterdb_query = Knowledge_check([entities[0]['uri'], candidate_property, '?o'])

		masterdb_result = db_linker.QueryToMasterKB(masterdb_query)
		userdb_result = db_linker.QueryToUserKB(userdb_query)

		if masterdb_result['boolean'] == False and userdb_result['boolean'] == False:
			question_list.append([entities[0]['uri'], candidate_property, '?o'])
			question_num += 1

	return question_list


def triple_question_generation(triple):
	s, p, o = triple
	s = s.split('/')[-1].rstrip('>')
	p = p.split('/')[-1].rstrip('>')
	question = s + '의 ' + p + '를 알려주세요.'
	return question


def save_knowledge_to_database(triple, utterance_id):
	s, p, o = triple
	# s = s.split('/')[-1].rstrip('>')
	# p = p.split('/')[-1].rstrip('>')
	# o = o.split('/')[-1].rstrip('>')
	datalist = []
	datadict = {
		'utterance_id': utterance_id,
		'subject': s,
		'property': p,
		'object': o
	}
	datalist.append(datadict)
	db_linker.InsertDataToTable('USERKB_LOG', datalist)


def knowledge_conversation(user_id=None, user_utterance=None):
	entities = sentence_parser.Entity_Linking(user_utterance)
	user_info = db_linker.GetUserInfo(user_id=user_id)
	user_name = user_info['user_name']
	print("entities: ", entities)
	answer = ''
	last_system_utterance_info = db_linker.getLatestUtterance(user_id=user_id, speaker='system')
	now_user_utterance_info = db_linker.getLatestUtterance(user_id=user_id, speaker='user')
	last_user_utterance_info = db_linker.getLatestUtterance(user_id=user_id, speaker='last_user')

	if last_system_utterance_info['intent_req'] == 'entity_question':
		entities = sentence_parser.Entity_Linking(user_utterance)
		answer = ''
		if len(entities) > 0:
			entity = entities[-1]['uri']
			question_info = db_linker.getTripleQuestion(last_user_utterance_info['utterance_id'])
			if len(question_info) == 0:
				return '질문이 뭐였는지 못찾았어요, 감사합니다.', 'entity_answer'
			triple = [question_info['subject'], question_info['property'], entity]
			save_knowledge_to_database(triple, now_user_utterance_info['utterance_id'])
			db_linker.InsertKnowledgeToUserKB(user_name, [triple])
			answer += nlg_with_triple([triple], 'Knowledge_inform')
		else:
			answer = '무슨말씀이신지 잘 모르겠어요. 넘어갈게요!\n'

		dialog_act = 'entity_answer'
		answer += '감사합니다.'
		# if len(self.entity_question_triple_list) > 0:
		# 	self.question_triple = self.entity_question_triple_list.pop(0)
		# 	answer = answer + self.triple_question_generation(self.question_triple)
		#
		return answer, dialog_act

	## entity가 잡힌 경우
	if len(entities) > 0:

		## Entity summarization을 통해 정보 제공
		print(entities[0]['text'])

		# summarized_triples = entity_summarization.ES(entities[0]['text'])
		#
		# answer = nlg_with_triple(summarized_triples, 'Knowledge_inform')
		# print("summarized_triples: ", summarized_triples)
		if entities[0]['text'] in entity_summarized:
			summarized_triples = entity_summarized[entities[0]['text']]['top5']
			answer = nlg_with_triple(summarized_triples, 'Knowledge_inform')

		entity_type = get_entity_type(entities)

		print("entity_type: ", entity_type)

		##entity type이 잡혀서 질문 목록 생성
		if entity_type is not None:
			entity_question_triple_list = get_entity_question_list(user_name, entities, entity_type)

		print("entity_question_triple_list: ", entity_question_triple_list)


		## 질문 목록에 대해 질문 시작
		if len(entity_question_triple_list) > 0:
			answer = answer + entities[0]['text'] + '에 대해서 물어보고 싶은게 있어요.\n'
			question_triple = entity_question_triple_list.pop(0)
			print(question_triple)
			save_knowledge_to_database(question_triple, now_user_utterance_info['utterance_id'])
			answer = answer + triple_question_generation(question_triple)
			dialog_act = 'entity_question'

		return answer, dialog_act

	return None, None


if __name__ == "__main__":
	question = '로마에서 휴가를 보냈어'
	user = 43
	print(knowledge_conversation(user_utterance=question, user_id=user))
