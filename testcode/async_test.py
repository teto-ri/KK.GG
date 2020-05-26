from time import time
import requests
import pandas as pd
import asyncio
api_key = "RGAPI-3f22d9e2-e72e-489f-ad65-c60290b70660"
name = "방랑의 가렌"
match_analysis_num = 20 #1게임당 1초정도 소요, 최대 20개
s = time()

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
  

def async_match_data_by_list(match_list,match_analysis_num,api_key):
    urls = ["https://kr.api.riotgames.com/lol/match/v4/matches/" + str(game_id) + "?api_key=" + api_key for game_id in list(match_list.iloc[:20,1])]
    async def getjson(url):
        r = await loop.run_in_executor(None,requests.get,url)
        r_json = r.json()
        return r_json
                                         
    async def task():
        fts = [asyncio.ensure_future(getjson(u)) for u in urls]
        r = await asyncio.gather(*fts)
        return r
    loop = asyncio.get_event_loop()
    json_list = loop.run_until_complete(task())
    loop.close
    match_df = pd.DataFrame()
    for i in range(match_analysis_num):
        temp_df = pd.DataFrame(list(json_list[i].values()),index=list(json_list[i].keys())).T
        match_df = pd.concat([match_df,temp_df])
    match_df.index = range(len(match_df))
    match_df.drop(["gameId","platformId","gameCreation","queueId","mapId","seasonId","gameVersion","gameMode","gameType"],axis=1,inplace=True) #필요없는 칼럼
    return match_df

match_list = match_list_by_name(name,api_key)
match_df = async_match_data_by_list(match_list,match_analysis_num,api_key)
e = time()

print(match_df)
print("{0:.2f}초 걸렸습니다".format(e - s))
