# Flagship 5차년도 SW작성 가이드

버전: 0.9
작성자: 김희성
히스토리: 2020/04/13, 초안작성

***

## 1. 개발환경

* 소프트웨어 개발 시 언어 및 프레임워크의 버전은 아래 명시된 버전을 기본으로 함

#### 목적
* 서비스 서버 환경의 업데이트에 따라 언어 및 프레임워크의 버전 가이드가 요구됨.
* 다만, 최종 모듈 소프트웨어가 Restful API 형태로로 제출하고 컨테이너 패키징하여 환경 의존성을 최소화하므로 요구된 인터페이스 요건을 충족하고 이유가 설명 가능할 경우 다른 버전을 사용할 수 있음

#### 서버환경
* OS: Ubuntu 18.04 or 16.04
* Container : Docker community 19.03, Nvidia-docker v2.*
* GPU driver : Nvidia CUDA 10.1 or 10.2

#### 권장사항
* 파이썬 : Python3.6 이상
* 프레임워크: Pytorch 1.3 이상
* Tensorflow 1.14 이상

* Python2 2020년 1월 공식 지원 종료

***

## 2. 코드스타일
* 파이썬 코드 작성 표준은 PEP8 문서를 기준으로 한다.
 
 * 표준 PEP 8 -- Style Guide for Python Code (https://www.python.org/dev/peps/pep-0008/)
 * 참조 http://google.github.io/styleguide/pyguide.html

 
***

## 3. README.md 작성양식

아래 양식 순서에 따라 작성하고 해당 없는 항목에 대해서는 해당 없음을 명시함.
향후 해당 자료로 소프트웨어 설계, 소개 문서 작성이 가능할 정도로 상세히 작성함.

***

#### (필수) Note

* 주요 알림 사항과 리비전 히스토리에 대해 공지

> e.g. (2020/04/14) 4월 마스터 버전이 업데이트 되었습니다.

***

#### (필수) System/SW Overview

* 개발목표와 최종 결과물의 동작을 설명하고, 시스템/SW 대표 그림을 첨부한다. 

> e.g. 이미지 삽입방법 예시: ![ex_screenshot](./img/screenshot.png)

***

#### (필수) How to Install

* 인스톨 방법과 커맨드를 명시한다.
* e.g. 
```(bash)
pip install -r requirements.txt -r requirements-local.txt
```

***

#### (필수) Main requirement

* 주요 라이브러리를 명시한다.

> e.g. 
> * python 3.6.2
> * tensorflow 1.14
> * keras 2.2.4

***

#### (필수) Network Architecture and features

* 대표 네트워크 아키텍처 그림을 첨부한다.
* 모델의 핵심기능을 나열한다.
* 레이어별 주요 특징을 설명한다.
* 평가방법에 대해 설명한다.

> e.g.
> * **Model:**
> * Hierarchical Recurrent Encoder-Decoder (HRED) architecture for handling deep dialog context[3].
> * Multilayer RNN with GRU cells. The first layer of the utterance-level encoder is always bidirectional. By default, CuDNNGRU implementation is used for ~25% acceleration during inference.
> * ...
> * **Word embedding layer:**
> * May be initialized using w2v model trained on your corpus.
> * Embedding layer may be either fixed or fine-tuned along with other weights of the network.
> * ...
> * **Decoding**
> * Reranking of the generated candidates is performed according to the log-likelihood or MMI-criteria. See configuration settings description for details. 
> * ...
> * **Metrics:**
> * Perplexity
> * n-gram distinct metrics adjusted to the samples size[4].
> * Ranking metrics: mean average precision and mean recall@k.
> * ...

***

#### (필수) Quick start

* 최종 결과에 대해 테스트할 수 있는 방법 및 절차에 대해 단계별로 작성한다.
* 설치부터 인풋, 모델을 통과한 출력을 기록한다. (아래는 양식에 대한 예시)
* Step0, Step1, Step2, ... 등으로 네이밍한다.

> e.g.
> * Step2. GPU Version - 호스트 머신에서 아래 명령을 실행한다. 
> ```
> python tools/test_api.py -f localhost -p 8080 -c "hi!" -c "hi, how are you?" -c "good!" -e "joy"
> ```
>
> * Step3. GPU Version - 다음과 같은 reponse를 얻는다.
> ```
> {'response': "I'm fine!"}
> ```

#### (선택) Training Data
* 트레이닝 데이터에 대한 소개

> *The model was trained on a preprocessed Twitter corpus with ~10 million dialogs (1Gb of text data).
> To clean up the corpus, we removed
> * URLs, retweets and citations;
> * mentions and hashtags that are not preceded by regular words or punctuation marks;
> * messages that contain more than 20 tokens.
>
> conversational datasets can be found here: https://www.github.io/DialogDatasets/

***

#### (선택) Training Model

* 모델을 트레이닝하는 방법에 대해
* Traing from Scratch or fine-tuning the provided trained model 중 해당 하는 것을 선택하여 기록한다.

> e.g. 
>1. Put your training text corpus to
>[`data/corpora_processed/train_processed_dialogs.txt`](data/corpora_processed/train_processed_dialogs.txt).

>1. Set up training parameters in [`test_api/config.py`](test_api/config.py).
>See [configuration settings description](#configuration-settings) for more details.

> 1. Consider running `PYTHONHASHSEED=42 python tools/prepare_index_files.py` to build the index files with tokens and
> conditions from the training corpus. Make sure to set `PYTHONHASHSEED` environment variable, otherwise you may get
> different index files for different launches of the script.
> **Warning:** this script overwrites the original tokens index files `data/tokens_index/t_idx_processed_dialogs.json` and
> `data/conditions_index/c_idx_processed_dialogs.json`.
> You should only run this script in case your corpus is large enough to contain all the words that you want your model
> to understand. Otherwise, consider fine-tuning the pre-trained model as described above. If you messed up with index
> files and want to get the default versions, delete your copies and run `python tools/fetch.py` anew.

> 1. Consider running `python tools/train_w2v.py` to build w2v embedding from the training corpus.
> **Warning:** this script overwrites the original w2v weights that are stored in `data/w2v_models`.
> You should only run this script in case your corpus is large enough to contain all the words that you want your model
> to understand. Otherwise, consider fine-tuning the pre-trained model as described above. If you messed up with w2v
> files and want to get the default version, delete your file copy and run `python tools/fetch.py` anew.

> 1. Run `python tools/train.py`.
>     1. Don't forget to set `CUDA_VISIBLE_DEVICES=<GPU_ID>` environment variable (with <GPU_ID>
>        as in output of **nvidia-smi** command) if you want to use GPU. For example `CUDA_VISIBLE_DEVICES=0 python tools/train.py`
>        will run the train process on the 0-th GPU.
>     1. Use parameter `-s` to train the model on a subset of the first N samples of your training data to speed up
> preprocessing for debugging. For example, run `python tools/train.py -s 1000` to train on the first 1000 samples.

> 1. You can also set `IS_DEV=1` to enable the "development mode". It uses a reduced number of model parameters
>    (decreased hidden layer dimensions, input and output sizes of token sequences, etc.) and performs verbose logging.
>    Refer to the bottom lines of `cakechat/config.py` for the complete list of dev params.

> Weights of the trained model are saved to `results/nn_models/`.

***

#### (선택) Validation metrics calculation

During training the following datasets are used for validations metrics calculation:

> e.g.
> * [`data/corpora_processed/val_processed_dialogs.txt`](data/corpora_processed/val_processed_dialogs.txt)(dummy example, replace with your data) – for the context-sensitive dataset
> * [`data/quality/context_free_validation_set.txt`](data/quality/context_free_validation_set.txt) – for the context-free validation dataset
> * [`data/quality/context_free_questions.txt`](data/quality/context_free_questions.txt) – is used for generating responses for logging and computing distinct-metrics
> * [`data/quality/context_free_test_set.txt`](data/quality/context_free_test_set.txt) – is used for computing metrics of the trained model, e.g. ranking metrics

> The metrics are stored to `test_api/results/tensorboard` and can be visualized using
> [Tensorboard](https://www.tensorflow.org/guide/summaries_and_tensorboard).
> If you run a docker container from the provided CPU or GPU-enabled docker image, tensorboard server should start
> automatically and serve on `http://localhost:6006`. Open this link in your browser to see the training graphs.

> If you installed the requirements manually, start tensorboard server first by running the following command from your

> test_api root directory:
> ```
> mkdir -p results/tensorboard && tensorboard --logdir=results/tensorboard 2>results/tensorboard/err.log &
> ```

> After that proceed to `http://localhost:6006`.

***

#### (필수) HTTP-server API description

* **path, parameter, response를 명시한다.**

> *  /test_api/v1/actions/get_response
> * JSON parameters are:

> |Parameter|Type|Description|
> |---|---|---|
> |context|list of strings|List of previous messages from the dialogue history (max. 3 is used)|
> |emotion|string, one of enum|One of {'neutral', 'anger', 'joy', 'fear', 'sadness'}. An emotion to condition the response on. Optional param, if not specified, 'neutral' is used|

> * Request
> ```
> POST /test_api/v1/actions/get_response
> data: {
> 'context': ['Hello', 'Hi!', 'How are you?'],
> 'emotion': 'joy'
> }
> ```

> * Response OK
> ```
> 200 OK
> {
>  'response': 'I\'m fine!'
> }
> ```

***

#### (필수) Repository overview

* 폴더 및 파일의 구조 및 역할(기능)을 설명한다.

> e.g. 
> * `test_api/dialog_model/` – contains computational graph, training procedure and other model utilities
> * `test_api/dialog_model/inference/` – algorithms for response generation
> * `test_api/dialog_model/quality/` – code for metrics calculation and logging
> * `test_api/utils/` – utilities for text processing, w2v training, etc.
> * `test_api/api/` – functions to run http server: API configuration, error handling
> * `tools/` – scripts for training, testing and evaluating your model
>     * [`tools/prepare_index_files.py`](tools/prepare_index_files.py) – Prepares index for the most commonly used tokens and conditions. Use this script before training the model from scratch on your own data.
>     * [`tools/train.py`](tools/train.py) – Trains the model on your data

***

#### (선택) configuration settings

* All the configuration parameters for the network architecture, training, predicting and logging steps are defined in
[`test_api/config.py`](test_api/config.py). Some inference parameters used in an HTTP-server are defined in
[`test_api/api/config.py`](test_api/api/config.py).

> e.g.
> * Network architecture and size
>    * `HIDDEN_LAYER_DIMENSION` is the main parameter that defines the number of hidden units in recurrent layers.
>    * `WORD_EMBEDDING_DIMENSION` and `CONDITION_EMBEDDING_DIMENSION` define the number of hidden units that each
>    token/condition are mapped into.
>
> * Decoding algorithm:
>    * `PREDICTION_MODE_FOR_TESTS` defines how the responses of the model are generated. The options are the following:
>        - **sampling** – response is sampled from output distribution token-by-token.
>        For every token the temperature transform is performed prior to sampling.

> * Note that there are other parameters that affect the response generation process.
>    See `REPETITION_PENALIZE_COEFFICIENT`, `NON_PENALIZABLE_TOKENS`, `MAX_PREDICTIONS_LENGTH`.
>
> |Key|Value|Description|
> |---|---|---|

***

## 4. API 작성

* flask API https://www.flaskapi.org/
* API Specificaion https://swagger.io/docs/specification/basic-structure/
* API 검증 : API 테스트 결과서

## 5. 단위테스트

* 5월 30일 코드 제출시 단위테스트 결과서 제출
* 단위테스트 결과 항목:
* ** API 테스트 **
* ** 컨테이너화 테스트 (도커이미지 생성파일: Dockerfile 작성, 도커이미지 빌드 결과:docker build, 도커 실행 결과:docker run 등) **

