import json
import requests
import sys
import modules_constant
import sentence_parser
import trained_sparql_qa

KB_AGENT_PATH = modules_constant.KB_AGENT_PATH

sys.path.append(KB_AGENT_PATH + 'DB_linker/')

import DB_Linker as db_linker


def jsonload(fname, encoding="utf-8"):
    with open(fname, encoding=encoding) as f:
        j = json.load(f)

    return j


ne_kb_type_path = KB_AGENT_PATH + 'KB_Agent/data/ne_tag_info.json'
ne_kb_type_dic = jsonload(ne_kb_type_path)


def get_etri_answer(sentence):
    targetURL = "http://aiopen.etri.re.kr:8000/WiseQAnal"
    accessKey = "abfa1639-8789-43e0-b1da-c29e46b431db"

    requestJson = {
        "access_key": accessKey,
        "argument": {
            "text": sentence
        }
    }
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    response = requests.post(targetURL, data=json.dumps(requestJson), headers=headers)
    result_json = response.json()
    return result_json


def get_temp_obj(sub, answer_types):
    query = '''SELECT ?o WHERE'''
    query_list = []

    for answer_type in answer_types:
        temp_query = '''
{
  <http://ko.dbpedia.org/resource/''' + sub.replace(' ', '_') + '''> ?p ?o .
  ?o rdf:type :''' + answer_type + ''' FILTER(REGEX(STR(?o),"http://ko.dbpedia.org/resource/")) .
}
    '''
        query_list.append(temp_query)

    query = query + '{' + 'UNION'.join(query_list) + '}'
    print('temp_query: ', query)
    result = db_linker.QueryToMasterKB(query)

    return result


def re_query_generate(sub, relation, answer_types):
    query = '''SELECT ?o WHERE'''
    query_list = []
    for answer_type in answer_types:
        temp_query = '''
{
  <http://ko.dbpedia.org/resource/''' + sub.replace(' ', '_') + '''> <http://dbpedia.org/ontology/''' + relation + '''> ?o .
  ?o rdf:type :''' + answer_type + ''' .
}
    '''
        query_list.append(temp_query)

    query = query + '{' + 'UNION'.join(query_list) + '}'

    return query


