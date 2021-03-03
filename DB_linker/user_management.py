import pymysql
import os
import copy
import constant

dialogDBHost = constant.dialogDBHost
dialogDBPort = constant.dialogDBPort
dialogDBUserName = constant.dialogDBUserName
dialogDBPassword = constant.dialogDBPassword
dialogDBDatabase = constant.dialogDBDatabase
dialogDBCharset = constant.dialogDBCharset

HOME_DIRECTORY = constant.HOME_DIRECTORY
DOCKER_EXEC_PREFIX = constant.DOCKER_EXEC_PREFIX


def get_user_id_with_user_account(user_num):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    #sql = "select user_id from USER where user_account='"+user_account+"'"
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


def DeleteUserListInfo(user_id=None, user_num=None, user_interest_celeb=[], user_interest_hobby=[], user_interest_location=[],
                       user_topic=[]):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor()
    if user_id is None:
        if user_num is None:
            return "ERROR: either user_id or user_num is essential"
        else:
            user_id = get_user_id_with_user_account(user_num)

    def sql_string(st):
        return "'" + st + "'"

    user_interest_celeb = list(map(sql_string, user_interest_celeb))
    user_interest_hobby = list(map(sql_string, user_interest_hobby))
    user_interest_location = list(map(sql_string, user_interest_location))
    user_topic = list(map(sql_string, user_topic))

    if len(user_interest_celeb) > 0:
        delete_string = ",".join(user_interest_celeb)
        sql = "DELETE FROM USER_INTEREST_CELEB WHERE celeb IN ({})".format(delete_string)
        try:
            curs.execute(sql)
        except Exception as e:
            print(e)
    if len(user_interest_hobby) > 0:
        delete_string = ",".join(user_interest_hobby)
        sql = "DELETE FROM USER_INTEREST_HOBBY WHERE hobby IN ({})".format(delete_string)

        try:
            curs.execute(sql)
        except Exception as e:
            print(e)
    if len(user_interest_location) > 0:
        delete_string = ",".join(user_interest_location)
        sql = "DELETE FROM USER_INTEREST_LOCATION WHERE location IN ({})".format(delete_string)
        try:
            curs.execute(sql)
        except Exception as e:
            print(e)
    if len(user_topic) > 0:
        delete_string = ",".join(user_topic)
        sql = "DELETE FROM USER_TOPIC WHERE topic IN ({})".format(delete_string)
        try:
            curs.execute(sql)
        except Exception as e:
            print(e)

    curs.close()
    conn.commit()
    conn.close()

    return GetUserInfo(user_id=user_id)


