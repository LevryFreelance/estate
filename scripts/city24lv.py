import datetime
import sys

import pymongo

sys.path.append("..")

from bs4 import BeautifulSoup
from queue import Queue
from requests import get
from threading import Thread
from dataclass.estate import Estate
from controllers.format_series import format_series
from controllers import db

import re
from selenium.webdriver import Firefox, FirefoxProfile, FirefoxOptions
from selenium.webdriver import PhantomJS
# driver = webdriver.Firefox()
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

binary = FirefoxBinary('../geckodriver.exe')
options = Options()
options.headless = True

# options = FirefoxOptions()
# options.set_headless(True)
#
# profile = FirefoxProfile()
# profile.set_preference('permissions.default.image', 2)
# profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')


def new_driver():
    return Firefox(options=options, firefox_binary=binary)
    # return Firefox(options=options, firefox_profile=profile)


domains = ['lv', 'ee']

category_count = {'lv': 4, 'ee': 7}


def base_url(domain: str):
    if domain == 'lv':
        return 'https://www.city24.{}/lv/'.format(domain)
    if domain == 'ee':
        return 'https://www.city24.{}/et/'.format(domain)


def list_url(domain: str, page):
    return '{}list?fr={}'.format(base_url(domain), page)


def export_cookies(driver):
    cookies = {cookie['name']: cookie['value']
               for cookie
               in driver.get_cookies()}

    return cookies


def driver_get(driver, url: str):
    try:
        driver.get(url)
    except Exception:
        driver_get(driver, url)


def lv_get_cookies(category):
    # try:
        driver = new_driver()
        print(driver)
        driver_get(driver, list_url('lv', 0))
        # print(driver.page_source)
        import time

        driver.find_element_by_css_selector(
            '#ttContainer > .SumoSelect > select').click()

        # driver.execute_script("var a = document.querySelector('iframe')[0]; a.remove()")

        driver.save_screenshot('a.png')
        for option in driver.find_elements_by_css_selector(
                '#ttContainer > .SumoSelect .opt:not(.disabled)'):
            option.click()

        driver.find_element_by_css_selector(
            '.new-search__object-type p.SelectBox').click()

        driver.find_elements_by_css_selector(
            '.new-search__object-type li.opt')[category].click()

        return export_cookies(driver)
    # finally:
    #     print('eee')
    #     driver.close()


def ee_get_cookies(category):
    try:
        driver = new_driver()

        driver_get(driver, list_url('ee', 0))

        for li in driver.find_elements_by_css_selector(
                '.selectFirst > ul > li > label')[1:]:
            li.click()

        driver.find_element_by_css_selector(
            '.selectFirstProperty > select').click()

        driver.find_elements_by_css_selector(
            '.selectFirstProperty > select > option')[category].click()

        return export_cookies(driver)
    finally:
        driver.close()


def get_text(soup, selector: str) -> str:
    try:
        return soup.select_one(selector).text
    except Exception:
        return None


needed_item_facts = {
    'Stāvs/Stāvi:': 'floor/total_floors',
    'Kadastra numurs:': 'kad_number',
    'Zemes platība:': 'ground_area',
    'Mājas sērija:': 'series',
    'Mājas tips:': 'house_type',
    'Pielietošanas mērķis:': 'purpose',
    'Tiešā norāde:': 'link'
}


def parse_combined_span(text: str) -> []:
    area_info = text.split('|')[0].strip()

    parts = [part.strip() for part in area_info.split(',')]

    if len(parts) == 1:
        if 'ista' in parts[0]:
            yield None
            yield parts[0]
        else:
            yield parts[0]
            yield None
    else:
        yield parts[0]
        yield parts[1]

    # yield parts[0]
    #
    # yield parts[1] if len(parts) > 1 else None


def parse_item_facts(soup: BeautifulSoup):
    for header, value in (
        zip([th.text for th in soup.select(
                '.itemFacts th:not([colspan=\'2\']) > span:first-child')],
            [td.text for td in soup.select(
                '.itemFacts td > span:first-child')])):
        if header in needed_item_facts:
            _header = needed_item_facts[header]
            if _header == 'floor/total_floors':
                parts = [part.strip() for part in value.split('/')]
                yield ('floor', parts[0])
                yield ('total_floors', parts[1] if len(parts) > 1 else '')
            else:
                yield (needed_item_facts[header], value)


