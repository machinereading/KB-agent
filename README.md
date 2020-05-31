# Flagship 5차년도 KB-Agent Readme

버전: 0.9
작성자: 정용빈

***

#### Note

* (2020/05/30) 5월 마스터 버전이 업데이트 되었습니다.

***

#### System/SW Overview

* 대화 모듈의 대화 흐름및 대화에 필요한 다양한 정보들을 사용자별로 기록 할 수 있는 데이터베이스 및 지식베이스 구성

* 데이터베이스에 사용자별 정보 기록 및 불러오기를 할 수 있는 모듈 제공(multi-Conv.Kernel)

* 데이터베이스 및 지식베이스를 활용한 대화 모듈 제공

  * SPARQLQA(KGQA) - 지식베이스를 활용하여 사용자의 일반지식 질문에 대하여 답변
  * FrameQA - Frame parser를 이용하여 사용자와의 대화에서 빠진 정보를 파악하여 사용자에게 질문
  * Knowledge acquisition conversation - 지금 대화 주제와 관련해 지식베이스에 존재하지 않는 지식에 대해 사용자에게 질문

* KB-Agent: multi-Conv.Kernel을 이용하여 사용자 조회 및 사용자의 과거 대화내용을 활용하여 어떤 대화 모듈을 선택할것인지 결정 등을 하는 채팅 모듈

* multi-Conv.Kernel: 지식베이스 및 데이터베이스에 접근 할 수 있는 다양한 기능 제공

  

![ex_screenshot](./img/main_picture.PNG)

***

#### How to Install

* conda를 이용하여 python package를 설치한다.
```(bash)
conda env create --file conda-environment.yaml (./KB_Agent/)
```

***

#### Main requirement

> * python 3.7.6
> * pymysql 0.9.3
> * flask

***

#### Network Architecture and features

* SPARQL QA에 대해 개발 예정

***

#### Quick start

> * Step0. Conda를 actication 한 뒤 DB_linker 및 KB_Agent에 있는 app.py를 각각 실행하여 API를 open한다.
> ```
> conda activate {ENV_NAME}
> python3 app.py (..../DB_linker/app.py)
> python3 app.py (..../KB_Agent/app.py)
> ```
>
> * Step1. Postman과 같은 tool을 이용하여 각 API를 호출한다.
> ```
> /respond_to_user_utterance
> {
> 	"user_id": "59",
> 	"user_name": null,
> 	"user_utterance": "나는 독일에서 지냈어",
> 	"session_id": null,
> 	"modules": ["sparql_qa", "frame_qa", "kowledge_acquire"]
> }
> ```
>
> * Step2. response된 결과를 확인한다.
>
> ```
> {
>     "answer": "누구와 지냈나요?"
> }
> ```

***

#### HTTP-server API description

* **DB_Linker(multi-Conv.Kernel)**

> *  /AddUserListInfo
> * JSON parameters are:

> |Parameter|Type|Description|
> |---|---|---|
> |*user_id|num|id of user in table USER (key) to refer|
> |user_interest_celeb|list of strings|celebs to add in user information|
> |user_interest_hobby|list of strings|hobbies to add in user information|
> |user_interest_location|list of strings|locations to add in user information|
> |user_topic|list of strings|topics to add in user information|

> * Request
> ```
> POST /AddUserListInfo
> data: {
> 	"user_id":53,
> 	"user_interest_celeb":["IU"],
> 	"user_interest_hobby":["soccer", "baseball"],
> 	"user_interest_location":["Jinju", "Roma"],
> 	"user_topic":["computer", "NLP"]
> }
> ```

> * Response OK (변경후 user의 정보를 반환)
> ```
> 200 OK
> {
>     "USER_INTEREST_CELEB": [
>         "IU"
>     ],
>     "USER_INTEREST_HOBBY": [
>         "soccer",
>         "baseball"
>     ],
>     "USER_INTEREST_LOCATION": [
>         "busan",
>         "seoul",
>         "Jinju",
>         "Roma"
>     ],
>     "USER_TOPIC": [
>         "food",
>         "computer",
>         "NLP"
>     ],
>     "user_age": 10,
>     "user_birth": "Thu, 28 Apr 1994 00:00:00 GMT",
>     "user_current_city": null,
>     "user_gender": null,
>     "user_hometown": "busan",
>     "user_id": 53,
>     "user_job_title": null,
>     "user_name": "test",
>     "user_professional": null
> }
> ```

> 
>
> *  /DeleteUserListInfo
> *  JSON parameters are:

