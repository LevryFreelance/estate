# -*- coding: utf-8 -*-
import sys
sys.path.append("..")


import requests
import datetime
from bs4 import BeautifulSoup as Soup
import pandas as pd
from dataclass.estate import Estate
import time
import re
from controllers import db
from controllers.format_series import format_series


LV_ESTATE = [('Dzīvokļi', 'Rīga', 'https://www.ss.com/lv/real-estate/flats/riga/all/'), ('Dzīvokļi', 'Jūrmala', 'https://www.ss.com/lv/real-estate/flats/jurmala/all/'), ('Dzīvokļi', 'Rīgas rajons', 'https://www.ss.com/lv/real-estate/flats/riga-region/all/'), ('Dzīvokļi', 'Aizkraukle un rajons', 'https://www.ss.com/lv/real-estate/flats/aizkraukle-and-reg/all/'), ('Dzīvokļi', 'Alūksne un rajons', 'https://www.ss.com/lv/real-estate/flats/aluksne-and-reg/all/'), ('Dzīvokļi', 'Balvi un rajons', 'https://www.ss.com/lv/real-estate/flats/balvi-and-reg/all/'), ('Dzīvokļi', 'Bauska un rajons', 'https://www.ss.com/lv/real-estate/flats/bauska-and-reg/all/'), ('Dzīvokļi', 'Cēsis un rajons', 'https://www.ss.com/lv/real-estate/flats/cesis-and-reg/all/'), ('Dzīvokļi', 'Daugavpils un rajons', 'https://www.ss.com/lv/real-estate/flats/daugavpils-and-reg/all/'), ('Dzīvokļi', 'Dobele un rajons', 'https://www.ss.com/lv/real-estate/flats/dobele-and-reg/all/'), ('Dzīvokļi', 'Gulbene un rajons', 'https://www.ss.com/lv/real-estate/flats/gulbene-and-reg/all/'), ('Dzīvokļi', 'Jēkabpils un rajons', 'https://www.ss.com/lv/real-estate/flats/jekabpils-and-reg/all/'), ('Dzīvokļi', 'Jelgava un rajons', 'https://www.ss.com/lv/real-estate/flats/jelgava-and-reg/all/'), ('Dzīvokļi', 'Krāslava un rajons', 'https://www.ss.com/lv/real-estate/flats/kraslava-and-reg/all/'), ('Dzīvokļi', 'Kuldīga un rajons', 'https://www.ss.com/lv/real-estate/flats/kuldiga-and-reg/all/'), ('Dzīvokļi', 'Liepāja un rajons', 'https://www.ss.com/lv/real-estate/flats/liepaja-and-reg/all/'), ('Dzīvokļi', 'Limbaži un rajons', 'https://www.ss.com/lv/real-estate/flats/limbadzi-and-reg/all/'), ('Dzīvokļi', 'Ludza un rajons', 'https://www.ss.com/lv/real-estate/flats/ludza-and-reg/all/'), ('Dzīvokļi', 'Madona un rajons', 'https://www.ss.com/lv/real-estate/flats/madona-and-reg/all/'), ('Dzīvokļi', 'Ogre un rajons', 'https://www.ss.com/lv/real-estate/flats/ogre-and-reg/all/'), ('Dzīvokļi', 'Preiļi un rajons', 'https://www.ss.com/lv/real-estate/flats/preili-and-reg/all/'), ('Dzīvokļi', 'Rēzekne un rajons', 'https://www.ss.com/lv/real-estate/flats/rezekne-and-reg/all/'), ('Dzīvokļi', 'Saldus un rajons', 'https://www.ss.com/lv/real-estate/flats/saldus-and-reg/all/'), ('Dzīvokļi', 'Talsi un rajons', 'https://www.ss.com/lv/real-estate/flats/talsi-and-reg/all/'), ('Dzīvokļi', 'Tukums un rajons', 'https://www.ss.com/lv/real-estate/flats/tukums-and-reg/all/'), ('Dzīvokļi', 'Valka un rajons', 'https://www.ss.com/lv/real-estate/flats/valka-and-reg/all/'), ('Dzīvokļi', 'Valmiera un rajons', 'https://www.ss.com/lv/real-estate/flats/valmiera-and-reg/all/'), ('Dzīvokļi', 'Ventspils un rajons', 'https://www.ss.com/lv/real-estate/flats/ventspils-and-reg/all/'), ('Mājas', 'Rīga', 'https://www.ss.com/lv/real-estate/homes-summer-residences/riga/all/'), ('Mājas', 'Jūrmala', 'https://www.ss.com/lv/real-estate/homes-summer-residences/jurmala/all/'), ('Mājas', 'Rīgas rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/riga-region/all/'), ('Mājas', 'Aizkraukle un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/aizkraukle-and-reg/all/'), ('Mājas', 'Alūksne un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/aluksne-and-reg/all/'), ('Mājas', 'Balvi un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/balvi-and-reg/all/'), ('Mājas', 'Bauska un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/bauska-and-reg/all/'), ('Mājas', 'Cēsis un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/cesis-and-reg/all/'), ('Mājas', 'Daugavpils un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/daugavpils-and-reg/all/'), ('Mājas', 'Dobele un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/dobele-and-reg/all/'), ('Mājas', 'Gulbene un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/gulbene-and-reg/all/'), ('Mājas', 'Jēkabpils un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/jekabpils-and-reg/all/'), ('Mājas', 'Jelgava un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/jelgava-and-reg/all/'), ('Mājas', 'Krāslava un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/kraslava-and-reg/all/'), ('Mājas', 'Kuldīga un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/kuldiga-and-reg/all/'), ('Mājas', 'Liepāja un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/liepaja-and-reg/all/'), ('Mājas', 'Limbaži un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/limbadzi-and-reg/all/'), ('Mājas', 'Ludza un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/ludza-and-reg/all/'), ('Mājas', 'Madona un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/madona-and-reg/all/'), ('Mājas', 'Ogre un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/ogre-and-reg/all/'), ('Mājas', 'Preiļi un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/preili-and-reg/all/'), ('Mājas', 'Rēzekne un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/rezekne-and-reg/all/'), ('Mājas', 'Saldus un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/saldus-and-reg/all/'), ('Mājas', 'Talsi un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/talsi-and-reg/all/'), ('Mājas', 'Tukums un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/tukums-and-reg/all/'), ('Mājas', 'Valka un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/valka-and-reg/all/'), ('Mājas', 'Valmiera un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/valmiera-and-reg/all/'), ('Mājas', 'Ventspils un rajons', 'https://www.ss.com/lv/real-estate/homes-summer-residences/ventspils-and-reg/all/'), ('Viensētas', 'Rīgas rajons', 'https://www.ss.com/lv/real-estate/farms-estates/riga-region/all/'), ('Viensētas', 'Aizkraukle un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/aizkraukle-and-reg/all/'), ('Viensētas', 'Alūksne un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/aluksne-and-reg/all/'), ('Viensētas', 'Balvi un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/balvi-and-reg/all/'), ('Viensētas', 'Bauska un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/bauska-and-reg/all/'), ('Viensētas', 'Cēsis un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/cesis-and-reg/all/'), ('Viensētas', 'Daugavpils un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/daugavpils-and-reg/all/'), ('Viensētas', 'Dobele un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/dobele-and-reg/all/'), ('Viensētas', 'Gulbene un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/gulbene-and-reg/all/'), ('Viensētas', 'Jēkabpils un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/jekabpils-and-reg/all/'), ('Viensētas', 'Jelgava un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/jelgava-and-reg/all/'), ('Viensētas', 'Krāslava un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/kraslava-and-reg/all/'), ('Viensētas', 'Kuldīga un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/kuldiga-and-reg/all/'), ('Viensētas', 'Liepāja un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/liepaja-and-reg/all/'), ('Viensētas', 'Limbaži un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/limbadzi-and-reg/all/'), ('Viensētas', 'Ludza un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/ludza-and-reg/all/'), ('Viensētas', 'Madona un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/madona-and-reg/all/'), ('Viensētas', 'Ogre un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/ogre-and-reg/all/'), ('Viensētas', 'Preiļi un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/preili-and-reg/all/'), ('Viensētas', 'Rēzekne un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/rezekne-and-reg/all/'), ('Viensētas', 'Saldus un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/saldus-and-reg/all/'), ('Viensētas', 'Talsi un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/talsi-and-reg/all/'), ('Viensētas', 'Tukums un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/tukums-and-reg/all/'), ('Viensētas', 'Valka un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/valka-and-reg/all/'), ('Viensētas', 'Valmiera un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/valmiera-and-reg/all/'), ('Viensētas', 'Ventspils un rajons', 'https://www.ss.com/lv/real-estate/farms-estates/ventspils-and-reg/all/'), ('Telpas', 'Angāri', 'https://www.ss.com/lv/real-estate/premises/hangars/all/'), ('Telpas', 'Bēniņi', 'https://www.ss.com/lv/real-estate/premises/garrets/all/'), ('Telpas', 'Celtnes un kompleksi', 'https://www.ss.com/lv/real-estate/premises/buildings-and-complexes/all/'), ('Telpas', 'Darbnīcas', 'https://www.ss.com/lv/real-estate/premises/workshops/all/'), ('Telpas', 'Garāžas', 'https://www.ss.com/lv/real-estate/premises/garages/all/'), ('Telpas', 'Noliktavas un glabātuves', 'https://www.ss.com/lv/real-estate/premises/storehouses-and-storages/all/'), ('Telpas', 'Pagrabi un puspagrabi', 'https://www.ss.com/lv/real-estate/premises/basements-and-semi-basements/all/'), ('Telpas', 'Penthausi', 'https://www.ss.com/lv/real-estate/premises/penthouses/all/'), ('Telpas', 'Pirtis', 'https://www.ss.com/lv/real-estate/premises/bathhouses/all/'), ('Telpas', 'Ražošanas telpas', 'https://www.ss.com/lv/real-estate/premises/production-facilities/all/'), ('Telpas', 'Restorāni, kafejnīcas, ēdnīcas', 'https://www.ss.com/lv/real-estate/premises/restaurants-cafe-dining-halls/all/'), ('Telpas', 'Saimniecības ēkas', 'https://www.ss.com/lv/real-estate/premises/household-buildings/all/'), ('Telpas', 'Saloni', 'https://www.ss.com/lv/real-estate/premises/saloons/all/'), ('Telpas', 'Spēļu zāles', 'https://www.ss.com/lv/real-estate/premises/playing-halls/all/'), ('Telpas', 'Sporta zāles', 'https://www.ss.com/lv/real-estate/premises/training-halls/all/'), ('Telpas', 'Telpas autoservisiem', 'https://www.ss.com/lv/real-estate/premises/premises-for-service-centers/all/'), ('Telpas', 'Veikali', 'https://www.ss.com/lv/real-estate/premises/shops/all/'), ('Biroji', 'Rīga', 'https://www.ss.com/lv/real-estate/offices/riga/all/'), ('Biroji', 'Jūrmala', 'https://www.ss.com/lv/real-estate/offices/jurmala/all/'), ('Biroji', 'Rīgas rajons', 'https://www.ss.com/lv/real-estate/offices/riga-region/all/'), ('Biroji', 'Aizkraukle un rajons', 'https://www.ss.com/lv/real-estate/offices/aizkraukle-and-reg/all/'), ('Biroji', 'Alūksne un rajons', 'https://www.ss.com/lv/real-estate/offices/aluksne-and-reg/all/'), ('Biroji', 'Balvi un rajons', 'https://www.ss.com/lv/real-estate/offices/balvi-and-reg/all/'), ('Biroji', 'Bauska un rajons', 'https://www.ss.com/lv/real-estate/offices/bauska-and-reg/all/'), ('Biroji', 'Cēsis un rajons', 'https://www.ss.com/lv/real-estate/offices/cesis-and-reg/all/'), ('Biroji', 'Daugavpils un rajons', 'https://www.ss.com/lv/real-estate/offices/daugavpils-and-reg/all/'), ('Biroji', 'Dobele un rajons', 'https://www.ss.com/lv/real-estate/offices/dobele-and-reg/all/'), ('Biroji', 'Gulbene un rajons', 'https://www.ss.com/lv/real-estate/offices/gulbene-and-reg/all/'), ('Biroji', 'Jēkabpils un rajons', 'https://www.ss.com/lv/real-estate/offices/jekabpils-and-reg/all/'), ('Biroji', 'Jelgava un rajons', 'https://www.ss.com/lv/real-estate/offices/jelgava-and-reg/all/'), ('Biroji', 'Krāslava un rajons', 'https://www.ss.com/lv/real-estate/offices/kraslava-and-reg/all/'), ('Biroji', 'Kuldīga un rajons', 'https://www.ss.com/lv/real-estate/offices/kuldiga-and-reg/all/'), ('Biroji', 'Liepāja un rajons', 'https://www.ss.com/lv/real-estate/offices/liepaja-and-reg/all/'), ('Biroji', 'Limbaži un rajons', 'https://www.ss.com/lv/real-estate/offices/limbadzi-and-reg/all/'), ('Biroji', 'Ludza un rajons', 'https://www.ss.com/lv/real-estate/offices/ludza-and-reg/all/'), ('Biroji', 'Madona un rajons', 'https://www.ss.com/lv/real-estate/offices/madona-and-reg/all/'), ('Biroji', 'Ogre un rajons', 'https://www.ss.com/lv/real-estate/offices/ogre-and-reg/all/'), ('Biroji', 'Preiļi un rajons', 'https://www.ss.com/lv/real-estate/offices/preili-and-reg/all/'), ('Biroji', 'Rēzekne un rajons', 'https://www.ss.com/lv/real-estate/offices/rezekne-and-reg/all/'), ('Biroji', 'Saldus un rajons', 'https://www.ss.com/lv/real-estate/offices/saldus-and-reg/all/'), ('Biroji', 'Tukums un rajons', 'https://www.ss.com/lv/real-estate/offices/tukums-and-reg/all/'), ('Biroji', 'Valka un rajons', 'https://www.ss.com/lv/real-estate/offices/valka-and-reg/all/'), ('Biroji', 'Valmiera un rajons', 'https://www.ss.com/lv/real-estate/offices/valmiera-and-reg/all/'), ('Biroji', 'Ventspils un rajons', 'https://www.ss.com/lv/real-estate/offices/ventspils-and-reg/all/'), ('Zeme', 'Rīga', 'https://www.ss.com/lv/real-estate/plots-and-lands/riga/all/'), ('Zeme', 'Jūrmala', 'https://www.ss.com/lv/real-estate/plots-and-lands/jurmala/all/'), ('Zeme', 'Rīgas rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/riga-region/all/'), ('Zeme', 'Aizkraukle un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/aizkraukle-and-reg/all/'), ('Zeme', 'Alūksne un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/aluksne-and-reg/all/'), ('Zeme', 'Balvi un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/balvi-and-reg/all/'), ('Zeme', 'Bauska un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/bauska-and-reg/all/'), ('Zeme', 'Cēsis un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/cesis-and-reg/all/'), ('Zeme', 'Daugavpils un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/daugavpils-and-reg/all/'), ('Zeme', 'Dobele un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/dobele-and-reg/all/'), ('Zeme', 'Gulbene un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/gulbene-and-reg/all/'), ('Zeme', 'Jēkabpils un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/jekabpils-and-reg/all/'), ('Zeme', 'Jelgava un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/jelgava-and-reg/all/'), ('Zeme', 'Krāslava un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/kraslava-and-reg/all/'), ('Zeme', 'Kuldīga un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/kuldiga-and-reg/all/'), ('Zeme', 'Liepāja un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/liepaja-and-reg/all/'), ('Zeme', 'Limbaži un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/limbadzi-and-reg/all/'), ('Zeme', 'Ludza un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/ludza-and-reg/all/'), ('Zeme', 'Madona un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/madona-and-reg/all/'), ('Zeme', 'Ogre un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/ogre-and-reg/all/'), ('Zeme', 'Preiļi un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/preili-and-reg/all/'), ('Zeme', 'Rēzekne un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/rezekne-and-reg/all/'), ('Zeme', 'Saldus un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/saldus-and-reg/all/'), ('Zeme', 'Talsi un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/talsi-and-reg/all/'), ('Zeme', 'Tukums un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/tukums-and-reg/all/'), ('Zeme', 'Valka un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/valka-and-reg/all/'), ('Zeme', 'Valmiera un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/valmiera-and-reg/all/'), ('Zeme', 'Ventspils un rajons', 'https://www.ss.com/lv/real-estate/plots-and-lands/ventspils-and-reg/all/')]
# RU_ESTATE = [('Квартиры', 'Рига', 'https://www.ss.com/ru/real-estate/flats/riga/all/'), ('Квартиры', 'Юрмала', 'https://www.ss.com/ru/real-estate/flats/jurmala/all/'), ('Квартиры', 'Рижский район', 'https://www.ss.com/ru/real-estate/flats/riga-region/all/'), ('Квартиры', 'Айзкраукле и район', 'https://www.ss.com/ru/real-estate/flats/aizkraukle-and-reg/all/'), ('Квартиры', 'Алуксне и район', 'https://www.ss.com/ru/real-estate/flats/aluksne-and-reg/all/'), ('Квартиры', 'Балви и район', 'https://www.ss.com/ru/real-estate/flats/balvi-and-reg/all/'), ('Квартиры', 'Бауска и район', 'https://www.ss.com/ru/real-estate/flats/bauska-and-reg/all/'), ('Квартиры', 'Валка и район', 'https://www.ss.com/ru/real-estate/flats/valka-and-reg/all/'), ('Квартиры', 'Валмиера и район', 'https://www.ss.com/ru/real-estate/flats/valmiera-and-reg/all/'), ('Квартиры', 'Вентспилс и район', 'https://www.ss.com/ru/real-estate/flats/ventspils-and-reg/all/'), ('Квартиры', 'Гулбене и район', 'https://www.ss.com/ru/real-estate/flats/gulbene-and-reg/all/'), ('Квартиры', 'Даугавпилс и район', 'https://www.ss.com/ru/real-estate/flats/daugavpils-and-reg/all/'), ('Квартиры', 'Добеле и район', 'https://www.ss.com/ru/real-estate/flats/dobele-and-reg/all/'), ('Квартиры', 'Екабпилс и район', 'https://www.ss.com/ru/real-estate/flats/jekabpils-and-reg/all/'), ('Квартиры', 'Елгава и район', 'https://www.ss.com/ru/real-estate/flats/jelgava-and-reg/all/'), ('Квартиры', 'Краславa и район', 'https://www.ss.com/ru/real-estate/flats/kraslava-and-reg/all/'), ('Квартиры', 'Кулдига и район', 'https://www.ss.com/ru/real-estate/flats/kuldiga-and-reg/all/'), ('Квартиры', 'Лиепая и район', 'https://www.ss.com/ru/real-estate/flats/liepaja-and-reg/all/'), ('Квартиры', 'Лимбажи и район', 'https://www.ss.com/ru/real-estate/flats/limbadzi-and-reg/all/'), ('Квартиры', 'Лудза и район', 'https://www.ss.com/ru/real-estate/flats/ludza-and-reg/all/'), ('Квартиры', 'Мадона и район', 'https://www.ss.com/ru/real-estate/flats/madona-and-reg/all/'), ('Квартиры', 'Огре и район', 'https://www.ss.com/ru/real-estate/flats/ogre-and-reg/all/'), ('Квартиры', 'Прейли и район', 'https://www.ss.com/ru/real-estate/flats/preili-and-reg/all/'), ('Квартиры', 'Резекне и район', 'https://www.ss.com/ru/real-estate/flats/rezekne-and-reg/all/'), ('Квартиры', 'Салдус и район', 'https://www.ss.com/ru/real-estate/flats/saldus-and-reg/all/'), ('Квартиры', 'Талси и район', 'https://www.ss.com/ru/real-estate/flats/talsi-and-reg/all/'), ('Квартиры', 'Тукумс и район', 'https://www.ss.com/ru/real-estate/flats/tukums-and-reg/all/'), ('Квартиры', 'Цесис и район', 'https://www.ss.com/ru/real-estate/flats/cesis-and-reg/all/'), ('Квартиры', 'Другой', 'https://www.ss.com/ru/real-estate/flats/other/all/'), ('Квартиры', 'За границей Латвии', 'https://www.ss.com/ru/real-estate/flats/flats-abroad-latvia/all/'), ('Дома, дачи', 'Рига', 'https://www.ss.com/ru/real-estate/homes-summer-residences/riga/all/'), ('Дома, дачи', 'Юрмала', 'https://www.ss.com/ru/real-estate/homes-summer-residences/jurmala/all/'), ('Дома, дачи', 'Рижский район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/riga-region/all/'), ('Дома, дачи', 'Айзкраукле и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/aizkraukle-and-reg/all/'), ('Дома, дачи', 'Алуксне и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/aluksne-and-reg/all/'), ('Дома, дачи', 'Балви и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/balvi-and-reg/all/'), ('Дома, дачи', 'Бауска и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/bauska-and-reg/all/'), ('Дома, дачи', 'Валка и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/valka-and-reg/all/'), ('Дома, дачи', 'Валмиера и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/valmiera-and-reg/all/'), ('Дома, дачи', 'Вентспилс и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/ventspils-and-reg/all/'), ('Дома, дачи', 'Гулбене и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/gulbene-and-reg/all/'), ('Дома, дачи', 'Даугавпилс и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/daugavpils-and-reg/all/'), ('Дома, дачи', 'Добеле и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/dobele-and-reg/all/'), ('Дома, дачи', 'Екабпилс и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/jekabpils-and-reg/all/'), ('Дома, дачи', 'Елгава и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/jelgava-and-reg/all/'), ('Дома, дачи', 'Краславa и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/kraslava-and-reg/all/'), ('Дома, дачи', 'Кулдига и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/kuldiga-and-reg/all/'), ('Дома, дачи', 'Лиепая и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/liepaja-and-reg/all/'), ('Дома, дачи', 'Лимбажи и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/limbadzi-and-reg/all/'), ('Дома, дачи', 'Лудза и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/ludza-and-reg/all/'), ('Дома, дачи', 'Мадона и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/madona-and-reg/all/'), ('Дома, дачи', 'Огре и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/ogre-and-reg/all/'), ('Дома, дачи', 'Прейли и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/preili-and-reg/all/'), ('Дома, дачи', 'Резекне и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/rezekne-and-reg/all/'), ('Дома, дачи', 'Салдус и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/saldus-and-reg/all/'), ('Дома, дачи', 'Талси и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/talsi-and-reg/all/'), ('Дома, дачи', 'Тукумс и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/tukums-and-reg/all/'), ('Дома, дачи', 'Цесис и район', 'https://www.ss.com/ru/real-estate/homes-summer-residences/cesis-and-reg/all/'), ('Дома, дачи', 'Другой', 'https://www.ss.com/ru/real-estate/homes-summer-residences/other/all/'), ('Дома, дачи', 'За границей Латвии', 'https://www.ss.com/ru/real-estate/homes-summer-residences/houses-abroad-latvia/all/'), ('Хутора, поместья', 'Рижский район', 'https://www.ss.com/ru/real-estate/farms-estates/riga-region/all/'), ('Хутора, поместья', 'Айзкраукле и район', 'https://www.ss.com/ru/real-estate/farms-estates/aizkraukle-and-reg/all/'), ('Хутора, поместья', 'Алуксне и район', 'https://www.ss.com/ru/real-estate/farms-estates/aluksne-and-reg/all/'), ('Хутора, поместья', 'Балви и район', 'https://www.ss.com/ru/real-estate/farms-estates/balvi-and-reg/all/'), ('Хутора, поместья', 'Бауска и район', 'https://www.ss.com/ru/real-estate/farms-estates/bauska-and-reg/all/'), ('Хутора, поместья', 'Валка и район', 'https://www.ss.com/ru/real-estate/farms-estates/valka-and-reg/all/'), ('Хутора, поместья', 'Валмиера и район', 'https://www.ss.com/ru/real-estate/farms-estates/valmiera-and-reg/all/'), ('Хутора, поместья', 'Вентспилс и район', 'https://www.ss.com/ru/real-estate/farms-estates/ventspils-and-reg/all/'), ('Хутора, поместья', 'Гулбене и район', 'https://www.ss.com/ru/real-estate/farms-estates/gulbene-and-reg/all/'), ('Хутора, поместья', 'Даугавпилс и район', 'https://www.ss.com/ru/real-estate/farms-estates/daugavpils-and-reg/all/'), ('Хутора, поместья', 'Добеле и район', 'https://www.ss.com/ru/real-estate/farms-estates/dobele-and-reg/all/'), ('Хутора, поместья', 'Екабпилс и район', 'https://www.ss.com/ru/real-estate/farms-estates/jekabpils-and-reg/all/'), ('Хутора, поместья', 'Елгава и район', 'https://www.ss.com/ru/real-estate/farms-estates/jelgava-and-reg/all/'), ('Хутора, поместья', 'Краславa и район', 'https://www.ss.com/ru/real-estate/farms-estates/kraslava-and-reg/all/'), ('Хутора, поместья', 'Кулдига и район', 'https://www.ss.com/ru/real-estate/farms-estates/kuldiga-and-reg/all/'), ('Хутора, поместья', 'Лиепая и район', 'https://www.ss.com/ru/real-estate/farms-estates/liepaja-and-reg/all/'), ('Хутора, поместья', 'Лимбажи и район', 'https://www.ss.com/ru/real-estate/farms-estates/limbadzi-and-reg/all/'), ('Хутора, поместья', 'Лудза и район', 'https://www.ss.com/ru/real-estate/farms-estates/ludza-and-reg/all/'), ('Хутора, поместья', 'Мадона и район', 'https://www.ss.com/ru/real-estate/farms-estates/madona-and-reg/all/'), ('Хутора, поместья', 'Огре и район', 'https://www.ss.com/ru/real-estate/farms-estates/ogre-and-reg/all/'), ('Хутора, поместья', 'Прейли и район', 'https://www.ss.com/ru/real-estate/farms-estates/preili-and-reg/all/'), ('Хутора, поместья', 'Резекне и район', 'https://www.ss.com/ru/real-estate/farms-estates/rezekne-and-reg/all/'), ('Хутора, поместья', 'Салдус и район', 'https://www.ss.com/ru/real-estate/farms-estates/saldus-and-reg/all/'), ('Хутора, поместья', 'Талси и район', 'https://www.ss.com/ru/real-estate/farms-estates/talsi-and-reg/all/'), ('Хутора, поместья', 'Тукумс и район', 'https://www.ss.com/ru/real-estate/farms-estates/tukums-and-reg/all/'), ('Хутора, поместья', 'Цесис и район', 'https://www.ss.com/ru/real-estate/farms-estates/cesis-and-reg/all/'), ('Хутора, поместья', 'Другой', 'https://www.ss.com/ru/real-estate/farms-estates/other/all/'), ('Помещения', 'Ангары', 'https://www.ss.com/ru/real-estate/premises/hangars/'), ('Помещения', 'Бани', 'https://www.ss.com/ru/real-estate/premises/bathhouses/'), ('Помещения', 'Гаражи', 'https://www.ss.com/ru/real-estate/premises/garages/all'), ('Помещения', 'Здания и комплексы', 'https://www.ss.com/ru/real-estate/premises/buildings-and-complexes/all'), ('Помещения', 'Игровые залы', 'https://www.ss.com/ru/real-estate/premises/playing-halls/'), ('Помещения', 'Магазины', 'https://www.ss.com/ru/real-estate/premises/shops/all'), ('Помещения', 'Мастерские', 'https://www.ss.com/ru/real-estate/premises/workshops/'), ('Помещения', 'Офисы и кабинеты', 'https://www.ss.com/ru/real-estate/offices/all'), ('Помещения', 'Пентхаусы', 'https://www.ss.com/ru/real-estate/premises/penthouses/'), ('Помещения', 'Подвалы и полуподвалы', 'https://www.ss.com/ru/real-estate/premises/basements-and-semi-basements/'), ('Помещения', 'Помещения для автосервиса', 'https://www.ss.com/ru/real-estate/premises/premises-for-service-centers/'), ('Помещения', 'Производственные помещения', 'https://www.ss.com/ru/real-estate/premises/production-facilities/all'), ('Помещения', 'Рестораны, кафе, столовые', 'https://www.ss.com/ru/real-estate/premises/restaurants-cafe-dining-halls/'), ('Помещения', 'Салоны', 'https://www.ss.com/ru/real-estate/premises/saloons/'), ('Помещения', 'Склады и хранилища', 'https://www.ss.com/ru/real-estate/premises/storehouses-and-storages/all'), ('Помещения', 'Спортивные залы', 'https://www.ss.com/ru/real-estate/premises/training-halls/'), ('Помещения', 'Хозпостройки', 'https://www.ss.com/ru/real-estate/premises/household-buildings/'), ('Помещения', 'Чердаки', 'https://www.ss.com/ru/real-estate/premises/garrets/'), ('Помещения', 'Другое', 'https://www.ss.com/ru/real-estate/premises/other/'), ('Офисы', 'Рига', 'https://www.ss.com/ru/real-estate/offices/riga/all/'), ('Офисы', 'Юрмала', 'https://www.ss.com/ru/real-estate/offices/jurmala/all/'), ('Офисы', 'Рижский район', 'https://www.ss.com/ru/real-estate/offices/riga-region/all/'), ('Офисы', 'Айзкраукле и район', 'https://www.ss.com/ru/real-estate/offices/aizkraukle-and-reg/all/'), ('Офисы', 'Алуксне и район', 'https://www.ss.com/ru/real-estate/offices/aluksne-and-reg/all/'), ('Офисы', 'Балви и район', 'https://www.ss.com/ru/real-estate/offices/balvi-and-reg/all/'), ('Офисы', 'Бауска и район', 'https://www.ss.com/ru/real-estate/offices/bauska-and-reg/all/'), ('Офисы', 'Валка и район', 'https://www.ss.com/ru/real-estate/offices/valka-and-reg/all/'), ('Офисы', 'Валмиера и район', 'https://www.ss.com/ru/real-estate/offices/valmiera-and-reg/all/'), ('Офисы', 'Вентспилс и район', 'https://www.ss.com/ru/real-estate/offices/ventspils-and-reg/all/'), ('Офисы', 'Гулбене и район', 'https://www.ss.com/ru/real-estate/offices/gulbene-and-reg/all/'), ('Офисы', 'Даугавпилс и район', 'https://www.ss.com/ru/real-estate/offices/daugavpils-and-reg/all/'), ('Офисы', 'Добеле и район', 'https://www.ss.com/ru/real-estate/offices/dobele-and-reg/all/'), ('Офисы', 'Екабпилс и район', 'https://www.ss.com/ru/real-estate/offices/jekabpils-and-reg/all/'), ('Офисы', 'Елгава и район', 'https://www.ss.com/ru/real-estate/offices/jelgava-and-reg/all/'), ('Офисы', 'Краславa и район', 'https://www.ss.com/ru/real-estate/offices/kraslava-and-reg/all/'), ('Офисы', 'Кулдига и район', 'https://www.ss.com/ru/real-estate/offices/kuldiga-and-reg/all/'), ('Офисы', 'Лиепая и район', 'https://www.ss.com/ru/real-estate/offices/liepaja-and-reg/all/'), ('Офисы', 'Лимбажи и район', 'https://www.ss.com/ru/real-estate/offices/limbadzi-and-reg/all/'), ('Офисы', 'Лудза и район', 'https://www.ss.com/ru/real-estate/offices/ludza-and-reg/all/'), ('Офисы', 'Мадона и район', 'https://www.ss.com/ru/real-estate/offices/madona-and-reg/all/'), ('Офисы', 'Огре и район', 'https://www.ss.com/ru/real-estate/offices/ogre-and-reg/all/'), ('Офисы', 'Прейли и район', 'https://www.ss.com/ru/real-estate/offices/preili-and-reg/all/'), ('Офисы', 'Резекне и район', 'https://www.ss.com/ru/real-estate/offices/rezekne-and-reg/all/'), ('Офисы', 'Салдус и район', 'https://www.ss.com/ru/real-estate/offices/saldus-and-reg/all/'), ('Офисы', 'Талси и район', 'https://www.ss.com/ru/real-estate/offices/talsi-and-reg/all/'), ('Офисы', 'Тукумс и район', 'https://www.ss.com/ru/real-estate/offices/tukums-and-reg/all/'), ('Офисы', 'Цесис и район', 'https://www.ss.com/ru/real-estate/offices/cesis-and-reg/all/'), ('Офисы', 'Другой', 'https://www.ss.com/ru/real-estate/offices/other/all/'), ('Земля и участки', 'Рига', 'https://www.ss.com/ru/real-estate/plots-and-lands/riga/all/'), ('Земля и участки', 'Юрмала', 'https://www.ss.com/ru/real-estate/plots-and-lands/jurmala/all/'), ('Земля и участки', 'Рижский район', 'https://www.ss.com/ru/real-estate/plots-and-lands/riga-region/all/'), ('Земля и участки', 'Айзкраукле и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/aizkraukle-and-reg/all/'), ('Земля и участки', 'Алуксне и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/aluksne-and-reg/all/'), ('Земля и участки', 'Балви и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/balvi-and-reg/all/'), ('Земля и участки', 'Бауска и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/bauska-and-reg/all/'), ('Земля и участки', 'Валка и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/valka-and-reg/all/'), ('Земля и участки', 'Валмиера и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/valmiera-and-reg/all/'), ('Земля и участки', 'Вентспилс и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/ventspils-and-reg/all/'), ('Земля и участки', 'Гулбене и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/gulbene-and-reg/all/'), ('Земля и участки', 'Даугавпилс и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/daugavpils-and-reg/all/'), ('Земля и участки', 'Добеле и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/dobele-and-reg/all/'), ('Земля и участки', 'Екабпилс и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/jekabpils-and-reg/all/'), ('Земля и участки', 'Елгава и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/jelgava-and-reg/all/'), ('Земля и участки', 'Краславa и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/kraslava-and-reg/all/'), ('Земля и участки', 'Кулдига и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/kuldiga-and-reg/all/'), ('Земля и участки', 'Лиепая и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/liepaja-and-reg/all/'), ('Земля и участки', 'Лимбажи и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/limbadzi-and-reg/all/'), ('Земля и участки', 'Лудза и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/ludza-and-reg/all/'), ('Земля и участки', 'Мадона и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/madona-and-reg/all/'), ('Земля и участки', 'Огре и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/ogre-and-reg/all/'), ('Земля и участки', 'Прейли и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/preili-and-reg/all/'), ('Земля и участки', 'Резекне и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/rezekne-and-reg/all/'), ('Земля и участки', 'Салдус и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/saldus-and-reg/all/'), ('Земля и участки', 'Талси и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/talsi-and-reg/all/'), ('Земля и участки', 'Тукумс и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/tukums-and-reg/all/'), ('Земля и участки', 'Цесис и район', 'https://www.ss.com/ru/real-estate/plots-and-lands/cesis-and-reg/all/'), ('Земля и участки', 'Другой', 'https://www.ss.com/ru/real-estate/plots-and-lands/other/all/')]
_ESTATE = [('Dzīvokļi', 'Jūrmala', 'https://www.ss.com/lv/real-estate/flats/jurmala/all/')]


