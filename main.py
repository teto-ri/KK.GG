# flask import
from flask import Flask, request, jsonify
import json
app = Flask(__name__)
import OutputFunction
import datapipe
import parser

api_key = datapipe.api_key
match_analysis_num = 3
# 서버 테스트
# https://url.com
@app.route("/")
def test():
    return "Test"

# https://url.com/processing
@app.route('/processing', methods=['POST'])
def processing():	# 함수선언
    req = request.get_json()
    utterance = req["userRequest"]["utterance"]# json파일 읽기
    
    #유저닉네임, 커맨드 반환
    user_name,request_type = OutputFunction.return_request(utterance)
    print(user_name, request_type)
    
    if request_type == "조회":
        OutputFunction.userInfo(parser.parseOPGG(user_name))
        temp = open("temp.txt","r")
        response = temp.read()
    elif request_type == "분석":
        OutputFunction.matchInfo(user_name,match_analysis_num,api_key)
        temp2 = open("temp2.txt","r")
        response = temp2.read()
    elif request_type == "invalid command":
        response = "유효하지 않은 명령어입니다"
    else:
        response = "구현중입니다"
	# 답변 설정
    res = {"version": "2.0","template": {"outputs": [{"simpleText": {"text": response}}]}}

	# 답변 발사!
    return jsonify(res)


# 메인 함수
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)