def AddUserInfo(user_num=None, user_name=None, user_age=None, user_birth=None, user_gender=None, user_current_city=None, user_hometown=None, user_professional=None, user_job_title=None, personality_E=None, personality_N=None, personality_C=None, personality_A=None, personality_O=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor()

    sql = "INSERT INTO USER(user_num, user_name, user_age, user_birth, user_gender, user_current_city, user_hometown, user_professional, user_job_title, personality_E, personality_N, personality_C, personality_A, personality_O) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    print(sql)
    try:
        curs.execute(sql, (user_num, user_name, user_age, user_birth, user_gender, user_current_city, user_hometown, user_professional, user_job_title, personality_E, personality_N, personality_C, personality_A, personality_O))

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
    #AddNewUserInKB(user_name)
    user_info = GetUserInfo(user_id=result[0][0])
    #	return result[0][0]
    return user_info



def AddUserListInfo(user_id=None, user_num=None, user_interest_celeb=[], user_interest_hobby=[], user_interest_location=[],
                    user_topic=[]):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor()

    if user_id == None:
        if user_num == None:
            return 'error'
        else:
            user_id = get_user_id_with_user_account(user_num)


    for celeb in user_interest_celeb:
        sql = "INSERT INTO USER_INTEREST_CELEB(user_id, celeb) VALUES(%s, %s)"
        try:
            curs.execute(sql, (user_id, celeb))
        except Exception as e:
            print(e)

    for hobby in user_interest_hobby:
        sql = "INSERT INTO USER_INTEREST_HOBBY(user_id, hobby) VALUES(%s, %s)"
        try:
            curs.execute(sql, (user_id, hobby))
        except Exception as e:
            print(e)

    for location in user_interest_location:
        sql = "INSERT INTO USER_INTEREST_LOCATION(user_id, location) VALUES(%s, %s)"
        try:
            curs.execute(sql, (user_id, location))
        except Exception as e:
            print(e)

    for topic in user_topic:
        sql = "INSERT INTO USER_TOPIC(user_id, topic) VALUES(%s, %s)"
        try:
            curs.execute(sql, (user_id, topic))
        except Exception as e:
            print(e)

    curs.close()
    conn.commit()
    conn.close()

    return GetUserInfo(user_id=user_id)


def UpdateUserListInfo(user_id=None, user_num=None, user_interest_celeb=[], user_interest_hobby=[], user_interest_location=[],
                    user_topic=[]):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor()

    if user_id == None:
        if user_num == None:
            return 'error'
        else:
            user_id = get_user_id_with_user_account(user_num)

    sql = "DELETE FROM USER_INTEREST_CELEB WHERE user_id={}".format(user_id)
    try:
        curs.execute(sql)
    except Exception as e:
        print(e)
    sql = "DELETE FROM USER_INTEREST_HOBBY WHERE user_id={}".format(user_id)
    try:
        curs.execute(sql)
    except Exception as e:
        print(e)
    sql = "DELETE FROM USER_INTEREST_LOCATION WHERE user_id={}".format(user_id)
    try:
        curs.execute(sql)
    except Exception as e:
        print(e)
    sql = "DELETE FROM USER_TOPIC WHERE user_id={}".format(user_id)
    try:
        curs.execute(sql)
    except Exception as e:
        print(e)

    curs.close()
    conn.commit()
    conn.close()

    return AddUserListInfo(user_id, user_num, user_interest_celeb, user_interest_hobby, user_interest_location, user_topic)


def UpdateUserInfo(user_id=None, user_num=None, user_name=None, user_age=None, user_birth=None, user_gender=None,
                   user_current_city=None, user_hometown=None, user_professional=None, user_job_title=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    update_list = []

    if user_id is None:
        if user_num is None:
            return "ERROR: either user_id or user_num is essential"
        else:
            user_id = get_user_id_with_user_account(user_num)
    if user_name:
        update_list.append("user_name='{}'".format(user_name))
    if user_age:
        update_list.append("user_age={}".format(user_age))
    if user_birth:
        update_list.append("user_birth='{}'".format(user_birth))
    if user_gender:
        update_list.append("user_gender='{}'".format(user_gender))
    if user_current_city:
        update_list.append("user_current_city='{}'".format(user_current_city))
    if user_hometown:
        update_list.append("user_hometown='{}'".format(user_hometown))
    if user_professional:
        update_list.append("user_professional='{}'".format(user_professional))
    if user_job_title:
        update_list.append("user_job_title='{}'".format(user_job_title))

    sql = "UPDATE USER SET " + ", ".join(update_list) + " WHERE user_id = {}".format(user_id)
    print(sql)
    curs.execute(sql)
    result = curs.fetchall()

    curs.close()
    conn.commit()
    conn.close()
    return GetUserInfo(user_id=user_id)


def LookUpUsers():
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM USER"
    try:
        curs.execute(sql)
        result = curs.fetchall()
    except Exception as e:
        print(e)

    curs.close()
    conn.close()
    result = {'user_list': result}
    return result


def GetUserInfo(user_id=None, user_num=None, user_name=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    if user_id:
        sql = "SELECT user_id, user_num, user_name, user_age, user_birth, user_gender, user_current_city, user_hometown, user_professional, user_job_title FROM USER WHERE user_id={}".format(user_id)
    elif user_num:
        sql = "SELECT user_id, user_num, user_name, user_age, user_birth, user_gender, user_current_city, user_hometown, user_professional, user_job_title FROM USER WHERE user_num='{}'".format(user_num)
    elif user_name:
        sql = "SELECT user_id, user_num, user_name, user_age, user_birth, user_gender, user_current_city, user_hometown, user_professional, user_job_title FROM USER WHERE user_name='{}'".format(
            user_name)

    # 	sql = "SELECT * FROM USER"

    print(sql)
    print(user_id)

    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)

    user_info = copy.deepcopy(result[0])
    user_id = user_info['user_id']
    tuple_list_of_user_interest = [('USER_TOPIC', 'topic'), ('USER_INTEREST_CELEB', 'celeb'),
                                   ('USER_INTEREST_HOBBY', 'hobby'), ('USER_INTEREST_LOCATION', 'location')]

    for temp in tuple_list_of_user_interest:

        sql = "SELECT * FROM " + temp[0] + " WHERE user_id={}".format(user_id)
        try:
            curs.execute(sql)
            result = curs.fetchall()
        except Exception as e:
            print(e)
        user_info[temp[0]] = []
        for info in result:
            user_info[temp[0]].append(info[temp[1]])

    curs.close()
    conn.close()

    return user_info


def get_convHistory_with_user_account(user_id, speaker):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    sql = "select d.utterance from USER u, SESSION s, UTTERANCE d where u.user_id=s.user_id and s.session_id=d.session_id and u.user_id={} and d.speaker='{}' ORDER BY d.date_time DESC LIMIT 30".format(user_id, speaker)

    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)

    result_list=[]
    for temp in result:
        result_list.append(temp['utterance'])

    result_list

    curs.close()
    conn.close()
    return result_list

def get_latest_emotion(user_id, speaker):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)

    sql = "select d.emotion from USER u, SESSION s, UTTERANCE d where u.user_id=s.user_id and s.session_id=d.session_id and u.user_id={} and d.speaker='{}' ORDER BY d.date_time DESC LIMIT 1".format(
        user_id, speaker)

    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)

    curs.close()
    conn.close()
    if len(result) == 0:
        return None
    else:
        return result[0]['emotion']


