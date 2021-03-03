import sentence_parser
import modules_constant
import entity_summarization
import sys
import json
import re
import random
import numpy as np

KB_AGENT_PATH = modules_constant.KB_AGENT_PATH
sys.path.append(KB_AGENT_PATH + 'DB_linker/')
import DB_Linker as db_linker

prior_property_path = KB_AGENT_PATH + 'KB_Agent/data/prior_property.json'
entity_summarized_path = KB_AGENT_PATH + 'KB_Agent/data/entity_summarized.json'
triple_template_path = KB_AGENT_PATH + 'KB_Agent/data/triple_template.json'
relation_template_path = KB_AGENT_PATH + 'KB_Agent/data/relations_template.json'

mapped_agreed_path = KB_AGENT_PATH + 'KB_Agent/data/mapped_agreed_20150714.txt'
mappings_release_path = KB_AGENT_PATH + 'KB_Agent/data/mappings_release_150529.txt'
p_ko_list_A_path = KB_AGENT_PATH + 'KB_Agent/data/p-ko-list-A.tsv'
p_ko_list_B_path = KB_AGENT_PATH + 'KB_Agent/data/p-ko-list-B.tsv'
class_parent_path = KB_AGENT_PATH + 'KB_Agent/data/class-parent.tsv'
type_predicate_dict_path = KB_AGENT_PATH + 'KB_Agent/data/type_predicate_dict.json'
sorted_pageview_list_path = KB_AGENT_PATH + 'KB_Agent/data/sorted_pageview.json'
type_of_property_path = KB_AGENT_PATH + 'KB_Agent/data/property_type.json'
ne_tag_info_path = KB_AGENT_PATH + 'KB_Agent/data/ne_tag_info.json'

class_dict = {'level_1': ['Agent', 'Place'],
              'level_2': ['Person', 'Organisation', 'PopulatedPlace'],
              'level_3': ['EducationalInstitution', 'Settlement', 'Artist'],
              'level_4': ['College', 'University', 'Actor', 'City', 'Town']}

f = open(type_predicate_dict_path, 'r', encoding='utf-8')
type_predicate_dict = json.load(f)
f.close()

f = open(prior_property_path, 'r', encoding='utf-8')
prior_property = json.load(f)
f.close()

f = open(entity_summarized_path, 'r', encoding='utf-8')
entity_summarized = json.load(f)
f.close()

f = open(triple_template_path, 'r', encoding='utf-8')
triple_template = json.load(f)
f.close()

f = open(relation_template_path, 'r', encoding='utf-8')
relation_template = json.load(f)
f.close()

f = open(sorted_pageview_list_path, 'r', encoding='utf-8')
sorted_pageview_list = json.load(f)
f.close()

f = open(type_of_property_path, 'r', encoding='utf-8')
type_of_property_dict = json.load(f)
f.close()

f = open(ne_tag_info_path, 'r', encoding='utf-8')
ne_tag_info_dict = json.load(f)
f.close()

class_parent_file = open(class_parent_path, 'r', encoding='utf-8')

class_parent_dict = {}
for line in class_parent_file.readlines():
    temp = line.split('\t')
    child = temp[0].split('/')[-1].strip()
    parent = temp[1].split('/')[-1].strip()
    class_parent_dict[child] = parent


def isHangul(text):
    count = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', text))
    return count > 0


def create_dict_dbpedia_en_to_ko_for_property():
    mapped_agreed_file = open(mapped_agreed_path, 'r', encoding='utf-8')
    mappings_release_file = open(mappings_release_path, 'r', encoding='utf-8')
    p_ko_list_A_file = open(p_ko_list_A_path, 'r', encoding='utf-8')
    p_ko_list_B_file = open(p_ko_list_B_path, 'r', encoding='utf-8')

    en_to_ko_dict = {}

    for line in mapped_agreed_file.readlines():
        temp = line.split('\t')
        ko_prop = temp[0].split('/')[-1]
        en_prop = temp[1].split('/')[-1]
        if isHangul(ko_prop) is False:
            continue
        if en_prop not in en_to_ko_dict:
            en_to_ko_dict[en_prop] = ko_prop

    for line in mappings_release_file.readlines():
        temp = line.split('\t')
        ko_prop = temp[1].split('/')[-1].strip('>')
        en_prop = temp[0].split('/')[-1].strip('>')
        if isHangul(ko_prop) is False:
            continue
        if en_prop not in en_to_ko_dict:
            en_to_ko_dict[en_prop] = ko_prop

    for line in p_ko_list_A_file.readlines():
        temp = line.split('\t')
        ko_prop = temp[1]
        en_prop = temp[0].split('/')[-1]
        if isHangul(ko_prop) is False:
            continue
        if en_prop not in en_to_ko_dict:
            en_to_ko_dict[en_prop] = ko_prop

    for line in p_ko_list_B_file.readlines():
        temp = line.split('\t')
        ko_prop = temp[1]
        en_prop = temp[0].split('/')[-1]
        if isHangul(ko_prop) is False:
            continue
        if en_prop not in en_to_ko_dict:
            en_to_ko_dict[en_prop] = ko_prop

    mapped_agreed_file.close()
    mappings_release_file.close()
    p_ko_list_A_file.close()
    p_ko_list_B_file.close()

    return en_to_ko_dict