def send_req(url):
    try:
        return requests.get(url)
    except Exception:
        print('Duplicated request!', url)
        time.sleep(1)
        return send_req(url)


def process_all_links(data):

    result = []

    for obj in data:
        for link in obj[-1]:

            parse_result: Estate
            if obj[0] == 'Dzīvokļi':
                parse_result = parse_one_flat(link)
            if obj[0] == 'Mājas':
                parse_result = parse_one_house(link)
            if obj[0] == 'Viensētas':
                parse_result = parse_one_farm(link)
            if obj[0] == 'Telpas':
                parse_result = parse_one_room(link)
                parse_result.purpose = obj[1]
            if obj[0] == 'Biroji':
                parse_result = parse_one_office(link)
            if obj[0] == 'Zeme':
                parse_result = parse_one_plot(link)

            parse_result.deal_type = obj[2]
            parse_result.property_type = obj[0]
            parse_result.series = format_series(parse_result.series)
            parse_result.country = 'LV'
            parse_result.resource = 'ss.com'
            if not parse_result.city_region:
                parse_result.city_region = obj[1]

            # print(len(result), parse_result.year, parse_result.month)
            result.append(parse_result.to_list())
            print(f'Parsing... {len(result)} items')

    return result


def parse_one_flat(url):
    req = send_req(url)
    html = Soup(req.text, features='html.parser')

    opts_name = [x.text.strip() for x in html.select('.ads_opt_name')]
    opts = [x.text.strip() for x in html.select('.ads_opt')]

    try:
        if 'Rajons:' in opts_name:
            district = opts[opts_name.index('Rajons:')]
        else:
            district = None
    except Exception:
        district = None

    try:
        if 'Pilsēta/pagasts:' in opts_name:
            volost = opts[opts_name.index('Pilsēta/pagasts:')]
        else:
            volost = None
    except Exception:
        volost = None

    try:
        if 'Iela:' in opts_name:
            street = opts[opts_name.index('Iela:')].replace('[Karte]', '').strip()
        else:
            street = None
    except Exception:
        street = None
    try:
        if 'Istabas:' in opts_name:
            room_number = int(opts[opts_name.index('Istabas:')])
        else:
            room_number = None
    except Exception:
        room_number = None
    try:
        if 'Platība:' in opts_name:
            area = opts[opts_name.index('Platība:')]
            area = pretty_value(area)
        else:
            area = None
    except Exception:
        area = None
    try:
        if 'Stāvs:' in opts_name:
            floor_number, all_floors = list(map(int, opts[opts_name.index('Stāvs:')].split('/')[:2]))
        else:
            floor_number, all_floors = None, None
    except Exception:
        floor_number, all_floors = None, None
    try:
        if 'Sērija:' in opts_name:
            series = opts[opts_name.index('Sērija:')]
            if series.endswith('.'):
                series = series[:-1]
        else:
            series = None
    except Exception:
        series = None
    try:
        if 'Mājas tips:' in opts_name:
            house_type = opts[opts_name.index('Mājas tips:')]
        else:
            house_type = None
    except Exception:
        house_type = None
    try:
        if 'Kadastra numurs:' in opts_name:
            kad_number = opts[opts_name.index('Kadastra numurs:')]
        else:
            kad_number = None
    except Exception:
        kad_number = None
    try:
        if 'Ērtības:' in opts_name:
            facilities = opts[opts_name.index('Ērtības:')]
        else:
            facilities = None
    except Exception:
        facilities = None

    try:
        price_sel = html.find('', {'class': 'ads_price'}).text
        price_all, price_m2 = list(map(lambda x: x.strip(), price_sel.replace('/м²', '').replace(')', '').split('(')))
        price_all = pretty_value(price_all)
        price_m2 = pretty_value(price_m2)
    except Exception:
        price_all, price_m2 = None, None

    try:
        date = html.select('td.msg_footer')[2].text
        date = datetime.datetime.strptime(date, 'Datums: %d.%m.%Y %H:%M')
        year, month, day = map(int, date.strftime('%Y %m %d').split())
    except Exception:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day

    return Estate(year=year, month=month, day=day, district=district, street=street, volost=volost, price=price_all, price_m2=price_m2, area=area, room_number=room_number, floor_number=floor_number, count_of_floors=all_floors, kad_number=kad_number, series=series, house_type=house_type, facilities=facilities, link=str(url))


