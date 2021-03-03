import sentence_parser
import json
import sys
import modules_constant

KB_AGENT_PATH = modules_constant.KB_AGENT_PATH
sys.path.append(KB_AGENT_PATH + 'DB_linker/')
import DB_Linker as db_linker

frame_info_path = KB_AGENT_PATH + 'KB_Agent/data/frame_info_full.json'
frame_ko_info_path = KB_AGENT_PATH + 'KB_Agent/data/frame_info_ko.json'
f = open(frame_info_path, 'r', encoding='utf-8')
frame_info = json.load(f)
f.close()
f = open(frame_ko_info_path, 'r', encoding='utf-8')
frame_ko_info = json.load(f)
f.close()


def get_korean_name_from_korean_definition(definition):
    temp1 = definition.split('>>')
    temp2 = temp1[0].split('<<')
    return temp2[1]


def get_frame_core_empty_argument(frame_input):
    frame = frame_input['frame']
    core_argument_list = []
    for argument_info in frame_info[frame]['arguments']:
        if argument_info['coreType'] == 'Core':
            core_argument_list.append(argument_info['fe'])

    denotation_argument_list = []
    for denotation in frame_input['denotations']:
        if denotation['role'] == 'ARGUMENT':
            denotation_argument_list.append(denotation['obj'])

    empty_argument_list = []
    for argument in core_argument_list:
        if argument not in denotation_argument_list:
            empty_argument_list.append(argument)

    return empty_argument_list


def frame_argument_question(lu, empty_argument_list, utterance_id, frame_log_id):
    question_argument = empty_argument_list.pop()

    frame_utt = lu

    temp = lu.split('.')

    kor_question_argument = question_argument
    if temp[2] in frame_ko_info:
        ko_frame = get_korean_name_from_korean_definition(frame_ko_info[temp[2]]['definition'])
        frame_utt = ko_frame + '(' + temp[0] + ')'

        for argument in frame_ko_info[temp[2]]['arguments']:
            if argument['fe'] == question_argument:
                kor_question_argument = get_korean_name_from_korean_definition(argument['definition'])

    frame_question = frame_utt + '의 ' + kor_question_argument + '는 무엇인가요?'
    datalist = []
    datadict = {
        'utterance_id': utterance_id,
        'frame_log_id': frame_log_id,
        'question_argument': question_argument
    }
    datalist.append(datadict)
    frame_question_id = db_linker.InsertDataToTable('FRAME_QUESTION', datalist)
    return frame_question


def save_frame_answer(frames, frame_question, utterance_id):
    print(frame_question)
    for denotation in frames[-1]['denotations']:
        datalist = []
        if denotation['role'] == 'TARGET':
            datadict = {
                'frame_log_id': frame_question['frame_log_id'],
                'utterance_id': utterance_id,
                'object': frame_question['question_argument'],
                'role': 'ARGUMENT'
            }
            datalist.append(datadict)
            frame_answered_denotation_id = db_linker.InsertDataToTable('FRAME_ANSWERED_DENOTATION', datalist)
            for span in denotation['token_span']:
                datalist = []
                datadict = {
                    'frame_answered_denotation_id': frame_answered_denotation_id,
                    'token_span': span
                }
                datalist.append(datadict)
                span_id = db_linker.InsertDataToTable('FRAME_ANSWERED_DENOTATION_SPAN', datalist)

        return denotation['text']


