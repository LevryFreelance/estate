import sys

import pymongo

sys.path.append("..")

import re
import json
import requests
from bs4 import BeautifulSoup as Soup
import pandas as pd

from dataclass.estate import Estate
from controllers import db


def get_all_links():
    pass


def find_cities(section_id):
    req = requests.get(f'https://flatfy.lv/geo_list?geo_type=city&section_id={section_id}')
    html = Soup(req.text, features='html.parser')

    links = ['https://flatfy.lv' + x['href'] for x in html.select('.hscroll-selector__option.symbol-paging__item a')]

    data = []
    for link in links:
        req = requests.get(link)
        html = Soup(req.text, features='html.parser')

        cities_links = ['https://flatfy.lv' + x['href'] for x in html.select('.multi-col-list__item a')]
        cities = [x.text for x in html.select('.multi-col-list__item a')]

        data.extend(zip(cities, cities_links))
    return data


def parse_geo(city, geo):
    g = list(map(lambda x: x.strip(), geo.split(',')))

    riga = ['Centrs', 'Āgenskalns', 'Aplokciems', 'Beberbeķi', 'Berģi', 'Bieriņi', 'Bolderāja', 'Brekši', 'Bukulti', 'Buļļi', 'Čiekurkalns', 'Dārzciems', 'Daugavgrīva', 'Dreiliņi', 'Dzegužkalns', 'Grīziņkalns', 'Iļģuciems', 'Imanta', 'Jāņavārti', 'Jaunciems', 'Jaunmīlgrāvis', 'Jugla', 'Katlakalns', 'Ķengarags', 'Ķīpsala', 'Kleisti', 'Klīversala', 'Krasta', 'r-ns', 'Kundziņsala', 'Mangaļi', 'Mangaļsala', 'Maskavas', 'priekšpilsēta', 'Mežaparks', 'Mežciems', 'Pļavnieki', 'Purvciems', 'Šampēteris-Pleskodāle', 'Sarkandaugava', 'Šķirotava', 'Teika', 'Torņakalns', 'Vecāķi', 'Vecdaugava', 'Vecmīlgrāvis', 'Vecrīga', 'Voleri', 'Zasulauks', 'Ziepniekkalns', 'Zolitūde', 'VEF']
    jurmala = ['Asari', 'Bulduri', 'Buļļuciems', 'Dubulti', 'Dzintari', 'Jaundubulti', 'Jaunķemeri', 'Kauguri', 'Ķemeri', 'Lielupe', 'Majori', 'Melluži', 'Priedaine', 'Pumpuri', 'Sloka', 'Vaivari', 'Valteri']

    address, district, region = None, None, None

    for x in g:
        if re.search('\d', x):
            address = x
        if city == 'Rīga':
            if x in riga:
                district = x
            region = city
        if city == 'Jūrmala':
            if x in jurmala:
                district = x
            region = city
    return region, district, address


def parse_page(html, city, section_id):
    script = ''
    for s in html.select('script'):
        try:
            if s['type'] == 'text/javascript':
                script = s
                break
        except KeyError as e:
            pass
    try:
        json_str = re.search('window.INITIAL_STATE = (.*);', str(script)).group(1)
        json_str = json_str.strip("'<>() ").replace('undefined', '"undefined"')

        json_dict = json.loads(json_str)
    except json.decoder.JSONDecodeError as e:
        print(e)
        return

    type_data = {1: ('Dzīvokļi', 'Pārdod'), 2: ('Dzīvokļi', 'Īrē'), 3: ('Mājas', 'Pārdod'), 4: ('Mājas', 'Īrē'),
                 5: ('Komercplatība', 'Pārdod'), 6: ('Komercplatība', 'Īrē')}


    result = []
    for estate in json_dict['search']['realties']['list']:
        room = estate['room_count']
        floor = estate['floor']
        floor_count = estate['floor_count']
        area = estate['area_total']
        price = estate['price']
        price_m2 = estate['price_sqm']
        geo = estate['geo']
        id = estate['id']
        date = estate['insert_time']
        year, month, day = map(int, re.search('(\d{4})-(\d{2})-(\d{2})', date).groups())

        req = requests.get(f'https://flatfy.lv/redirect/{id}')
        html = Soup(req.text, features='html.parser')

        link = html.select('.redirect-link')[0]['href']

        property_type = type_data[section_id][0]
        deal_type = type_data[section_id][1]

        region, district, address = parse_geo(city, geo)

        result.append(
            Estate(year=year, month=month, day=day, country='LV', resource='flatfy.lv', property_type=property_type,
                   region=region, city=city, district=district, address=address, deal_type=deal_type, price=price,
                   price_m2=price_m2, area=area, room_number=room, floor_number=floor, count_of_floors=floor_count,
                   link=link).to_list())

    return result


def get_max_page(html):
    pages = []
    for x in html.select('.paging-button'):
        page = x.text

        if page != '':
            pages.append(int(page))

    if pages:
        return max(pages)


def get_all():

    data = []

    for section_id in range(1, 7):
        for city, link in find_cities(section_id):
            req = requests.get(link)
            html = Soup(req.text, features='html.parser')

            try:
                data.extend(parse_page(html, city, section_id))
            except Exception as e:
                print(e, link)

            print(city, link)
            max_page = get_max_page(html)

            if max_page is not None:
                for page in range(2, max_page + 1):
                    print('page', page)
                    req = requests.get(link + f'?page={page}')
                    html = Soup(req.text, features='html.parser')

                    try:
                        data.extend(parse_page(html, city, section_id))
                    except Exception as e:
                        print(e, link + f'?page={page}')
            print(len(data))
    return data


def unique(data):
    exist_links = db.get_exist_links('latvia', 'flatfy.lv')
    unique = []
    for obj in data:
        if obj['link'] not in exist_links:
            unique.append(obj)
    return unique


def main():
    data = get_all()
    print('All: ', len(data))

    data = unique(data)
    print('Unique: ', len(data))

    return data