def parse_one_house(url):
    # url = 'https://www.ss.com/msg/ru/real-estate/flats/riga/centre/afcxd.html'

    req = send_req(url)
    html = Soup(req.text, features='html.parser')


    opts_name = [x.text.strip() for x in html.select('.ads_opt_name')]
    opts = [x.text.strip() for x in html.select('.ads_opt')]

    try:
        if 'Rajons:' in opts_name:
            district = opts[opts_name.index('Rajons:')]
        else:
            district = None
    except Exception:
        district = None

    try:
        if 'Pilsēta/pagasts:' in opts_name:
            volost = opts[opts_name.index('Pilsēta/pagasts:')]
        else:
            volost = None
    except Exception:
        volost = None

    try:
        if 'Iela:' in opts_name:
            street = opts[opts_name.index('Iela:')].replace('[Karte]', '').strip()
        else:
            street = None
    except Exception:
        street = None
    try:
        if 'Platība:' in opts_name:
            area = opts[opts_name.index('Platība:')]
            area = pretty_value(area)
        else:
            area = None
    except Exception:
        area = None
    try:
        if 'Stāvu skaits:' in opts_name:
            floor_number = int(opts[opts_name.index('Stāvu skaits:')])
        else:
            floor_number = None
    except Exception:
        floor_number = None
    try:
        if 'Istabas:' in opts_name:
            room_number = int(opts[opts_name.index('Istabas:')])
        else:
            room_number = None
    except Exception:
        room_number = None
    try:
        if 'Zemes platība:' in opts_name:
            ground_area = opts[opts_name.index('Zemes platība:')]
            ground_area = pretty_value(ground_area)
        else:
            ground_area = None
    except Exception:
        ground_area = None
    try:
        if 'Ērtības:' in opts_name:
            facilities = opts[opts_name.index('Ērtības:')]
        else:
            facilities = None
    except Exception:
        facilities = None
    try:
        if 'Kadastra numurs:' in opts_name:
            kad_number = opts[opts_name.index('Kadastra numurs:')]
        else:
            kad_number = None
    except Exception:
        kad_number = None

    try:
        price_all = html.find('', {'class': 'ads_price'}).text.strip()
        price_all = pretty_value(price_all)
    except Exception:
        price_all = None

    try:
        price_m2 = str(price_all / area)
        price_m2 = float(price_m2[:price_m2.index('.') + 1])
    except Exception:
        price_m2 = None

    try:
        date = html.select('td.msg_footer')[2].text
        date = datetime.datetime.strptime(date, 'Datums: %d.%m.%Y %H:%M')
        year, month, day = map(int, date.strftime('%Y %m %d').split())
    except Exception:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day

    return Estate(year=year, month=month, day=day, district=district, street=street, volost=volost, price=price_all, price_m2=price_m2, area=area, room_number=room_number, ground_area=ground_area, floor_number=floor_number, kad_number=kad_number, facilities=facilities, link=url)


