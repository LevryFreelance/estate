# -*- coding: utf8 -*-

import sys

import pymongo

sys.path.append("..")

import re

from selenium import webdriver
import requests
from bs4 import BeautifulSoup as Soup

from dataclass.estate import Estate
import datetime
from controllers import db
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

binary = FirefoxBinary('../geckodriver.exe')
options = Options()
options.headless = True

driver = webdriver.Firefox(options=options, firefox_binary=binary)
data = [
          ('Dzīvokļi', 'Pārdod', 'http://latio.lv/lv/ipasumi?object_group=apartments&client_activity=to_buy'),
        ('Dzīvokļi', 'Izīrē', 'http://latio.lv/lv/ipasumi?object_group=apartments&client_activity=to_rent'),
        ('Mājas', 'Pārdod', 'http://latio.lv/lv/ipasumi?object_group=houses&client_activity=to_buy'),
        ('Mājas', 'Izīrē', 'http://latio.lv/lv/ipasumi?object_group=houses&client_activity=to_rent'),
        ('Zeme', 'Pārdod', 'http://latio.lv/lv/ipasumi?object_group=land&client_activity=to_buy'),
        ('Zeme', 'Izīrē', 'http://latio.lv/lv/ipasumi?object_group=land&client_activity=to_rent'),
        # ('Komercīpašumi', 'Pārdod', 'http://latio.lv/lv/ipasumi?object_group=commercial_spaces&client_activity=to_buy'),
        # ('Komercīpašumi', 'Izīrē', 'http://latio.lv/lv/ipasumi?object_group=commercial_spaces&client_activity=to_rent'),
        ('Namīpašums', 'Pārdod', 'https://latio.lv/lv/ipasumi?object_group=commercial_spaces&client_activity=to_buy&object_type=building'),
        ('Namīpašums', 'Izīrē', 'https://latio.lv/lv/ipasumi?object_group=commercial_spaces&client_activity=to_rent&object_type=building'),
        ('Birojs', 'Pārdod',
         'https://latio.lv/lv/ipasumi?object_group=commercial_spaces&client_activity=to_buy&object_type=office'),
        ('Birojs', 'Izīrē',
         'https://latio.lv/lv/ipasumi?object_group=commercial_spaces&client_activity=to_rent&object_type=office'),
        ('Tirdzniecības telpas', 'Pārdod',
         'https://latio.lv/lv/ipasumi?object_group=commercial_spaces&client_activity=to_buy&object_type=retail_space'),
        ('Tirdzniecības telpas', 'Izīrē',
         'https://latio.lv/lv/ipasumi?object_group=commercial_spaces&client_activity=to_rent&object_type=retail_space'),
        ('Ražošanas un loģistikas telpas', 'Pārdod',
         'https://latio.lv/lv/ipasumi?object_group=commercial_spaces&client_activity=to_buy&object_type=industrial_space'),
        ('Ražošanas un loģistikas telpas', 'Izīrē',
         'https://latio.lv/lv/ipasumi?object_group=commercial_spaces&client_activity=to_rent&object_type=industrial_space'),
        ('Viesnīcas un atpūtas komplekss', 'Pārdod',
         'https://latio.lv/lv/ipasumi?object_group=commercial_spaces&client_activity=to_buy&object_type=hotel'),
        ('Viesnīcas un atpūtas komplekss', 'Izīrē',
         'https://latio.lv/lv/ipasumi?object_group=commercial_spaces&client_activity=to_rent&object_type=hotel'),
        ]


def get_all_links():
    res = set()
    for estate in data:
        # print(estate, len(res))
        for page in range(1, 100000):
            url = estate[2] + f'&page={page}'
            # html = Soup(requests.get(url).text, features='html.parser')
            driver.get(url)
            html = Soup(driver.page_source, features='html.parser')
            if html.select('.nothing-found'):
                break

            elems = html.select('div.item.clearfix')
            for x in elems:
                try:
                    floor = x.find('div', {'data-field': 'floor'}).select('span.value')[0].text
                    floor = int(floor.split('/')[1].strip())
                except Exception:
                    floor = None

                if x.select('.building-details a'):
                    for link in get_links_from_url(x.select('.building-details a')[0]['href']):
                        res.add((link, estate[0], estate[1], floor))
                        # print('Collecting links...' + str(len(res)))
                else:
                    l = x.select('.primary-line a')[0]['href']
                    if 'latio.lv' in l:
                        res.add((l, estate[0], estate[1], floor))
                    else:
                        res.add(('http://latio.lv' + l, estate[0], estate[1], floor))
                    # print('Collecting links...' + str(len(res)))
    return list(res)


