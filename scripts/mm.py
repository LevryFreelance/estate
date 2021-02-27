import sys

import pymongo

sys.path.append("..")


import requests
from bs4 import BeautifulSoup as Soup
from dataclass.estate import Estate
import datetime
import re

from selenium.webdriver import PhantomJS, Firefox
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.options import Options

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

binary = FirefoxBinary('../geckodriver.exe')
options = Options()
options.headless = True



data = [
    ('Dzīvokļi', 'https://mm.lv/dzivokli'),
        ('Mājas', 'https://mm.lv/majas'),
        ('Zeme', 'https://mm.lv/zeme'), ('Viensētas', 'https://mm.lv/fermas-viensetas-muizas'), ('Biroji', 'https://mm.lv/biroji'), ('Pirts mājas', 'https://mm.lv/pirts-majas'), ('Ēkas', 'https://mm.lv/ekas'), ('Angāri', 'https://mm.lv/angari-lv'), ('Veikali', 'https://mm.lv/veikali'), ('Telpas', 'https://mm.lv/telpas'), ('Noliktavas', 'https://mm.lv/noliktavas')
        ]
driver = webdriver.Firefox(options=options, firefox_binary=binary)
# options = Options()
# options.set_headless(True)
# driver = Firefox(executable_path='/usr/local/bin/geckodriver')

INPUT_VALUES = ['103', '103.', '104', '104.', '119', '119.', '467', '467.', '602', '602.', 'Čehu', 'Čehu pr', 'Hrušč', 'Hruščova laika', 'Jaun', 'Jaunceltne', 'Lietuviešu', 'LT proj', 'M. ģim', 'Mazģimeņu', 'P. kara', 'Pirmskara', 'Priv. m', 'Rekonstruēts', 'Renov', 'Specpr', 'Specprojekts', 'Staļina', 'Staļina laika', 'Hruščova', 'Jaunais']
OUTPUT_VALUES = ['103', '103', '104', '104', '119', '119', '467', '467', '602', '602', 'Čehu pr', 'Čehu pr', 'Hruščova laika', 'Hruščova laika', 'Jaun', 'Jaun', 'Lietuviešu', 'Lietuviešu', 'Mazģimeņu', 'Mazģimeņu', 'Pirmskara', 'Pirmskara', 'Priv. m', 'Rekonstruēts', 'Rekonstruēts', 'Specprojekts', 'Specprojekts', 'Staļina laika', 'Staļina laika', 'Hruščova laika', 'Jaun']


def format_series(input):
    if input in INPUT_VALUES:
        return OUTPUT_VALUES[INPUT_VALUES.index(input)]
    else:
        return input


def collect_links():
    links = []
    for link in collect_links_estate():
        links.append(link)
    # for link in collect_links_room():
    #     links.append(('Telpas', link[0], link[1]))
    print(f'Collected {len(links)} links')
    return links


def collect_links_estate():
    links = set()
    for estate in data:
        for page in range(1, 10000):

            if page == 1:
                # req = requests.get(estate[1] + '?all')
                driver.get(estate[1] + '?all')
            else:
                # req = requests.get(f'{estate[1]}/{page}')
                driver.get(f'{estate[1]}/{page}')
            # html = Soup(req.text, features='html.parser')

            # if page != 1 and html.select('.searchPaginationSelected')[0].text == 1:
            if driver.current_url not in [estate[1] + '?all', f'{estate[1]}/{page}']:
                print('exit')
                break

            # for x in html.select('a.link'):
            for x in driver.find_elements_by_css_selector('a.link'):
                # links.add((estate[0], x['href']))
                links.add((estate[0], x.get_attribute('href')))
                print(f'Collecting estate links: {len(links)}')
    return list(links)


def collect_links_room():
    links = set()
    for room in data[-1][-1]:

        for page in range(1, 100000):
            req = requests.get(f'{room[1]}/{page}')
            html = Soup(req.text, features='html.parser')


            if page != 1 and str(page) not in html.select('title')[0].text:
                break
            for x in html.select('a.link'):
                links.add((room[0], x['href']))
                # print(f'Collecting room links: {len(links)}')

    return links