def parse_one_farm(url):
    # url = 'https://www.ss.com/msg/ru/real-estate/flats/riga/centre/afcxd.html'

    req = send_req(url)
    html = Soup(req.text, features='html.parser')


    opts_name = [x.text.strip() for x in html.select('.ads_opt_name')]
    opts = [x.text.strip() for x in html.select('.ads_opt')]

    try:
        if 'Rajons:' in opts_name:
            district = opts[opts_name.index('Rajons:')]
        else:
            district = None
    except Exception:
        district = None

    try:
        if 'Pilsēta/pagasts:' in opts_name:
            volost = opts[opts_name.index('Pilsēta/pagasts:')]
        else:
            volost = None
    except Exception:
        volost = None

    try:
        if 'Ciems:' in opts_name:
            country = opts[opts_name.index('Ciems:')].replace('[Karte]', '').strip()
        else:
            country = None
    except Exception:
        country = None
    try:
        if 'Platība:' in opts_name:
            area = int(opts[opts_name.index('Platība:')])
            area = pretty_value(area)
        else:
            area = None
    except Exception:
        area = None
    try:
        if 'Stāvu skaits:' in opts_name:
            floor_number = int(opts[opts_name.index('Stāvu skaits:')])
        else:
            floor_number = None
    except Exception:
        floor_number = None
    try:
        if 'Istabas:' in opts_name:
            room_number = int(opts[opts_name.index('Istabas:')])
        else:
            room_number = None
    except Exception:
        room_number = None
    try:
        if 'Zemes platība:' in opts_name:
            ground_area = opts[opts_name.index('Zemes platība:')]
            ground_area = pretty_value(ground_area)
        else:
            ground_area = None
    except Exception:
        ground_area = None
    try:
        if 'Ērtības:' in opts_name:
            facilities = opts[opts_name.index('Ērtības:')]
        else:
            facilities = None
    except Exception:
        facilities = None
    try:
        if 'Kadastra numurs:' in opts_name:
            kad_number = opts[opts_name.index('Kadastra numurs:')]
        else:
            kad_number = None
    except Exception:
        kad_number = None

    try:
        price_all = html.find('', {'class': 'ads_price'}).text.strip()
        price_all = pretty_value(price_all)
    except Exception:
        price_all = None

    try:
        date = html.select('td.msg_footer')[2].text
        date = datetime.datetime.strptime(date, 'Datums: %d.%m.%Y %H:%M')
        year, month, day = map(int, date.strftime('%Y %m %d').split())
    except Exception:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day

    return Estate(year=year, month=month, day=day, district=district, volost=volost, country=country, ground_area=ground_area, price=price_all, area=area, room_number=room_number, floor_number=floor_number, kad_number=kad_number, facilities=facilities, link=url)