> | Parameter              | Type            | Description                             |
> | ---------------------- | --------------- | --------------------------------------- |
> | *user_id               | num             | id of user in table USER (key) to refer |
> | user_interest_celeb    | list of strings | celebs to delete in user information    |
> | user_interest_hobby    | list of strings | hobbies to delete in user information   |
> | user_interest_location | list of strings | locations to delete in user information |
> | user_topic             | list of strings | topics to delete in user information    |

> * Request
>
> ```
> POST /DeleteUserListInfo
> data: {
> 	"user_id":53,
> 	"user_interest_celeb":["IU"],
> 	"user_interest_hobby":["soccer", "baseball"],
> 	"user_interest_location":["Jinju", "Roma"],
> 	"user_topic":["computer", "NLP"]
> }
> ```

> * Response OK (변경후 user의 정보를 반환)
>
> ```
> 200 OK
> {
>     "USER_INTEREST_CELEB": [],
>     "USER_INTEREST_HOBBY": [],
>     "USER_INTEREST_LOCATION": [
>         "busan",
>         "seoul"
>     ],
>     "USER_TOPIC": [
>         "food"
>     ],
>     "user_age": 10,
>     "user_birth": "Thu, 28 Apr 1994 00:00:00 GMT",
>     "user_current_city": null,
>     "user_gender": null,
>     "user_hometown": "busan",
>     "user_id": 53,
>     "user_job_title": null,
>     "user_name": "test",
>     "user_professional": null
> }
> ```

> 
>
> *  /UpdateUserInfo
> *  JSON parameters are: 
> *  (user_id or user_name 중 하나는 필수, 변경하고싶지 않은 칼럼은 null값 입력)

> | Parameter         | Type                | Description                             |
> | ----------------- | ------------------- | --------------------------------------- |
> | *user_id          | num                 | id of user in table USER (key) to refer |
> | user_name         | string              | user name                               |
> | user_age          | num                 | user age                                |
> | user_birth        | datetime            | user birth date                         |
> | user_gender       | string, one of enum | one of ["M","F"], user gender           |
> | user_current_city | string              | user current city                       |
> | user_hometown     | string              | user hometown                           |
> | user_professional | string              | user professional                       |
> | user_job_title    | string              | user job name                           |

> * Request
>
> ```
> POST /UpdateUserInfo
> data: {
> 	"user_id":53,
> 	"user_name":null,
> 	"user_age":null,
> 	"user_birth":"1994-03-18",
> 	"user_gender":"M",
> 	"user_current_city":null,
> 	"user_hometown":"Jinju",
> 	"user_professional":"NLP",
> 	"user_job_title":"Student"
> }
> ```

> * Response OK (변경후 user의 정보를 반환)
>
> ```
> 200 OK
> {
>     "USER_INTEREST_CELEB": [
>         "IU"
>     ],
>     "USER_INTEREST_HOBBY": [
>         "soccer",
>         "baseball"
>     ],
>     "USER_INTEREST_LOCATION": [
>         "busan",
>         "seoul",
>         "Jinju",
>         "Roma"
>     ],
>     "USER_TOPIC": [
>         "food",
>         "computer",
>         "NLP"
>     ],
>     "user_age": 10,
>     "user_birth": "Fri, 18 Mar 1994 00:00:00 GMT",
>     "user_current_city": null,
>     "user_gender": "M",
>     "user_hometown": "Jinju",
>     "user_id": 53,
>     "user_job_title": "Student",
>     "user_name": "test",
>     "user_professional": "NLP"
> }
> ```

> 
>
> *  /LookUpUsers
> *  JSON parameters are:

> | Parameter | Type | Description |
> | --------- | ---- | ----------- |
> | None      |      |             |

> * Request (POST, GET)
>
> ```
> POST /LookUpUsers
> data: 
> ```

