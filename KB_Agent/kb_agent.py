import sys
import requests

sys.path.append('../DB_linker/')
sys.path.append('./modules/')
import SPARQL_QA
import frame_QA
import knowledge_question
import DB_Linker as db_linker

fact_checking_QA_url = 'http://143.248.135.194:18978/service'


def user_access(user_name=None, user_id=None):
    result = db_linker.LookUpUsers()

    user_info = None

    for user in result['user_list']:
        if user_name:
            if user['user_name'] == user_name:
                user_info = user

        if user_id:
            if user['user_id'] == user_id:
                user_info = user

    if user_info:
        print(user_info)
    else:
        print('user_not_found')
        user_info = db_linker.AddNewUser(user_name)

    session_info = db_linker.AddNewSession(user_id=user_info['user_id'])

    result = {
        'session_info': session_info,
        'user_info': user_info
    }

    return result

def respond_to_user_utterance(user_id=None, user_name=None, user_utterance=None, session_id=None, modules=[]):
    if user_id is None and user_name is None:
        return False
    user_info = db_linker.GetUserInfo(user_id=user_id, user_name=user_name)

    db_linker.SaveUtterance(user_id=user_info['user_id'], speaker='user', utterance=user_utterance,
                            session_id=session_id)

    # answer, dialog_act, system_statement = kb_agent(user_id=user_info['user_id'], user_utterance=user_utterance,
    #                                                 modules=modules)

    try:
        answer, dialog_act, system_statement = kb_agent(user_id=user_info['user_id'], user_utterance=user_utterance, modules=modules)
    except Exception as e:
        print('Error: ', e)
        answer = '제가 잘 못 이해했습니다.'
        dialog_act = 'System Error'
        system_statement = None

    intent_emp = None
    if system_statement is not None and len(system_statement) > 0:
        if 'selected_module' in system_statement:
            intent_emp = system_statement['selected_module']


    print('answer', answer)
    utterance_info = db_linker.SaveUtterance(user_id=user_info['user_id'], speaker='system', utterance=answer, session_id=session_id,
                            intent_req=dialog_act, intent_emp=intent_emp)

    count_of_knowledge = db_linker.get_count_of_knowledge_in_session(utterance_info['session_id'])['count(*)']

    response = {
        'answer': answer,
        'dialog_act': dialog_act,
        'system_statement': system_statement,
        'count_of_knowledge_in_this_session': count_of_knowledge,
        'used_module': modules
    }

    return response


def kb_agent(user_id=None, user_utterance=None, modules=[]):
    answer = '어떤 응답을 해야할지 모르겠어요.'
    last_system_utterance_info = db_linker.getLatestUtterance(user_id=user_id, speaker='system')
    # if 'fact_checking_QA' in modules and (last_system_utterance_info['intent_req'] not in ['frame_question',
    #                                                                                       'entity_question']):

    if len(user_utterance) == 0:
        user_utterance = '.'

    # if 'fact_checking_QA' in modules and user_utterance[-1] == '?':
    if 'fact_checking_QA' in modules:
        print('fact_checking_QA')
        inp = {
            "question": user_utterance
        }
        r = requests.post(fact_checking_QA_url, json=inp)
        result = r.json()
        answer = result['answer']
        system_statement = result
        print('result: ', result)
        if len(modules) == 1:
            return answer, 'fact_checking_qa', system_statement
        if answer != '질문을 이해할 수 없습니다.' and '글쎄요' not in answer:
            return answer, 'fact_checking_qa', system_statement

    # if 'sparql_qa' in modules and (last_system_utterance_info['intent_req'] not in ['frame_question', 'entity_question']):
    # if 'sparql_qa' in modules and user_utterance[-1] == '?':
    if 'sparql_qa' in modules:
        print('sparql_qa')
        sparql_answer, dialog_act, system_statement = SPARQL_QA.sparql_conversation(user_id=user_id, sentence=user_utterance)

        print('system_statement: ', system_statement)

        if sparql_answer is not None:
            answer = sparql_answer
            return answer, dialog_act, system_statement
        return '잘 모르겠어요..', dialog_act, system_statement

    if 'frame_qa' in modules and last_system_utterance_info['intent_req'] not in ['entity_question']:
        print('frame_qa')
        frame_answer, dialog_act, system_statement = frame_QA.frame_conversation(user_id=user_id, utterance=user_utterance)

        if frame_answer is not None:
            answer = frame_answer
            return answer, dialog_act, system_statement

    if 'knowledge_acquire' in modules:
        print('knowledge_qa')
        knowledge_answer, dialog_act, system_statement = knowledge_question.knowledge_conversation(user_id=user_id,
                                                                                 user_utterance=user_utterance)
        if knowledge_answer is not None:
            answer = knowledge_answer
            return answer, dialog_act, system_statement

    return answer, 'none', None


global_command = ['stop']

if __name__ == "__main__":
    print('system 작동 시작')
    access_result = user_access(user_name='test2')
    print(access_result)
    user_info = access_result['user_info']
    session_info = access_result['session_info']

    response = respond_to_user_utterance(user_id=user_info['user_id'], user_utterance='로마에서 휴가를 보냈어',
                                         session_id=session_info['session_id'], modules=['knowledge_acquire'])

    print(response)
    response = respond_to_user_utterance(user_id=user_info['user_id'], user_utterance='이탈리아야',
                                         session_id=session_info['session_id'], modules=['knowledge_acquire'])

    print(response)