def parse_one_room(url):
    req = send_req(url)
    html = Soup(req.text, features='html.parser')


    opts_name = [x.text.strip() for x in html.select('.ads_opt_name')]
    opts = [x.text.strip() for x in html.select('.ads_opt')]

    try:
        if 'Pilsēta, rajons:' in opts_name:
            district = opts[opts_name.index('Pilsēta, rajons:')]
        else:
            district = None
    except Exception:
        district = None

    try:
        if 'Pilsēta/pagasts:' in opts_name:
            volost = opts[opts_name.index('Pilsēta/pagasts:')]
        else:
            volost = None
    except Exception:
        volost = None

    try:
        if 'Ciems:' in opts_name:
            country = opts[opts_name.index('Ciems:')].replace('[Karte]', '').strip()
        else:
            country = None
    except Exception:
        country = None
    try:
        if 'Platība:' in opts_name:
            area = int(opts[opts_name.index('Platība:')])
            area = pretty_value(area)
        else:
            area = None
    except Exception:
        area = None
    try:
        if 'Stāvu skaits:' in opts_name:
            floor_number = int(opts[opts_name.index('Stāvu skaits:')])
        else:
            floor_number = None
    except Exception:
        floor_number = None
    try:
        if 'Istabas:' in opts_name:
            room_number = int(opts[opts_name.index('Istabas:')])
        else:
            room_number = None
    except Exception:
        room_number = None
    try:
        if 'Zemes platība:' in opts_name:
            ground_area = opts[opts_name.index('Zemes platība:')]
            ground_area = pretty_value(ground_area)
        else:
            ground_area = None
    except Exception:
        ground_area = None
    try:
        if 'Ērtības:' in opts_name:
            facilities = opts[opts_name.index('Ērtības:')]
        else:
            facilities = None
    except Exception:
        facilities = None
    try:
        if 'Kadastra numurs:' in opts_name:
            kad_number = opts[opts_name.index('Kadastra numurs:')]
        else:
            kad_number = None
    except Exception:
        kad_number = None

    try:
        price_sel = html.find('', {'class': 'ads_price'}).text.strip()
        price_all, price_m2 = list(map(lambda x: x.strip(), price_sel.replace('/м²', '').replace(')', '').split('(')))
        price_all = pretty_value(price_all)
        price_m2 = pretty_value(price_m2)
    except Exception:
        price_all, price_m2 = None, None

    try:
        date = html.select('td.msg_footer')[2].text
        date = datetime.datetime.strptime(date, 'Datums: %d.%m.%Y %H:%M')
        year, month, day = map(int, date.strftime('%Y %m %d').split())
    except Exception:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day

    return Estate(year=year, month=month, day=day, city_region=district, volost=volost, country=country, ground_area=ground_area, price=price_all, price_m2=price_m2, area=area, room_number=room_number, floor_number=floor_number, kad_number=kad_number, facilities=facilities, link=str(url))


