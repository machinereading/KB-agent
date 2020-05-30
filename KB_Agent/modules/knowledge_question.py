import DB_Linker as db_linker

import constant
KB_AGENT_PATH = constant.KB_AGENT_PATH

prior_property_path = KB_AGENT_PATH + 'KB_Agent/data/prior_property.json'
class_dict = {'level_1': ['Agent', 'Place'],
				'level_2': ['Person', 'Organisation', 'PopulatedPlace'],
				'level_3': ['EducationalInstitution', 'Settlement', 'Artist'],
				'level_4': ['College', 'University', 'Actor', 'City', 'Town']}


def nlg_with_triple(self, triple_list, dialogAct):
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
			question_list.append([entities[0]['uri'], candidate_property, '?o'])
			question_num += 1

	return question_list


def triple_question_generation(self, triple):
	s, p, o = triple
	s = s.split('/')[-1].rstrip('>')
	p = p.split('/')[-1].rstrip('>')
	question = s + '의 ' + p + '를 알려주세요.'
	return question


def save_knowledge(self, triple, utterance_id):
	db_linker.InsertKnowledgeToUserKB(self.user_name, triple)
	s, p, o = triple[0]
	s = s.split('/')[-1].rstrip('>')
	p = p.split('/')[-1].rstrip('>')
	o = o.split('/')[-1].rstrip('>')
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
	return '기본응답', 1