property_en_to_ko_dict = create_dict_dbpedia_en_to_ko_for_property()


def nlg_with_triple(triple_list, dialogAct, entity_type):
    answer = ''

    if dialogAct == 'Knowledge_inform':

        for triple in triple_list:
            if str(type(triple)) == "<class 'str'>":
                s, p, o = triple.split('\t')
            else:
                s, p, o = triple
            s = s.split('/')[-1].rstrip('>').replace('_', ' ')
            p = p.split('/')[-1].rstrip('>')
            if 'http://kbox' in o or 'dbpedia.org' in o:
                o = o.split('/')[-1].rstrip('>')
            elif '^^' in o:
                o = o.split('"')[1]

            found = False
            if entity_type in triple_template:
                if p in triple_template[entity_type]:
                    template = triple_template[entity_type][p]["Knowledge_Inform"][0]
                    temp = template.replace('<SUB>', s).replace('<OBJ>', o)
                    found = True

            if found is False:
                if p in triple_template['Thing']:
                    template = triple_template['Thing'][p]["Knowledge_Inform"][0]
                    temp = template.replace('<SUB>', s).replace('<OBJ>', o)
                else:
                    if p in relation_template:
                        template = relation_template[p]['template']
                        temp = template.replace('<SUB>', s).replace('<OBJ>', o)
                    else:
                        if p in property_en_to_ko_dict:
                            temp = s + '의 ' + property_en_to_ko_dict[p] + '는 ' + o + '에요.'
                        else:
                            temp = s + '의 ' + p + '는 ' + o + '에요.'
            if 'wiki' in temp or 'abstract' in temp:
                continue
            answer = answer + temp + '\n'

    # if dialogAct == 'triple_question':
    # 	s, p, o = triple
    # 	s = s.split('/')[-1].rstrip('>')
    # 	p = p.split('/')[-1].rstrip('>')
    # 	question = s + '의 ' + p + '를 알려주세요.'
    # 	return question

    return answer


def get_entity_type(entity):
    entity_list = []

    for entity_type in entity['type']:
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
        result_query = result_query + ' where { graph <http://kbox.kaist.ac.kr/username/' + user_id + '> {{ ' + s + ' ' + p + ' ' + o + ' }UNION{ ' + s.replace(
            'http://kbox.kaist.ac.kr', 'http://ko.dbpedia.org') + ' ' + p + ' ' + o.replace(
            'http://kbox.kaist.ac.kr', 'http://ko.dbpedia.org') + '}} }'
    else:
        result_query = result_query + ' where {{ ' + s + ' ' + p + ' ' + o + ' }UNION{' + s.replace(
            'http://kbox.kaist.ac.kr', 'http://ko.dbpedia.org') + ' ' + p + ' ' + o.replace(
            'http://kbox.kaist.ac.kr', 'http://ko.dbpedia.org') + '}}'
    print(result_query)

    return result_query


def get_entity_question_list(user_id, user_name, entity, entity_type):
    if entity_type not in type_predicate_dict:
        return [], None
    predicate_dict = type_predicate_dict[entity_type]
    question_property_list = []
    count = 1
    for key, item in predicate_dict.items():
        if key in ['picture', 'pictureDescription', 'recordLabel']:
            continue
        question_property_list.append('http://dbpedia.org/ontology/' + key)
        count += 1
        # 1111#     break

    # question_property_list = prior_property[entity_type]
    question_num = 0
    question_list = []

    ret_m_type = None
    for candidate_property in question_property_list:
        if question_num == 3:
            break

        userdb_query = Knowledge_check([entity['uri'], candidate_property, '?o'], user_name)
        masterdb_query = Knowledge_check([entity['uri'], candidate_property, '?o'])

        print('userdb_query: ', userdb_query)
        print('masterdb_query: ', masterdb_query)

        masterdb_result = db_linker.QueryToMasterKB(masterdb_query)
        userdb_result = db_linker.QueryToUserKB(userdb_query)

        print('masterdb_result: ', masterdb_result)
        print('userdb_result: ', userdb_result)

        if masterdb_result['boolean'] == False and userdb_result['boolean'] == False:

            is_asked = is_asked_knowledge(user_id, entity['uri'], candidate_property)
            if is_asked is not False:
                max_module_type = 'A'
                for module_type in is_asked:
                    m_type = module_type['intent_emp']
                    if m_type > max_module_type:
                        max_module_type = m_type
                if max_module_type < 'D':
                    ret_m_type = max_module_type
                else:
                    continue

            question_list.append([entity['uri'], candidate_property, '?o'])
            question_num += 1
            break

    return question_list, ret_m_type


def triple_question_generation(triple, entity_type):
    s, p, o = triple
    s = s.split('/')[-1].rstrip('>').replace('_', ' ')
    p = p.split('/')[-1].rstrip('>')

    found = False

    if entity_type in triple_template:
        if p in triple_template[entity_type]:
            template = triple_template[entity_type][p]["Knowledge_Question"][0]
            question_sentence = template.replace('<SUB>', s)
            found = True
    if found is False:
        if p in triple_template['Thing']:
            template = triple_template['Thing'][p]["Knowledge_Question"][0]
            question_sentence = template.replace('<SUB>', s)
        else:
            if p in relation_template:
                ko_relation = relation_template[p]['ko_relation']
                question_sentence = s + '의 ' + ko_relation + '을(를) 알려주세요.'
            else:
                if p in property_en_to_ko_dict:
                    question_sentence = s + '의 ' + property_en_to_ko_dict[p] + '를 알려주세요.'
                else:
                    question_sentence = s + '의 ' + p + '를 알려주세요.'

    return question_sentence