def parse_one_office(url):
    req = send_req(url)
    html = Soup(req.text, features='html.parser')


    opts_name = [x.text.strip() for x in html.select('.ads_opt_name')]
    opts = [x.text.strip() for x in html.select('.ads_opt')]

    try:
        if 'Rajons:' in opts_name:
            district = opts[opts_name.index('Rajons:')]
        else:
            district = None
    except Exception:
        district = None

    try:
        if 'Pilsēta/pagasts:' in opts_name:
            volost = opts[opts_name.index('Pilsēta/pagasts:')]
        else:
            volost = None
    except Exception:
        volost = None

    try:
        if 'Iela:' in opts_name:
            street = opts[opts_name.index('Iela:')].replace('[Karte]', '').strip()
        else:
            street = None
    except Exception:
        street = None
    try:
        if 'Istabas:' in opts_name:
            room_number = int(opts[opts_name.index('Istabas:')])
        else:
            room_number = None
    except Exception:
        room_number = None
    try:
        if 'Platība:' in opts_name:
            area = int(opts[opts_name.index('Platība:')])
            area = pretty_value(area)
        else:
            area = None
    except Exception:
        area = None
    try:
        if 'Stāvs:' in opts_name:
            floor_number, all_floors = list(map(int, opts[opts_name.index('Stāvs:')].split('/')))[:2]
        else:
            floor_number, all_floors = None, None
    except Exception:
        floor_number, all_floors = None, None
    try:
        if 'Kadastra numurs:' in opts_name:
            kad_number = opts[opts_name.index('Kadastra numurs:')]
        else:
            kad_number = None
    except Exception:
        kad_number = None
    try:
        if 'Ērtības:' in opts_name:
            facilities = opts[opts_name.index('Ērtības:')]
        else:
            facilities = None
    except Exception:
        facilities = None

    try:
        price_sel = html.find('', {'class': 'ads_price'}).text
        price_all, price_m2 = list(map(lambda x: x.strip(), price_sel.replace('/м²', '').replace(')', '').split('(')))
        price_all = pretty_value(price_all)
        price_m2 = pretty_value(price_m2)
    except Exception:
        price_all, price_m2 = None, None

    try:
        date = html.select('td.msg_footer')[2].text
        date = datetime.datetime.strptime(date, 'Datums: %d.%m.%Y %H:%M')
        year, month, day = map(int, date.strftime('%Y %m %d').split())
    except Exception:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day

    return Estate(year=year, month=month, day=day, district=district, street=street, volost=volost, price=price_all, price_m2=price_m2, area=area, room_number=room_number, floor_number=floor_number, count_of_floors=all_floors, kad_number=kad_number, facilities=facilities, link=url)


