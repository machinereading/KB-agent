import requests

global_stop_command = ['stop']
kb_agent_url = 'kbox.kaist.ac.kr:8292/'

if __name__ == "__main__":
    print('system 작동 시작')
    print('system : 사용자 이름을 입력해주세요.')
    user_name = input()
    user_data = {"user_name": user_name}
    r = requests.post(kb_agent_url+'user_access', json=user_data)

    print('system : ' + user_name + '님 안녕하세요.')

    while True:
        user_utterance = input()

        if user_utterance in global_stop_command:
            print('감사합니다.')
            break
        utterance_data = {"user_id": user_name, "user_utterance": user_utterance}
        r = requests.post(kb_agent_url+'user_utterance', json=utterance_data)
        result = r.json()
        system_utterance = result['response']

        print('system : ' + system_utterance)