def item_generator(soup: BeautifulSoup):
    district_text = get_text(soup, '.itemTitleColumnLeft > h1')
    do_not_need = get_text(soup, '.itemTitleColumnLeft > h1 > span')
    district_text = district_text.replace(do_not_need, '').strip()
    if ',' in district_text:
        if len(district_text.split(',')) > 2:
            street, district = district_text.split(',')[-2:]
        else:
            street, district = district_text.split(',')
        yield street.strip()
        yield district.strip()
    else:
        yield district_text
        yield None

    yield get_text(soup, 'span.price')
    yield get_text(soup, 'span.priceSqrM')

    for x in parse_combined_span(get_text(soup,
                                          '.itemTitleColumnRight > h3 > span')):
        yield x
    yield get_text(soup, '.itemTitleColumnLeft > h3')

    facts = {header: ''.join(list(filter(lambda ch: ch != '\n', value)))
             for header, value in parse_item_facts(soup)}

    keys = list(needed_item_facts.values()) + ['floor', 'total_floors']

    for key in keys[1:]:
        yield facts[key] if key in facts else None


def get_domain(url: str):
    return url.split('/')[2]


def get_root_domain(domain: str):
    return domain.split('.')[-1]


def parse_item(url: str) -> Estate:
    # print(url)
    soup = BeautifulSoup(get(url).text, 'html.parser')

    # print(soup)
    if 'Lapa netika atrasta (kļūda 410)' in soup.text:
        print(url, '----------------------------------------------')
        return Estate()

    domain = get_domain(url)
    root_domain = get_root_domain(domain)

    [street, district, price, price_sqr_m,
        area, rooms, city,
        kad_number, ground_area, series, house_type,
        purpose, link, floor, total_floors] = list(item_generator(soup))

    city = city.split(',')[0]

    price = pretty_value(price)
    area = pretty_value(area)
    price_sqr_m = pretty_value(price_sqr_m)
    rooms = pretty_value(rooms)
    floor = pretty_value(floor)
    total_floors = pretty_value(total_floors)
    ground_area = pretty_value(ground_area)

    if series is not None:
        series = series.replace(' projekts', '')
        series = series.replace(' pr', '')
        series = series.replace('sērija', '')
        series = series.strip()
        if series.endswith('.'):
            series = series[:-1]
        series = format_series(series)

    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day

    if price_sqr_m is None and (price is not None and area is not None):
        price_sqr_m = str(price / area)
        if price_sqr_m.endswith('.0'):
            price_sqr_m = int(price_sqr_m[:-2])
        else:
            try:
                price_sqr_m = float(price_sqr_m[:price_sqr_m.index('.') + 3])
            except IndexError:
                price_sqr_m = float(price_sqr_m)

    if city in ['Rīga','Jūrmala']:
        region = city
    else:
        region = None
        district = None

    return Estate(link=url if link is None else link,
                price=price,
                price_m2=price_sqr_m,
                area=area,
                region=region,
                city=city,
                district=district,
                address=street,
                country={'lv': 'LV', 'ee': 'EE'}[root_domain],
                resource=domain[4:] if domain.startswith('www.') else domain,
                floor_number=floor,
                count_of_floors=total_floors,
                kad_number=kad_number,
                ground_area=ground_area,
                series=series,
                house_type=house_type,
                room_number=rooms,
                purpose=purpose,
                year=year,
                month=month,
                day=day)


def change_type(x):
    house_type = None
    deal_type = None

    if 'zīvokli' in x:
        house_type = 'Dzīvokli'
    elif 'āja' in x:
        house_type = 'Mājas'
    elif 'omerc' in x:
        house_type = 'Komerc'
    elif 'eme' in x:
        house_type = 'Zeme'

    if 'Pārdod' in x:
        deal_type = 'Pārdod'
    elif 'Izīrē' in x:
        deal_type = 'Izīrē'
    elif 'īrē' in x:
        deal_type = 'Īrē'
    # print(house_type, deal_type)
    return house_type, deal_type


def worker(queue: Queue):
    while not queue.empty():
        yield parse_item(queue.get())


def worker_wrapper(links_queue: Queue, processed_queue: Queue):
    for result in worker(links_queue):
        processed_queue.put(result)


def worker_thread(links_queue: Queue, processed_queue: Queue) -> Thread:
    return Thread(target=worker_wrapper, args=(links_queue, processed_queue))


def get_cookies(domain: str, category: int) -> dict:
    return {'lv': lv_get_cookies, 'ee': ee_get_cookies}[domain](category)


def fetch_list_page(domain: str, page: int, cookies: dict) -> BeautifulSoup:
    return BeautifulSoup(get(list_url(domain, page), cookies=cookies).text,
                         'html.parser')