def parse_one_plot(url):
    req = send_req(url)
    html = Soup(req.text, features='html.parser')


    opts_name = [x.text.strip() for x in html.select('.ads_opt_name')]
    opts = [x.text.strip() for x in html.select('.ads_opt')]

    try:
        if 'Rajons:' in opts_name:
            district = opts[opts_name.index('Rajons:')]
        else:
            district = None
    except Exception:
        district = None

    try:
        if 'Pilsēta/pagasts:' in opts_name:
            volost = opts[opts_name.index('Pilsēta/pagasts:')]
        else:
            volost = None
    except Exception:
        volost = None

    try:
        if 'Iela:' in opts_name:
            street = opts[opts_name.index('Iela:')].replace('[Karte]', '').strip()
        else:
            street = None
    except Exception:
        street = None
    try:
        if 'Platība:' in opts_name:
            area = int(opts[opts_name.index('Platība:')])
            area = pretty_value(area)
        else:
            area = None
    except Exception:
        area = None
    try:
        if 'Pielietojums:' in opts_name:
            purpose = opts[opts_name.index('Pielietojums:')]
        else:
            purpose = None
    except Exception:
        purpose = None

    try:
        price_sel = html.find('', {'class': 'ads_price'}).text
        price_all, price_m2 = list(map(lambda x: x.strip(), price_sel.replace('/м²', '').replace(')', '').split('(')))
        price_m2 = pretty_value(price_m2)
        price_all = pretty_value(price_all)
    except Exception:
        price_all, price_m2 = None, None

    try:
        date = html.select('td.msg_footer')[2].text
        date = datetime.datetime.strptime(date, 'Datums: %d.%m.%Y %H:%M')
        year, month, day = map(int, date.strftime('%Y %m %d').split())
    except Exception:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day

    return Estate(year=year, month=month, day=day, district=district, street=street, volost=volost, price=price_all, price_m2=price_m2, purpose=purpose, area=area, link=url)

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


