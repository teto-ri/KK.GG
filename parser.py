import requests
from bs4 import BeautifulSoup

hdr = {'Accept-Language': 'ko_KR,en;q=0.8', 'User-Agent': (
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Mobile Safari/537.36')}

def parseOPGG(Name):
    Container = {}
    Container
    SummonerName = ""
    Level = ""
    Ranking = ""
    Most = ""
    MostKDA = ""
    mostchamp = []
    most_kda = []
    Tier = []
    LP = []
    Wins = []
    Losses = []
    Ratio = []
    url = 'https://www.op.gg/summoner/userName=' + Name
    req = requests.get(url, headers=hdr)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')

    for i in soup.select('div[class=SummonerName]'):
        SummonerName = i.text
    Container['SummonerName'] = SummonerName
    
    try:
        level = soup.find("span",{"class":"Level tip"}).text
        Container["Level"] = level
    except AttributeError:
        Container["Level"] = ""
    
    try:
        ranking = soup.find("a",{"class":"tip Link"})
        ranking = ranking.text.replace("\n","").strip()
        Container['Ranking'] = ranking
    except AttributeError:
        Container['Ranking'] = ""
    
    try:
        mostchamp = soup.find("meta",{"name":"description"}).get("content").split("/")[3].strip().split(",")
        Container['Most'] = mostchamp
    except (AttributeError,IndexError):
        Container["Most"] : ""
            
    for i in soup.find_all("div",{"class":"PersonalKDA"}):
        most_kda.append(i.find("span",{"class":"KDA"}).text)
    Container["MostKDA"] = most_kda  
    
    for j in soup.select('div[class=Tier]'):
        Tier.append(j.text.strip())

    Container['Tier'] = Tier
    for i in soup.select('div[class=LP]'):
        LP.append(i.text)

    Container['LP'] = LP
    for i in soup.select('span[class=Wins]'):
        if len(Wins) >= len(Tier):
            break
        Wins.append(i.text)

    Container['Wins'] = Wins
    for i in soup.select('span[class=Losses]'):
        if len(Losses) >= len(Tier):
            break
        Losses.append(i.text)

    Container['Losses'] = Losses
    for i in soup.select('span[class=Ratio]'):
        Ratio.append(i.text)

    Container['Ratio'] = Ratio
    return Container
