# flask import
from flask import Flask, request, jsonify
import json
app = Flask(__name__)
import OutputFunction
import datapipe
import parser
import user_logger

api_key = datapipe.api_key

# 서버 테스트
# https://url.com
@app.route("/")
def test():
    return "Server Online"

# https://url.com/processing
@app.route('/processing', methods=['POST'])
def processing():	# 함수선언
    user_log = open("log/userlog.txt","a")
    req = request.get_json()
    utterance = req["userRequest"]["utterance"]# json파일 읽기
    
    #유저닉네임, 커맨드 반환
    user_name,request_type = OutputFunction.return_request(utterance)
    print(user_name, request_type)
    
    #커맨드별 함수 실행
    if request_type == "조회":
        OutputFunction.userInfo(parser.parseOPGG(user_name))
        temp = open("data/usertemp.txt","r")
        response = temp.read()
        user_logger.user_log(user_name,request_type,user_log)
    elif request_type == "분석":
        OutputFunction.matchInfo(user_name,1,api_key)
        temp2 = open("data/matchtemp.txt","r")
        response = temp2.read()
        user_logger.user_log(user_name,request_type,user_log)
    elif request_type == "분석1":
        OutputFunction.matchInfo(user_name,2,api_key)
        temp2 = open("data/matchtemp.txt","r")
        response = temp2.read()
        user_logger.user_log(user_name,request_type,user_log)
    elif request_type == "분석2":
        OutputFunction.matchInfo(user_name,3,api_key)
        temp2 = open("data/matchtemp.txt","r")
        response = temp2.read()
        user_logger.user_log(user_name,request_type,user_log)
    elif request_type == "분석3":
        OutputFunction.matchInfo(user_name,4,api_key)
        temp2 = open("data/matchtemp.txt","r")
        response = temp2.read()
        user_logger.user_log(user_name,request_type,user_log)
    elif request_type == "예측":
        OutputFunction.predictInfo(user_name,20,api_key)
        temp3 = open("data/predictemp.txt","r")
        response = temp3.read()
        user_logger.user_log(user_name,request_type,user_log)
    elif request_type == "invalid command":
        response = "유효하지 않은 명령어입니다, 올바른 명령어를 입력해주세요."
        user_logger.user_log(user_name,request_type,user_log)
    else:
        response = "구현중입니다"
        
	# 답변 설정
    res = {"version": "2.0","template": {"outputs": [{"simpleText": {"text": response}}]}}
	# 답변 발사!
    return jsonify(res)


# 메인 함수
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)