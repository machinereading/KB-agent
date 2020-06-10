from flask import Flask, request, jsonify
import kb_agent
import json

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello():
    return 'hello'


@app.route('/user_access', methods=['GET', 'POST'])
def user_access():
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    user_id = None
    user_name = None
    if 'user_id' in myjson:
        user_id = myjson['user_id']
    if 'user_name' in myjson:
        user_name = myjson['user_name']

    if user_id is None and user_name is None:
        return "ERROR: input user_id or user_name"

    return kb_agent.user_access(user_name=user_name, user_id=user_id)


@app.route('/respond_to_user_utterance', methods=['GET', 'POST'])
def respond_to_user_utterance():
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    user_id = None
    user_name = None
    user_utterance = None
    session_id = None

    if 'user_id' in myjson:
        user_id = myjson['user_id']
    if 'user_name' in myjson:
        user_name = myjson['user_name']

    if user_id is None and user_name is None:
        return "ERROR: input user_id or user_name"

    if 'user_utterance' in myjson:
        user_utterance = myjson['user_utterance']
    else:
        return "ERROR: input user_utterance"

    if 'session_id' in myjson:
        session_id = myjson['session_id']

    if 'modules' in myjson:
        modules = myjson['modules']
    else:
        modules = []

    return kb_agent.respond_to_user_utterance(user_id=user_id, user_name=user_name, user_utterance=user_utterance, session_id=session_id, modules=modules)


if __name__ == "__main__":
    app.run(port=8292, host='143.248.135.146')