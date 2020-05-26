
# 플레이어 스탯을 받아 레이팅 계산하는 함수

def kill_rating(row):
    if row["kill_rate"]<0:
        return 0.1
    return row["kill_rate"]
def death_rating(row):
    if row["death_rate"]>100:
        return 100
    return row["death_rate"]
def totalDamage_rating(row):
    if row["totalDamageDealt_rate"]<0:
        return 0.1
    return row["totalDamageDealt_rate"]
def gold_rating(row):
    if row["gold_rate"]<0:
        return 0.1
    return row["gold_rate"]
def visionScore_rating(row):
    if row["visionScore_rate"]<0:
        return 0.1
    return row["visionScore_rate"]

def kill_label(row):
    rate = row["kill_rate"]
    if rate<1:
        return "SS"
    elif (rate>=1)&(rate<5):
        return "S+"
    elif (rate>=5)&(rate<10):
        return "S"
    elif (rate>=10)&(rate<20):
        return "A+"
    elif (rate>=20)&(rate<30):
        return "A"
    elif (rate>=30)&(rate<40):
        return "B+"
    elif (rate>=40)&(rate<50):
        return "B"
    elif (rate>=50)&(rate<60):
        return "C+"
    elif (rate>=60)&(rate<70):
        return "C"
    elif (rate>=70)&(rate<80):
        return "D+"
    else:
        return "D"

def death_label(row):
    rate = row["death_rate"]
    if rate<1:
        return "SS"
    elif (rate>=1)&(rate<5):
        return "S+"
    elif (rate>=5)&(rate<10):
        return "S"
    elif (rate>=10)&(rate<20):
        return "A+"
    elif (rate>=20)&(rate<30):
        return "A"
    elif (rate>=30)&(rate<40):
        return "B+"
    elif (rate>=40)&(rate<50):
        return "B"
    elif (rate>=50)&(rate<60):
        return "C+"
    elif (rate>=60)&(rate<70):
        return "C"
    elif (rate>=70)&(rate<80):
        return "D+"
    else:
        return "D"


def totalDamage_label(row):
    rate = row["totalDamageDealt_rate"]
    if rate<1:
        return "SS"
    elif (rate>=1)&(rate<5):
        return "S+"
    elif (rate>=5)&(rate<10):
        return "S"
    elif (rate>=10)&(rate<20):
        return "A+"
    elif (rate>=20)&(rate<30):
        return "A"
    elif (rate>=30)&(rate<40):
        return "B+"
    elif (rate>=40)&(rate<50):
        return "B"
    elif (rate>=50)&(rate<60):
        return "C+"
    elif (rate>=60)&(rate<70):
        return "C"
    elif (rate>=70)&(rate<80):
        return "D+"
    else:
        return "D"

def gold_label(row):
    rate = row["gold_rate"]
    if rate<1:
        return "SS"
    elif (rate>=1)&(rate<5):
        return "S+"
    elif (rate>=5)&(rate<10):
        return "S"
    elif (rate>=10)&(rate<20):
        return "A+"
    elif (rate>=20)&(rate<30):
        return "A"
    elif (rate>=30)&(rate<40):
        return "B+"
    elif (rate>=40)&(rate<50):
        return "B"
    elif (rate>=50)&(rate<60):
        return "C+"
    elif (rate>=60)&(rate<70):
        return "C"
    elif (rate>=70)&(rate<80):
        return "D+"
    else:
        return "D"

def visionScore_label(row):
    rate = row["visionScore_rate"]
    if rate<1:
        return "SS"
    elif (rate>=1)&(rate<5):
        return "S+"
    elif (rate>=5)&(rate<10):
        return "S"
    elif (rate>=10)&(rate<20):
        return "A+"
    elif (rate>=20)&(rate<30):
        return "A"
    elif (rate>=30)&(rate<40):
        return "B+"
    elif (rate>=40)&(rate<50):
        return "B"
    elif (rate>=50)&(rate<60):
        return "C+"
    elif (rate>=60)&(rate<70):
        return "C"
    elif (rate>=70)&(rate<80):
        return "D+"
    else:
        return "D"
    
def player_rating(player_stat,game_minute):
    player_stat["kill_rate"] = 100 - (((player_stat["player_kill"]/game_minute)/0.45) *100)
    player_stat["death_rate"] = (((player_stat["player_death"]/game_minute)/0.45) *100)
    player_stat["totalDamageDealt_rate"] = 100 - (((player_stat["player_totalDamageDealt"]/game_minute)/1250) *100)
    player_stat["gold_rate"] = 100 - (((player_stat["player_goldEarned"]/game_minute)/510) *100)
    player_stat["visionScore_rate"] = 100 - (((player_stat["player_visionScore"]/game_minute)/2.45) *100)
    
    player_stat["kill_rate"] = player_stat.apply(kill_rating,axis=1)
    player_stat["death_rate"] = player_stat.apply(death_rating,axis=1)
    player_stat["totalDamageDealt_rate"] = player_stat.apply(totalDamage_rating,axis=1)
    player_stat["gold_rate"] = player_stat.apply(gold_rating,axis=1)
    player_stat["visionScore_rate"] = player_stat.apply(visionScore_rating,axis=1)
    
    player_stat["kill_label"] = player_stat.apply(kill_label,axis=1)
    player_stat["death_label"] = player_stat.apply(death_label,axis=1)
    player_stat["totalDamageDealt_label"] = player_stat.apply(totalDamage_label,axis=1)
    player_stat["gold_label"] = player_stat.apply(gold_label,axis=1)
    player_stat["visionScore_label"] = player_stat.apply(visionScore_label,axis=1)
    return player_stat