> * Response OK (user 목록 반환)
>
> ```
> 200 OK
> {
>     "user_list": [
>         {
>             "user_age": null,
>             "user_birth": null,
>             "user_current_city": null,
>             "user_gender": null,
>             "user_hometown": null,
>             "user_id": 42,
>             "user_job_title": null,
>             "user_name": "jyb",
>             "user_professional": null
>         },
>         {
>             "user_age": null,
>             "user_birth": null,
>             "user_current_city": null,
>             "user_gender": null,
>             "user_hometown": null,
>             "user_id": 43,
>             "user_job_title": null,
>             "user_name": "ybjeong",
>             "user_professional": null
>         },
>         {
>             "user_age": null,
>             "user_birth": null,
>             "user_current_city": null,
>             "user_gender": null,
>             "user_hometown": null,
>             "user_id": 46,
>             "user_job_title": null,
>             "user_name": "apiTestUser",
>             "user_professional": null
>         },
>         {
>             "user_age": null,
>             "user_birth": null,
>             "user_current_city": null,
>             "user_gender": null,
>             "user_hometown": null,
>             "user_id": 49,
>             "user_job_title": null,
>             "user_name": "apiTestUser2",
>             "user_professional": null
>         },
>         {
>             "user_age": null,
>             "user_birth": null,
>             "user_current_city": null,
>             "user_gender": null,
>             "user_hometown": null,
>             "user_id": 51,
>             "user_job_title": null,
>             "user_name": "apiTestUser3",
>             "user_professional": null
>         },
>         {
>             "user_age": null,
>             "user_birth": null,
>             "user_current_city": null,
>             "user_gender": null,
>             "user_hometown": null,
>             "user_id": 52,
>             "user_job_title": null,
>             "user_name": "apiTestUser4",
>             "user_professional": null
>         },
>         {
>             "user_age": 10,
>             "user_birth": "Fri, 18 Mar 1994 00:00:00 GMT",
>             "user_current_city": null,
>             "user_gender": "M",
>             "user_hometown": "Jinju",
>             "user_id": 53,
>             "user_job_title": "Student",
>             "user_name": "test",
>             "user_professional": "NLP"
>         },
>         {
>             "user_age": null,
>             "user_birth": null,
>             "user_current_city": null,
>             "user_gender": null,
>             "user_hometown": null,
>             "user_id": 54,
>             "user_job_title": null,
>             "user_name": "test1",
>             "user_professional": null
>         },
>         {
>             "user_age": null,
>             "user_birth": null,
>             "user_current_city": null,
>             "user_gender": null,
>             "user_hometown": null,
>             "user_id": 55,
>             "user_job_title": null,
>             "user_name": "test2",
>             "user_professional": null
>         }
>     ]
> }
> ```

> 
>
> *  /GetUserInfo
> *  JSON parameters are:
> *  (user_id or user_name 중 하나는 필수)

> | Parameter | Type   | Description                             |
> | --------- | ------ | --------------------------------------- |
> | user_id   | num    | id of user in table USER (key) to refer |
> | user_name | string | user name                               |

> * Request (POST, GET)
>
> ```
> POST /GetUserInfo
> data: {
> 	"user_id":53,
> 	"user_name":null
> }
> ```

> * Response OK (요청한 user의 정보 반환)
>
> ```
> 200 OK
> {
>     "USER_INTEREST_CELEB": [
>         "IU"
>     ],
>     "USER_INTEREST_HOBBY": [
>         "soccer",
>         "baseball"
>     ],
>     "USER_INTEREST_LOCATION": [
>         "busan",
>         "seoul",
>         "Jinju",
>         "Roma"
>     ],
>     "USER_TOPIC": [
>         "food",
>         "computer",
>         "NLP"
>     ],
>     "user_age": 10,
>     "user_birth": "Fri, 18 Mar 1994 00:00:00 GMT",
>     "user_current_city": null,
>     "user_gender": "M",
>     "user_hometown": "Jinju",
>     "user_id": 53,
>     "user_job_title": "Student",
>     "user_name": "test",
>     "user_professional": "NLP"
> }
> ```

> 
>
> *  /AddNewUser
> *  JSON parameters are:

> | Parameter | Type   | Description      |
> | --------- | ------ | ---------------- |
> | *name     | string | user name to add |

> * Request
>
> ```
> POST /AddNewUser
> data: {
> 	"user_name":"new_user2"
> }
> ```

> * Response OK (추가된 user의 정보를 반환)
>
> ```
> 200 OK
> {
>     "USER_INTEREST_CELEB": [],
>     "USER_INTEREST_HOBBY": [],
>     "USER_INTEREST_LOCATION": [],
>     "USER_TOPIC": [],
>     "user_age": null,
>     "user_birth": null,
>     "user_current_city": null,
>     "user_gender": null,
>     "user_hometown": null,
>     "user_id": 58,
>     "user_job_title": null,
>     "user_name": "new_user2",
>     "user_professional": null
> }
> ```

> 
>
> *  /GetUtterances
> *  JSON parameters are:

> | Parameter  | Type | Description                                                  |
> | ---------- | ---- | ------------------------------------------------------------ |
> | *user_id   | num  | id of user in table USER (key) to refer                      |
> | session_id | num  | target session id to get utterances (if session_id is null, all utterances of user are selected) |