def GetUserInfoFull(user_id=None, user_num=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    if user_id is None:
        if user_num is None:
            return "ERROR: either user_id or user_account is essential"
        else:
            user_id = get_user_id_with_user_account(user_num)

    sql = "SELECT user_id, user_num, user_name, user_age, user_birth, user_gender, user_current_city, user_hometown, user_professional, user_job_title, personality_E, personality_N, personality_C, personality_A, personality_O FROM USER WHERE user_id={}".format(user_id)
    # 	sql = "SELECT * FROM USER"

    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)

    user_info = copy.deepcopy(result[0])
    user_id = user_info['user_id']
    tuple_list_of_user_interest = [('USER_TOPIC', 'topic'), ('USER_INTEREST_CELEB', 'celeb'),
                                   ('USER_INTEREST_HOBBY', 'hobby'), ('USER_INTEREST_LOCATION', 'location')]

    for temp in tuple_list_of_user_interest:

        sql = "SELECT * FROM " + temp[0] + " WHERE user_id={}".format(user_id)
        try:
            curs.execute(sql)
            result = curs.fetchall()
        except Exception as e:
            print(e)
        user_info[temp[0]] = []
        for info in result:
            user_info[temp[0]].append(info[temp[1]])

    user_info['user_convHistory'] = get_convHistory_with_user_account(user_id, 'user')
    user_info['bot_convHistory'] = get_convHistory_with_user_account(user_id, 'bot')

    user_info['user_emotion'] = get_latest_emotion(user_id, 'user')
    user_info['bot_emotion'] = get_latest_emotion(user_id, 'bot')

    curs.close()
    conn.close()

    return user_info



def GetUserInfoLight(user_id=None, user_num=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    if user_id is None:
        if user_num is None:
            return "ERROR: either user_id or user_num is essential"
        else:
            user_id = get_user_id_with_user_account(user_num)

    sql = "SELECT user_id, user_num, user_name, user_age, user_birth, user_gender, personality_E, personality_N, personality_C, personality_A, personality_O FROM USER WHERE user_id={}".format(user_id)
    # 	sql = "SELECT * FROM USER"

    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)

    user_info = copy.deepcopy(result[0])

    user_info['user_convHistory'] = get_convHistory_with_user_account(user_id, 'user')
    user_info['bot_convHistory'] = get_convHistory_with_user_account(user_id, 'bot')

    user_info['user_emotion'] = get_latest_emotion(user_id, 'user')
    user_info['bot_emotion'] = get_latest_emotion(user_id, 'bot')

    curs.close()
    conn.close()

    return user_info