def get_class_level(input_type):
    level = 0
    while True:
        if input_type not in class_parent_dict:
            return level
        input_type = class_parent_dict[input_type]
        level += 1


def get_highest_level_type(type_list):
    highest_class_level = -1

    highest_type = False
    if type_list is False:
        return False
    for t in type_list:
        if 'http://dbpedia.org/ontology/' not in t:
            continue
        temp_type = t.split('/')[-1].strip()
        level = get_class_level(temp_type)
        if level > highest_class_level:
            highest_class_level = level
            highest_type = temp_type

    return highest_type


def save_knowledge_to_database(triple, utterance_id):
    s, p, o = triple
    # s = s.split('/')[-1].rstrip('>')
    # p = p.split('/')[-1].rstrip('>')
    # o = o.split('/')[-1].rstrip('>')
    datalist = []
    if o != '?o':
        try:
            # kv_result = sentence_parser.knowledge_validation(triple)
            # kv_score = kv_result[1]
            kv_score = -1
        except:
            kv_score = -1
    else:
        kv_score = 0

    datadict = {
        'utterance_id': utterance_id,
        'subject': s,
        'property': p,
        'object': o,
        'kv_module_score': kv_score
    }
    datalist.append(datadict)
    db_linker.InsertDataToTable('USERKB_LOG', datalist)


def inform_question_related(sub_type, predicate):
    type_uri = '<http://dbpedia.org/ontology/' + sub_type + '>'
    predicate = '<' + predicate + '>'
    query = '''SELECT * where {
  ?s ''' + predicate + ''' ?o .
  ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>	''' + type_uri + ''' .
                       }
'''
    print('test_query: ', query)
    masterdb_result = db_linker.QueryToMasterKB(query)

    if len(masterdb_result['results']['bindings']) == 0:
        return False
    else:
        for temp in masterdb_result['results']['bindings']:
            s = temp['s']['value'].split('/')[-1]
            p = predicate.split('/')[-1].strip('>')
            o = temp['o']['value'].split('/')[-1]

            if isHangul(s) is False:
                continue

            if p in relation_template:
                ko_relation = relation_template[p]['ko_relation']
                question_sentence = s + '의 ' + ko_relation + '는 ' + o + ' 인데, '
            else:
                if p in property_en_to_ko_dict:
                    question_sentence = s + '의 ' + property_en_to_ko_dict[p] + '는 ' + o + ' 인데, '
                else:
                    question_sentence = s + '의 ' + p + '는 ' + o + ' 인데, '
            return question_sentence, temp['s']['value']+"\t"+predicate+'\t'+temp['o']['value']


def get_entity_type_from_knowledge_base(uri=None):
    query = '''select distinct ?o where{
  {
    <''' + uri + '''> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?o
    }
    union
  {
    <''' + uri + '''> owl:sameAs ?ko .
    ?ko <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?o
    }
    union
  {
    ?ko owl:sameAs <''' + uri + '''> .
    ?ko <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?o
    }
 }'''
    masterdb_result = db_linker.QueryToMasterKB(query)

    print('test_result: ', masterdb_result)
    if len(masterdb_result['results']['bindings']) == 0:
        return False
    else:
        type_list = []
        for t in masterdb_result['results']['bindings']:
            type_list.append(t['o']['value'])
        return type_list


def get_user_interesting_entity(user_id=None):
    query_result = db_linker.getEntityListWithUserID(user_id=user_id)
    entity_appearance = []
    print(query_result)
    uri_netype_dict = {}
    if query_result is not None:
        for entity in query_result:
            entity_appearance.append(entity['entity_uri'])
            if entity['entity_uri'] not in uri_netype_dict:
                uri_netype_dict[entity['entity_uri']] = entity['entity_ne_type']
        idx = random.randint(0, len(entity_appearance)-1)

        entity_uri = entity_appearance[idx]
        text = entity_uri.split('/')[-1]
        type_list = get_entity_type_from_knowledge_base(entity_uri)

        result = {
            'text': text,
            'type': type_list,
            'ne_type': uri_netype_dict[entity_uri],
            'uri': entity_uri
        }

        return result
    else:
        return get_system_interesting_entity()


def get_system_interesting_entity():
    while True:

        idx = int(abs(np.random.randn(1)) * 1000)
        page_name = sorted_pageview_list[idx][0]
        view = sorted_pageview_list[idx][1]
        print(page_name)
        print(view)
        if ':' in page_name:
            continue
        elif '-' == page_name:
            continue
        elif '위키' in page_name:
            continue

        entity_uri = 'http://kbox.kaist.ac.kr/resource/' + page_name
        text = entity_uri.split('/')[-1]
        type_list = get_entity_type_from_knowledge_base(entity_uri)
        if type_list is False:
            continue
        else:
            result = {
                'text': text,
                'type': type_list,
                'uri': entity_uri
            }
            return result


