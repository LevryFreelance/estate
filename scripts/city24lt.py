import requests
from bs4 import BeautifulSoup as Soup


html = Soup(requests.get('https://www.city24.ee/en/real-estate/apartments-for-sale/Tallinn-Lasnamae-linnaosa/3981208').text, features='html.parser')

print(html)