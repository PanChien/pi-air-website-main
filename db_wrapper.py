from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from pprint import pprint
from utils import *

days_back = -0.5
range = 2.2  # 顯示的寬度，以1為1天
start_date = datetime(2022, 1, 4, 20)  # 開始的日期
search = 1  # 如果要開啟搜尋功能，要將這個調成1


class DbWrapper:
    def __init__(self):
        self.client = MongoClient(  # 連到資料庫的connection string
            'mongodb+srv://chien:kLgXPLGv9y6yA3F@cluster0.q1ala.mongodb.net/air?retryWrites=true&w=majority')
        self.db = self.client.air

    # 拿資料的method
    # 要拿minute的資料，要將False調成True，才可以拿到
    # 否則是拿到limit資料(秒的資料)
    def get_data(self, limit=None, minute=False):
        if minute:  # 如果minute為True
            if search:  # 搜尋的功能，可以查一個區間的空氣品質
                start_dt = start_date
                end_dt = start_date + timedelta(days=range)
                cursor = self.db.air_minute.find({'at': {'$gte': start_dt, '$lte': end_dt}}).sort([('_id', -1)])
            else:
                # day_ago = datetime.now(timezone.utc) + timedelta(days=days_back)
                # cursor = self.db.air_minute.find({'at': {'$gte': day_ago}}).sort([('_id', -1)])
                cursor = self.db.air_minute.find().sort([('_id', -1)]).limit(limit)
        else:  # 否則
            if limit:  # 拿回來的資料量
                cursor = self.db.air.find().sort([('_id', -1)]).limit(limit)
            else:
                cursor = self.db.air.find().sort([('_id', -1)])

        if not cursor:
            print('cursor empty! in get_data')
            cursor = []
        # print(cursor)
        return list(cursor)

    # 確認設備是否還在線上online的狀態
    def is_online(self):
        cursor = list(self.db.air.find().sort([('_id', -1)]).limit(1))  # limit(1)是要拿最新的1個資料
        if not cursor:
            print('cursor empty! in is_online')
            return False

        now = datetime.now(timezone.utc)
        dt = utc_to_local(cursor[-1]['at'])  # 是一個help function，幫助時區轉換

        diff = now - dt
        if diff > timedelta(minutes=5):  # 如果資料庫裡的資料跟現在的時間差大於5分鐘，表示sensor不在線上
            return False

        return True

    # 把資料庫裡的資料刪除
    def clear_db(self):
        # self.db.air.remove({})  # 把collection air裡的資料全部刪除
        day_ago = datetime.now(timezone.utc) + timedelta(days=-10)
        self.db.air.remove()  # 括號裡可以自已寫參數
        print('done')
        # self.db.air.remove({'at': {'$lte': day_ago}})  # 刪除小於10天的資料
        # self.db.tgs.remove({'at': {'$lte': day_ago}})