def re_qa(sentence, user_name):
    etri_result = get_etri_answer(sentence)
    max = 0
    for vSATs in etri_result['return_object']['orgQInfo']['orgQUnit']['vSATs']:
        if vSATs['dConfidenceSAT'] > max:
            max = vSATs['dConfidenceSAT']
            answer_etri_type = vSATs['strSAT']

    if answer_etri_type not in ne_kb_type_dic:
        # return 'answer type error', None, None
        return False, None, None

    if len(ne_kb_type_dic[answer_etri_type]['mapped_dbo']) == 1:
        answer_kb_type = [ne_kb_type_dic[answer_etri_type]['mapped_dbo'][0]]
    else:
        answer_kb_type = ne_kb_type_dic[answer_etri_type]['mapped_dbo']

    entities = sentence_parser.Entity_Linking(sentence)

    vQTopicList = set()
    for vQTopic in etri_result['return_object']['orgQInfo']['orgQUnit']['vQTopic']:
        vQTopicList.add(vQTopic['strEntity'])

    print('vTitleList: ', vQTopicList)
    print('entities: ', entities)
    sub_Entity = None
    # for entity in entities:
    #     text = entity['text']
    #     if text in vQTopicList:
    #         sub_Entity = text
    if len(entities) == 0:
        # return 'Entity not found error', None, None
        return False, None, None
    sub_Entity = entities[0]['text']

    print('sub_entity: ', sub_Entity)
    if sub_Entity is None:
        return False, None, None
        # return 'Entity not found error', None, None

    temp_obj = get_temp_obj(sub_Entity, answer_kb_type)
    print(temp_obj)
    if len(temp_obj['results']['bindings']) < 1:
        # return 'answer type error', sub_Entity, None
        return False, sub_Entity, None
    if 'o' not in temp_obj['results']['bindings'][0]:
        # return 'answer type error', sub_Entity, None
        return False, sub_Entity, None
    temp_obj = temp_obj['results']['bindings'][0]['o']['value'].split('/')[-1]

    print('temp_obj: ', temp_obj)

    question_part = 'nevernevernevernever'
    if len(etri_result['return_object']['orgQInfo']['orgQUnit']['vQFs']) > 0:
        if 'strQF' in etri_result['return_object']['orgQInfo']['orgQUnit']['vQFs'][0]:
            question_part = etri_result['return_object']['orgQInfo']['orgQUnit']['vQFs'][0]['strQF']

    if question_part in sentence:
        temp_sentence = sentence.replace(sub_Entity, ' [' + sub_Entity + '] ').replace('?', '.').replace(question_part,
                                                                                                         ' [' + temp_obj + '] ')
    else:
        temp_sentence = sentence.replace(sub_Entity, ' [' + sub_Entity + '] ').replace('?',
                                                                                       ',') + ' [' + temp_obj + '] 인가요.'

    print('temp_sentence: ', temp_sentence)
    re_result = sentence_parser.relation_extraction(temp_sentence)
    print(re_result)
    if len(re_result['result']) == 0:
        return False, None, None
        # return 'Entity not found error', None, None
    triples = re_result['result'].split('\n')
    for triple in triples:
        splited_triple = triple.split('\t')
        if splited_triple[0] == sub_Entity and splited_triple[2] == temp_obj:
            sub = splited_triple[0]
            relation = splited_triple[1]
            obj = splited_triple[2]
            break

    re_query = re_query_generate(sub, relation, answer_kb_type)

    print(re_query)
    query_result = db_linker.QueryToMasterKB(re_query)
    user_query_result = db_linker.QueryToUserKB(re_query, user_name)
    result_list = []
    is_mydb_found = True
    is_userkb_found = True
    if len(query_result['results']['bindings']) == 0:
        is_mydb_found = False
        # return False, sub_Entity, relation
        # return 'answer type or re error', sub_Entity, relation
    else:
        for temp in query_result['results']['bindings']:
            result_list.append(temp['o']['value'].split('/')[-1])

    if len(user_query_result['results']['bindings']) == 0:
        is_userkb_found = False
    else:
        for temp in user_query_result['results']['bindings']:
            result_list.append(temp['o']['value'].split('/')[-1])

    if is_mydb_found is False and is_userkb_found is False:
        return False, sub_Entity, relation

    return result_list, sub_Entity, relation