def get_links_for_archive():
    result = []

    for estate in LV_ESTATE:
        # print(estate[0], estate[1])
        url = estate[2]

        req = send_req(url)
        html = Soup(req.text, features='html.parser')

        districts = html.select('select.filter_sel')[-1]
        districts = [('https://www.ss.com' + x['value'].replace('lv/', 'lv/archive/'), x.text) for x in districts.select('option') if
                   x.text != 'Visi']

        for district in districts:
            # print(estate[0], estate[1], district[1])
            url = district[0]

            req = send_req(url)
            html = Soup(req.text, features='html.parser')

            options = [('https://www.ss.com' + x['value'], x.text) for x in html.select('.filter_sel.l100 option') if
                       x.text != 'Visi']

            for option in options:
                # print(estate[0], estate[1], district[1], option[1])
                page = 1
                all_links = []

                while True:

                    link = option[0] + f'page{page}.html'

                    req = send_req(link)
                    html = Soup(req.text, features='html.parser')
                    links = ['https://www.ss.com' + x.div.a['href'] for x in html.find_all('', {'class': 'msg2'})]

                    if links:
                        if links[0] not in all_links:
                            for l in links:
                                all_links.append(l)
                        else:
                            break
                    else:
                        break

                    page += 1

                result.append((estate[0], estate[1], option[1], all_links))

                c = 0
                for x in result:
                    c += len(x[3])
                print(f'Collecting links... {c}')

                # if result[-1][0] == 'Mājas':
                #     return result


    return result


def to_excel(data):
    df = pd.DataFrame(data)

    print(df)
    headers = ['year', 'month', 'day', 'country', 'resource', 'deal_type', 'property_type', 'city_region', 'district', 'street', 'volost',
               'village', 'price', 'price_m2', 'area', 'ground_area', 'room_number', 'floor_number',
               'count_of_floors', 'kad_number', 'series', 'house_type', 'facilities', 'purpose', 'link']

    df.to_excel('ss.xlsx', index=False, header=headers)


def to_excel_arc(data):
    df = pd.DataFrame(data)

    print(df)
    headers = ['year', 'month', 'day', 'country', 'resource', 'deal_type', 'property_type', 'city_region', 'district', 'street', 'volost',
               'village', 'price', 'price_m2', 'area', 'ground_area', 'room_number', 'floor_number',
               'count_of_floors', 'kad_number', 'series', 'house_type', 'facilities', 'purpose', 'link']

    df.to_excel('ss_archive.xlsx', index=False, header=headers)


def unique(data):
    exist_links = db.get_exist_links('archive', 'ss.com')
    unique = []
    for obj in data:
        o = []
        for x in obj[-1]:
            if x not in exist_links:
                o.append((x))
        unique.append((obj[0], obj[1], obj[2], o))
    return unique


def main():
    print('Getting links...')
    # links = get_all_links()
    links = get_links_for_archive()

    c = 0
    for v in links:
        c += len(v[3])
    print('SS: ', str(c), ' links')

    links = unique(links)
    # print(links)
    c = 0
    for v in links:
        c += len(v[3])
    print('SS: ', str(c), ' unique links')

    if links:
        print('Processing...')
        parse_result = process_all_links(links)

        db.save(parse_result, 'archive')
        # to_excel_arc(parse_result)


if __name__ == '__main__':
    main()
    # print('Getting links...')
    # # links = get_all_links()
    # links = get_links_for_archive()
    #
    # c = 0
    # for v in links:
    #     c += len(v[3])
    # print('SS: ', str(c), ' links')
    #
    # # links = unique(links)
    # # print(links)
    # c = 0
    # for v in links:
    #     c += len(v[3])
    # print('SS: ', str(c), ' unique links')
    #
    # if links:
    #     print('Processing...')
    #     parse_result = process_all_links(links)
    #
    #     # db.save(parse_result, 'latvia')
    #     to_excel_arc(parse_result)