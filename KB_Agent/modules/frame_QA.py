import sentence_parser
import json
import sys
import constant
KB_AGENT_PATH = constant.KB_AGENT_PATH
sys.path.append(KB_AGENT_PATH+'DB_linker/')
import DB_Linker as db_linker

frame_info_path = KB_AGENT_PATH+'KB_Agent/data/frame_info_full.json'
f = open(frame_info_path,'r',encoding='utf-8')
frame_info = json.load(f)
f.close()

def get_frame_core_empty_argument(frames):
    frame = frames[-1]['frame']
    core_argument_list = []
    for argument_info in frame_info[frame]['arguments']:
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


def frame_argument_question(frames):
    question_argument = empty_argument_list.pop()
    question_argument = question_argument
    question = lu + '의 ' + question_argument + '는 무엇인가요?'
    return question


def save_frame_answer(frames, utterance_id):
    for denotation in frames[-1]['denotations']:
        datalist = []
        if denotation['role'] == 'TARGET':
            datadict = {
                'frame_log_id': frame_log_id,
                'utterance_id': utterance_id,
                'object': question_argument,
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

def react_frame_answer(sentence, utterance_id):
    frames = sentence_parser.Frame_Interpreter(sentence, target='n')

    ## 대답에서 frame을 잡은 경우
    if len(frames) > 0:
        obj = save_frame_answer(frames, utterance_id)
        answer = question_argument + '는 ' + obj + ' 이군요 '
        answer = answer + '감사합니다.'

        ## 질문이 더 남은 경우
        if len(empty_argument_list) > 0:
            pre_system_dialog_act = 'frame_question'
            answer = answer + ' ' + frame_argument_question(frames)

        ## 질문이 더 남지 않은 경우
        else:
            pre_system_dialog_act = None

    ## 대답에서 frame을 잡지 못한 경우
    else:
        answer = '죄송한데, 잘 이해를 못했어요. 다시 알려주세요.'

    return answer

def frame_conversation(utterance=None, user_id=None):

    return '기본응답', 1

    last_utterance_info = db_linker.getLatestUtterance(user_id=user_id)

    if last_utterance_info['intent_req'] == 822:
        return react_frame_answer(sentence, utterance_id)
    else:
        frames = sentence_parser.Frame_Interpreter(utterance, target='v')
        if len(frames) > 0:
            frame_log_id = save_frame_info(frames, utterance_id)
            lu = frames[-1]['lu']
            empty_argument_list = get_frame_core_empty_argument(frames)

            ## frame이 잡혔고, 비어있는 core element가 존재하는 경우
            if len(empty_argument_list) > 0:
                dialog_act = 822
                return frame_argument_question(frames)

if __name__ == "__main__":
    question = '나는 독일에서 태어났어'
    user = 'ybjeong'
    print(frame_conversation(utterance=question, user_id=user))
