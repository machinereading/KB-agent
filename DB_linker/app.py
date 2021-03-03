import DB_Linker
from flask import Flask, request, jsonify
import json
from flask_cors import CORS
import ssl
app = Flask(__name__)
CORS(app)


@app.route('/DeleteUserListInfo', methods=['POST'])
def _deleteUserListInfo():
    print('_deleteUserListInfo')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.DeleteUserListInfo(myjson['user_id'], myjson['user_num'], myjson['user_interest_celeb'],
                                          myjson['user_interest_hobby'], myjson['user_interest_location'],
                                          myjson['user_topic'])
    return result


@app.route('/AddUserInfo', methods=['POST'])
def _addUserInfo():
    print('_addUserInfo')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.AddUserInfo(user_num=myjson['user_num'], user_name=myjson['user_name'],
                                   user_age=myjson['user_age'],
                                   user_birth=myjson['user_birth'], user_gender=myjson['user_gender'],
                                   user_current_city=myjson['user_current_city'],
                                   user_hometown=myjson['user_hometown'], user_professional=myjson['user_professional'],
                                   user_job_title=myjson['user_job_title'], personality_E=myjson['personality_E'],
                                   personality_N=myjson['personality_N'], personality_C=myjson['personality_C'],
                                   personality_A=myjson['personality_A'], personality_O=myjson['personality_O'])
    print(result)

    return result


@app.route('/AddUserListInfo', methods=['POST'])
def _addUserListInfo():
    print('_addUserListInfo')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.AddUserListInfo(myjson['user_id'], myjson['user_num'], myjson['user_interest_celeb'],
                                       myjson['user_interest_hobby'],
                                       myjson['user_interest_location'], myjson['user_topic'])
    print(result)

    return result


@app.route('/UpdateUserListInfo', methods=['POST'])
def _updateUserListInfo():
    print('_updateUserListInfo')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.UpdateUserListInfo(myjson['user_id'], myjson['user_num'], myjson['user_interest_celeb'],
                                          myjson['user_interest_hobby'],
                                          myjson['user_interest_location'], myjson['user_topic'])
    print(result)

    return result


@app.route('/UpdateUserInfo', methods=['POST'])
def _updateUserInfo():
    print('_updateUserInfo')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.UpdateUserInfo(myjson['user_id'], myjson['user_num'], myjson['user_name'],
                                      myjson['user_age'],
                                      myjson['user_birth'], myjson['user_gender'], myjson['user_current_city'],
                                      myjson['user_hometown'], myjson['user_professional'], myjson['user_job_title'])

    return result


@app.route('/LookUpUsers', methods=['POST', 'GET'])
def _lookUpUsers():
    print('_lookUpUsers')

    result = DB_Linker.LookUpUsers()
    print(result)
    return result


@app.route('/GetUserInfo', methods=['POST', 'GET'])
def _getUserInfo():
    print('_getUserInfo')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)

    if 'user_id' in myjson:
        user_id = myjson['user_id']
    else:
        user_id = None

    if 'user_name' in myjson:
        user_name = myjson['user_name']
    else:
        user_name = None

    if 'user_num' in myjson:
        user_num = myjson['user_num']
    else:
        user_num = None

    result = DB_Linker.GetUserInfo(user_id=user_id, user_num=user_num, user_name=user_name)
    return result


@app.route('/GetUserInfoFull', methods=['POST', 'GET'])
def _getUserInfoFull():
    print('_getUserInfoFull')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.GetUserInfoFull(user_id=myjson['user_id'], user_num=myjson['user_num'])
    return result


@app.route('/GetUserInfoLight', methods=['POST', 'GET'])
def _getUserInfoLight():
    print('_getUserInfoLight')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.GetUserInfoLight(user_id=myjson['user_id'], user_num=myjson['user_num'])
    return result


@app.route('/AddNewUser', methods=['POST'])
def _addNewUser():
    print('_addNewUser')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    user_name = myjson['user_name']
    result = DB_Linker.AddNewUser(user_name)
    return result


@app.route('/GetUtterances', methods=['POST'])
def _getUtterances():
    print('_getUtterances')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.GetUtterances(user_id=myjson['user_id'], session_id=myjson['session_id'])
    return result


@app.route('/SaveUtterance', methods=['POST'])
def _saveUtterance():
    print('_saveUtterance')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.SaveUtterance(user_id=myjson['user_id'], utterance=myjson['utterance'],
                                     session_id=myjson['session_id'], speaker=myjson['speaker'],
                                     emotion=myjson['emotion'], intent_req=myjson['intent_req'],
                                     intent_emp=myjson['intent_emp'])
    return result


@app.route('/AddConvHistory', methods=['POST'])
def _addConvHistory():
    print('_addConvHistory')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.AddConvHistory(user_id=myjson['user_id'], user_num=myjson['user_num'], utterance=myjson['utterance'],
                                     session_id=myjson['session_id'], speaker=myjson['speaker'],
                                     emotion=myjson['emotion'], intent_req=myjson['intent_req'],
                                     intent_emp=myjson['intent_emp'])
    return result


@app.route('/GetCurrentUserConv', methods=['POST'])
def _getCurrentUserConv():
    print('_getCurrentUserConv')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.GetCurrentUserConv(user_id=myjson['user_id'], user_num=myjson['user_num'],
                                     session_id=myjson['session_id'])
    return result


