import pymysql
import datetime
import copy
import constant

dialogDBHost = constant.dialogDBHost
dialogDBPort = constant.dialogDBPort
dialogDBUserName = constant.dialogDBUserName
dialogDBPassword = constant.dialogDBPassword
dialogDBDatabase = constant.dialogDBDatabase
dialogDBCharset = constant.dialogDBCharset



def get_user_id_with_user_account(user_num):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    #sql = "select user_id from USER where user_num='" + user_account + "'"
    sql = "select user_id from USER where user_num="+str(user_num)

    print(sql)

    try:
        curs.execute(sql)
        result = curs.fetchall()
        print(result)

    except Exception as e:
        print(e)

    user_info = result[0]
    user_id = user_info['user_id']

    return user_id


def getTripleQuestion(utterance_id=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM USERKB_LOG WHERE utterance_id={}".format(utterance_id)
    print()
    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)
    curs.close()
    conn.close()
    print(result)
    if len(result) == 0:
        return []
    return result[-1]


def GetUtterances(user_id=None, session_id=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if session_id:
        sql = "SELECT * FROM SESSION s, UTTERANCE u WHERE s.session_id=u.session_id and u.session_id={}".format(
            session_id)
    elif user_id:
        sql = "SELECT * FROM SESSION s, UTTERANCE u WHERE s.session_id=u.session_id and s.user_id={}".format(user_id)
    curs.execute(sql)
    result = curs.fetchall()
    result = {"utterances": result}
    curs.close()
    conn.close()
    return result


def GetCurrentUserConv(user_id=None, user_num=None, session_id=None):
    if user_id is None:
        if user_num is None:
            if session_id is None:
                return "ERROR: either user_id or user_num or session_id is essential"
        else:
            user_id = get_user_id_with_user_account(user_num)

    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if session_id:
        sql = "SELECT p.user_id as user_id, p.user_num as user_num, s.session_id as session_id, u.turn_id as turn_id, u.query_id as query_id, u.emotion as user_emotion, u.utterance as user_utterance FROM USER p, SESSION s, UTTERANCE u WHERE p.user_id=s.user_id and s.session_id=u.session_id and u.session_id={} and u.speaker='user' ORDER BY date_time DESC LIMIT 1".format(
            session_id)
    elif user_id:
        sql = "SELECT p.user_id as user_id, p.user_num as user_num, s.session_id as session_id, u.turn_id as turn_id, u.query_id as query_id, u.emotion as user_emotion, u.utterance as user_utterance FROM USER p, SESSION s, UTTERANCE u WHERE p.user_id=s.user_id and  s.session_id=u.session_id and s.user_id={} and u.speaker='user' ORDER BY date_time DESC LIMIT 1".format(
            user_id)

    curs.execute(sql)
    result = curs.fetchall()
    print(result[0])
    # print(result[0]['date_time'])
    curs.close()
    conn.close()

    if len(result) > 0:
        #result[0]['date_time'] = str(result[0]['date_time'])
        result[0]['date_time'] = str(datetime.datetime.now().time())
        return result[0]

    else:
        return None


def getLatestSession(user_id):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM SESSION WHERE session_id=(SELECT max(session_id) FROM SESSION WHERE user_id={})".format(
        user_id)

    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)
    curs.close()
    conn.close()

    return result[0]


def GetSessionConv(user_id=None, user_num=None, session_id=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    if session_id is None:
        if user_id is None:
            if user_num is None:
                return "ERROR: either user_id or user_account or session_id is essential"
            else:
                user_id = get_user_id_with_user_account(user_num)

        session_id = getLatestSession(user_id)['session_id']

    sql = "SELECT u.user_id, u.user_num, d.utterance, d.emotion, d.speaker FROM USER u, SESSION s, UTTERANCE d WHERE u.user_id=s.user_id and s.session_id=d.session_id and s.session_id={} ORDER BY date_time DESC".format(session_id)
    # 	sql = "SELECT * FROM USER"

    result_dict = {
        "user_id": user_id,
        "user_num": user_num,
        'session_id': session_id,
        'date_time': None,
        'user_emotion': None,
        'user_convHistory':[],
        'bot_emotion': None,
        'bot_convHistory':[]
    }

    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)

    print(result)

    if len(result) > 0:
        result_dict['user_id'] = result[0]['user_id']
        result_dict['user_num'] = result[0]['user_num']
        #result_dict['date_time'] = str(result[0]['date_time'])
        result_dict['date_time'] = str(datetime.datetime.now().time())

        user_emotion_flag = False
        bot_emotion_flag = False
        for temp in result:

            if temp['speaker'] == 'bot':
                result_dict['bot_convHistory'].append(temp['utterance'])
                if bot_emotion_flag is False:
                    result_dict['bot_emotion'] = temp['emotion']
                    bot_emotion_flag = True
            if temp['speaker'] == 'user':
                result_dict['user_convHistory'].append(temp['utterance'])
                if user_emotion_flag is False:
                    result_dict['user_emotion'] = temp['emotion']
                    user_emotion_flag = True

    curs.close()
    conn.close()

    return result_dict