> * Request (session_id를 입력하면 해당 session의 대화만 불러오지만 null을 입력하면 해당 유저의 모든 대화 기록을 가져온다.)
>
> ```
> POST /GetUtterances
> data: {
> 	"user_id":55,
> 	"session_id":330
> }
> ```

> * Response OK (대화 기록 반환)
>
> ```
> 200 OK
> {
>     "utterances": [
>         {
>             "date_time": "Thu, 28 May 2020 18:32:22 GMT",
>             "emotion": null,
>             "feedback": null,
>             "intent_emp": null,
>             "intent_req": null,
>             "mission_id": null,
>             "model_id": null,
>             "query_id": 1,
>             "session_id": 330,
>             "speaker": "user",
>             "turn_id": 1,
>             "u.session_id": 330,
>             "user_id": 55,
>             "utterance": "user test2의 말입니다.",
>             "utterance_id": 14
>         },
>         {
>             "date_time": "Thu, 28 May 2020 18:32:22 GMT",
>             "emotion": null,
>             "feedback": null,
>             "intent_emp": null,
>             "intent_req": null,
>             "mission_id": null,
>             "model_id": null,
>             "query_id": 2,
>             "session_id": 330,
>             "speaker": "system",
>             "turn_id": 1,
>             "u.session_id": 330,
>             "user_id": 55,
>             "utterance": "아무런 모듈에 속하지 않습니다.",
>             "utterance_id": 15
>         }
>     ]
> }
> ```

> 
>
> *  /SaveUtterance
> *  JSON parameters are: 
> *  (session_id가 null이라면 가장 최근 session에 추가)

> | Parameter  | Type                | Description                                        |
> | ---------- | ------------------- | -------------------------------------------------- |
> | *user_id   | num                 | id of user in table USER (key) to refer            |
> | *utterance | string              | sentenct to save                                   |
> | session_id | num                 | session_id to add                                  |
> | speaker    | string, one of enum | one of ["user","system"], it means who's utterance |
> | emotion    | string              | emotion of speaker for this sentence               |
> | intent_req | string              | intent req                                         |
> | intent_emp | string              | intent emp                                         |

> * Request
>
> ```
> POST /SaveUtterance
> data: {
> 	"user_id":55,
> 	"utterance":"save_new_utterance",
> 	"session_id":null,
> 	"speaker":"user",
> 	"emotion":"pleasure",
> 	"intent_req":"test_req",
> 	"intent_emp":"test_emp"
> }
> ```

> * Response OK (저장된 utterance의 정보 반환)
>
> ```
> 200 OK
> {
>     "date_time": "Sat, 30 May 2020 03:38:34 GMT",
>     "emotion": "pleasure",
>     "intent_emp": "test_emp",
>     "intent_req": "test_req",
>     "query_id": 5,
>     "session_id": 330,
>     "speaker": "user",
>     "turn_id": 4,
>     "utterance": "save_new_utterance",
>     "utterance_id": 18
> }
> ```

> 
>
> *  /LookUpSessionOfUser
> *  JSON parameters are:
> *  (user_id or user_name 중 하나는 필수)

> | Parameter | Type   | Description                             |
> | --------- | ------ | --------------------------------------- |
> | user_id   | num    | id of user in table USER (key) to refer |
> | user_name | string | name of user                            |

> * Request
>
> ```
> POST /LookUpSessionOfUser
> data: {
> 	"user_id":55,
> 	"user_name":null
> }
> ```

> * Response OK (해당 user의 모든 session 정보 반환)
>
> ```
> 200 OK
> {
>     "sessions": [
>         {
>             "feedback": null,
>             "mission_id": null,
>             "model_id": null,
>             "session_id": 323,
>             "user_id": 55
>         },
>         {
>             "feedback": null,
>             "mission_id": null,
>             "model_id": null,
>             "session_id": 324,
>             "user_id": 55
>         },
>         {
>             "feedback": null,
>             "mission_id": null,
>             "model_id": null,
>             "session_id": 325,
>             "user_id": 55
>         },
>         {
>             "feedback": null,
>             "mission_id": 1,
>             "model_id": null,
>             "session_id": 326,
>             "user_id": 55
>         },
>         {
>             "feedback": null,
>             "mission_id": null,
>             "model_id": null,
>             "session_id": 327,
>             "user_id": 55
>         },
>         {
>             "feedback": null,
>             "mission_id": null,
>             "model_id": null,
>             "session_id": 328,
>             "user_id": 55
>         },
>         {
>             "feedback": null,
>             "mission_id": null,
>             "model_id": null,
>             "session_id": 329,
>             "user_id": 55
>         },
>         {
>             "feedback": null,
>             "mission_id": null,
>             "model_id": null,
>             "session_id": 330,
>             "user_id": 55
>         }
>     ]
> }
> ```

