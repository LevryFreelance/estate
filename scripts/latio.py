import re

from selenium import webdriver
import requests
from bs4 import BeautifulSoup as Soup

from dataclass.estate import Estate
import datetime
import pandas as pd
from controllers import db


driver = webdriver.PhantomJS()
data = [
          ('flats', 'buy', 'http://latio.lv/en/properties?object_group=apartments&client_activity=to_buy'),
        ('flats', 'rent', 'http://latio.lv/en/properties?object_group=apartments&client_activity=to_rent'),
        ('houses', 'buy', 'http://latio.lv/en/properties?object_group=houses&client_activity=to_buy'),
        ('houses', 'rent', 'http://latio.lv/en/properties?object_group=houses&client_activity=to_rent'),
        ('land', 'buy', 'http://latio.lv/en/properties?object_group=land&client_activity=to_buy'),
        ('land', 'lease', 'http://latio.lv/en/properties?object_group=land&client_activity=to_rent'),
        ('commercial', 'buy', 'http://latio.lv/en/properties?object_group=commercial_spaces&client_activity=to_buy'),
        ('commercial', 'lease', 'http://latio.lv/en/properties?object_group=commercial_spaces&client_activity=to_rent')
        ]



def get_all_links():
    res = set()
    for estate in data:
        for page in range(1, 100000):
            url = estate[2] + f'&page={page}'
            # html = Soup(requests.get(url).text, features='html.parser')
            driver.get(url)
            html = Soup(driver.page_source, features='html.parser')
            if html.select('.nothing-found'):
                break

            elems = html.select('div.item.clearfix')
            for x in elems:

                if x.select('.building-details a'):
                    for link in get_links_from_url(x.select('.building-details a')[0]['href']):
                        res.add((link, estate[0], estate[1]))
                        print('Collecting links...' + str(len(res)))
                else:
                    l = x.select('.primary-line a')[0]['href']
                    if 'latio.lv' in l:
                        res.add((l, estate[0], estate[1]))
                    else:
                        res.add(('http://latio.lv' + l, estate[0], estate[1]))
                    print('Collecting links...' + str(len(res)))
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
        parse_result.parsing_date = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,
                                                      datetime.datetime.now().day)

        res.append(parse_result.to_list())

        print('Processing links... ', len(res))
    return res


def parse_one(link):
    html = Soup(requests.get(link).text, features='html.parser')

    try:
        street = html.select('h2.primary-line')[0].text.strip().title()
    except Exception:
        street = None

    try:
        title = html.select('.secondary-line')[0].text.strip()

        if ',' in title:
            district, city_region = title.split(',')
        else:
            city_region = title.strip()
            district = None
    except Exception:
        city_region, district = None, None

    room, area, floor, land = None, None, None, None
    try:
        details = [x.text.strip() for x in html.select('#content .details .feature')]
        for det in details:
            if 'room' in det:
                room = int(det.split()[0])

            if 'floor' in det:
                floor = int(det.split()[0].replace('.', ''))

            if 'm²' in det and 'land' not in det:
                area = float(det.split()[0])

            if 'land' in det:
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

    return Estate(year=datetime.datetime.now().year, month=datetime.datetime.now().month, country='LV', resource='latio.lv', city_region=city_region, district=district, street=street, room_number=room, floor_number=floor, area=area, ground_area=land, price=price, price_m2=price_m2, link=link)


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


def to_excel(data):
    df = pd.DataFrame(data)

    print(df)
    headers = ['year', 'month', 'country', 'resource', 'deal_type', 'property_type', 'city_region', 'district', 'street', 'volost',
               'village', 'price', 'price_m2', 'area', 'ground_area', 'room_number', 'floor_number',
               'count_of_floors', 'kad_number', 'series', 'house_type', 'facilities', 'purpose', 'link']

    df.to_excel('latio.xlsx', index=False, header=headers)


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
    print('Collecting links...')

    links = get_all_links()
    print('Latio: ', str(len(links)), ' links')

    print('Processing links...')
    res = process_links(links)

    to_excel(res)