def is_same_type(entity_type=None, property_range=None):
    range_type_list = []
    if entity_type is None or property_range is None:
        print('entity_type: ', entity_type)
        print('property_range: ', property_range)
        return False

    if len(property_range) == 0:
        return True

    for range in property_range:
        range_list = []
        temp = range.split('/')[-1]
        while True:
            range_list.append(temp)
            if temp not in class_parent_dict:
                break
            temp = class_parent_dict[temp]

        if entity_type in range_list:
            return True
    return False


def is_correct_range(entity_types=None, property_range=None):
    print('entity_types: ', entity_types)
    print('property_range: ', property_range)
    if entity_types is None or property_range is None:
        return False

    if len(property_range) == 0:
        return True

    if entity_types is False:
        return True

    for entity_type in entity_types:
        if is_same_type(entity_type=entity_type.split('/')[-1], property_range=property_range) is True:
            return True
    return False


def type_summarization(linked_entity, highest_entity_type, user_name=None):
    print('type: ',highest_entity_type)
    if highest_entity_type not in type_predicate_dict:
        return []
    predicate_dict = type_predicate_dict[highest_entity_type]
    important_property_list = []
    for key, item in predicate_dict.items():
        important_property_list.append('http://dbpedia.org/ontology/' + key)

    triple_list = []

    for property in important_property_list:

        if user_name:
            query = 'select ?p ?o where { graph <http://kbox.kaist.ac.kr/username/' + user_name + '> {{ <' + linked_entity + '> <' + property + '> ?o }UNION{ <' + linked_entity.replace(
                'http://kbox.kaist.ac.kr', 'http://ko.dbpedia.org') + '> <' + property + '> ?o}} }'
            userdb_result = db_linker.QueryToUserKB(query)
            if len(userdb_result['results']['bindings']) == 0:
                pass
            else:
                count = 0
                for t in userdb_result['results']['bindings']:
                    if 'http' in t['o']['value']:
                        obj = '<' + t['o']['value'] + '>'
                    else:
                        obj = "'" + t['o']['value'] + "'"
                    triple = '<' + linked_entity + '>\t<' + property + '>\t' + obj
                    triple_list.append(triple)
                    if count == 2:
                        break

        query = 'select ?p ?o where {{ <' + linked_entity + '> <' + property + '> ?o }UNION{ <' + linked_entity.replace(
            'http://kbox.kaist.ac.kr', 'http://ko.dbpedia.org') + '> <' + property + '> ?o}}'
        masterdb_result = db_linker.QueryToMasterKB(query)
        for t in masterdb_result['results']['bindings']:
            if 'http' in t['o']['value']:
                obj = '<' + t['o']['value'] + '>'
            else:
                obj = "'" + t['o']['value'] + "'"
            triple = '<' + linked_entity + '>\t<' + property + '>\t' + obj
            triple_list.append(triple)
        if len(triple_list) > 5:
            break
    return triple_list


def set_year(number_str):
    y = int(number_str)
    if y < 30:
        year = '20' + number_str
    else:
        year = '19' + number_str

    return year


def set_month(number_str):
    if int(number_str) < 1 or int(number_str) > 12:
        return False

    if len(number_str) == 1:
        month = '0' + number_str
    else:
        month = number_str
    return month


def set_day(number_str):
    if int(number_str) < 1 or int(number_str) > 31:
        return False

    if len(number_str) == 1:
        day = '0' + number_str
    else:
        day = number_str
    return day


def extract_date_from_utterance(utterance):
    number_sequence_length = 0
    number_str_list = []
    number_str = ''
    year = False
    month = False
    day = False

    for i in range(len(utterance) + 1):
        if i == len(utterance):
            c = '끝'
        else:
            c = utterance[i]
        if '0' <= c <= '9':
            number_sequence_length += 1
            number_str += c
        else:
            if number_sequence_length == 8:
                year = number_str[:4]
                month = set_month(number_str[4:6])
                day = set_day(number_str[6:8])

            elif number_sequence_length == 6:
                year = set_year(number_str[:2])
                month = set_month(number_str[2:4])
                day = set_day(number_str[4:6])

            elif number_sequence_length == 4:

                if i != len(utterance) and utterance[i] == '년':
                    year = number_str

                if year == False:
                    year = number_str

            elif number_sequence_length == 2 or number_sequence_length == 1:
                if i != len(utterance) and utterance[i] == '년':
                    year = set_year(number_str)
                elif i != len(utterance) and utterance[i] == '월':
                    month = set_month(number_str)
                elif i != len(utterance) and utterance[i] == '일':
                    day = set_day(number_str)
                else:
                    number_str_list.append(number_str)

            number_str = ''
            number_sequence_length = 0

    for number_str in number_str_list:
        if year == False and len(number_str) == 2:
            year = set_year(number_str)
            continue

        if month == False and (len(number_str) == 2 or len(number_str) == 1):
            month = set_month(number_str)
            continue

        if day == False and (len(number_str) == 2 or len(number_str) == 1):
            day = set_day(number_str)

    if year != False and month != False and day != False:
        return year + '-' + month + '-' + day
    return False