def find_max_page_number(soup: BeautifulSoup) -> int:
    return int(soup.select('.resultPager li a.page strong')[-1].text)


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


def item_links_generator():
    for domain in domains:
        # print(domain)
        for category in range(category_count[domain]):
            # print(category)
            cookies = get_cookies(domain, category)
            # print(cookies)
            soup = fetch_list_page(domain, 0, cookies)

            for page in range(find_max_page_number(soup)):
                if page != 0:
                    soup = fetch_list_page(domain, page, cookies)

                for a in soup.select('.result .addressLink[href]'):
                    link: str = a['href']

                    # print(link)
                    if link.startswith('http'):
                        yield link
                    else:

                        yield '{}{}'.format(base_url(domain),
                                            link[6:]
                                            if link.startswith('../lv/')
                                            else
                                            link[1:]
                                            if link.startswith('/')
                                            else
                                            link)


def collect_links():
    print('city24lv collecting links')
    all_links = set()
    driver = new_driver()

    deal_list = ['pardod', 'izire']
    deal_list_label = ['Pārdod', 'Izīrē']
    property_list = ['dzivoklis', 'maja', 'zeme', 'komercplatiba/birojs', 'komercplatiba/loft-birojs', 'komercplatiba/birojs-noliktava']
    property_list_label = ['Dzīvokļi', 'Mājas', 'Zeme', 'Biroji', 'Loft biroji', 'Noliktava']


    property_list = ['dzivoklis', 'maja', 'zeme', 'komercplatiba/birojs']
    property_list_label = ['Dzīvokļi', 'Mājas', 'Zeme', 'Biroji']
    for property, property_label in zip(property_list, property_list_label):
        for deal, deal_label in zip(deal_list, deal_list_label):
            print(f'https://www.city24.lv/lv/saraksts/{deal}/{property}')
            # print(property, deal)
            # driver.get(f'https://www.city24.lv/lv/saraksts/{deal}/{property}')
            html = BeautifulSoup(get(f'https://www.city24.lv/lv/saraksts/{deal}/{property}').text, features='html.parser')
            # print(req.text)
            # links = driver.find_elements_by_css_selector('.dots a.page')
            last_page = int(html.find_all("a", class_="page")[-2].get_text())
            # print(driver.page_source)
            # pages_num = [x.text for x in links if x.text != '']
            # # print(pages_num)
            # while not pages_num[-1].isdigit():
            #     del pages_num[-1]
            # last_page = int(pages_num[-1])
            for page in range(last_page):
                # print("!!!!!!!!!!  3   !!!!!!!!")
                html = BeautifulSoup(get(f'https://www.city24.lv/lv/saraksts/{deal}/{property}?fr={str(page)}').text, features='html.parser')
                # driver.get('https://www.city24.lv/lv/saraksts?fr=' + str(page))

                links = html.find_all("a", class_='addressLink')
                # links = driver.find_elements_by_class_name('addressLink')
                for el in links:
                    # print("!!!!!!!!!!  4   !!!!!!!!")
                    l = el['href'].replace('?selectedTabMenu=list', '')
                    if ';' in l:
                        l = l.split(';')[0]
                    l = l.replace('../', '')
                    if 'https://www.city24.lv/' not in l:
                        l = 'https://www.city24.lv/' + l
                    all_links.add((property_label, deal_label, l))
                    # print(len(all_links))
                    # print(l)
                    # all_links.add((property_label, deal_label, el.get_attribute('href')))

                # if len(all_links) > 8000:
                #     return all_links
                # print(len(all_links), len(lll))
    return all_links


def unique(data):
    exist_links = db.get_exist_links('latvia', 'city24.lv')
    unique = []
    for x in data:
        if x[-1] not in exist_links:
            # print(x, x in exist_links)
            unique.append(x)
    return unique


def main():
    links = collect_links()
    print('Links: ', len(links))
    links = unique(links)
    print('Unique: ', len(links))

    all = []
    for link in links:
        try:
            parsed = parse_item(link[-1])
            parsed.property_type = link[0]
            parsed.deal_type = link[1]

            all.append(parsed.to_list())
            print(len(all))
        except:
            print(link)

    return all


if __name__ == '__main__':
    # data = main()
    c = 'mongodb+srv://smartdataestate:estate4628134@estate-dqksq.gcp.mongodb.net/test?retryWrites=true&w=majority'
    client = pymongo.MongoClient(c)
    db = client.Estate

    d = list(db.latvia.find({'resource': 'mm.lv'}))

    import pandas as pd

    pd.DataFrame(d).to_excel('mm.xlsx')
