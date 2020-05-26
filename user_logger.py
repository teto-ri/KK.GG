from datetime import datetime
from pytz import timezone

def user_log(user_name,request_type,user_log):
    now = datetime.now(timezone('Asia/Seoul'))
    return print("%s년 %s월 %s일 %s시 %s분, %s, %s" %(now.year, now.month, now.day, now.hour, now.minute, user_name,request_type),file=user_log)