> 
>
> *  /GetSessionInfo
> *  JSON parameters are:

> | Parameter   | Type | Description                                  |
> | ----------- | ---- | -------------------------------------------- |
> | *session_id | num  | id of session in table SESSION(key) to refer |

> * Request
>
> ```
> POST /GetSessionInfo
> data: {
> 	"session_id":323
> }
> ```

> * Response OK (변경후 user의 정보를 반환)
>
> ```
> 200 OK
> {
>     "feedback": null,
>     "mission_id": null,
>     "model_id": null,
>     "session_id": 323,
>     "user_id": 55
> }
> ```

> 
>
> *  /AddNewSession
> *  JSON parameters are:

> | Parameter  | Type   | Description                             |
> | ---------- | ------ | --------------------------------------- |
> | *user_id   | num    | id of user in table USER (key) to refer |
> | model_id   | string | model id                                |
> | mission_id | string | mission id                              |
> | feedback   | string | feedback for session                    |

> * Request
>
> ```
> POST /AddNewSession
> data: {
> 	"user_id":55,
> 	"model_id":1,
> 	"mission_id":1,
> 	"feedback":1
> }
> ```

> * Response OK (추가된 session 정보 반환)
>
> ```
> 200 OK
> {
>     "feedback": 1,
>     "mission_id": 1,
>     "model_id": 1,
>     "session_id": 331,
>     "user_id": 55
> }
> ```







* **KB_Agent**

> *  /user_access
> * JSON parameters are:

> (user_id or user_name 중 하나는 입력하여야함)
> 
> |Parameter|Type|Description|
> |---|---|---|
> |user_id|num|user_id for access|
> |user_name|string|name of user for access|

> * Request
> ```
> POST /user_access
> {
> 	"user_id":null,
> 	"user_name": "ybjeong"
> }
> ```

> * Response OK (해당 user의 정보와 새로 추가한 session의 정보를 반환, user가 신규 유저라면 새로 추가)
> ```
> 200 OK
> {
>        "session_info": {
>            "feedback": null,
>            "mission_id": null,
>            "model_id": null,
>            "session_id": 332,
>            "user_id": 43
>        },
>        "user_info": {
>            "user_age": null,
>            "user_birth": null,
>            "user_current_city": null,
>            "user_gender": null,
>            "user_hometown": null,
>            "user_id": 43,
>            "user_job_title": null,
>            "user_name": "ybjeong",
>            "user_professional": null
>        }
>    }
>    ```


> 
>
> *  /respond_to_user_utterance
> * JSON parameters are:

> (user_id or user_name 중 하나는 입력하여야함)
>
> |Parameter|Type|Description|
> |---|---|---|
> |user_id|num|user_id for access|
> |user_name|string|name of user for access|
> |*user_utterance|string|utterance of user|
> |session_id|num|session id in conversation (if session_id is null, latest session will be selected automatically)|
> |modules|list of string, one or many of enum|One of many of {'sparql_ql', 'frame_qa', 'knowledge_acquire'}. what modules in kb_agent are used for generating answer.|

> * Request
> ```
> POST /respond_to_user_utterance
> {
> 	"user_id": "59",
> 	"user_name": null,
> 	"user_utterance": "기분이 어떠세요.",
> 	"session_id": null,
> 	"modules": ["sparql_qa", "frame_qa", "knowledge_acquire"]
> }
> ```

> * Response OK
> ```
> 200 OK
> {
>        "answer": "어떤 응답을 해야할지 모르겠어요."
>    }
>    ```



***

#### Repository overview

* 폴더 및 파일의 구조 및 역할(기능)을 설명한다.

> * `DB_linker/` – multi-Conv.Kernel module directory
>     * [`DB_linker/app.py`](DB_linker/app.py) – run API of DB_linker(multi-Conv.Kernel)
> * `KB_Agent/` – KB_Agent module directory
>     * [`KB_Agent/app.py`](KB_Agent/app.py) – run API of KB_Agent
> * `KB_Agent/data/` – static data for modules in KB_Agent
> * `KB_Agent/modules/` – modules in KB_Agen
> * `KB_Agent/modules/tf_models` – pre-trained tf_models

***

#### configuration settings

* 미적용 - 추후 적용 예정
