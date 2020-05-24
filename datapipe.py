import json
from pandas.io.json import json_normalize
import requests
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import time
import logging
import logging.handlers

#Riot developer's api key
api_key = ""

def match_list_by_name(name,api_key):
    api_name = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key=" + api_key
    r = requests.get(api_name)
    while r.status_code!=200: # 오류를 리턴할 경우 지연하고 다시 시도
        if r.status_code==404:
            return "no_name"
        time.sleep(5)
        r = requests.get(api_name)
        if r.status_code!=200:
            return "error"
    account_Id = r.json()["accountId"]
    season = str(13) # 13시즌의 데이터 수집
    api_url = "https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/" + account_Id + "?season=" + season + "&api_key=" + api_key
    r = requests.get(api_url)
    match_list = pd.DataFrame(r.json()["matches"])
    match_list = match_list[(match_list["queue"]==420) |(match_list["queue"]==430)|(match_list["queue"]==440)]
    match_list = match_list.drop_duplicates("gameId") #중복 경기기록은 삭제
    return match_list

def user_info_by_name(name,api_key):
    api_name = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key=" + api_key
    r = requests.get(api_name)
    while r.status_code!=200: # 오류를 리턴할 경우 지연하고 다시 시도
        if r.status_code==404:
            return "no_name"
        time.sleep(5)
        r = requests.get(api_name)
        if r.status_code!=200:
            return "error"
    summoner_id = r.json()["id"]
    api_url = "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/" + summoner_id + "?api_key=" + api_key
    r = requests.get(api_url)
    user_info = r.json()
    return user_info
    
def match_data_by_match_list(match_list,match_analysis_num,api_key):
    if match_analysis_num > 20: #최대 20게임
        return print("match_analysis_num is down 20(riot api 20 request limit per second)")
    else:
        match_df = pd.DataFrame()
        for game_id in list(match_list.iloc[:match_analysis_num,1]):
            api_url = "https://kr.api.riotgames.com/lol/match/v4/matches/" + str(game_id) + "?api_key=" + api_key
            r = requests.get(api_url)
            while r.status_code!=200: # 오류를 리턴할 경우 지연하고 다시 시도
                time.sleep(5)
                r = requests.get(api_url)
            r_json = r.json()
            temp_df = pd.DataFrame(list(r_json.values()), index=list(r_json.keys())).T
            match_df = pd.concat([match_df, temp_df])

        match_df.index = range(len(match_df))

        match_df.drop(["gameId","platformId","gameCreation","queueId","mapId","seasonId","gameVersion","gameMode","gameType"],axis=1,inplace=True) #필요없는 칼럼
    return match_df

def team_json_to_column(name,match_df):

    num = len(match_df)

    team_id_list = [] #name에 해당하는 플레이어의 소속 팀 id
    #해당 플레이어의 전적 기록용 데이터프레임
    player_champ=[]
    player_kill=[]
    player_death=[]
    player_assist=[]
    player_totalDamageDealt=[]
    player_totalDamageTaken=[]
    player_level=[]
    player_cs=[]
    player_goldEarned=[]
    player_visionScore=[]
    player_turretKills=[]
    for i in range(num):
        for j in range(10):
            if name == match_df["participantIdentities"].iat[i][j]["player"]["summonerName"]:#해당 플레이어 탐색
                team_id_list.append(match_df["participants"].iat[i][j]["teamId"])
                player_champ.append(match_df["participants"].iat[i][j]["championId"])
                player_kill.append(match_df["participants"].iat[i][j]["stats"]["kills"])
                player_death.append(match_df["participants"].iat[i][j]["stats"]["deaths"])
                player_assist.append(match_df["participants"].iat[i][j]["stats"]["assists"])
                player_totalDamageDealt.append(match_df["participants"].iat[i][j]["stats"]["totalDamageDealtToChampions"])
                player_totalDamageTaken.append(match_df["participants"].iat[i][j]["stats"]["totalDamageTaken"])
                player_level.append(match_df["participants"].iat[i][j]["stats"]["champLevel"])
                player_cs.append(match_df["participants"].iat[i][j]["stats"]["totalMinionsKilled"])
                player_goldEarned.append(match_df["participants"].iat[i][j]["stats"]["goldEarned"])
                player_visionScore.append(match_df["participants"].iat[i][j]["stats"]["visionScore"])
                player_turretKills.append(match_df["participants"].iat[i][j]["stats"]["turretKills"])
                break
    player_stat = pd.DataFrame(data={"player_champ":player_champ,"player_kill":player_kill,"player_death":player_death,"player_assist":player_assist,"player_totalDamageDealt":player_totalDamageDealt,"player_totalDamageTaken":player_totalDamageTaken,"player_level":player_level,"player_cs":player_cs,"player_goldEarned":player_goldEarned,"player_visionScore":player_visionScore,"player_turretKills":player_turretKills})           
    a_ls = list(match_df['teams'])
    team_df = pd.DataFrame() #name에 해당하는 플레이어의 소속 팀 경기기록
    for i,teamId in zip(range(num),team_id_list):
        if teamId == 100:
            a_ls[i][0].pop('bans',None)
            team = pd.DataFrame(list(a_ls[i][0].values()),index = list(a_ls[i][0].keys())).T
            team_df = team_df.append(team)
        else:
            a_ls[i][1].pop('bans',None)
            team = pd.DataFrame(list(a_ls[i][1].values()),index = list(a_ls[i][1].keys())).T
            team_df = team_df.append(team)

    team_df.index = range(len(team_df))

    match_df = pd.concat([match_df,team_df],axis=1)

    match_df.drop(["teams","participantIdentities","vilemawKills","dominionVictoryScore"],axis=1,inplace=True)
    
    return match_df,player_stat

