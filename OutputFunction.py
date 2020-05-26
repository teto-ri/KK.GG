import datapipe
import parser
from xgboost import XGBClassifier
from sklearn.externals import joblib
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import warnings
import rating
import gc
from datetime import datetime
from pytz import timezone
warnings.filterwarnings("ignore")

api_key = datapipe.api_key

#KDA계산용
def KDA(row):
    if row["player_death"] == 0:
        return "Perfect"
    return (row["player_kill"]+row["player_assist"])/row["player_death"]

#유저 정보 프린팅 함수
def userInfo(Container):
    temp = open("data/usertemp.txt","w")
    rankCase = ['솔로', '자유']
    if (Container['SummonerName'] != '')&(Container['Ranking'] != ''):
        print("🔍『"+ Container['SummonerName'] + "』님의 정보입니다.\n==========================\n🎖 " + Container["Ranking"]+"\n🎮 소환사 레벨 : "+Container["Level"],file=temp)
    else:
        if (Container['SummonerName'] == ''):
            return print("※ 등록된 소환사가 없습니다. 다시 입력해 주세요",file=temp)
        else:
            return print("※ " + Container['SummonerName'] + "님은 Unranked입니다.\n(유저 정보 조회는 티어 배치를 받은 다음 가능합니다.)",file=temp)
    for i in range(len(Container['Tier'])):
        if Container['SummonerName'] != '':
            print("==========================",file=temp)
            if len(Container['Tier']):
                print("▶ " + Container['SummonerName'] + "님의 " + rankCase[i] + "랭크 정보입니다.",file=temp)
                print("==========================",file=temp)
                print("▪ 티어: " + Container['Tier'][i],file=temp)
                print("▪ LP: " + Container['LP'][i],file=temp)
                print("▪ 승/패: " + Container['Wins'][i] + "/" + Container['Losses'][i],file=temp)
                print("▪ 승률: " + Container['Ratio'][i],file=temp)
            else:
                print(Container['SummonerName'] + "님은 Unranked입니다.",file=temp)
                print("==========================",file=temp)
                
    #모스트 챔피언
    if (Container['SummonerName'] != '')&(Container['Ranking'] != ''):
        print("==========================",file=temp)
        print("🔥 "+Container['SummonerName'] + "님의 모스트 챔피언 정보입니다.",file=temp)
        print("==========================",file=temp)
        for i in range(len(Container["Most"])):
            print(str(i+1) +"순위: " + str(Container["Most"][i]).strip() + " (KDA: " + Container["MostKDA"][i] +")",file=temp)
        return print("==========================",file=temp)

    