def trained_qa(sentence, user_name, user_id=None):
    print('trained_qa')
    print(sentence)
    relation, score = trained_sparql_qa.property_prediction_from_sentence(sentence)
    entities = sentence_parser.Entity_Linking(sentence)

    if len(entities) == 0:
        return False, None, 0, relation, score, None

    now_user_utterance_info = db_linker.getLatestUtterance(user_id=user_id, speaker='user')
    if len(entities) > 0:
        db_linker.save_entity_info(entities, now_user_utterance_info['utterance_id'])


    # sub_Entity = entities[0]['text']
    #
    # if str(type(relation)) == "<class 'str'>":
    #
    #     query = '''SELECT distinct ?o WHERE{
    #       <http://ko.dbpedia.org/resource/''' + sub_Entity.replace(' ', '_') + '''> <''' + relation + '''> ?o .
    #     }
    #             '''
    # elif str(type(relation)) == "<class 'list'>":
    #     query = '''SELECT distinct ?o WHERE{{
    #                   <http://ko.dbpedia.org/resource/''' + sub_Entity.replace(' ', '_') + '''> <''' + relation[0] + '''> ?o .
    #                 } UNION
    #                 {
    #                   <http://ko.dbpedia.org/resource/''' + sub_Entity.replace(' ', '_') + '''> <''' + relation[1] + '''> ?o .
    #                 }}
    #                         '''
    result_list = []

    sub_Entity = entities[0]['text']
    sub_Entity_score = entities[0]['score']
    sub_Entity_confidence = entities[0]['confidence']
    sub_uri = entities[0]['uri']
    # ko.dbpedia uri
    # sub_uri = sub_uri.replace('http://kbox.kaist.ac.kr', 'http://ko.dbpedia.org')

    if str(type(relation)) == "<class 'str'>":

        query = '''SELECT distinct ?o WHERE{
        {
  <''' + sub_uri + '''> <''' + relation + '''> ?o .
  }
  UNION
  {
  <''' + sub_uri + '''> owl:sameAs ?ko .
  ?ko <''' + relation + '''> ?o .
  }
  UNION
  {
  ?ko owl:sameAs <''' + sub_uri + '''> .
  ?ko <''' + relation + '''> ?o .
  }
}
        '''
    elif str(type(relation)) == "<class 'list'>":
        query = '''SELECT distinct ?o WHERE{{
                <''' + sub_uri + '''> <''' + relation[0] + '''> ?o .
            } 
            UNION
            {
                <''' + sub_uri + '''> owl:sameAs ?ko .
                ?ko <''' + relation[0] + '''> ?o .
            }
            UNION
            {
                ?ko owl:sameAs <''' + sub_uri + '''> .
                ?ko <''' + relation[0] + '''> ?o .
            }
            UNION
            {
              <''' + sub_uri + '''> <''' + relation[1] + '''> ?o .
            }
            UNION
            {
                <''' + sub_uri + '''> owl:sameAs ?ko .
                ?ko <''' + relation[1] + '''> ?o .
            }
            UNION
            {
                ?ko owl:sameAs <''' + sub_uri + '''> .
                ?ko <''' + relation[1] + '''> ?o .
            }
            }
                    '''

    print(query)
    query_result = db_linker.QueryToMasterKB(query)

    user_query_result = db_linker.QueryToUserKB(query, user_name)

    if len(query_result['results']['bindings']) > 0:
        for temp in query_result['results']['bindings']:
            result_list.append(temp['o']['value'].split('/')[-1])

    if len(user_query_result['results']['bindings']) > 0:
        for temp in user_query_result['results']['bindings']:
            result_list.append(temp['o']['value'].split('/')[-1])

    # # kbox uri
    # sub_uri = entities[0]['uri']
    # if str(type(relation)) == "<class 'str'>":
    #
    #     query = '''SELECT distinct ?o WHERE{
    #   <''' + sub_uri + '''> <''' + relation + '''> ?o .
    # }
    #         '''
    # elif str(type(relation)) == "<class 'list'>":
    #     query = '''SELECT distinct ?o WHERE{{
    #               <''' + sub_uri + '''> <''' + relation[0] + '''> ?o .
    #             } UNION
    #             {
    #               <''' + sub_uri + '''> <''' + relation[1] + '''> ?o .
    #             }}
    #                     '''
    #
    # print(query)
    # query_result = db_linker.QueryToMasterKB(query)
    #
    # user_query_result = db_linker.QueryToUserKB(query, user_name)
    #
    # if len(query_result['results']['bindings']) > 0:
    #     for temp in query_result['results']['bindings']:
    #         result_list.append(temp['o']['value'].split('/')[-1])
    #
    # if len(user_query_result['results']['bindings']) > 0:
    #     for temp in user_query_result['results']['bindings']:
    #         result_list.append(temp['o']['value'].split('/')[-1])

    return result_list, sub_Entity, sub_Entity_confidence, relation, score, query


