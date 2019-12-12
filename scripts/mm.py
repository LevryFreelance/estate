import sys
sys.path.append("..")


import requests
from bs4 import BeautifulSoup as Soup
from dataclass.estate import Estate
import datetime
import pandas as pd
import re
from controllers import db
from controllers.format_series import format_series


data = [
    ('Dzīvokļi', 'https://mm.lv/dzivokli'),
        ('Mājas', 'https://mm.lv/majas'),
        ('Zeme', 'https://mm.lv/zeme'), ('Viensētas', 'https://mm.lv/fermas-viensetas-muizas'), ('Biroji', 'https://mm.lv/biroji'), ('Telpas', [('Pirts mājas', 'https://mm.lv/pirts-majas'), ('Ēkas', 'https://mm.lv/ekas'), ('Angāri', 'https://mm.lv/angari-lv'), ('Veikali', 'https://mm.lv/veikali'), ('Telpas', 'https://mm.lv/telpas'), ('Noliktavas', 'https://mm.lv/noliktavas')])
        ]


def collect_links():
    links = []
    for link in collect_links_estate():
        links.append(link)
    for link in collect_links_room():
        links.append(('Telpas', link[0], link[1]))
    print(f'Collected {len(links)} links')
    return links


def collect_links_estate():
    links = set()
    for estate in data[:-1]:
        for page in range(1, 10000):

            if page == 1:
                req = requests.get(estate[1] + '?all')
            else:
                req = requests.get(f'{estate[1]}/{page}')

            html = Soup(req.text, features='html.parser')

            if html.select('span.counter-search.no-results'):
                break
            for x in html.select('a.link'):
                links.add((estate[0], 'https://mm.lv' + x['href']))
                print(f'Collecting estate links: {len(links)}')
    return list(links)


def collect_links_room():
    links = set()
    for room in data[-1][-1]:

        for page in range(1, 100000):
            req = requests.get(f'{room[1]}/{page}')
            html = Soup(req.text, features='html.parser')

            if html.select('span.counter-search.no-results'):
                break
            for x in html.select('a.link'):
                links.add((room[0], 'https://mm.lv' + x['href']))
                print(f'Collecting room links: {len(links)}')

    return links


def parse_one(url):
    req = requests.get(url)
    html = Soup(req.text, features='html.parser')

    detail_label = [x.text.strip() for x in html.select('label.detail_label')]
    detail_value = [x.text.strip() for x in html.select('label.detail_value')]

    parse_result = Estate()
    options = ['Darījuma veids', 'Platība', 'Istabu skaits', 'Stāvs', 'Sērija', 'Pilsēta', 'Mikrorajons', 'Adrese',
               'Ēkas tips', 'Reģions', 'Majas platība', 'Zemes platība', 'Stāvu skaits', 'Istabu skaits', 'Garāžas platība']
    options_equivalents = ['deal_type', 'area', 'room_number', 'floor_number', 'series', 'city_region', 'district',
                           'street', 'house_type', 'district', 'area', 'ground_area', 'count_of_floors', 'room_number', 'area']
    option_values = []

    for o in detail_label:
        try:
            if o in detail_label:
                setattr(parse_result, options_equivalents[options.index(o)], detail_value[detail_label.index(o)])
        except Exception:
            pass

    try:
        if parse_result.deal_type == 'Vēlas īrēt':
            parse_result.deal_type = 'Īrē'
    except Exception:
        pass

    try:
        if parse_result.city_region is None:
            parse_result.city_region = html.find_all('a', {'itemprop': 'item'})[3]['title']
    except Exception:
        pass

    parse_result.ground_area = pretty_value(parse_result.ground_area)
    parse_result.count_of_floors = pretty_value(parse_result.count_of_floors)

    try:
        parse_result.area = float(parse_result.area.split()[0])
    except Exception:
        pass
    try:
        price = float(html.find('span', {'class': 'currency-value'})['content'])
        parse_result.price = price
        price_m2 = round(price / parse_result.area)
        parse_result.price_m2 = price_m2
    except Exception:
        pass
    try:
        room = parse_result.room_number.split()[0]
        if room.isnumeric():
            parse_result.room_number = int(room)
        else:
            parse_result.room_number = room
    except Exception:
        parse_result.room_number = None
    try:
        parse_result.floor_number = int(parse_result.floor_number.split()[0])
    except Exception:
        pass

    try:
        sel = html.find('li', {'class': 'last-child', 'property': 'itemListElement'}).text.strip()
        parse_result.district = sel
    except Exception:
        pass

    try:
        if len(parse_result.series.split()) > 1:
            parse_result.series = ' '.join(parse_result.series.split()[:-1])
        parse_result.series = format_series(parse_result.series)
    except Exception:
        pass

    parse_result.country = 'LV'
    parse_result.resource = 'mm.lv'

    try:
        date = html.find('span', {'class': 'date'}).text
        if ':' in date:
            parse_result.year = datetime.datetime.now().year
            parse_result.month = datetime.datetime.now().month
            parse_result.day = datetime.datetime.now().day
        else:
            date = date.split('/')
            parse_result.year = int(date[2])
            parse_result.month = int(date[1])
            parse_result.day = int(date[0])
    except Exception:
        pass

    parse_result.link = url
    return parse_result


def pretty_value(x):
    if x is not None:
        if re.search('[\d ]*', str(x)).group():
            if re.search('[\d .]*', str(x)).group().replace(' ', '').endswith('.0'):
                p = int(re.search('[\d .]*', str(x)).group().replace(' ', ''))
            else:
                p = float(re.search('[\d .]*', str(x)).group().replace(' ', ''))
            return p
        else:
            return None
    else:
        return None


def process_links(data):
    result = []
    for x in data:
        parse_result = parse_one(x[-1])
        parse_result.property_type = x[0]
        result.append(parse_result.to_list())
        print(f'Parsing objects: {len(result)}')

    return result


def to_excel(data):
    df = pd.DataFrame(data)

    print(df)
    headers = ['year', 'month', 'day', 'country', 'resource', 'deal_type', 'property_type', 'city_region', 'district', 'street', 'volost',
               'village', 'price', 'price_m2', 'area', 'ground_area', 'room_number', 'floor_number',
               'count_of_floors', 'kad_number', 'series', 'house_type', 'facilities', 'purpose', 'link']

    df.to_excel('mm.xlsx', index=False, header=headers)


def unique(data):
    exist_links = db.get_exist_links('latvia', 'mm.lv')
    unique = []
    for x in data:
        if x[-1] not in exist_links:
            unique.append(x)
    return unique



def main():
    print('Collecting links...')
    links = collect_links()
    print('MM: ', str(len(links)), ' links')
    links = unique(links)
    print('MM: ', str(len(links)), ' unique links')
    if links:
        res = process_links(links)
        return res


if __name__ == '__main__':
    print(parse_one('https://mm.lv/dzivokli-riga-purvciems/dzivoklis-riga-purvciema-30-m-1-ist-5-stavs_i7792.html'))

