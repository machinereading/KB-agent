import DB_Linker
from flask import Flask, request, jsonify
import json

app = Flask(__name__)


@app.route('/DeleteUserListInfo', methods=['POST'])
def _deleteUserListInfo():
    print('_deleteUserListInfo')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.DeleteUserListInfo(myjson['user_id'], myjson['user_interest_celeb'],
                                          myjson['user_interest_hobby'], myjson['user_interest_location'],
                                          myjson['user_topic'])
    return result


@app.route('/AddUserListInfo', methods=['POST'])
def _addUserListInfo():
    print('_addUserListInfo')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.AddUserListInfo(myjson['user_id'], myjson['user_interest_celeb'], myjson['user_interest_hobby'],
                                       myjson['user_interest_location'], myjson['user_topic'])
    print(result)

    return result


@app.route('/UpdateUserInfo', methods=['POST'])
def _updateUserInfo():
    print('_updateUserInfo')
    data = request.data.decode('utf-8')
    myjson = json.loads(data)
    result = DB_Linker.UpdateUserInfo(myjson['user_id'], myjson['user_name'], myjson['user_age'],
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
    result = DB_Linker.GetUserInfo(user_id=myjson['user_id'], user_name=myjson['user_name'])
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
    result = DB_Linker.AddNewSession(user_id=myjson['user_id'], model_id=myjson['model_id'],
                                     mission_id=myjson['mission_id'], feedback=myjson['feedback'])
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
    app.run(port=8291, host='143.248.135.146')