def extract_float_value_from_sentence(utterance):
    number_sequence_length = 0
    number_str_list = []
    number_str = ''

    for i in range(len(utterance)):
        c = utterance[i]
        if '0' <= c <= '9':
            number_sequence_length += 1
            number_str += c
        elif number_sequence_length > 0 and (c in ['.', 'E', 'e', '^']):
            number_sequence_length += 1
            number_str += c
        else:
            if number_sequence_length > 0:
                number_str_list.append(number_str)
                number_str = ''
            number_sequence_length = 0

    if number_sequence_length > 0:
        number_str_list.append(number_str)
        number_str = ''
        number_sequence_length = 0

    if len(number_str_list) == 0:
        return False

    return number_str_list[0]


def extract_year_value_from_sentence(utterance):
    number_sequence_length = 0
    number_str_list = []
    number_str = ''
    year = False

    for i in range(len(utterance) + 1):
        if i == len(utterance):
            c = '끝'
        else:
            c = utterance[i]
        if '0' <= c <= '9':
            number_sequence_length += 1
            number_str += c
        else:
            if number_sequence_length == 8:
                year = number_str[:4]

            elif number_sequence_length == 6:
                year = set_year(number_str[:2])

            elif number_sequence_length == 4:

                if i != len(utterance) and utterance[i] == '년':
                    year = number_str

                if year == False:
                    year = number_str


            elif number_sequence_length == 2 or number_sequence_length == 1:
                if i != len(utterance) and utterance[i] == '년':
                    year = set_year(number_str)
                else:
                    number_str_list.append(number_str)

            number_str = ''
            number_sequence_length = 0

    for number_str in number_str_list:
        if year == False and len(number_str) == 2:
            year = set_year(number_str)

    if year != False:
        return year
    return False


def extract_uri_value_from_sentence(utterance):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, utterance)

    if len(url) > 0:
        return url[0][0]
    else:
        return False


def get_module_type():

    module_count_dict = {}

    sql = "select count(*) from UTTERANCE where intent_emp='A' and speaker='user'"
    result = db_linker.query(sql)
    module_count_dict['A'] = result[0]['count(*)']

    sql = "select count(*) from UTTERANCE where intent_emp='B' and speaker='user'"
    result = db_linker.query(sql)
    module_count_dict['B'] = result[0]['count(*)']

    sql = "select count(*) from UTTERANCE where intent_emp='C' and speaker='user'"
    result = db_linker.query(sql)
    module_count_dict['C'] = result[0]['count(*)']

    sql = "select count(*) from UTTERANCE where intent_emp='D' and speaker='user'"
    result = db_linker.query(sql)
    module_count_dict['D'] = result[0]['count(*)']

    sql = "select count(*) from UTTERANCE where intent_emp='E' and speaker='user'"
    result = db_linker.query(sql)
    module_count_dict['E'] = result[0]['count(*)']

    selected_module = 'A'

    print(module_count_dict)

    for m in module_count_dict.keys():
        if module_count_dict[selected_module] > module_count_dict[m]:
            selected_module = m

    return selected_module


def is_asked_knowledge(user_id, subject, property):

    inner_sql = "select intent_emp from USERKB_LOG l, UTTERANCE u, SESSION s where s.user_id={} and s.session_id=u.session_id and l.utterance_id=u.utterance_id and l.subject='{}' and l.property='{}' and l.object='FAIL' ".format(user_id, subject, property)

    result = db_linker.query(inner_sql)

    print(result)
    if len(result) > 0:
        return result
    else:
        return False

user_dialog_act_dict = {}


def get_entity_information(linked_entity, highest_entity_type, user_name=None, user_id=None):
    print('type: ', highest_entity_type)
    if highest_entity_type not in type_predicate_dict:
        return []
    predicate_dict = type_predicate_dict[highest_entity_type]
    important_property_list = []
    for key, item in predicate_dict.items():
        important_property_list.append('http://dbpedia.org/ontology/' + key)

    triple_list = []

    for property in important_property_list:

        if user_name:
            query = 'select ?p ?o where { graph <http://kbox.kaist.ac.kr/username/' + user_name + '> {{ <' + linked_entity + '> <' + property + '> ?o }UNION{ <' + linked_entity.replace(
                'http://kbox.kaist.ac.kr', 'http://ko.dbpedia.org') + '> <' + property + '> ?o}} }'
            userdb_result = db_linker.QueryToUserKB(query)
            if len(userdb_result['results']['bindings']) == 0:
                pass
            else:
                obj = []
                for t in userdb_result['results']['bindings']:
                    obj.append(t['o']['value'])
                triple = [linked_entity, property, ', '.join(obj), 'user_db']
                triple_list.append(triple)
                continue

        query = 'select ?p ?o where {{ <' + linked_entity + '> <' + property + '> ?o }UNION{ <' + linked_entity.replace(
            'http://kbox.kaist.ac.kr', 'http://ko.dbpedia.org') + '> <' + property + '> ?o}}'
        masterdb_result = db_linker.QueryToMasterKB(query)
        if len(masterdb_result['results']['bindings']) == 0:
            if is_asked_knowledge(user_id, linked_entity, property) is False:
                triple = [linked_entity, property, None, 'main_db']
            else:
                triple = [linked_entity, property, "non-response", 'user_db']
            triple_list.append(triple)

        else:
            obj = []
            for t in masterdb_result['results']['bindings']:
                obj.append(t['o']['value'])
            triple = [linked_entity, property, ', '.join(obj), 'main_db']
            triple_list.append(triple)

        if len(triple_list) > 10:
            break
    return triple_list