#천상계는 전체적으로 하위 티어보다 킬, 데스의 분포 범위가 다름을 고려, 킬/데스의 비율로 킬데스를 반영.
def kdc(df):
    if df["team_deaths"]==0:
        return df["team_kills"]/(df["team_deaths"]+1)*1.2 #만약 팀의 총 데스가 0일경우 퍼펙트 게임을 적용해 가중치 1.2 적용
    return df["team_kills"]/df["team_deaths"]

# 개인기록 / 총합 통계용
def kills_per_total(df):
    if df["team_kills"]==0:
        return 0
    return df["player_kill"] / df["team_kills"]

def deaths_per_total(df):
    if df["team_deaths"]==0:
        return 0
    return df["player_death"] / df["team_deaths"]

def towerkill_per_total(df):
    if df["team_towerKills"]==0:
        return 0
    return df["player_turretKills"] / df["team_towerKills"]

def stat_preprocessing(stats_df,match_df,player_stat,remove_col):
    #게임시간 (초) -> 분
    stats_df["gameMinute"] = match_df["gameDuration"] / 60

    #팀의 킬카운트 총합
    stats_df["team_kills"] = stats_df["kills1"] + stats_df["kills2"] + stats_df["kills3"] + stats_df["kills4"] + stats_df["kills5"]

    #팀의 데스카운트 총합
    stats_df["team_deaths"] = stats_df["deaths1"] + stats_df["deaths2"] + stats_df["deaths3"] + stats_df["deaths4"] + stats_df["deaths5"]

    #팀이 가한 총 피해량
    stats_df["team_totalDamageDealtToChampions"] = stats_df["totalDamageDealtToChampions1"] + stats_df["totalDamageDealtToChampions2"] + stats_df["totalDamageDealtToChampions3"] + stats_df["totalDamageDealtToChampions4"] + stats_df["totalDamageDealtToChampions5"]

    #팀이 가한 총 CC기 시간
    stats_df["team_totalTimeCrowdControlDealt"] = stats_df["totalTimeCrowdControlDealt1"] + stats_df["totalTimeCrowdControlDealt2"] + stats_df["totalTimeCrowdControlDealt3"] + stats_df["totalTimeCrowdControlDealt4"] + stats_df["totalTimeCrowdControlDealt5"]

    #팀의 총 시야점수
    stats_df["team_visionScore"] = stats_df["visionScore1"] + stats_df["visionScore2"] + stats_df["visionScore3"] + stats_df["visionScore4"] + stats_df["visionScore5"]
    
    #팀의 킬/데스 지표
    stats_df["team_K/D"] = stats_df.apply(kdc,axis=1)

    #분당 팀의 킬,데스 스코어

    stats_df["team_kills_per_minute"] = stats_df["team_kills"] / stats_df["gameMinute"]

    stats_df["team_deaths_per_minute"]= stats_df["team_deaths"] / stats_df["gameMinute"]

    stats_df["team_K/D_per_minute"] = stats_df["team_K/D"] / stats_df["gameMinute"]

    #분당 팀이 가한 총 데미지
    stats_df["team_totalDamageDealt_per_minute"] = stats_df["team_totalDamageDealtToChampions"] / stats_df["gameMinute"]

    #분당 팀이 가한 CC기 시간
    stats_df["team_totalTimeCrowdControlDealt_per_minute"] =  stats_df["team_totalTimeCrowdControlDealt"] / stats_df["gameMinute"]

    #분당 팀의 시야 점수
    stats_df["team_visionScore_per_minute"] = stats_df["team_visionScore"] / stats_df["gameMinute"]
    
    #플레이어가 해당 팀에서 차지한 지분율
    remove_col2 = ["team_kills","team_deaths","team_totalDamageDealtToChampions","team_visionScore","team_towerKills"] 
    
    player_stat["team_kills"] = stats_df["team_kills"]
    player_stat["team_deaths"] = stats_df["team_deaths"]
    player_stat["team_totalDamageDealtToChampions"] = stats_df["team_totalDamageDealtToChampions"]
    player_stat["team_visionScore"] = stats_df["team_visionScore"]
    player_stat["team_towerKills"] = match_df["towerKills"]
    player_stat["kills_per_total"] = player_stat.apply(kills_per_total,axis=1)*100
    player_stat["deaths_per_total"] = player_stat.apply(deaths_per_total,axis=1)*100
    player_stat["totalDamageDealtToChampions_per_total"] = (player_stat["player_totalDamageDealt"] / player_stat["team_totalDamageDealtToChampions"])*100
    player_stat["visionScore_per_total"] = (player_stat["player_visionScore"] / player_stat["team_visionScore"])*100
    player_stat["towerKills_per_total"] = player_stat.apply(towerkill_per_total,axis=1)*100
    stats_df.drop(remove_col,axis=1,inplace=True)
    player_stat.drop(remove_col2,axis=1,inplace=True)
    return stats_df,player_stat

