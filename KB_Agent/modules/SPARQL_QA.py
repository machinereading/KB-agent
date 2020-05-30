import json
import tensorflow_hub as hub
import tensorflow as tf
import requests
import sys
import numpy as np
import constant
KB_AGENT_PATH = constant.KB_AGENT_PATH

sys.path.append(KB_AGENT_PATH+'DB_linker/')
import DB_Linker as db_linker


def jsonload(fname, encoding="utf-8"):
    with open(fname, encoding=encoding) as f:
        j = json.load(f)

    return j


embed = hub.load(KB_AGENT_PATH+"KB_Agent/modules/tf_models/063d866c06683311b44b4992fd46003be952409c")
# session = tf.Session()
# session.run([tf.global_variables_initializer(), tf.tables_initializer()])

template_dict_path = KB_AGENT_PATH+'KB_Agent/data/template_dict.jsonv2'
template_dict = jsonload(template_dict_path)


def sentence_to_template(sentence):
    targetURL = "http://aiopen.etri.re.kr:8000/WiseQAnal"
    accessKey = "abfa1639-8789-43e0-b1da-c29e46b431db"

    requestJson = {
        "access_key": accessKey,
        "argument": {
            "text": sentence
        }
    }
    replaced_word_dict = {}
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    response = requests.post(targetURL, data=json.dumps(requestJson), headers=headers)
    result_json = response.json()

    for named_entity in result_json['return_object']['orgQInfo']['orgQUnit']['ndoc']['sentence'][0]['NE']:
        temp = 'VAL_<' + named_entity['type'] + '>'
        sentence = sentence.replace(named_entity['text'], temp)
        replaced_word_dict[temp] = named_entity['text']
        if result_json['return_object']['orgQInfo']['orgQUnit']['vLATs']:
            temp = 'ANS_<' + result_json['return_object']['orgQInfo']['orgQUnit']['vSATs'][0]['strSAT'] + '>'
            sentence = sentence.replace(result_json['return_object']['orgQInfo']['orgQUnit']['vLATs'][0]['strLAT'],
                                        'ANS_<' + result_json['return_object']['orgQInfo']['orgQUnit']['vSATs'][0][
                                            'strSAT'] + '>')
            replaced_word_dict[temp] = result_json['return_object']['orgQInfo']['orgQUnit']['vLATs'][0]['strLAT']

    return sentence, replaced_word_dict


def get_highest_similar_sparql(sentence_template):
    # embedding = session.run(embed([sentence_template]))
    embedding = embed([sentence_template])
    print(sentence_template)
    top_score = 0
    sparql_query = None
    for template in template_dict:
        score = np.inner(embedding[0], np.array(template['template_use_embedding']))
        if score > top_score:
            sparql_query = template['template_sparql']
            top_score = score

    return top_score, sparql_query


def get_complete_sparql(replaced_word_dict, templated_sparql_query):
    for template, word in replaced_word_dict.items():
        if template.split('_')[0] == 'VAL':
            sep = 'resource'
        elif template.split('_')[0] == 'ANS':
            sep = 'property'
        else:
            sep = 'ontology'
        uri = '<http://ko.dbpedia.org/' + sep + '/' + word.replace(' ', '_') + '>'

        templated_sparql_query = templated_sparql_query.replace(template, uri)

    print(templated_sparql_query)
    return templated_sparql_query


def sparql_conversation(sentence):
    sentence_template, replaced_word_dict = sentence_to_template(sentence)
    top_score, sparql_query = get_highest_similar_sparql(sentence_template)
    print(top_score)
    if top_score > 0.9:
        sparql_query = get_complete_sparql(replaced_word_dict, sparql_query)
        masterdb_result = db_linker.QueryToMasterKB(sparql_query)
        print(masterdb_result)
        if 'results' in masterdb_result:
            if len(masterdb_result['results']['bindings']) == 0:
                return '잘 모르겠어요'
            answer = json.dumps(masterdb_result['results']['bindings'], indent=4)
            return answer
        elif 'boolean' in masterdb_result:
            if masterdb_result['boolean'] == True:
                return '네 맞아요'
            else:
                return '아닌것 같아요'
        else:
            return '질문이 어려워요'
    return None

def jsondump(j, fname):
    with open(fname, "w", encoding="UTF8") as f:
        json.dump(j, f, ensure_ascii=False, indent="\t")


def update_template_dict():
    for template in template_dict:
        embedding = embed([template['template']])
        template['template_use_embedding'] = embedding[0].numpy().tolist()
    print(template_dict[0])
    jsondump(template_dict, template_dict_path+'v2')


if __name__ == "__main__":
    question = '나탈리 포트만은 미국에서 태어났습니까?'
    print(sparql_conversation(question))