def get_links_from_url(url):
    links = []
    for page in range(1, 100000):
        driver.get(url  + f'&page={page}')
        if driver.find_elements_by_css_selector('.nothing-found'):
            break

        for x in driver.find_elements_by_xpath('//a[@data-field="path"]'):
            l = x.get_attribute('href')
            if 'latio.lv' in l:
                links.append(l)
            else:
                links.append('http://latio.lv' + l)
    return links


def process_links(links):
    res = []
    for estate in links:
        parse_result = parse_one(estate[0])
        parse_result.property_type = estate[1]
        parse_result.deal_type = estate[2]
        parse_result.count_of_floors = estate[3]

        # print(parse_result)
        res.append(parse_result.to_list())

        # print('Processing links... ', len(res))
    return res


def parse_one(link):
    html = Soup(requests.get(link).text, features='html.parser')

    try:
        title = html.select('.secondary-line')[0].text

        city, region, district = [None] * 3
        if title.count(',') == 0:
            city = title.strip()
            if city in ['Rīga', 'Jūrmala']:
                region = title.strip()

        elif ('Jūrmala' in title or 'Rīga' in title) and title.count(',') == 1:
            district, city = [j.strip() for j in title.split(',')]
            region = city

        else:
            city = title.split(',')[0].strip()

        if district is not None:
            if district == 'Botāniskais dārzs':
                district = 'Āgenskalns'
            elif district == 'Vef rajons':
                district = 'VEF'
            elif district == 'Centrs (Vecrīga)':
                district = 'Vecrīga'
            elif 'Centrs' in district:
                district = 'Centrs'
            elif district == 'Rumbula (rīga)':
                district = 'Rumbula'
            elif district == 'Āgenskalna priedes':
                district = 'Āgenskalns'
            elif district == 'Bukulti (rīga)':
                district = 'Bukulti'
            elif district == 'Tuvā Pārdaugava':
                district = 'Pārdaugava'

        if city is not None:
            city = city.replace('novads', 'nov.')
            city = city.replace('Novads', 'nov.')
            city = city.replace('pagasts', 'pag.')

            if city == 'Bukulti (rīga)':
                region = city = 'Rīga'
                district = 'Bukulti'

        if region is not None:
            region = region.replace('novads', 'nov.')
            region = region.replace('Novads', 'nov.')
            region = region.replace('pagasts', 'pag.')

    except Exception:
        city, region, district = None, None, None


    room, area, floor, land = None, None, None, None
    try:
        details = [x.text.strip() for x in html.select('#content .details .feature')]
        for det in details:
            if 'istaba' in det:
                room = int(det.split()[0])

            if 'stāvs' in det:
                floor = int(det.split()[0].replace('.', ''))

            if 'm²' in det and 'zeme' not in det:
                area = float(det.split()[0])

            if 'zeme' in det:
                land = float(det.split()[0])

    except Exception:
        pass

    try:
        price = pretty_value(html.select('span.value.price')[0].text)
    except Exception:
        price = None

    try:
        price_m2 = pretty_value(html.select('span.value.price-per-sqm')[0].text)
    except Exception:
        price_m2 = None

    return Estate(year=datetime.datetime.now().year, month=datetime.datetime.now().month, day=datetime.datetime.now().day, country='LV', resource='latio.lv', city=city, region=region, district=district, room_number=room, floor_number=floor, area=area, ground_area=land, price=price, price_m2=price_m2, link=link)


def pretty_value(x):
    if x is not None:
        if re.search('[\d ]*', str(x)).group():
            if re.search('[\d .]*', str(x)).group().replace(' ', '').endswith('.0'):
                p = int(re.search('[\d .]*', str(x)).group().replace(' ', ''))
            else:
                p = float(re.search('[\d .]*', str(x)).group().replace(' ', ''))
            if 'ha' in x:
                return round(p * 10000, 2)
            else:
                return round(p, 2)
        else:
            return None
    else:
        return None


def unique(data):
    exist_links = db.get_exist_links('latvia', 'latio.lv')
    unique = []
    for x in data:
        if x[0] not in exist_links:
            unique.append(x)
    return unique


def main():
    print('Collecting links...')

    links = get_all_links()
    print('Latio: ', str(len(links)), ' links')
    links = unique(links)
    print('Latio: ', str(len(links)), ' unique links')
    if links:
        print('Processing links...')
        res = process_links(links)

        # to_excel(res)
        return res


if __name__ == '__main__':
    # c = 'mongodb+srv://smartdataestate:estate4628134@estate-dqksq.gcp.mongodb.net/test?retryWrites=true&w=majority'
    # client = pymongo.MongoClient(c)
    # db = client.Estate

    pd.DataFrame(db.latio.find({})).to_excel('latio.xlsx')
    print("latio saved to xlsx")
    # d = main()
    # db.latio.insert_many(d)