#경기 분석 프린팅 함수
def matchInfo(name,match_analysis_num,api_key):
    temp2 = open("data/matchtemp.txt","w")
    match_df,player_stat,minute,win_lable = datapipe.collect_predict_data_by_name(name,match_analysis_num,api_key)
    del [[match_df]]
    gc.collect()
    if(win_lable[0]==-1):
        return print("※ 등록된 소환사가 없습니다. 다시 입력해 주세요.",file=temp2)
    elif(win_lable[0]==-404):
        return print("※ 죄송합니다. 현재 라이엇 API 서버가 점검중입니다.",file=temp2)
    else:
        player_stat = rating.player_rating(player_stat,minute)
        player_stat["KDA"] = player_stat.apply(KDA,axis=1)
        champ_kor = pd.read_csv("data/champ_id.csv")
        champ_kor.columns = ["player_champ","name"]
        player_stat = pd.merge(player_stat,champ_kor,how="left",on="player_champ")
        
        #게임 정보 출력
        i = match_analysis_num-1
        if i==0:
            print("📊『"+name+ "』님의 솔로/자유/일반 최근 게임 분석결과입니다.",file=temp2)
        else:
            print("📊『"+name+ "』님의 최근 게임으로부터 "+str(i)+"번째 이전 게임 분석결과입니다.",file=temp2)
        print("==========================",file=temp2)
        if list(win_lable)[i]==1:
            print("📘《승리》 / 🕔진행시간: " + str(round(list(minute)[i],1)) + "분\n",file=temp2)
        else:
            print("📕《패배》 / 🕔진행시간:" + str(round(list(minute)[i],1)) + "분\n",file=temp2)

        print("▪ 챔피언: " + str(player_stat.iat[i,27]) +" / "+str(player_stat.iat[i,6])+"레벨",file=temp2)
        if player_stat.iat[i,26]=="Perfect":
            print("▪ K/D/A : " + str(player_stat.iat[i,1])+"/"+str(player_stat.iat[i,2])+"/"+str(player_stat.iat[i,3])+" (Perfect)",file=temp2)
        else:
            print("▪ K/D/A : " + str(player_stat.iat[i,1])+"/"+str(player_stat.iat[i,2])+"/"+str(player_stat.iat[i,3])+" ("+str(round(player_stat.iat[i,26],2))+":1)",file=temp2)
        print("▪ 가한 피해량/받은 피해량: \n" + str(player_stat.iat[i,4]) + " / " + str(player_stat.iat[i,5]),file=temp2)
        print("▪ 골드 및 CS: " + str(player_stat.iat[i,8]) + "골드 (cs : "+str(player_stat.iat[i,7])+")",file=temp2)
        print("▪ 시야점수/타워파괴: " + str(player_stat.iat[i,9]) + "점 / " + str(player_stat.iat[i,10]) + "개 부쉈음.",file=temp2)
        
        #게임 분석 및 평가
        print("\n####### 분석 레포트 #######",file=temp2)
        print("\n⚔ [팀 기여도] - (개인)/(팀 총합)\n\t-킬 "+str(round(player_stat.iat[i,11],1))+"% / 100%\n\t-데스 "+str(round(player_stat.iat[i,12],1))+"% / 100%",file=temp2)
        print("\t-딜량 "+str(round(player_stat.iat[i,13],1))+"% / 100%\n\t-시야점수 "+str(round(player_stat.iat[i,14],1))+"% / 100%\n\t-타워 킬 "+str(round(player_stat.iat[i,15],1))+"% / 100%",file=temp2)
        print("\n🏹 [스탯 평가]\n\t-킬량 "+str(player_stat.iat[i,21])+" (상위 "+str(round(player_stat.iat[i,16],1))+"%)\n\t-데스량 "+str(player_stat.iat[i,22])+" (상위 "+str(round(player_stat.iat[i,17],1))+"%)",file=temp2)
        print("\t-딜량 "+str(player_stat.iat[i,23])+" (상위 "+str(round(player_stat.iat[i,18],1))+"%)\n\t-시야점수 "+str(player_stat.iat[i,25])+"(상위 "+str(round(player_stat.iat[i,20],1))+"%)\n\t-골드량 "+str(player_stat.iat[i,24])+" (상위 "+str(round(player_stat.iat[i,19],1))+"%)",file=temp2)
        
        #게임 피드백
        print("\n📝 [게임 피드백]",file=temp2)
        print("안녕하세요? KK.GG 피드백 서비스입니다.\n"+name+"님은 "+str(round(list(minute)[i],1))+"분대 게임 플레이를 하셨군요?",file=temp2)
        if (list(minute)[i]<15):
            print(str(round(list(minute)[i],1))+"분대 게임은 포탑을 누가 먼저 부수는 가에 따라 중요해요!, 천상계 게임 분석 결과, "+str(round(list(minute)[i],1))+"분 이내에 포탑을 먼저 부수거나 억제기를 먼저 부쉈을 경우 90% 이상 확률로 승리했답니다.",file=temp2)
            print("또한 포탑을 2개 이상 연속으로 부쉈을 경우는 상대팀 사기가 크게 저하되서 거의 100% 확률로 승리했습니다.",file=temp2)
            print("만약 소환사님이 포탑을 부술 자신이 없다면, 로밍을 통해 다른 라인의 포탑을 먼저 부숴뜨리는 것을 추천해드려요.",file=temp2)
            print("\n💻 ["+str(round(list(minute)[i],1))+"분대 통계상 이긴 팀의 1인분 기준]",file=temp2)
            print("킬 : 2.9, 데스 : 0.78\n골드 : 5391.9, 딜량 : 4297.8\nCC기 사용시간 : 85.5초, 시야점수 : 7.3",file=temp2)
        elif (list(minute)[i]<20):
            print(str(round(list(minute)[i],1))+"분대 게임은 포탑,용,죽은 횟수가 중요해요!, 천상계 게임 분석 결과, "+str(round(list(minute)[i],1))+"분 이내에 포탑을 먼저 부수거나 용을 2번 처치할 경우 90% 이상 확률로 승리했답니다.",file=temp2)
            print("또한 죽은 횟수가 0이라면 승률이 97% 이상으로 집계되었습니다.",file=temp2)
            print("소환사님이 용 싸움, 죽지 않는 것에 신경쓰면서 플레이하면 승률이 올라갈거에요.",file=temp2)
            print("\n💻 ["+str(round(list(minute)[i],1))+"분대 통계상 이긴 팀의 1인분 기준]",file=temp2)
            print("킬 : 4.2, 데스 : 1.6\n골드 : 7169.0, 딜량 : 7733.9\nCC기 사용시간 : 122.2초, 시야점수 : 15.0",file=temp2)
        elif (list(minute)[i]<25):
            print(str(round(list(minute)[i],1))+"분대 게임은 억제기,전령,용이 중요해요!, 천상계 게임 분석 결과, "+str(round(list(minute)[i],1))+"분 이내에 억제기를 먼저 부수거나 전령을 2번 처치할 경우 80% 이상 확률로 승리했답니다.",file=temp2)
            print("만약 바론을 처치한다면 승률이 97% 이상으로 집계되었습니다.",file=temp2)
            print("소환사님이 분석을 보았다면 감이 오셨겠지만, 이 시간대 게임은 오브젝트가 중요해지는 시점이에요.\n라인전에 매진하지 말고, 팀에 합류하여 바위게, 용 중심의 운영을 펼쳐보세요!",file=temp2)
            print("\n💻 ["+str(round(list(minute)[i],1))+"분대 통계상 이긴 팀의 1인분 기준]",file=temp2)
            print("킬 : 5.4, 데스 : 2.7\n골드 : 9411.9, 딜량 : 12039.7\nCC기 사용시간 : 162.0초, 시야점수 : 24.2",file=temp2)
        elif (list(minute)[i]<30):
            print(str(round(list(minute)[i],1))+"분대 게임부터는 이제 개인으로는 승리에 영향이 적어집니다. 천상계 게임 분석 결과, "+str(round(list(minute)[i],1))+"CC기 사용시간은 거의 영향이 없으며, 딜량도 크게 중요하지 않습니다.",file=temp2)
            print("놀라운 점은, 다른 최초 관련 지표들은 승리에 미치는 영향이 줄어들었지만, 최초 억제기 파괴는 승률이 80%을 유지합니다.",file=temp2)
            print("억제기를 부수는 쪽으로 운영하되, 용을 꾸준히 챙기고 죽음 횟수를 4 이하로 유지하세요.",file=temp2)
            print("\n💻 ["+str(round(list(minute)[i],1))+"분대 통계상 이긴 팀의 1인분 기준]",file=temp2)
            print("킬 : 6.3, 데스 : 3.9\n골드 : 11342.2, 딜량 : 16406.7\nCC기 사용시간 : 196.8초, 시야점수 : 32.5",file=temp2)
        elif (list(minute)[i]<35):
            print(str(round(list(minute)[i],1))+"분대 게임은 혼자서는 승리에 영향을 줄 수 없고, 골드를 많이 쌓는게 중요합니다. 천상계 게임 분석 결과, "+str(round(list(minute)[i],1))+"억제기를 2개 이상 파괴하거나 용을 4번 처치하면 승률이 높다고 판단됩니다",file=temp2)
            print("만약, 바론을 두번 이상 처치할 경우는 굉장히 승률이 높아집니다.",file=temp2)
            print("따라서 이 시간대 게임은 전반적인 오브젝트 운영을 실시하며, 골드를 차곡차곡 쌓아나가세요. 준비된 팀은 한타를 이기고 게임을 끝냅니다.",file=temp2)
            print("\n💻 ["+str(round(list(minute)[i],1))+"분대 통계상 이긴 팀의 1인분 기준]",file=temp2)
            print("킬 : 6.9, 데스 : 5.1\n골드 : 13020.3, 딜량 : 20563.9\nCC기 사용시간 : 232.9초, 시야점수 : 39.9",file=temp2)
        else:
            print(str(round(list(minute)[i],1))+"분대 게임은 실력보다는 운이 좀 더 크게 작용하는 시간대로, 후반대 게임입니다. 천상계 게임 분석 결과, "+str(round(list(minute)[i],1))+"크게 승리를 보장하는 지표가 없으며, 게임 기록상의 스코어보다, 외부적인 플레이어의 컨디션이 중요합니다.",file=temp2)
            print("가능한 피드백은, 오브젝트를 제때 챙기고 포탑 파괴를 최대한 노리시건대, 죽지 마세요. 백도어(상대방이 싸우고 있을 때 후방의 빈 타워를 치는 것), 스플릿(미드를 중점으로 대치하고, 이동기가 좋은 챔피언이 주기적으로 몰려오는 상단로/하단로의 미니언 처리)를 새겨두세요.",file=temp2)
            print("\n💻 ["+str(round(list(minute)[i],1))+"분대 통계상 이긴 팀의 1인분 기준]",file=temp2)
            print("킬 : 7.7, 데스 : 6.5\n골드 : 15095.3, 딜량 : 26416.1\nCC기 사용시간 : 280.7초, 시야점수 : 48.6",file=temp2)
        print("\n==========================",file=temp2)
        return print("※ 스탯 평가는 천상계(챌린저,그랜드마스터,마스터)의 게임 성적과 비교하여 산출됩니다.",file=temp2)