def stat_json_to_column(match_analysis_num,match_df,player_stat):
    #스탯 데이터에서 가져올 칼럼
    use_cols = ["kills","deaths","totalDamageDealtToChampions", "visionScore","totalTimeCrowdControlDealt"]
    #데이터 통합 이후 삭제할 칼럼
    remove_col = ['kills1', 'kills2', 'kills3', 'kills4', 'kills5','deaths1', 'deaths2', 'deaths3', 'deaths4', 'deaths5','totalDamageDealtToChampions1', 'totalDamageDealtToChampions2',
       'totalDamageDealtToChampions3', 'totalDamageDealtToChampions4',
       'totalDamageDealtToChampions5','visionScore1',
       'visionScore2', 'visionScore3', 'visionScore4', 'visionScore5',
       'totalTimeCrowdControlDealt1', 'totalTimeCrowdControlDealt2',
       'totalTimeCrowdControlDealt3', 'totalTimeCrowdControlDealt4',
       'totalTimeCrowdControlDealt5']
    stats_df = pd.DataFrame()
    for i in range(match_analysis_num):
        temp = pd.DataFrame()
        for col in use_cols:
            if match_df["teamId"].iat[i]==100:
                cur_values = {f"{col}{j+1}": match_df["participants"].iat[i][j]["stats"][col] for j in range(5)}
                temp = pd.concat([temp, pd.Series(cur_values)], axis=0, sort=False)
            else:
                cur_values = {f"{col}{j-4}": match_df["participants"].iat[i][j]["stats"][col] for j in range(5,10)}
                temp = pd.concat([temp, pd.Series(cur_values)], axis=0, sort=False)
        stats_df = pd.concat([stats_df, temp], axis=1, sort=False)
    stats_df = stats_df.T.reset_index(drop=True)
    stats_df,player_stat = stat_preprocessing(stats_df,match_df,player_stat,remove_col)
    match_df = pd.concat([match_df,stats_df],axis=1)
    match_df.drop("participants",axis=1,inplace=True)
    return match_df,player_stat

def team_preprocessing(match_df):
    #분당 팀의 타워 파괴량
    match_df["towerKills_per_minute"] = match_df["towerKills"] / match_df["gameMinute"]

    #분당 팀의 억제기 파괴량
    match_df["inhibitorKills_per_minute"] = match_df["inhibitorKills"] /match_df["gameMinute"]

    #분당 팀의 바론 처치량
    match_df["baronKills_per_minute"] = match_df["baronKills"] / match_df["gameMinute"]

    #분당 팀의 드래곤 처치량
    match_df["dragonKills_per_minute"] = match_df["dragonKills"] / match_df["gameMinute"]

    #분당 팀의 전령 처치량
    match_df["riftHeraldKills_per_minute"] = match_df["riftHeraldKills"] / match_df["gameMinute"]
    
    remove_col = ['towerKills','inhibitorKills','baronKills','dragonKills','riftHeraldKills','team_kills', 'team_deaths','team_totalDamageDealtToChampions', 
            'team_totalTimeCrowdControlDealt','team_visionScore','team_K/D']

    match_df.drop(remove_col,axis=1,inplace=True)
    return match_df

