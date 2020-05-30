# KK.GG
KK.GG is KakaoTalk league of legend support chatbot, It supports user information such as tier ranking, most champ, match analysis and future winning rate prediction service when input user name.

KK.GG는 카카오톡 롤 서포트 챗봇 서비스로, 최신 패치노트와 Riot API를 이용해 유저 이름을 입력하면 랭킹, 티어, 모스트 챔피언 등의 유저 정보, 개인화 맞춤 전적 분석, 승률 예측 기능을 제공합니다.

카카오톡 채널 링크 : <http://pf.kakao.com/_yxhfxmxb> 

서버 상태는 <https://test0712.run.goorm.io/> 에 접속하여, connection refused가 뜨면 서버가 열려있지 않고, server online이 뜨면 서버가 가동중입니다.

![](https://i.imgur.com/CE4HnPS.png)

## Dependency Manage / 의존성 관리

Sever : Ubuntu 18.04 LTS ,Python 3.7.4, Flask 1.1.1

Sever specification : 2 Core CPU, 1GB ram, 10GB hdd
* pip install pandas
* pip install numpy
* pip install BeautifulSoup
* pip install xgboost
* pip install pytz
* pip install scikit-learn=0.21.2.post1 (use for scaler joblib file)

현재 해당 챗봇은 아마존 AWS EC2, t2 micro 서비스로 배포되어있습니다.

## 소스코드 설명

1. main.py : Flask 기반의 API 웹서버 실행파일 입니다. 프론트단에서 들어온 요청을 처리하고, 해당하는 답변을 반환합니다.
2. OutputFunction.py : 유저에게 제공할 답변을 구성하는 프린팅 함수들로 이루어져 있습니다.
3. datapipe.py : Riot API를 이용하는 핵심 파일로, 유저 이름을 받으면 경기 기록과, 유저 기록 등을 반환하는 함수로 이루어져 있습니다.
4. parser.py : 패치내역과 필요한 정보들을 외부에서 가져오는 크롤링 함수들로 이루어져 있습니다.
5. rating.py : 유저의 개인기록을 랭킹화하고, 통계로 상위 퍼센트를 계산하는 함수들로 이루어져 있습니다.

이외 파일은 유저 정보 로깅과, 데이터 기록용 파일들입니다.

Log 파일 내의 로그들은 개발시에 테스트된 로그들로, 실제 사용자 로그들은 안전하게 보관됩니다.

해당 파일들은 디버깅용 파일로, 실제 서비스중인 코드와는 약간 차이가 있습니다.