@app.route('/GetConvHistory', methods=['POST'])
def _getConvHistory():
    print('_getConvHistory')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.GetConvHistory(user_id=myjson['user_id'], user_num=myjson['user_num'])
    return result


@app.route('/GetUserConvHistory', methods=['POST'])
def _getUserConvHistory():
    print('_getUserConvHistory')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.GetUserConvHistory(user_id=myjson['user_id'], user_num=myjson['user_num'])
    return result


@app.route('/GetBotConvHistory', methods=['POST'])
def _getBotConvHistory():
    print('_getBotConvHistory')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.GetBotConvHistory(user_id=myjson['user_id'], user_num=myjson['user_num'])
    return result


@app.route('/GetSessionConv', methods=['POST'])
def _getSessionConv():
    print('_getSessionConv')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.GetSessionConv(user_id=myjson['user_id'], user_num=myjson['user_num'], session_id=myjson['session_id'])
    return result


@app.route('/LookUpSessionOfUser', methods=['POST'])
def _lookUpSessionOfUser():
    print('_saveUtterance')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.LookUpSessionOfUser(user_id=myjson['user_id'], user_name=myjson['user_name'])
    return result


@app.route('/GetSessionInfo', methods=['POST'])
def _getSessionInfo():
    print('_getSessionInfo')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.GetSessionInfo(myjson['session_id'])
    return result


@app.route('/AddNewSession', methods=['POST'])
def _addNewSession():
    print('_addNewSession')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    if 'session_id' in myjson:
        session_id = myjson['session_id']
    else:
        session_id = None
    result = DB_Linker.AddNewSession(session_id=session_id, user_id=myjson['user_id'], model_id=myjson['model_id'],
                                     mission_id=myjson['mission_id'], feedback=myjson['feedback'])
    return result


@app.route('/GetUtteranceWithKnowledgeBySessionID', methods=['POST'])
def _getUtteranceWithKnowledgeBySessionID():
    print('_getUtteranceWithKnowledgeBySessionID')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.getUtteranceWithKnowledgeBySessionID(myjson['session_id'])
    return result

# @app.route('/DescribeTable', methods=['POST'])
# def _describeTable():
#     print('describeTable')
#
#     data = request.data.decode('utf-8')
#     myjson = json.loads(data)
#     table_name = myjson['table_name']
#
#     result = DB_Linker.DescribeTable(table_name)
#     print(result)
#     return json.dumps(result, ensure_ascii=False)


# @app.route('/InsertDataToTable', methods=['POST', 'GET'])
# def _insertDataToTable():
#     print('insertDataToTable')
#
#     data = request.data.decode('utf-8')
#     myjson = json.loads(data)
#     table_name = myjson['table_name']
#     data_list = myjson['data_list']
#
#     DB_Linker.InsertDataToTable(table_name, data_list)
#
#     return 'okay'


# @app.route('/LookUpTables', methods=['POST'])
# def _lookUpTables():
#     print('LookUpTables')
#
#     result = DB_Linker.LookUpTables()
#     print(result)
#     return json.dumps(result, ensure_ascii=False)


# @app.route('/GetUtteranceByUser', methods=['POST'])
# def _getUtteranceByUser():
#     print('GetUtteranceByUser')
#
#     data = request.data.decode('utf-8')
#     myjson = json.loads(data)
#     user_name = myjson['user_name']
#
#     result = DB_Linker.GetUtteranceByUser(user_name)
#
#     def func(x):
#         if 'date_time' in x:
#             x['date_time'] = str(x['date_time'])
#         return x
#
#     result = list(map(func, result))
#     print(result)
#     return json.dumps(result, ensure_ascii=False)


# @app.route('/QueryToDatabase', methods=['POST'])
# def _queryToDatabase():
#     print('QueryToDatabase')
#
#     data = request.data.decode('utf-8')
#     myjson = json.loads(data)
#     query = myjson['query']
#
#     result = DB_Linker.QueryToDatabase(query)
#
#     def func(x):
#         if 'date_time' in x:
#             x['date_time'] = str(x['date_time'])
#         return x
#
#     result = list(map(func, result))
#     print(result)
#     return json.dumps(result, ensure_ascii=False)


# @app.route('/CreateNewTable', methods=['POST'])
# def _createNewTable():
#     print('CreateNewTable')
#     data = request.data.decode('utf-8')
#     myjson = json.loads(data)
#     table_name = myjson['table_name']
#     column_list = myjson['column_list']
#
#     DB_Linker.CreateNewTable(table_name, column_list)
#     return 'okay'


@app.route('/QueryToUserKB', methods=['POST'])
def _queryToUserKB():
    print('QueryToUserKB')

    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    query = myjson['query']

    result = DB_Linker.QueryToUserKB(query)
    print(result)
    return result


@app.route('/QueryToMasterKB', methods=['POST'])
def _queryToMasterKB():
    print('QueryToMasterKB')

    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    query = myjson['query']

    result = DB_Linker.QueryToMasterKB(query)
    print(result)
    return result


@app.route('/InsertKnowledgeToUserKB', methods=['POST'])
def _insertKnowledgeToUserKB():
    print('InsertKnowledgeToUserKB')

    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    user_name = myjson['user_name']
    triple = myjson['triple']
    print(triple)
    result = DB_Linker.InsertKnowledgeToUserKB(user_name, triple)

    return 'okay'


if __name__ == "__main__":
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem', password='ybjeong')
    app.run(
        port=8291,
        host='143.248.135.146',
        ssl_context=ssl_context
    )