def region_mapping(region):
    a = ['Pļaviņu novads', 'Aizkraukles novads', 'Kokneses novads', 'Jaunjelgavas novads', 'Kokneses novads', 'Jaunjelgavas novads', 'Pļaviņu novads', 'Kokneses novads', 'Vecumnieku novads', 'Neretas novads', 'Pļaviņu novads', 'Jaunjelgavas novads', 'Jaunjelgavas novads', 'Skrīveru novads', 'Jaunjelgavas novads', 'Vecumnieku novads', 'Pļaviņu novads', 'Neretas novads', 'Alūksnes novads', 'Apes novads', 'Baltinavas novads', 'Balvu novads', 'Viļakas novads', 'Rugāju novads', 'Vecumnieku novads', 'Bauskas novads', 'Iecavas novads', 'Rundāles novads', 'Amatas novads', 'Cēsu novads', 'Raunas novads', 'Vecpiebalgas novads', 'Jaunpiebalgas novads', 'Priekuļu novads', 'Līgatnes novads', 'Siguldas novads', 'Pārgaujas novads', 'Daugavpils', 'Daugavpils novads', 'Ilūkstes novads', 'Dobeles novads', 'Auces novads', 'Tērvetes novads', 'Gulbenes novads', 'Jēkabpils novads', 'Aknīstes novads', 'Krustpils novads', 'Viesītes novads', 'Republikas pilsēta', 'Salas novads', 'Jelgava', 'Jelgavas novads', 'Ozolnieku novads', 'Jūrmala', 'Dagdas novads', 'Krāslavas novads', 'Aglonas novads', 'Alsungas novads', 'Kuldīgas novads', 'Skrundas novads', 'Liepāja', 'Aizputes novads', 'Grobiņas novads', 'Priekules novads', 'Durbes novads', 'Rucavas novads', 'Vaiņodes novads', 'Nīcas novads', 'Pāvilostas novads', 'Salacgrīvas novads', 'Alojas novads', 'Limbažu novads', 'Krimuldas novads', 'Ciblas novads', 'Ludzas novads', 'Kārsavas novads', 'Zilupes novads', 'Madonas novads', 'Cesvaines novads', 'Ērgļu novads', 'Lubānas novads', 'Varakļānu novads', 'Ķeguma novads', 'Ikšķiles novads', 'Lielvārdes novads', 'Ogres novads', 'Aglonas novads', 'Līvānu novads', 'Preiļu novads', 'Riebiņu novads', 'Vārkavas novads', 'Rēzekne', 'Rēzeknes novads', 'Viļānu novads', 'Rīga', 'Ādažu novads', 'Siguldas novads', 'Babītes novads', 'Baldones novads', 'Ķekavas novads', 'Carnikavas novads', 'Garkalnes novads', 'Inčukalna novads', 'Krimuldas novads', 'Mālpils novads', 'Mārupes novads', 'Olaines novads', 'Ropažu novads', 'Salaspils novads', 'Saulkrastu novads', 'Sējas novads', 'Stopiņu novads', 'Brocēnu novads', 'Saldus novads', 'Talsu novads', 'Dundagas novads', 'Rojas novads', 'Tukuma novads', 'Engures novads', 'Jaunpils novads', 'Kandavas novads', 'Smiltenes novads', 'Valkas novads', 'Burtnieku novads', 'Strenču novads', 'Beverīnas novads', 'Valmieras novads', 'Beverīnas novads', 'Burtnieku novads', 'Rūjienas novads', 'Naukšēnu novads', 'Mazsalacas novads', 'Republikas pilsēta', 'Ventspils', 'Ventspils novads', '']
    b = ['Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Aizkraukles rajons', 'Alūksnes rajons', 'Alūksnes rajons', 'Balvu rajons', 'Balvu rajons', 'Balvu rajons', 'Balvu rajons', 'Bauskas rajons', 'Bauskas rajons', 'Bauskas rajons', 'Bauskas rajons', 'Cēsu rajons', 'Cēsu rajons', 'Cēsu rajons', 'Cēsu rajons', 'Cēsu rajons', 'Cēsu rajons', 'Cēsu rajons', 'Cēsu rajons', 'Cēsu rajons', 'Daugavpils', 'Daugavpils rajons', 'Daugavpils rajons', 'Dobeles rajons', 'Dobeles rajons', 'Dobeles rajons', 'Gulbenes rajons', 'Jēkabpils rajons', 'Jēkabpils rajons', 'Jēkabpils rajons', 'Jēkabpils rajons', 'Jēkabpils rajons', 'Jēkabpils rajons', 'Jelgava', 'Jelgavas rajons', 'Jēkabpils rajons', 'Jūrmala', 'Krāslavas rajons', 'Krāslavas rajons', 'Krāslavas rajons', 'Kuldīgas rajons', 'Kuldīgas rajons', 'Kuldīgas rajons', 'Liepāja', 'Liepājas rajons', 'Liepājas rajons', 'Liepājas rajons', 'Liepājas rajons', 'Liepājas rajons', 'Liepājas rajons', 'Liepājas rajons', 'Liepājas rajons', 'Limbažu rajons', 'Limbažu rajons', 'Limbažu rajons', 'Limbažu rajons', 'Ludzas rajons', 'Ludzas rajons', 'Ludzas rajons', 'Ludzas rajons', 'Madonas rajons', 'Madonas rajons', 'Madonas rajons', 'Madonas rajons', 'Madonas rajons', 'Ogres rajons', 'Ogres rajons', 'Ogres rajons', 'Ogres rajons', 'Preiļu rajons', 'Preiļu rajons', 'Preiļu rajons', 'Preiļu rajons', 'Preiļu rajons', 'Rēzekne', 'Rēzeknes rajons', 'Rēzeknes rajons', 'Rīga', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Rīgas rajons', 'Saldus rajons', 'Saldus rajons', 'Talsu rajons', 'Talsu rajons', 'Talsu rajons', 'Tukuma rajons', 'Tukuma rajons', 'Tukuma rajons', 'Tukuma rajons', 'Valkas rajons', 'Valkas rajons', 'Valkas rajons', 'Valkas rajons', 'Valkas rajons', 'Valmieras rajons', 'Valmieras rajons', 'Valmieras rajons', 'Valmieras rajons', 'Valmieras rajons', 'Valmieras rajons', 'Valmieras rajons', 'Ventspils', 'Ventspils rajons', '']

    if region in a:
        return b[a.index(region)]
    return region


def parse_one(url):
    # req = requests.get(url)
    # html = Soup(req.text, features='html.parser')
    driver.get(url)

    # detail_label = [x.text.strip() for x in html.select('label.detail_label')]
    # detail_value = [x.text.strip() for x in html.select('label.detail_value')]

    detail_label = [x.text.strip() for x in driver.find_elements_by_css_selector('label.detail_label')]
    detail_value = [x.text.strip() for x in driver.find_elements_by_css_selector('label.detail_value')]

    if 'Kadastra numurs' in detail_label:
        detail_label.remove('Kadastra numurs')

    parse_result = Estate()
    options = ['Darījuma veids', 'Platība', 'Istabu skaits', 'Stāvs', 'Sērija', 'Pilsēta', 'Mikrorajons', 'Adrese',
               'Ēkas tips', 'Reģions', 'Majas platība', 'Zemes platība', 'Stāvu skaits', 'Istabu skaits', 'Garāžas platība', 'Telpas platība']
    options_equivalents = ['deal_type', 'area', 'room_number', 'floor_number', 'series', 'city', 'district',
                           'address', 'house_type', 'region', 'area', 'ground_area', 'count_of_floors', 'room_number', 'area', 'area']

    for o in detail_label:
        try:
            if detail_value[detail_label.index(o)] is not None:
                setattr(parse_result, options_equivalents[options.index(o)], detail_value[detail_label.index(o)])
        except Exception:
            pass

    try:
        if parse_result.city in ['Rīga', 'Jūrmala']:
            parse_result.region = parse_result.city
    except Exception:
        pass

    try:
        parse_result.region = region_mapping(parse_result.region)
    except Exception:
        pass

    if parse_result.city not in ['Rīga', 'Jūrmala']:
        parse_result.district = None

    try:
        if parse_result.deal_type == 'Vēlas īrēt':
            parse_result.deal_type = 'Īrē'
    except Exception:
        pass

    parse_result.ground_area = pretty_value(parse_result.ground_area)
    parse_result.count_of_floors = pretty_value(parse_result.count_of_floors)

    try:
        parse_result.area = float(parse_result.area.split()[0])
    except Exception:
        pass

    try:
        # price = float(html.find('span', {'class': 'currency-value'})['content'])
        price = float(driver.find_element_by_css_selector('span.currency-value').get_attribute('content'))
        parse_result.price = price
    except Exception:
        pass

    try:
        if parse_result.price:
            if parse_result.area:
                price_m2 = parse_result.price / parse_result.area
                parse_result.price_m2 = round(price_m2, 2)
            elif parse_result.ground_area:
                price_m2 = parse_result.price / parse_result.ground_area
                parse_result.price_m2 = round(price_m2, 2)
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

    # if parse_result.district is None:
    #     try:
    #         sel = html.find('li', {'class': 'last-child', 'property': 'itemListElement'}).text.strip()
    #         parse_result.district = sel
    #     except Exception:
    #         pass

    try:
        if len(parse_result.series.split()) > 1:
            parse_result.series = ' '.join(parse_result.series.split()[:-1])
        parse_result.series = format_series(parse_result.series)
    except Exception:
        pass

    parse_result.country = 'LV'
    parse_result.resource = 'mm.lv'

    try:
        # date = html.find('span', {'class': 'date'}).text
        date = driver.find_element_by_css_selector('span.date').text
        if date.count('/') == 2:
            date = date.split('/')
            parse_result.year = int(date[2])
            parse_result.month = int(date[1])
            parse_result.day = int(date[0])
        else:
            parse_result.year = datetime.datetime.now().year
            parse_result.month = datetime.datetime.now().month
            parse_result.day = datetime.datetime.now().day
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
            if 'ha' in x:
                return round(p * 10000, 2)
            else:
                return round(p, 2)
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



def get_exist_links(country, resource):
    exist_links = set()
    exist_data = db[country].find({'resource': resource})
    for x in exist_data:
        exist_links.add(x['link'])

    return list(exist_links)


def unique(data):
    exist_links = get_exist_links('latvia', 'mm.lv')
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


def save(data, country):
    db[country].insert_many(data)


if __name__ == '__main__':
    c = 'mongodb+srv://smartdataestate:estate4628134@estate-dqksq.gcp.mongodb.net/test?retryWrites=true&w=majority'
    client = pymongo.MongoClient(c)
    db = client.Estate

    data = main()

    db.latvia.insert_many(data)