def sparql_conversation(user_id=None, sentence=None):
    user_info = db_linker.GetUserInfo(user_id=user_id)
    user_name = user_info['user_name']
    trained_qa_result, entity, entity_score, relation, relation_score, sparql_query = trained_qa(sentence, user_name, user_id=user_id)

    if trained_qa_result is not False:
        query_result = ', '.join(trained_qa_result)
    else:
        query_result = 'fail'
    system_statement = {
        'entity': entity,
        'entity_score': float(entity_score),
        'relation': relation,
        'relation_score': float(relation_score),
        'query_result': query_result,
        'sparql_query': sparql_query
    }

    if trained_qa_result is not False:
        if len(trained_qa_result) > 0:
            return ', '.join(trained_qa_result) + '입니다.', 'sparql_qa', system_statement

    re_qa_result, entity, relation = re_qa(sentence, user_name)

    # if re_qa_result is not False:
    #     query_result = ', '.join(re_qa_result)
    # else:
    #     query_result = 'fail'
    #
    # system_statement = {
    #     'entity': entity,
    #     'relation': relation,
    #     'query_result': query_result
    # }

    if re_qa_result is not False:
        return ', '.join(re_qa_result) + '입니다.', 'sparql_qa', system_statement

    return None, 'sparql_qa', system_statement


def jsondump(j, fname):
    with open(fname, "w", encoding="UTF8") as f:
        json.dump(j, f, ensure_ascii=False, indent="\t")


def score_re_qa():
    test_data_path = '../../SPARQL_QA_MODEL/data/_test_qa.json'
    test_data = jsonload(test_data_path)
    Entity_not_found_error = 0
    answer_type_error = 0
    answer_type_or_re_error = 0
    correct_count = 0
    answered_count = 0

    re_qa_result = []

    for data in test_data:
        sentence = data['question_sentence']
        answer = data['object']
        result, entity, relation = re_qa(sentence)

        temp = {
            'question_sentence': sentence,
            'gold_subject': data['subject'],
            'gold_property': data['property'],
            'gold_answer': data['object'],
            'predicted_property': relation,
            'predicted_entity': entity,
            'sparql_result': result
        }
        re_qa_result.append(temp)
        if result == 'answer type error':
            answer_type_error += 1
            continue
        elif result == 'Entity not found error':
            Entity_not_found_error += 1
            continue
        elif result == 'answer type or re error':
            answer_type_or_re_error += 1
            continue
        else:
            answered_count += 1
            for re in result:
                if re.replace(' ', '_') in answer:
                    correct_count += 1
                    break
    jsondump(re_qa_result, 'result_re_qa.json')
    print('Entity_not_found_error: ', Entity_not_found_error)
    print('answer_type_error: ', answer_type_error)
    print('answer_type_or_re_error: ', answer_type_or_re_error)
    print('correct_count: ', correct_count)
    print('answered_count: ', answered_count)
    print('length: ', len(test_data))


def score_trained_qa():
    test_data_path = '../../SPARQL_QA_MODEL/data/_test_qa.json'
    test_data = jsonload(test_data_path)
    label_to_uri = jsonload('./sparql_qa_model/property_uri.json')
    entity_not_found_count = 0
    correct_answer_count = 0
    correct_property_count = 0

    result_trained_qa = []

    for data in test_data:
        sentence = data['question_sentence']
        result_list, entities, relation = trained_qa(sentence,'ybjeong')
        answer = data['object']
        answer_uri = label_to_uri[data['property']]

        if answer_uri == relation:
            correct_property_count += 1
        if entities is None:
            entity_not_found_count += 1
            continue

        temp = {
            'question_sentence': sentence,
            'gold_subject': data['subject'],
            'gold_property': data['property'],
            'gold_answer': data['object'],
            'predicted_property': relation,
            'predicted_entity': entities,
            'sparql_result': result_list
        }
        result_trained_qa.append(temp)
        print(answer)
        print()
        print(result_list)
        for result in result_list:
            if result.replace(' ', '_') in answer:
                correct_answer_count += 1
                break
    print('entity_not_found_count: ', entity_not_found_count)
    print('correct_answer_count: ', correct_answer_count)
    print('correct_property_count: ', correct_property_count)
    print('length: ', len(test_data))

    jsondump(result_trained_qa, 'result_trained_qa.json')


if __name__ == "__main__":
    question = '어니스트 헤밍웨이는 어떤 작품으로 잘 알려졌나요'
    # print(re_qa(question))
    # print(trained_qa('김연아는 어느나라 사람인가요?'))
    score_trained_qa()
    # score_re_qa()