def knowledge_conversation(user_id=None, user_utterance=None):
    if user_id not in user_dialog_act_dict:
        user_dialog_act_dict[user_id] = {
            'last_dialog_act': None,
            'last_question': None,
            'last_module_type': None
        }
    user_info = db_linker.GetUserInfo(user_id=user_id)
    user_name = user_info['user_name']
    dialog_act = None
    answer = ''
    is_get_knowledge=False

    if user_utterance is not None:

        entity_list = []
        print('entity linking')
        entities = sentence_parser.Entity_Linking(user_utterance)
        print('entity_linking complete')
        now_user_utterance_info = db_linker.getLatestUtterance(user_id=user_id, speaker='user')
        if len(entities) > 0:
            db_linker.save_entity_info(entities, now_user_utterance_info['utterance_id'])
        value = False
        print("entities: ", entities)

        last_system_utterance_info = db_linker.getLatestUtterance(user_id=user_id, speaker='system')
        now_user_utterance_info = db_linker.getLatestUtterance(user_id=user_id, speaker='user')
        last_user_utterance_info = db_linker.getLatestUtterance(user_id=user_id, speaker='last_user')

        if now_user_utterance_info['session_id'] == last_system_utterance_info['session_id']:
            # 이전 대답이 답변에 대한 응답인 경우
            if last_system_utterance_info['intent_req'] == 'entity_question' or user_dialog_act_dict[user_id]['last_dialog_act'] == 'entity_question':
                entity_uri = user_dialog_act_dict[user_id]['last_sub_entity']
                highest_entity_type = user_dialog_act_dict[user_id]['last_sub_entity_type']
                print('response')
                user_dialog_act_dict[user_id]['last_dialog_act'] = 'Knowledge_inform'
                db_linker.update_utterance_intent_emp(utterance_id=now_user_utterance_info['utterance_id'],
                                                      intent_emp=user_dialog_act_dict[user_id]['last_module_type'])
                # entities = sentence_parser.Entity_Linking(user_utterance)
                answer = ''
                if last_system_utterance_info['intent_req'] != 'entity_question':
                    question_info = {
                        'subject': user_dialog_act_dict[user_id]['last_question'][0],
                        'property': user_dialog_act_dict[user_id]['last_question'][1],
                        'object': user_dialog_act_dict[user_id]['last_question'][2]
                    }
                else:
                    question_info = db_linker.getTripleQuestion(last_user_utterance_info['utterance_id'])
                    if len(question_info) == 0:
                        return '질문이 뭐였는지 못찾았어요, 어떤 주제를 좋아하시나요?.', 'entity_answer', {
                    'question_info': question_info,
                    'property_type': None,
                    'property_range': None,
                    'entities': ", ".join(entity_list),
                    'user_answer': None,
                }
                print(question_info)
                property_type = type_of_property_dict[question_info['property']]['type']
                property_range = type_of_property_dict[question_info['property']]['range']
                if "http://www.w3.org/2002/07/owl#ObjectProperty" in property_type:
                    relation_type = "http://www.w3.org/2002/07/owl#ObjectProperty"
                    user_answer = False
                    # objectProperty 일 경우
                    if len(entities) > 0:
                        for t in entities:
                            # entity = entities[-1]['uri']
                            entity = t['uri']
                            entity_list.append(entity)
                            entity_types = get_entity_type_from_knowledge_base(t['uri'])
                            if entity_types is False or len(entity_types) == 0:
                                if t['ne_type'] in ne_tag_info_dict:
                                    entity_types = ne_tag_info_dict[t['ne_type']]

                            print('entity: {}, question["subject"]: {}'.format(entity, question_info['subject']))
                            if entity == question_info['subject']:
                                print('same')
                                continue

                            if not is_correct_range(entity_types=entity_types, property_range=property_range):
                                continue

                            triple = [question_info['subject'], question_info['property'], entity]
                            print('tttttttttttttttttttttttttttt1: ', triple)
                            user_answer = entity
                            save_knowledge_to_database(triple, now_user_utterance_info['utterance_id'])
                            print('tttttttttttttttttttttttttttt2: ', triple)
                            db_linker.InsertKnowledgeToUserKB(user_name, [triple])
                            answer += nlg_with_triple([triple], 'Knowledge_inform', None)
                            is_get_knowledge = True
                            break

                    if user_answer is False:
                        triple = [question_info['subject'], question_info['property'], 'FAIL']
                        save_knowledge_to_database(triple, now_user_utterance_info['utterance_id'])
                        answer = '무슨말씀이신지 잘 모르겠어요. 넘어갈게요!\n'

                elif "http://www.w3.org/2002/07/owl#DatatypeProperty" in property_type:
                    # datatypeProperty일 경우
                    relation_type = "http://www.w3.org/2002/07/owl#DatatypeProperty"
                    print('datatype')
                    print('property_type: ', property_type)
                    print('property_range: ', property_range)
                    property_range = property_range[0]

                    if property_range == 'http://www.w3.org/2001/XMLSchema#double':
                        float_value = extract_float_value_from_sentence(user_utterance)
                        if float_value is not False:
                            value = '"' + float_value + '"^^<http://www.w3.org/2001/XMLSchema#double>'
                    elif property_range == 'http://www.w3.org/2001/XMLSchema#float':
                        float_value = extract_float_value_from_sentence(user_utterance)
                        if float_value is not False:
                            value = '"' + float_value + '"^^<http://www.w3.org/2001/XMLSchema#float>'
                    elif property_range == 'http://dbpedia.org/datatype/valvetrain':  # triple 없음
                        value = False
                    elif property_range == 'http://www.w3.org/2001/XMLSchema#anyURI':
                        uri_value = extract_uri_value_from_sentence(user_utterance)
                        if uri_value is not False:
                            value = '"' + uri_value + '"^^<http://www.w3.org/2001/XMLSchema#anyURI>'
                    elif property_range == 'http://www.w3.org/2001/XMLSchema#boolean':  # triple 없음
                        value = False
                    elif property_range == 'http://www.w3.org/2001/XMLSchema#nonNegativeInteger':
                        nni = extract_float_value_from_sentence(user_utterance)
                        if nni is not False:
                            if nni >= 0:
                                value = '"' + str(int(nni)) + '"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>'
                    elif property_range == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#langString':  # string인데, 다른나라 언어 포함
                        value = '"' + user_utterance + '"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#langString>'
                    elif property_range == 'http://dbpedia.org/datatype/fuelType':  # triple 없음
                        value = False
                    elif property_range == 'http://www.w3.org/2001/XMLSchema#gYear':  # 연도만 1994
                        year = extract_year_value_from_sentence(user_utterance)
                        if year is not False:
                            value = '"' + year + '"^^<http://www.w3.org/2001/XMLSchema#gYear>'
                    elif property_range == 'http://www.w3.org/2001/XMLSchema#date':  # 날짜까지, 1994-04-28
                        date = extract_date_from_utterance(user_utterance)
                        if date is not False:
                            value = '"' + date + '"^^<http://www.w3.org/2001/XMLSchema#date>'
                    elif property_range == 'http://www.w3.org/2001/XMLSchema#gYearMonth':  # triple 없음
                        value = False
                    elif property_range == 'http://www.w3.org/2001/XMLSchema#dateTime':  # triple 없음
                        value = False
                    elif property_range == 'http://www.w3.org/2001/XMLSchema#integer':
                        float_value = extract_float_value_from_sentence(user_utterance)
                        if float_value is not False:
                            value = '"' + str(int(float_value)) + '"^^<http://www.w3.org/2001/XMLSchema#integer>'
                    elif property_range == 'http://www.w3.org/2001/XMLSchema#positiveInteger':
                        pi = extract_float_value_from_sentence(user_utterance)
                        if pi is not False:
                            if pi > 0:
                                value = '"' + str(int(pi)) + '"^^<http://www.w3.org/2001/XMLSchema#positiveInteger>'
                    elif property_range == 'http://dbpedia.org/datatype/engineConfiguration':  # triple 없음
                        value = False
                    elif property_range == 'http://www.w3.org/2001/XMLSchema#string':  # 보통 숫자, 단위가 포함돼있는 경우가 많음
                        print('string')
                        value = '"' + user_utterance + '"'
                        print(value)

                    if value is not False:
                        triple = [question_info['subject'], question_info['property'], value]
                        save_knowledge_to_database(triple, now_user_utterance_info['utterance_id'])
                        print('tttttttttttttttttttttttttttt: ', triple)
                        triple[0] = '<' + triple[0] + '>'
                        triple[1] = '<' + triple[1] + '>'

                        db_linker.InsertKnowledgeToUserKBTTL(user_name, [triple])
                        answer += nlg_with_triple([triple], 'Knowledge_inform', None)
                        is_get_knowledge=True
                    else:
                        triple = [question_info['subject'], question_info['property'], 'FAIL']
                        save_knowledge_to_database(triple, now_user_utterance_info['utterance_id'])
                        answer = '무슨말씀이신지 잘 모르겠어요. 넘어갈게요!\n'

                    property_range = [property_range]
                    user_answer = value
                dialog_act = 'entity_answer'
                # answer += '또 무엇에 대해 잘 아시나요?'
                # if len(self.entity_question_triple_list) > 0:
                # 	self.question_triple = self.entity_question_triple_list.pop(0)
                # 	answer = answer + self.triple_question_generation(self.question_triple)
                #
                system_statement = {
                    'question_info': question_info,
                    'property_type': relation_type,
                    'property_range': ", ".join(property_range),
                    'entities': ", ".join(entity_list),
                    'user_answer': user_answer,
                    'knowledge_triples': get_entity_information(entity_uri, highest_entity_type,
                                                                     user_name=user_name, user_id=user_id)
                }


                # return answer, dialog_act, system_statement

    # test
    # selected_module = get_module_type()

    interested_entity = None

    # 사용자 맞춤이 아닌, 중요 Entity를 System이 선정하는 경우
    if user_utterance is None:
        selected_module = 'D'
        interested_entity = get_system_interesting_entity()

    else:
        if len(entities) > 0 and is_get_knowledge is False:
            # Entity가 잡힌 경우
            # 현재의 대화에서 entity 선정
            answer = ""
            for entity in entities:
                print(entity['uri'].split('/')[-1])
                if entity['uri'].split('/')[-1][0] != '_':
                    interested_entity = entity

        elif entity_uri is not None:
            interested_entity={}
            interested_entity['uri'] = entity_uri
            interested_entity['type'] = ["http://dbpedia.org/ontology/"+highest_entity_type]
            print('saved_last_highest_entity_type: ', highest_entity_type)
            interested_entity['text'] = entity_uri.split('/')[-1].replace('_', ' ')
            interested_entity['ne_type'] = user_dialog_act_dict[user_id]['last_sub_entity_ne_type']
        print(interested_entity)

        # running
        selected_module = 'E'

        if selected_module == 'E':
            if interested_entity is None:
                # 과거 대화에서 Entity 선정
                interested_entity = get_user_interesting_entity(user_id=user_id)
        else:
            if interested_entity is None:
                interested_entity = get_system_interesting_entity()


    while True:

        print(interested_entity['text'])
        entity_uri = interested_entity['uri']
        linked_entity = entity_uri.split('/')[-1]

        # entity_type = get_entity_type(entities[0])
        highest_entity_type = get_highest_level_type(interested_entity['type'])

        if highest_entity_type is False:
            if interested_entity['ne_type'] in ne_tag_info_dict:
                highest_entity_type = ne_tag_info_dict[interested_entity['ne_type']]
                if len(highest_entity_type['mapped_dbo']) == 0:
                    return interested_entity['text'] + '말고 다른건 어때요?', None, None
                else:
                    highest_entity_type = highest_entity_type['mapped_dbo'][0]

            else:
                return interested_entity['text'] + '말고 다른건 어때요?', None, None
        print('entities[0]: ', interested_entity)
        print('highest_entity_type: ', highest_entity_type)


        ##entity type이 잡혀서 질문 목록 생성
        if highest_entity_type is not None:
            entity_question_triple_list, module_type = get_entity_question_list(user_id, user_name, interested_entity,
                                                                                highest_entity_type)
        if len(entity_question_triple_list) > 0:
            break
        else:
            interested_entity = get_system_interesting_entity()
            module_type = 'A'

    if module_type == 'A':
        t = random.random()
        if t > 0.5:
            selected_module = 'B'
        else:
            selected_module = 'C'
    elif module_type in ['B', 'C']:
        selected_module = 'D'


    # Entity summarization을 통해 정보 제공
    try:

        if highest_entity_type in type_predicate_dict:
            summarized_triples = type_summarization(entity_uri, highest_entity_type, user_name=user_name)
        else:
            summarized_triples = entity_summarization.ES(linked_entity)
    except:
        summarized_triples = []
    print("summarized_triples: ", summarized_triples)
    # if selected_module in ['B', 'D', 'E']:
    #     answer += nlg_with_triple(summarized_triples, 'Knowledge_inform', highest_entity_type)


    print("entity_question_triple_list: ", entity_question_triple_list)
    question_triple = None
    ## 질문 목록에 대해 질문 시작
    if len(entity_question_triple_list) > 0:
        answer = answer + interested_entity['text'] + '에 대해서 물어보고 싶은게 있어요.\n'

        question_triple = entity_question_triple_list.pop(0)

        if selected_module in ['C', 'D', 'E']:
            inform_sentence, temp_triple = inform_question_related(highest_entity_type, question_triple[1])
            answer = answer + inform_sentence
            summarized_triples.append(temp_triple)
        print(question_triple)
        save_knowledge_to_database(question_triple, now_user_utterance_info['utterance_id'])
        answer = answer + triple_question_generation(question_triple, highest_entity_type)
        dialog_act = 'entity_question'
        user_dialog_act_dict[user_id]['last_dialog_act'] = 'entity_question'
        user_dialog_act_dict[user_id]['last_question'] = question_triple
        user_dialog_act_dict[user_id]['last_module_type'] = selected_module
        user_dialog_act_dict[user_id]['last_sub_entity'] = entity_uri
        user_dialog_act_dict[user_id]['last_sub_entity_type'] = highest_entity_type
        print('save_last_highest_entity_type: ', highest_entity_type)
        user_dialog_act_dict[user_id]['last_sub_entity_ne_type'] = interested_entity['ne_type']

    system_statement = {
        'entities': entities,
        'inform_knowledge': summarized_triples,
        'interesting_entity': interested_entity,
        'interesting_entity_type': highest_entity_type,
        'question_triple': question_triple,
        'selected_module': selected_module,
        'knowledge_triples': get_entity_information(entity_uri, highest_entity_type, user_name=user_name, user_id=user_id)
    }

    return answer, dialog_act, system_statement


if __name__ == "__main__":
    question = '김연아는 정말 대단해'
    user = 43
    print('t')
    # (knowledge_conversation(user_utterance=None, user_id=user))
    #print(type_summarization('http://kbox.kaist.ac.kr/resource/김연아', 'FigureSkater', user_name='ybjeong'))
    # print(get_user_interesting_entity(user_id=43))
    # print(get_entity_type_from_knowledge_base('http://kbox.kaist.ac.kr/resource/김연아'))
    # print(get_system_interesting_entity())
    # print(get_system_interesting_entity())
    # print(get_system_interesting_entity())
    # print(get_system_interesting_entity())
    # print(get_system_interesting_entity())
    is_asked_knowledge(43, 'http://kbox.kaist.ac.kr/resource/호나우두', 'http://dbpedia.org/ontology/youthClub')
