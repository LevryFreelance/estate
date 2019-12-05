import time

from bs4 import BeautifulSoup
from queue import Queue
from requests import get
from threading import Thread
from dataclasses import dataclass
from selenium.webdriver import PhantomJS

options = PhantomJS()


def new_driver():
    return PhantomJS()


domains = ['lv', 'ee']

category_count = {'lv': 5, 'ee': 7}


def base_url(domain: str):
    return 'https://www.city24.{}/en/'.format(domain)


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
    try:
        driver = new_driver()

        driver_get(driver, list_url('lv', 0))

        driver.find_element_by_css_selector(
            '#ttContainer > .SumoSelect').click()
        time.sleep(10)
        driver.save_screenshot('a.png')
        for option in driver.find_elements_by_css_selector(
                '#ttContainer > .SumoSelect .opt:not(.disabled)'):
            option.click()

        driver.find_element_by_css_selector(
            '.new-search__object-type p.SelectBox').click()

        driver.find_elements_by_css_selector(
            '.new-search__object-type li.opt')[category].click()

        return export_cookies(driver)
    finally:
        driver.close()


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


@dataclass
class Item:
    url: str
    price: str
    price_sqr_m: str
    area: str
    city: str
    deal_type: str
    country: str
    resource: str
    floor: str
    total_floors: str
    kad_number: str
    ground_area: str
    series: str
    year: str
    rooms: str
    purpose: str


def get_text(soup, selector: str) -> str:
    try:
        return soup.select_one(selector).text
    except Exception:
        return ''


needed_item_facts = {
    'Floor / Total floors:': 'floor/total_floors',
    'Cadaster number:': 'kad_number',
    'Plot size:': 'ground_area',
    'House Type:': 'series',
    'Construction year:': 'year',
    'Purpose of use:': 'purpose',
    'Direct reference:': 'link'
}


def parse_combined_span(text: str) -> []:
    [area_info, deal_type] = [x.strip() for x in text.split('|')]

    parts = [part.strip() for part in area_info.split(',')]

    yield deal_type

    yield parts[0]

    yield parts[1] if len(parts) > 1 else ''


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
    yield get_text(soup, 'span.price')
    yield get_text(soup, 'span.priceSqrM')
    for x in parse_combined_span(get_text(soup,
                                          '.itemTitleColumnRight > h3 > span'
                                          )):
        yield x
    yield get_text(soup, '.itemTitleColumnLeft > h3')

    facts = {header: ''.join(list(filter(lambda ch: ch != '\n', value)))
             for header, value in parse_item_facts(soup)}

    keys = list(needed_item_facts.values()) + ['floor', 'total_floors']

    for key in keys[1:]:
        yield facts[key] if key in facts else ''


def get_domain(url: str):
    return url.split('/')[2]


def get_root_domain(domain: str):
    return domain.split('.')[-1]


def parse_item(url: str) -> Item:
    soup = BeautifulSoup(get(url).text, 'html.parser')

    domain = get_domain(url)
    root_domain = get_root_domain(domain)

    [price, price_sqr_m, deal_type,
        area, rooms, city,
        kad_number, ground_area, series, year,
        purpose, link, floor, total_floors] = list(item_generator(soup))

    return Item(url if link is None else link,
                price,
                price_sqr_m,
                area,
                city,
                deal_type,
                {'lv': 'Latvia', 'ee': 'Estonia'}[root_domain],
                domain[4:] if domain.startswith('www.') else domain,
                floor,
                total_floors,
                kad_number,
                ground_area,
                series,
                year,
                rooms,
                purpose)


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


def item_links_generator():
    for domain in domains:
        for category in range(category_count[domain]):
            cookies = get_cookies(domain, category)

            soup = fetch_list_page(domain, 0, cookies)

            for page in range(find_max_page_number(soup)):
                if page != 0:
                    soup = fetch_list_page(domain, page, cookies)

                for a in soup.select('.result .addressLink[href]'):
                    link: str = a['href']

                    if link.startswith('http'):
                        yield link
                    else:
                        yield '{}{}'.format(base_url(domain),
                                            link[6:]
                                            if link.startswith('../en/')
                                            else
                                            link[1:]
                                            if link.startswith('/')
                                            else
                                            link)


if __name__ == '__main__':
    for link in item_links_generator():
        print(parse_item(link))