def GetConvHistory(user_id=None, user_num=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    if user_id is None:
        if user_num is None:
            return "ERROR: either user_id or user_num is essential"
        else:
            user_id = get_user_id_with_user_account(user_num)

    sql = "SELECT user_id, user_num FROM USER WHERE user_id={}".format(
        user_id)
    # 	sql = "SELECT * FROM USER"

    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)

    user_info = copy.deepcopy(result[0])

    user_info['user_convHistory'] = get_convHistory_with_user_account(user_id, 'user')
    user_info['bot_convHistory'] = get_convHistory_with_user_account(user_id, 'bot')

    user_info['user_emotion'] = get_latest_emotion(user_id, 'user')
    user_info['bot_emotion'] = get_latest_emotion(user_id, 'bot')

    curs.close()
    conn.close()

    return user_info


def GetUserConvHistory(user_id=None, user_num=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    if user_id is None:
        if user_num is None:
            return "ERROR: either user_id or user_num is essential"
        else:
            user_id = get_user_id_with_user_account(user_num)

    sql = "SELECT user_id, user_num FROM USER WHERE user_id={}".format(
        user_id)
    # 	sql = "SELECT * FROM USER"

    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)

    user_info = copy.deepcopy(result[0])

    user_info['user_convHistory'] = get_convHistory_with_user_account(user_id, 'user')
    user_info['user_emotion'] = get_latest_emotion(user_id, 'user')

    curs.close()
    conn.close()

    return user_info


def GetBotConvHistory(user_id=None, user_num=None):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    if user_id is None:
        if user_num is None:
            return "ERROR: either user_id or user_account is essential"
        else:
            user_id = get_user_id_with_user_account(user_num)

    sql = "SELECT user_id, user_num FROM USER WHERE user_id={}".format(
        user_id)
    # 	sql = "SELECT * FROM USER"

    try:
        curs.execute(sql)
        result = curs.fetchall()

    except Exception as e:
        print(e)

    user_info = copy.deepcopy(result[0])

    user_info['bot_convHistory'] = get_convHistory_with_user_account(user_id, 'bot')

    user_info['bot_emotion'] = get_latest_emotion(user_id, 'bot')

    curs.close()
    conn.close()

    return user_info


def AddNewUserInKB(user_name: str) -> int:
    if user_name in ["my", "iterative"]: return 1
    print("CREATE USER: %s" % user_name)
    code = os.system("%s mkdir %s" % (DOCKER_EXEC_PREFIX, HOME_DIRECTORY + user_name))

    return code


def AddNewUser(user_name):
    conn = pymysql.connect(host=dialogDBHost, port=dialogDBPort, user=dialogDBUserName, passwd=dialogDBPassword,
                           db=dialogDBDatabase,
                           charset=dialogDBCharset)
    curs = conn.cursor()

    sql = "INSERT INTO USER(user_name) VALUES(%s)"
    try:
        curs.execute(sql, (user_name.strip()))

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
    AddNewUserInKB(user_name)
    user_info = GetUserInfo(user_id=result[0][0])
    #	return result[0][0]
    return user_info


if __name__ == "__main__":
    print('system 작동 시작')
    # access_result = UpdateUserInfo(user_id=53, user_age=10, user_birth='1994-04-28', user_hometown='busan')
    # access_result = AddUserListInfo(user_id=53, user_topic=['computer', 'food'], user_interest_celeb=['IU'])
    # access_result = DeleteUserListInfo(user_id=53, user_topic=['computer', 'apple'], user_interest_celeb=['IU'])
    # print('test : ', db_linker.GetUserInfo(user_id=55))
    # print(access_result)
    print(get_latest_emotion(91, 'system'))