def getLatestUtterance(session_id=None, user_id=None, speaker=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if speaker == 'last_user':
        sql = "SELECT * FROM UTTERANCE WHERE utterance_id=(SELECT utterance_id FROM UTTERANCE u, SESSION s WHERE u.session_id=s.session_id and s.user_id={} and u.speaker='user' ORDER BY utterance_id DESC LIMIT 1,1)".format(
            user_id)
    else:
        if session_id:
            sql = "SELECT * FROM UTTERANCE WHERE utterance_id=(SELECT max(utterance_id) FROM UTTERANCE WHERE session_id={})".format(
                session_id)
            if speaker is not None:
                sql = sql[:-1] + " and speaker='" + speaker + "')"
        elif user_id:
            sql = "SELECT * FROM UTTERANCE WHERE utterance_id=(SELECT max(utterance_id) FROM UTTERANCE u, SESSION s WHERE u.session_id=s.session_id and s.user_id={})".format(
                user_id)
            if speaker is not None:
                sql = sql[:-1] + " and u.speaker='" + speaker + "')"

    result = []

    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)
    curs.close()
    conn.close()
    if len(result) > 0:
        answer = result[0]
    else:
        answer = {
            'speaker': 'system',
            'turn_id': 0,
            'query_id': 0,
            'session_id': 0,
            'intent_req': None
        }

    return answer


def getUtteranceById(utterance_id):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM UTTERANCE WHERE utterance_id={}".format(utterance_id)

    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)
    curs.close()
    conn.close()

    return result[0]


def update_utterance_intent_emp(utterance_id=None, intent_emp=None):
    if utterance_id is None:
        return False

    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor()

    sql = "update UTTERANCE set intent_emp='{}' where utterance_id={}".format(intent_emp, utterance_id)
    print('sql: ', sql)

    try:
        curs.execute(sql)
    except Exception as e:
        print(e)
    curs.close()
    conn.commit()
    conn.close()

    return True

def SaveUtterance(user_id=None, utterance=None, session_id=None, speaker=None, emotion=None, intent_req=None,
                  intent_emp=None):
    if user_id is None or utterance is None:
        return False
    if session_id is None:
        session_info = getLatestSession(user_id)
        session_id = session_info['session_id']

    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor()

    now = datetime.datetime.now()
    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
    latest_utterance = getLatestUtterance(session_id=session_id)
    if speaker is None:
        if latest_utterance['speaker'] == 'user':
            speaker = 'system'
        elif latest_utterance['speaker'] == 'system':
            speaker = 'user'

    if speaker == 'system':
        turn_id = latest_utterance['turn_id']
    else:
        turn_id = latest_utterance['turn_id'] + 1

    query_id = latest_utterance['query_id'] + 1

    sql = "INSERT INTO UTTERANCE(utterance, date_time, speaker, turn_id, query_id, emotion, intent_req, intent_emp, session_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        curs.execute(sql,
                     (utterance, nowDatetime, speaker, turn_id, query_id, emotion, intent_req, intent_emp, session_id))

    except Exception as e:
        print(e)

    sql = "SELECT LAST_INSERT_ID()"
    result = None
    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)

    curs.close()
    conn.commit()
    conn.close()

    return getUtteranceById(result[0][0])


def AddConvHistory(user_id=None, user_num=None, utterance=None, session_id=None, speaker=None, emotion=None,
                   intent_req=None, intent_emp=None):
    if user_id is None:
        if user_num is None:
            return "ERROR: either user_id or user_account is essential"
        else:
            user_id = get_user_id_with_user_account(user_num)

    if session_id is None:
        return "ERROR: session_id is essential"

    session_info = GetSessionInfo(session_id)
    if session_info is None:
        AddNewSession(session_id=session_id, user_id=user_id, model_id=None, mission_id=None, feedback=None)

    return SaveUtterance(user_id=user_id, utterance=utterance, session_id=session_id, speaker=speaker, emotion=emotion,
                         intent_req=intent_req, intent_emp=intent_emp)


def LookUpSessionOfUser(user_id=None, user_name=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if user_id:
        sql = "SELECT * FROM SESSION WHERE user_id={}".format(user_id)
    elif user_name:
        sql = "SELECT * FROM SESSION WHERE user_id=(SELECT user_id FROM USER WHERE user_name={})".format(user_name)
    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)
    curs.close()
    conn.close()

    result = {
        'sessions': result
    }

    return result


def GetSessionInfo(session_id):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM SESSION WHERE session_id={}".format(session_id)

    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)
    curs.close()
    conn.close()

    if len(result) > 0:
        return result[0]
    else:
        return None


def AddNewSession(session_id=None, user_id=None, model_id=None, mission_id=None, feedback=None):
    if user_id is None:
        return False

    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor()
    if session_id is None:
        sql = "INSERT INTO SESSION(user_id, model_id, mission_id, feedback) VALUES(%s, %s, %s, %s)"
    else:
        sql = "INSERT INTO SESSION(session_id, user_id, model_id, mission_id, feedback) VALUES(%s, %s, %s, %s, %s)"

    print(sql)
    try:
        if session_id is None:
            curs.execute(sql, (user_id, model_id, mission_id, feedback))
        else:
            curs.execute(sql, (session_id, user_id, model_id, mission_id, feedback))

    except Exception as e:
        print(e)

    sql = "SELECT LAST_INSERT_ID()"
    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)

    curs.close()
    conn.commit()
    conn.close()

    session_info = GetSessionInfo(session_id=result[0][0])

    return session_info


if __name__ == "__main__":
    print('system 작동 시작')
    # access_result = SaveUtterance(user_id=55, utterance='안녕하세요', intent_req=3)
    #access_result = GetUtterances(session_id=330)
    result = AddConvHistory(user_id=43, user_num=None, utterance='test_utterance', session_id=999, speaker='bot', emotion=None,
                   intent_req=None, intent_emp=None)
    # print('test : ', db_linker.GetUserInfo(user_id=55))
    import pprint

    pprint.pprint(result)