def react_frame_answer(sentence, last_user_utterance_id, user_utterance_id):
    frames = sentence_parser.Frame_Interpreter(sentence, target='n')
    print(frames)
    print(user_utterance_id)
    ## 대답에서 frame을 잡은 경우
    if len(frames) > 0:
        frame_question = db_linker.getFrameQuestionByUtteranceID(last_user_utterance_id)
        frame_log = db_linker.getFrameLogWithFrameLogID(frame_question['frame_log_id'])
        obj = save_frame_answer(frames, frame_question, user_utterance_id)
        frame = frame_log['frame']
        f_q = frame_question['question_argument']
        if frame in frame_ko_info:
            for argument in frame_ko_info[frame]['arguments']:
                if argument['fe'] == f_q:
                    f_q = get_korean_name_from_korean_definition(argument['definition'])

        if frame_question:
            answer = f_q + '는 ' + obj + ' 이군요 '
            answer = answer + '감사합니다.'
        else:
            answer = "그렇군요."
        ## 질문이 더 남은 경우
        # if len(empty_argument_list) > 0:
        #     pre_system_dialog_act = 'frame_question'
        #     answer = answer + ' ' + frame_argument_question(frames)

        ## 질문이 더 남지 않은 경우
        # else:
        #    pre_system_dialog_act = None

        system_statement = {
            'frame_question': f_q,
            'obj': obj
        }

    ## 대답에서 frame을 잡지 못한 경우
    else:
        system_statement = {
            'frames': frames,
        }
        answer = '죄송한데, 잘 이해를 못했어요.'
        return answer, "frame_answer", system_statement
    return answer, "frame_answer", system_statement


def save_frame_info(frames, utterance_id):
    for frame in frames:

        datalist = []
        datadict = {
            'utterance_id': utterance_id,
            'lu': frame['lu'],
            'frame': frame['frame']
        }
        datalist.append(datadict)
        frame_log_id = db_linker.InsertDataToTable('FRAME_LOG', datalist)

        for denotation in frame['denotations']:
            datalist = []
            datadict = {
                'frame_log_id': frame_log_id,
                'object': denotation['obj'],
                'role': denotation['role']
            }
            datalist.append(datadict)
            denotation_log_id = db_linker.InsertDataToTable('FRAME_DENOTATION', datalist)
            for token_span in denotation['token_span']:
                datalist = []
                datadict = {
                    'denotation_log_id': denotation_log_id,
                    'token_span': token_span
                }
                datalist.append(datadict)
                span_id = db_linker.InsertDataToTable('FRAME_DENOTATION_SPAN', datalist)

    return frame_log_id


def frame_conversation(utterance=None, user_id=None):
    last_system_utterance_info = db_linker.getLatestUtterance(user_id=user_id, speaker='system')
    now_user_utterance_info = db_linker.getLatestUtterance(user_id=user_id, speaker='user')
    last_user_utterance_info = db_linker.getLatestUtterance(user_id=user_id, speaker='last_user')
    #print(last_utterance_info)
    print(last_user_utterance_info)

    if last_system_utterance_info['intent_req'] == "frame_question":
        return react_frame_answer(utterance, last_user_utterance_info['utterance_id'], now_user_utterance_info['utterance_id'])
    else:
        frames = sentence_parser.Frame_Interpreter(utterance, target='v')
        print(frames)

        if len(frames) <= 0:
            frames = sentence_parser.Frame_Interpreter(utterance, target='n')

        if len(frames) > 0:
            frame_log_id = save_frame_info(frames, now_user_utterance_info['utterance_id'])

            lu = frames[-1]['lu']
            empty_argument_list = get_frame_core_empty_argument(frames[-1])
            system_statement = {
                'lu': lu,
                'empty_argument_list': empty_argument_list,
                'frames': frames
            }

            ## frame이 잡혔고, 비어있는 core element가 존재하는 경우
            if len(empty_argument_list) > 0:
                dialog_act = "frame_question"
                return frame_argument_question(lu, empty_argument_list, now_user_utterance_info['utterance_id'],
                                               frame_log_id), dialog_act, system_statement

    return None, None, None


if __name__ == "__main__":
    # question = '아빠랑 지냈어'
    # user = 43
    # print(frame_conversation(utterance=question, user_id=user))
    print(get_korean_name_from_korean_definition("<<효과>> 현상에 대한 긍정적 또는 부정적 평가."))
