import datapipe
import parser
from xgboost import XGBClassifier
from sklearn.externals import joblib
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import warnings
warnings.filterwarnings("ignore")

api_key = datapipe.api_key
name = "최소실버가목표"
match_analysis_num = 10 #1게임당 1초정도 소요, 최대 20개

def userInfo(Container):
    temp = open("temp.txt","w")
    rankCase = ['솔로', '자유']
    if (Container['SummonerName'] != '')&(Container['Ranking'] != ''):
        print("『"+ Container['SummonerName'] + "』님의 정보입니다.\n ◎ " + Container["Ranking"],file=temp)
    else:
        if (Container['SummonerName'] == ''):
            print("※ 등록된 소환사가 없습니다. 다시 입력해 주세요",file=temp)
        else:
            print("※ " + Container['SummonerName'] + "님은 Unranked입니다.\n(유저 정보 조회는 티어 배치를 받은 다음 가능합니다.)",file=temp)
    for i in range(len(Container['Tier'])):
        if Container['SummonerName'] != '':
            print("==========================",file=temp)
            if len(Container['Tier']):
                print("▶ " + Container['SummonerName'] + "님의 " + rankCase[i] + "랭크 정보입니다.",file=temp)
                print("==========================",file=temp)
                print("- 티어: " + Container['Tier'][i],file=temp)
                print("- LP: " + Container['LP'][i],file=temp)
                print("- 승/패: " + Container['Wins'][i] + "/" + Container['Losses'][i],file=temp)
                print("- 승률: " + Container['Ratio'][i],file=temp)
            else:
                print(Container['SummonerName'] + "님은 Unranked입니다.",file=temp)
                print("==========================",file=temp)
    if (Container['SummonerName'] != '')&(Container['Ranking'] != ''):
        print("==========================",file=temp)
        print("▣ "+Container['SummonerName'] + "님의 모스트 챔피언 정보입니다.",file=temp)
        print("==========================",file=temp)
        for i in range(len(Container["Most"])):
            print(str(i+1) +"순위: " + str(Container["Most"][i]).strip() + " (KDA: " + Container["MostKDA"][i] +")",file=temp)

def player_rating(player_stat,game_minute):
    player_stat["kill rate"] = 100 - (((player_stat["player_kill"]/game_minute)/0.45) *100)
    player_stat["death_rate"] = (((player_stat["player_death"]/game_minute)/0.45) *100)
    player_stat["totalDamageDealt_rate"] = 100 - (((player_stat["player_totalDamageDealt"]/game_minute)/1250) *100)
    player_stat["gold_rate"] = 100 - (((player_stat["player_goldEarned"]/game_minute)/510) *100)
    player_stat["visionScore_rate"] = 100 - (((player_stat["player_visionScore"]/game_minute)/2.45) *100)
    return player_stat

def matchInfo(name,match_analysis_num,api_key):
    temp2 = open("temp2.txt","w")
    match_df,player_stat,minute,win_lable = datapipe.collect_predict_data_by_name(name,match_analysis_num,api_key)
    player_stat = player_rating(player_stat,minute)
    champ_kor = pd.read_csv("champ_id.csv")
    champ_kor.columns = ["player_champ","name"]
    player_stat = pd.merge(player_stat,champ_kor,how="left",on="player_champ")
    print(name + "님의 솔로/자유/일반 최근 3게임 분석결과입니다.",file=temp2)
    print("==========================\n",file=temp2)
    for i in range(3):
        if list(win_lable)[i]==1:
            print("【승리】 / 진행시간: " + str(round(list(minute)[i],1)) + "분",file=temp2)
        else:
            print("【패배】 / 진행시간:" + str(round(list(minute)[i],1)) + "분",file=temp2)

        print("챔피언: " + str(player_stat.iloc[i,21]) +"/"+str(player_stat.iloc[i,6])+"레벨",file=temp2)
        print("K/D/A : " + str(player_stat.iloc[i,1])+"/"+str(player_stat.iloc[i,2])+"/"+str(player_stat.iloc[i,3]),file=temp2)
        print("가한 피해량/받은 피해량: " + str(player_stat.iloc[i,4]) + "/" + str(player_stat.iloc[i,5]),file=temp2)
        print("골드 및 CS: " + str(player_stat.iloc[i,8]) + "골드 (cs : "+str(player_stat.iloc[i,7])+")",file=temp2)
        print("시야점수/타워파괴: " + str(player_stat.iloc[i,9]) + "점/ " + str(player_stat.iloc[i,10]) + "개 부숨",file=temp2)
        print("\n#######분석 레포트#######",file=temp2)
        print("[팀 기여도 지분]\n\t킬 "+str(round(player_stat.iloc[i,11],1))+"%\n\t데스 "+str(round(player_stat.iloc[i,12],1))+"%",file=temp2)
        print("\t딜량 "+str(round(player_stat.iloc[i,13],1))+"%\n\t시야점수 "+str(round(player_stat.iloc[i,14],1))+"%\n\t타워 킬 "+str(round(player_stat.iloc[i,15],1))+"%",file=temp2)
        print("[스탯 평가]\n\t킬량 상위 "+str(round(player_stat.iloc[i,16],1))+"%\n\t데스량 상위 "+str(round(player_stat.iloc[i,17],1))+"%",file=temp2)
        print("\t딜량 상위 "+str(round(player_stat.iloc[i,18],1))+"%\n\t시야점수 상위 "+str(round(player_stat.iloc[i,20],1))+"%\n\t골드량 상위 "+str(round(player_stat.iloc[i,19],1))+"%",file=temp2)
        print("==========================\n",file=temp2)

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
    else:
        user_name = utterance
        request_type = "invalid command"
    return user_name, request_type
        
def predict():
    #모델 및 데이터 로드
    ss = joblib.load("standard_scaler.pkl")
    xgb = XGBClassifier()
    xgb.load_model("LOL_predict_xgb.bst")
    match_df,player_stat,game_minute,win_lable = datapipe.collect_data_by_name(name,match_analysis_num,api_key)
    
    #승률예측
    match_scaled = ss.fit_transform(match_df)
    win_rate = cbr.predict_proba(match_scaled)
    real_win_rate = win_lable.mean()
    predict_win_rate = win_late[:,1].mean()
    return real_win_rate, predict_win_rate