import pymysql
import datetime

dialogDBHost = '143.248.135.146'
dialogDBPort = 3142
dialogDBUserName = 'flagship'
dialogDBPassword = 'kbagent'
dialogDBDatabase = 'dialogDB'
dialogDBCharset = 'utf8'


def GetUtterances(user_id=None, session_id=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if session_id:
        sql = "SELECT * FROM SESSION s, UTTERANCE u WHERE s.session_id=u.session_id and u.session_id={}".format(session_id)
    elif user_id:
        sql = "SELECT * FROM SESSION s, UTTERANCE u WHERE s.session_id=u.session_id and s.user_id={}".format(user_id)
    curs.execute(sql)
    result = curs.fetchall()
    result = {"utterances": result}
    curs.close()
    conn.close()
    return result


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


def getLatestUtterance(session_id=None, user_id=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    if session_id:
        sql = "SELECT * FROM UTTERANCE WHERE utterance_id=(SELECT max(utterance_id) FROM UTTERANCE WHERE session_id={})".format(session_id)
    elif user_id:
        sql = "SELECT * FROM UTTERANCE WHERE utterance_id=(SELECT max(utterance_id) FROM UTTERANCE u, SESSION s WHERE u.session_id=s.session_id and s.user_id={})".format(user_id)
    result = None

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
            'query_id': 0
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


def SaveUtterance(user_id=None, utterance=None, session_id=None, speaker=None, emotion=None, intent_req=None, intent_emp=None):
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
        turn_id = latest_utterance['turn_id']+1

    query_id = latest_utterance['query_id']+1

    sql = "INSERT INTO UTTERANCE(utterance, date_time, speaker, turn_id, query_id, emotion, intent_req, intent_emp, session_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        curs.execute(sql, (utterance, nowDatetime, speaker, turn_id, query_id, emotion, intent_req, intent_emp, session_id))

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

    return result[0]


def AddNewSession(user_id=None, model_id=None, mission_id=None, feedback=None):
    if user_id is None:
        return False

    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor()

    sql = "INSERT INTO SESSION(user_id, model_id, mission_id, feedback) VALUES(%s, %s, %s, %s)"
    try:
        curs.execute(sql, (user_id, model_id, mission_id, feedback))

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
    #access_result = SaveUtterance(user_id=55, utterance='안녕하세요', intent_req=3)
    access_result = GetUtterances(session_id=330)
    # print('test : ', db_linker.GetUserInfo(user_id=55))
    import pprint
    pprint.pprint(access_result)