#원 핫 인코더
def timebin_one_hot_encoder(match_df):
    dummies = pd.DataFrame()
    for i in range(len(match_df)):
        if match_df["time_bin"][i]==1:
            ohe = [1,0,0,0]
            dummies = dummies.append(pd.DataFrame(ohe).T)
        elif match_df["time_bin"][i]==2:
            ohe = [0,1,0,0]
            dummies = dummies.append(pd.DataFrame(ohe).T)
        elif match_df["time_bin"][i]==3:
            ohe = [0,0,1,0]
            dummies = dummies.append(pd.DataFrame(ohe).T)
        else:
            ohe = [0,0,0,1]
            dummies = dummies.append(pd.DataFrame(ohe).T)
    dummies.columns = ["time_bin_1","time_bin_2","time_bin_3","time_bin_4"]
    dummies.reset_index(drop=True,inplace=True)
    return dummies

def match_data_preprocessing(match_df,bins):
    match_df = team_preprocessing(match_df) #팀 데이터 전처리
    
    #bool dtype 맵핑
    bool_mapping = {True:1,False:0}
    bool_col = match_df.select_dtypes('bool').columns.tolist()

    for col in bool_col:
        match_df[col] = match_df[col].map(bool_mapping)
    
    #win칼럼 맵핑,분리
    win_mapping = {"Win":1,"Fail":0}
    match_df["win"] = match_df["win"].map(win_mapping)
    win_lable = match_df["win"]
    match_df.drop("win",axis=1,inplace=True)
    
    #모든칼럼 숫자화
    match_df = match_df.astype(float)
    
    #time_bin생성
    match_df["time_bin"] = np.digitize(match_df["gameMinute"],bins)
    dummies = timebin_one_hot_encoder(match_df)
    match_df = pd.concat([match_df,dummies],axis=1)
    game_minute = match_df["gameMinute"]
    match_df.drop(["gameDuration","gameMinute","time_bin"],axis=1,inplace=True)
    
    #모델에 맞도록 전처리
    column_sequence = ['teamId','firstBlood','firstTower','firstInhibitor','firstBaron','firstDragon','firstRiftHerald','team_kills_per_minute','team_deaths_per_minute','team_K/D_per_minute','team_totalDamageDealt_per_minute','team_totalTimeCrowdControlDealt_per_minute','team_visionScore_per_minute','towerKills_per_minute','inhibitorKills_per_minute','baronKills_per_minute','dragonKills_per_minute','riftHeraldKills_per_minute','time_bin_1','time_bin_2','time_bin_3','time_bin_4']
    match_df.reindex(columns=column_sequence)
    match_df.iloc[:,:7] = match_df.iloc[:,:7].astype(int)
    
    return match_df,game_minute,win_lable

logger = logging.getLogger("status")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s")

fileHandler = logging.FileHandler("status.log")
streamHandler = logging.StreamHandler()

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

#데이터 수집용 함수| (플레이어 닉네임, 분석할 경기 갯수, API_KEY) return (예측용 경기 데이터프레임, 통계용 플레이어 전적 데이터프레임, 게임 진행 시간, 경기 승/패)
def collect_predict_data_by_name(name,match_analysis_num,api_key,bins = [0, 20, 25, 30]):
    logger.info("Initialize Data Loading..")
    match_list = match_list_by_name(name,api_key)
    if(list(match_list)==list("no_name")):
        logger.error("Name Not Found")
        return -1,-1,-1,-1
    elif(list(match_list)==list("error")):
        logger.error("Server error, Try regenerate API Key")
        return -404,-404,-404,-404
    else:
        match_df = match_data_by_match_list(match_list,match_analysis_num,api_key)
        match_df,player_stat = team_json_to_column(name,match_df)
        match_df,player_stat = stat_json_to_column(match_analysis_num,match_df,player_stat)
        match_df,game_minute,win_lable = match_data_preprocessing(match_df,bins)
        logger.info(f"User : {name} Data Loading Sucessful")
        return match_df,player_stat,game_minute,win_lable
