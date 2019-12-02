import datetime
import threading
import time

import pandas as pd
import requests
import schedule
import os
from controllers import db

from scripts.ss import main as ss_controller
from scripts.mm import main as mm_controller
from scripts.latio import main as latio_controller


def save_daily(df):
    print('save daily')

    headers = ['year', 'month', 'country', 'resource', 'deal_type', 'property_type', 'city_region', 'district', 'street', 'volost',
               'village', 'price', 'price_m2', 'area', 'ground_area', 'room_number', 'floor_number',
               'count_of_floors', 'kad_number', 'series', 'house_type', 'facilities', 'purpose', 'link']


    path = 'tables/daily/' + str(datetime.datetime.now().year) + '/' + str(datetime.datetime.now().month) + '/'
    filename = str(datetime.datetime.now().day) + '-' + str(datetime.datetime.now().month) + '-' + str(datetime.datetime.now().year) + '.xlsx'
    if not os.path.exists(path):
        os.makedirs(path)
    df.to_excel(path + '/' + filename, index=False, header=headers)


def merge_dfs(df):
    # df = pd.read_excel('tables/daily/2019/11/13-11-2019.xlsx')
    df_all = pd.read_excel('tables/estate.xlsx')
    pd.concat([df, df_all]).to_excel('tables/estate.xlsx', index=False)


def split_table_to_countries():
    df = pd.read_excel('tables/estate.xlsx')

    df[df['country'] == 'LV'].to_excel('tables/estate_lv.xlsx', index=False)
    df[df['country'] == 'LT'].to_excel('tables/estate_lt.xlsx', index=False)
    df[df['country'] == 'EE'].to_excel('tables/estate_ee.xlsx', index=False)


def refresh_tables():
    print('Refresh')

    ss = ss_controller()
    if ss is not None:
        db.save(ss, 'latvia')

    mm = mm_controller()
    if mm is not None:
        db.save(mm, 'latvia')

    latio = latio_controller()
    if latio is not None:
        db.save(latio, 'latvia')

    print('Finished refresh')


def sched():
    print(2)
    schedule.every().day.at('13:20').do(refresh_tables)
    # threading.Thread(target=refresh_tables).start()
    def s():
        while True:
            schedule.run_pending()
    threading.Thread(target=s).start()





if __name__ == '__main__':
    refresh_tables()