#승률 예측 함수
def predict(name,match_analysis_num,api_key):
    #모델 및 데이터 로드
    ss = joblib.load("model/standard_scaler.pkl")
    xgb = XGBClassifier()
    xgb.load_model("model/LOL_predict_xgb.bst")
    match_df,player_stat,game_minute,win_lable = datapipe.collect_predict_data_by_name(name,match_analysis_num,api_key)
    del [[player_stat]]
    gc.collect
    if(win_lable[0]==-1):
        return -1, -1
    elif(win_lable[0]==-404):
        return -404, -404
    else:
        #승률예측
        match_scaled = ss.fit_transform(match_df)
        win_rate = xgb.predict_proba(match_scaled)
        real_win_rate = win_lable.mean()
        predict_win_rate = win_rate[:,1].mean()
        return real_win_rate, predict_win_rate

def predictInfo(name,match_analysis_num,api_key):
    temp3 = open("data/predictemp.txt","w")
    real,pred = predict(name,match_analysis_num,api_key)
    if(real==-1):
        return print("※ 등록된 소환사가 없습니다. 다시 입력해 주세요.",file=temp3)
    elif(real==-404):
        return print("※ 죄송합니다. 현재 라이엇 API 서버가 점검중입니다.",file=temp3)
    else:
        diff = pred - real
        print("📈『"+name+"』 님의 승률 예측 결과입니다.",file=temp3)
        print("==========================\n",file=temp3)
        if (diff)>0:
            print("🎉AI가 "+name+"님의 최근 20게임을 기반으로 분석/예측한 결과, 소환사님의 발전가능성이 높다고 판단됩니다!!\n",file=temp3)
            print("▪ 실제 20게임 승률 : "+str(round(real*100,2))+"%",file=temp3)
            print("▪ AI승률 예측 결과: "+str(round(pred*100,2))+"%",file=temp3)
            print("AI 예측승률이 실제 승률보다 높은 경우,이는 패배한 게임에서 사실 소환사님이 이겼을 확률이 높게 예측되었다는 것입니다.",file=temp3)
            print("예측과 실제승률 차이는 "+str(round(diff*100,2))+"% 로, 차이가 커질수록 소환사님의 앞으로의 발전 가능성이 더욱 기대됩니다!",file=temp3)
        else:
            print("😂AI가 "+name+"님의 최근 20게임을 기반으로 분석/예측한 결과, 소환사님의 발전가능성이 낮다고 판단됩니다ㅠㅠ\n",file=temp3)
            print("▪ 실제 20게임 승률 : "+str(round(real*100,2))+"%",file=temp3)
            print("▪ AI승률 예측 결과: "+str(round(pred*100,2))+"%",file=temp3)
            print("\nAI 예측승률이 실제 승률보다 낮은 경우,이는 이겼던 게임에서 사실 소환사님이 패배했을 확률이 높게 예측되었다는 것입니다.",file=temp3)
            print("예측과 실제승률 차이는 "+str(round(-diff*100,2))+"% 로, 차이가 작아질수록 소환사님이 앞으로 발전하는 지표가 될겁니다!",file=temp3)
        print("\n==========================",file=temp3)
        return print("※ 현재 AI 피드백 봇의 정확도는 97퍼센트로, 18만개의 게임을 학습하였고, 극 후반부 게임이 아니라면 대부분의 상황에서 옳은 확률을 도출합니다.",file=temp3)
    

#main단의 요청처리, 요청분류
def return_request(utterance):
    if utterance[0] =="!":
        request_type = "조회"
        user_name = utterance[1:]
    elif utterance[0] =="?":
        request_type = "분석"
        user_name = utterance[1:]
    elif (utterance[len(utterance)-3:].strip() == "조회")|(utterance[len(utterance)-3:].strip() == "분석")|(utterance[len(utterance)-3:].strip() == "예측"):
        request_type = utterance[len(utterance)-3:].strip()
        user_name = utterance[:len(utterance)-3].strip()
    elif (utterance[len(utterance)-1]=="1")|(utterance[len(utterance)-1]=="2")|(utterance[len(utterance)-1]=="3"):
        if utterance[len(utterance)-2]=="석":
            user_name = utterance[:len(utterance)-4].strip()
            request_type = "분석"+utterance[len(utterance)-1]
        else:
            user_name = utterance
            request_type = "invalid command"
    else:
        user_name = utterance
        request_type = "invalid command"
    return user_name, request_type
