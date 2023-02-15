import csv
import time
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial
from os import path

import requests
from fake_useragent import UserAgent
from random import choice

from httpx import ConnectError, RemoteProtocolError
from selectolax.parser import HTMLParser
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
import httpx
from dataclasses import dataclass, asdict
import re

proxies = [
           '192.126.253.48:8800',
           '192.126.250.22:8800',
           '192.126.253.197:8800',
           '192.126.253.59:8800',
           '192.126.253.134:8800',
           '192.126.250.223:8800'
           ]

# company_urls = [
#         'https://de.indeed.com/cmp/Hotel-Mssngr?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jnhgjjiv802&fromjk=2626f305ad399745',
#         'https://de.indeed.com/cmp/Sonnen?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6joj1jqvi802&fromjk=e846fde655293c2e',
#         'https://de.indeed.com/cmp/Nh-8adc4d2a?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jpa32e11003&fromjk=cc7dd09f67a7720d',
#         'https://de.indeed.com/cmp/Highcoordination-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jpupl22k801&fromjk=e4374dd769afabe7',
#         'https://de.indeed.com/cmp/Instinct3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jqj5k5ro803&fromjk=dc8355820312c198',
#         'https://de.indeed.com/cmp/Svarmony?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jr9rkkd7801&fromjk=c0f24575b0cdd119',
#         'https://de.indeed.com/cmp/Varc-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jrv0k7sn805&fromjk=17fb64f24bbd28b3',
#         'https://de.indeed.com/cmp/Trakken-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jskr2m5n000&fromjk=3c9e429cd64ad558',
#         'https://de.indeed.com/cmp/Berry-Global,-Inc?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jtn4ir3o802&fromjk=2f307529e5e74403',
#         'https://de.indeed.com/cmp/All-For-One-Group-Se?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6juc6ikd9800&fromjk=6fb8710cc3cb1be1',
#         'https://de.indeed.com/cmp/Targomo?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jv0qj3vv800&fromjk=f7ff39626cd0f56f',
#         'https://de.indeed.com/cmp/Kreuzwerker-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jvlskkfn802&fromjk=e6b45259b1d839d6',
#         'https://de.indeed.com/cmp/Coffee-Circle-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6k0ccjjgs802&fromjk=da42d794164550f8',
#         'https://de.indeed.com/cmp/Pair-Finance-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6k11ojqun802&fromjk=7849b844150895fb',
#         'https://de.indeed.com/cmp/Make-IT-Fix-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6k234jjgs802&fromjk=d7da040a0c4e08ad',
#         'https://de.indeed.com/cmp/Park-&-Control-Pac-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l5kok7t1802&fromjk=e6571b36e8743b24',
#         'https://de.indeed.com/cmp/Hrworks-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l6mbirp1802&fromjk=340238d4d02a7f0d',
#         'https://de.indeed.com/cmp/Adevinta-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l7bijqvd802&fromjk=b69ad2d7b20d6203',
#         'https://de.indeed.com/cmp/A.-Lange-&-S%C3%B6hne?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l80pk7ej802&fromjk=41a8cddcc5a80de1',
#         'https://de.indeed.com/cmp/Likeminded-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l93jj3v7801&fromjk=2861be7ef9dd894a',
#         'https://de.indeed.com/cmp/Tts-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6la53ikrh801&fromjk=c662129170711dba',
#         'https://de.indeed.com/cmp/Unzer?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lpmek7qa802&fromjk=f70c0e03a8bfa532',
#         'https://de.indeed.com/cmp/Johnson-Controls?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lqotl237802&fromjk=4fe8ab8f7185c97c',
#         'https://de.indeed.com/cmp/Dream-Broker-Oy?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lrf4je0n800&fromjk=d7d4136101cd0fce',
#         'https://de.indeed.com/cmp/Precise-Hotels-&-Resorts-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ls56ki8k802&fromjk=9f43f92aa33b57cd',
#         'https://de.indeed.com/cmp/Krongaard-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lsqe2m5n000&fromjk=54e865d43a169ce2',
#         'https://de.indeed.com/cmp/Vinci?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lu3fk7rk802&fromjk=21df39ebdc36181b',
#         'https://de.indeed.com/cmp/Powercloud-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lv55ikd9802&fromjk=896be62c6754a5b7',
#         'https://de.indeed.com/cmp/Lieferando?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lvqnk7qa800&fromjk=2f92467356626881',
#         'https://de.indeed.com/cmp/Easypark-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n027k7bn802&fromjk=d0267431f6b2811b',
#         "https://de.indeed.com/cmp/Marc-O'polo?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n13vi3rg800&fromjk=85c6bfc5f1bc6731",
#         'https://de.indeed.com/cmp/Mediamarktsaturn?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n1q7lhed802&fromjk=279cda594803afaf',
#         'https://de.indeed.com/cmp/E--vendo-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n2h3k5og802&fromjk=e7c274e6f22afd19',
#         'https://de.indeed.com/cmp/Too-Good-to-Go?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n377lhdn800&fromjk=e22657761c6117c1',
#         'https://de.indeed.com/cmp/Codary?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n49fjjj7802&fromjk=e3f800e120c62399',
#         'https://de.indeed.com/cmp/Youngcapital?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n4tllhdn802&fromjk=4df7dbf10035ae1b',
#         'https://de.indeed.com/cmp/Vialytics?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n609ip9j800&fromjk=aab9e83cc1d680cd',
#         'https://de.indeed.com/cmp/Quadriga-Media-Berlin-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n714k7ej800&fromjk=4d620a04147eb20b',
#         'https://de.indeed.com/cmp/Sanofi?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n7nqk7qa802&fromjk=456e0fe674084f28',
#         'https://de.indeed.com/cmp/Homburg-&-Partner?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n8d5lhej800&fromjk=fd87426e320e2a3b',
#         'https://de.indeed.com/cmp/Inmediasp?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n939jjiu804&fromjk=b0779e787e8ec359',
#         'https://de.indeed.com/cmp/Nextcoder-Softwareentwicklungs-Ug?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6na43lhdn802&fromjk=02291b4c35c12bf0',
#         'https://de.indeed.com/cmp/Berger?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6nao3k7fs802&fromjk=eeea07a54876f9eb',
#         'https://de.indeed.com/cmp/Anschutz-Entertainment-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6nbpilhdk800&fromjk=d316a4fce5584139',
#         'https://de.indeed.com/cmp/Inmediasp?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ocaij3ut802&fromjk=b0779e787e8ec359',
#         "https://de.indeed.com/cmp/Marc-O'polo?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6odcbjqvd800&fromjk=85c6bfc5f1bc6731",
#         'https://de.indeed.com/cmp/Lieferando?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oe4gjkv6802&fromjk=2f92467356626881',
#         'https://de.indeed.com/cmp/Hewlett-Packard-Enterprise-Hpe-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oer1ki8k800&fromjk=848a90d1ab19907b',
#         'https://de.indeed.com/cmp/Anschutz-Entertainment-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ofg0l22k800&fromjk=d316a4fce5584139',
#         'https://de.indeed.com/cmp/Eat-Happy-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6og6kje1l800&fromjk=41ac10034fc16733',
#         'https://de.indeed.com/cmp/Powercloud-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oh6okkfn800&fromjk=896be62c6754a5b7',
#         'https://de.indeed.com/cmp/Precise-Hotels-&-Resorts-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ohrtk7ts800&fromjk=9f43f92aa33b57cd',
#         'https://de.indeed.com/cmp/Fanpage-Karma?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oifajgap802&fromjk=3b4e9ec705c22ba7',
#         'https://de.indeed.com/cmp/Berger?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oj3jlhdg802&fromjk=eeea07a54876f9eb',
#         'https://de.indeed.com/cmp/Ivu-Traffic-Technologies-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ojp3ip9j802&fromjk=7c99bdec2fa15359',
#         'https://de.indeed.com/cmp/Capmo-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6okf5k7bn804&fromjk=97b2c83e899ad791',
#         'https://de.indeed.com/cmp/Http-Www.trendence.com-Karriere-Stellenangebote.html?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ol52jjgs800&fromjk=f88aa90f55260d15',
#         'https://de.indeed.com/cmp/Quadriga-Media-Berlin-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6om6ok7ej800&fromjk=4d620a04147eb20b',
#         'https://de.indeed.com/cmp/U--blox?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6on9glhdk802&fromjk=f0df3e68d6a93836',
#         'https://de.indeed.com/cmp/Scout24-Se-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6pqldikd9802&fromjk=d3327c7ee79328e2',
#         'https://de.indeed.com/cmp/Primal-State?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6prmtkkfc804&fromjk=6ad12bdfd5d8e9fb',
#         'https://de.indeed.com/cmp/Adsquare-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6psppk7d4800&fromjk=51f958aab5f7e873',
#         'https://de.indeed.com/cmp/Berlin-Cuisine-Metzger-&-Jensen-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ptsdlhdn800&fromjk=a5ce09402fddc001',
#         'https://de.indeed.com/cmp/Hewlett-Packard-Enterprise-Hpe-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6puutlhdd801&fromjk=848a90d1ab19907b',
#         'https://de.indeed.com/cmp/Herm%C3%A8s-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q017je36800&fromjk=63df9a9e254f26f0',
#         'https://de.indeed.com/cmp/Vattenfall?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q136j3v7802&fromjk=2d1da6110893f134',
#         'https://de.indeed.com/cmp/Online-Birds-Hotel-Marketing-Solutions?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q255je1l800&fromjk=3daaa833ecd47e51',
#         'https://de.indeed.com/cmp/Accenture?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q36skkfc800&fromjk=01fbc74f6bce501f',
#         'https://de.indeed.com/cmp/Nia-Health-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q499jjgs800&fromjk=2e2e962ef4cf606e',
#         'https://de.indeed.com/cmp/IBM-Ix-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q5b0jg9b800&fromjk=9994c25c7c874823',
#         'https://de.indeed.com/cmp/Unzer?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q6d5k7ts803&fromjk=81d7138283eda9bf',
#         'https://de.indeed.com/cmp/Deloitte?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q7f82bc4003&fromjk=75d3a0743bcbd1ae',
#         'https://de.indeed.com/cmp/Giga.green?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q8hdkojo802&fromjk=aa5ca76412181b7f',
#         'https://de.indeed.com/cmp/Saatchi-&-Saatchi?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q9jqk7sn802&fromjk=db07fe2a39c17491',
#         'https://de.indeed.com/cmp/Dataguard-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6rjr8lhdd802&fromjk=37066ac8ee53e985',
#         'https://de.indeed.com/cmp/Diconium-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6rks5jjjs802&fromjk=f9afb40cd075124e',
#         'https://de.indeed.com/cmp/Smarketer-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6rlj7k7sn802&fromjk=15f6d88298624e90',
#         'https://de.indeed.com/cmp/Berlin-Brands-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s567l22k802&fromjk=50f4744cd5754274',
#         'https://de.indeed.com/cmp/Care-With-Care?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s66rl22o807&fromjk=be82878656ef7cec',
#         'https://de.indeed.com/cmp/Smartclip-Europe-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s6tplheg805&fromjk=00ef1c15bf5b5939',
#         'https://de.indeed.com/cmp/Bonial?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s7tdki8k800&fromjk=24d158ec1fd24ec9',
#         'https://de.indeed.com/cmp/Re-Cap?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s8km2m5n002&fromjk=514faab177900060',
#         'https://de.indeed.com/cmp/Schindler-59cfe7ee?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s99ajqvi800&fromjk=1619b0e0ab6a2b5b',
#         'https://de.indeed.com/cmp/Sonnen?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s9uc2fbr002&fromjk=be1fd61011ef7e08',
#         'https://de.indeed.com/cmp/Angel-Last-Mile-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6saltk5og803&fromjk=afae896c15b4b92b',
#         'https://de.indeed.com/cmp/Capgemini?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6sbe1j3v7802&fromjk=a9e76fa7d7d568f9',
#         'https://de.indeed.com/cmp/Hrlab-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6sc1uip9j800&fromjk=ee2ed6b1d8a3a033',
#         'https://de.indeed.com/cmp/Sabienzia-Technologies-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6scnol233802&fromjk=e901abc02f6d3bad',
#         'https://de.indeed.com/cmp/Adsquare-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tga1ir2n800&fromjk=0946d72d5f01ee6b',
#         'https://de.indeed.com/cmp/Alstom?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6thj9k7bn802&fromjk=7c59e0e5cc24defc',
#         'https://de.indeed.com/cmp/Vodafone?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tiluikcj800&fromjk=c2d9b4fe54366208',
#         'https://de.indeed.com/cmp/Cenit?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tjo7k7bn802&fromjk=6505e394e293cc72',
#         'https://de.indeed.com/cmp/The-Social-Chain-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tkp7k7fs802&fromjk=6e94fb9ac295feba',
#         'https://de.indeed.com/cmp/Dataguard-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tlsvjjik804&fromjk=a3e7e16e164c6094',
#         'https://de.indeed.com/cmp/Spendesk?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tn08k6r3800&fromjk=0715219702bf2ad2',
#         'https://de.indeed.com/cmp/Humanoo-Etherapists-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6to1jjjiu802&fromjk=e4b92fad1ac40cd1',
#         'https://de.indeed.com/cmp/U--blox?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tp3ik7fs801&fromjk=f0df3e68d6a93836',
#         'https://de.indeed.com/cmp/Deutsche-Bank?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tqabikcj803&fromjk=5748085de433fa25',
#         'https://de.indeed.com/cmp/Live-Nation?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6trrt2m5n005&fromjk=3cd1ed52272f1b5c',
#         'https://de.indeed.com/cmp/Krongaard-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tt7ij326802&fromjk=3fccdb4eace9bf64',
#         'https://de.indeed.com/cmp/Michael-Page?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tu9jir3o800&fromjk=22f72c1aaf7608ea',
#         'https://de.indeed.com/cmp/Yoc-France?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tvafk7cg801&fromjk=98c98956530df48c',
#         'https://de.indeed.com/cmp/Smartbroker?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6u010ir2n802&fromjk=12eb3afd69bcb4b1',
#         'https://de.indeed.com/cmp/Deutsche-Bank?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v21dl22p800&fromjk=5748085de433fa25',
#         'https://de.indeed.com/cmp/Humanoo-Etherapists-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v33e2fbv000&fromjk=e4b92fad1ac40cd1',
#         'https://de.indeed.com/cmp/Avart-Personal-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v3oekojo802&fromjk=914685aa3e3d3f81',
#         'https://de.indeed.com/cmp/Capgemini?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v4dbl237802&fromjk=371a49fb77b100cb',
#         'https://de.indeed.com/cmp/Smartbroker?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v5f9kkd7802&fromjk=12eb3afd69bcb4b1',
#         'https://de.indeed.com/cmp/Michael-Page?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v672ikcj802&fromjk=22f72c1aaf7608ea',
#         'https://de.indeed.com/cmp/Bilendi?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v6tvjjiu802&fromjk=86393400f2b96819',
#         'https://de.indeed.com/cmp/Kranus-Health-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v800lhdh802&fromjk=46c69764204b3c61',
#         'https://de.indeed.com/cmp/Humanoo?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v8mki46f803&fromjk=7699949131a89839',
#         'https://de.indeed.com/cmp/Steinbeis-School-of-International-Business-and-Entrepreneurship-(sibe)-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v9brl22k802&fromjk=5d0b0708bbce7955',
#         'https://de.indeed.com/cmp/Youngcapital?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vadjlhej802&fromjk=6cb7dfc77311fc22',
#         'https://de.indeed.com/cmp/Hewlett-Packard-Enterprise-Hpe-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vb2jj3ut801&fromjk=609757da0649b591',
#         'https://de.indeed.com/cmp/Headmatch-Gmbh-&-Co.kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vbo4k7rk802&fromjk=e6a4a905c6e092d8',
#         'https://de.indeed.com/cmp/Krongaard-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vck5jjiv800&fromjk=3fccdb4eace9bf64',
#         'https://de.indeed.com/cmp/Dps-Business-Solutions-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vdg02m5n002&fromjk=7ec5e1d8620690ae',
#         'https://de.indeed.com/cmp/Gkm-Recruitment-Services?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70eeejg9n800&fromjk=648749532e95b692',
#         'https://de.indeed.com/cmp/Bilendi?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70fmmikrh801&fromjk=86393400f2b96819',
#         'https://de.indeed.com/cmp/Just-Spices-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70gk0ikcj807&fromjk=85e469b5ebcb7c4c',
#         'https://de.indeed.com/cmp/Noris-Network?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70hmh2bc4003&fromjk=c05495fbcebba4e4',
#         'https://de.indeed.com/cmp/Headmatch-Gmbh-&-Co.kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70iovl22p801&fromjk=e6a4a905c6e092d8',
#         'https://de.indeed.com/cmp/Avart-Personal-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70jr3l21j802&fromjk=914685aa3e3d3f81',
#         'https://de.indeed.com/cmp/Kranus-Health-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70ktuj3ut802&fromjk=46c69764204b3c61',
#         'https://de.indeed.com/cmp/Comsysto-Reply-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70qt3k5ro805&fromjk=63bcf919b26239a3',
#         'https://de.indeed.com/cmp/Bearingpoint?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70rjqje36802&fromjk=095c85169a38d8f9',
#         'https://de.indeed.com/cmp/Hoppecke-Batterien?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70slvlheg802&fromjk=ef8d22ff0e30d255',
#         'https://de.indeed.com/cmp/Steinbeis-School-of-International-Business-and-Entrepreneurship-(sibe)-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70to32fbv002&fromjk=5d0b0708bbce7955',
#         'https://de.indeed.com/cmp/Dps-Business-Solutions-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70upvjgap802&fromjk=7ec5e1d8620690ae',
#         'https://de.indeed.com/cmp/Michael-Page?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70vsal210802&fromjk=5de951a85fcd8738',
#         'https://de.indeed.com/cmp/Robert-Half?campaignid=mobvjcmp&from=mobviewjob&tk=1gou710ujl22k800&fromjk=8d57969b3839fb6b',
#         'https://de.indeed.com/cmp/Hays?campaignid=mobvjcmp&from=mobviewjob&tk=1gou71205jjiu800&fromjk=e4dc737964d8b1c9',
#         'https://de.indeed.com/cmp/Noris-Network?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7226qir3o800&fromjk=1b324c8ac18fc90e',
#         'https://de.indeed.com/cmp/Zalando?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7236tki8k803&fromjk=085baa86ea598d78',
#         'https://de.indeed.com/cmp/Deutsche-Bank?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7249ql22o802&fromjk=24598c474fdc87a0',
#         'https://de.indeed.com/cmp/Solique-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7251rikd9802&fromjk=e5d9af519388ea3b',
#         'https://de.indeed.com/cmp/Tesvolt-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou725oa2fbv000&fromjk=752e32e80fbf8f02',
#         'https://de.indeed.com/cmp/Floris-Catering-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou726gbikdg802&fromjk=88e644be36905113',
#         'https://de.indeed.com/cmp/Michael-Page?campaignid=mobvjcmp&from=mobviewjob&tk=1gou727gqjjjs802&fromjk=247325277bdef0d5',
#         'https://de.indeed.com/cmp/Capgemini?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72882ikdg803&fromjk=371a49fb77b100cb',
#         'https://de.indeed.com/cmp/Broadgate-Search?campaignid=mobvjcmp&from=mobviewjob&tk=1gou728u6l22p802&fromjk=48c95cae49a33de5',
#         'https://de.indeed.com/cmp/Connected-Gs-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou729hjjkvo803&fromjk=f8178e2ab395f8b1',
#         'https://de.indeed.com/cmp/Kuehne+nagel?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72a62k7qa802&fromjk=15060a73d20ce616',
#         'https://de.indeed.com/cmp/Spendesk?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72b8lk5ro800&fromjk=eae533cf0cccd9f5',
#         'https://de.indeed.com/cmp/Apcoa-Parking-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72bv7jqvd802&fromjk=381396175176161a',
#         'https://de.indeed.com/cmp/Aemtec-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72ckdl210802&fromjk=d668c4faa81606e2',
#         'https://de.indeed.com/cmp/Alogis-Ag-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72daukkd7802&fromjk=f0baff0610131fe2',
#         'https://de.indeed.com/cmp/Fischerappelt?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73errjg9n802&fromjk=a0808e7270c93486',
#         'https://de.indeed.com/cmp/Hoppecke-Batterien?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73fr2j3v7802&fromjk=ab829ff6a51ef812',
#         'https://de.indeed.com/cmp/Ib-Vogt-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73gi4kkfn802&fromjk=2fd275f557831d51',
#         'https://de.indeed.com/cmp/Deutsche-Bank?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73h7tlhdh802&fromjk=2690f5c402dc43a2',
#         'https://de.indeed.com/cmp/Studydrive-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73httjqvd801&fromjk=b14d5c0ba161ab7e',
#         'https://de.indeed.com/cmp/Nobel-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73iiuikrh800&fromjk=af3b3a0bac211aec',
#         'https://de.indeed.com/cmp/Oliver-Wyman-Group-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7420pk7bn802&fromjk=e9a47934c2050555',
#         'https://de.indeed.com/cmp/Hubject-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7433hk7cg800&fromjk=41cb640230fe52bd',
#         'https://de.indeed.com/cmp/Usu-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou743o3k7ej802&fromjk=6b23fceb8ef2859c',
#         'https://de.indeed.com/cmp/Software-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou744qeje36802&fromjk=ce7a9d00b5e453cb',
#         'https://de.indeed.com/cmp/Nobel-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gou745fgjjiv802&fromjk=5ac57abcdbe2ba13',
#         'https://de.indeed.com/cmp/Lingoda-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7465nkkfc803&fromjk=31ac7e7d0960a35b',
#         'https://de.indeed.com/cmp/Ey?campaignid=mobvjcmp&from=mobviewjob&tk=1gou746t9jksu800&fromjk=2d1b5a0d8bfbb466',
#         'https://de.indeed.com/cmp/Strategy&?campaignid=mobvjcmp&from=mobviewjob&tk=1gou747jjlhdh802&fromjk=e35ae750d842c7df',
#         'https://de.indeed.com/cmp/Usu-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75hnjjjj7802&fromjk=6b23fceb8ef2859c',
#         'https://de.indeed.com/cmp/Studydrive-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75imul233800&fromjk=b14d5c0ba161ab7e',
#         'https://de.indeed.com/cmp/Lingoda-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75joml21j800&fromjk=31ac7e7d0960a35b',
#         'https://de.indeed.com/cmp/Software-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75krfiqv3800&fromjk=ce7a9d00b5e453cb',
#         'https://de.indeed.com/cmp/Kuehne+nagel?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75lgv2m5n002&fromjk=15060a73d20ce616',
#         'https://de.indeed.com/cmp/Spendesk?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75mivl21j800&fromjk=a6426709248c7dfe',
#         'https://de.indeed.com/cmp/Thermo-Fisher-Scientific?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75n9fk7ts804&fromjk=b85e4519093e889d',
#         'https://de.indeed.com/cmp/Spendesk?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75o0rir2n802&fromjk=344c94ba993dfc79',
#         'https://de.indeed.com/cmp/Ib-Vogt-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75on1lhed800&fromjk=2fd275f557831d51',
#         'https://de.indeed.com/cmp/Alstom?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75pffje1l800&fromjk=dccd8a1400aae357',
#         'https://de.indeed.com/cmp/Avantgarde-Experts?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75qg4irp1800&fromjk=581cc252f3c405f8',
#         'https://de.indeed.com/cmp/Orange-Quarter?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75r5fk5og802&fromjk=d3a2efd4549cea35',
#         'https://de.indeed.com/cmp/Realworld-One-Gmbh-&-Co.-Kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75rqok7d4803&fromjk=60042adbeda42da5',
#         'https://de.indeed.com/cmp/Frg-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75sf5k7ts802&fromjk=c734f98e71b6dc59',
#         'https://de.indeed.com/cmp/Veeva-Systems?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75t56lheg803&fromjk=8785c08cfd511493',
#         'https://de.indeed.com/cmp/Usu-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou76v6fi46f800&fromjk=16bd223191897413',
#         'https://de.indeed.com/cmp/Avantgarde-Experts?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7707s2e11002&fromjk=de3ed4dca6c3473a',
#         'https://de.indeed.com/cmp/Deutsche-Telekom?campaignid=mobvjcmp&from=mobviewjob&tk=1gou770unj3vv802&fromjk=e2849bddec87183f',
#         'https://de.indeed.com/cmp/Workstreams.ai-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou771mgkkfd800&fromjk=8615a4952d2ebb65',
#         'https://de.indeed.com/cmp/Yara-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou772o5i46f803&fromjk=eaeedfd9a3eff58b',
#         'https://de.indeed.com/cmp/Flaconi-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou773e6jjiu802&fromjk=7d34dcbd390c4335',
#         'https://de.indeed.com/cmp/Ml6?campaignid=mobvjcmp&from=mobviewjob&tk=1gou774h2jg9n800&fromjk=fc9f30ea8c5a197a',
#         'https://de.indeed.com/cmp/Vanilla-Steel-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou775imk7qa800&fromjk=1be83b54ce988bd6',
#         'https://de.indeed.com/cmp/Br%C3%B6er-&-Partner-Gmbh-&-Co-Kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7768hje1l801&fromjk=36d392cb282a5926',
#         'https://de.indeed.com/cmp/Bunch?campaignid=mobvjcmp&from=mobviewjob&tk=1gou77737ikrh800&fromjk=caf1e55ecbcdadda',
#         'https://de.indeed.com/cmp/Trinckle-3d-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou777vel233801&fromjk=20ff3807007d5057',
#         'https://de.indeed.com/cmp/Leanlancer-Ug?campaignid=mobvjcmp&from=mobviewjob&tk=1gou778nli46f802&fromjk=737a3c699338a650',
#         'https://de.indeed.com/cmp/Leanlancer-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou779qvjg9n800&fromjk=6e6f8019d8d34a7c',
#         'https://de.indeed.com/cmp/Clariness?campaignid=mobvjcmp&from=mobviewjob&tk=1gou77atglhdd800&fromjk=c489e6cf51e209d7',
#         'https://de.indeed.com/cmp/Mindbody?campaignid=mobvjcmp&from=mobviewjob&tk=1gou77bihhdhg802&fromjk=971f5370df68a00f',
#         'https://de.indeed.com/cmp/Masterplan.com-4?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78hbdjg90802&fromjk=33fb2fa9cb4db6db',
#         'https://de.indeed.com/cmp/Picture-Tree-International-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78id8ikd9803&fromjk=7e8045daf4f3b4df',
#         'https://de.indeed.com/cmp/Enpal-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78ja2jg9n802&fromjk=74615c24ba07dd6f',
#         'https://de.indeed.com/cmp/Fairsenden-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78k7ukkfn802&fromjk=13669fae46359423',
#         'https://de.indeed.com/cmp/Centrovital-Berlin?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78laqje1l80h&fromjk=75c37f2f66027ec0',
#         'https://de.indeed.com/cmp/Dedo-Media-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78mcklhej802&fromjk=7bea898030156603',
#         'https://de.indeed.com/cmp/Briink?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78n2ik7dg802&fromjk=518b11ae627b2710',
#         'https://de.indeed.com/cmp/First-Berlin-Equity-Research-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78nnqlhdh802&fromjk=8bc298f3503e47ce',
#         'https://de.indeed.com/cmp/Merantix?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78odejqun801&fromjk=8bc140309ac56efb',
#         'https://de.indeed.com/cmp/Delphai?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78p36jqvd802&fromjk=dcf4c5badc1e6163',
#         'https://de.indeed.com/cmp/Contentbird-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78pp2lhdg800&fromjk=6f311172db2ca662',
#         'https://de.indeed.com/cmp/Easylivestream?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78qeoje0n801&fromjk=d5071b1589294ef2',
#         'https://de.indeed.com/cmp/Bvdw-Services-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78r5rk7fs800&fromjk=e0364340a38c6258',
#         'https://de.indeed.com/cmp/Cytosorbents-Europe-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78s7flhdk802&fromjk=75ecae871b101e8b',
#         'https://de.indeed.com/cmp/Oceansapart?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78ta4kkfd800&fromjk=9a3f148ea2272336',
#         'https://de.indeed.com/cmp/K&K-Handelsgesellschaft-Mbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a3dj2fbr000&fromjk=d8c368565350162e',
#         'https://de.indeed.com/cmp/Leanlancer-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a4etjkvj802&fromjk=6e6f8019d8d34a7c',
#         'https://de.indeed.com/cmp/Circulee-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a547k7t1801&fromjk=8020ce1d27ab81cc',
#         'https://de.indeed.com/cmp/Briink?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a5q4jjgs800&fromjk=518b11ae627b2710',
#         'https://de.indeed.com/cmp/Equeo-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a6rkl22p802&fromjk=c1e9440d1854d634',
#         'https://de.indeed.com/cmp/Clariness?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a7htl22k802&fromjk=c489e6cf51e209d7',
#         'https://de.indeed.com/cmp/Heyrecruit?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a8k8kkd7802&fromjk=65f8dc6dcbaaa512',
#         'https://de.indeed.com/cmp/Weroad-4?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a9all22o802&fromjk=2e551c5f448515c0',
#         'https://de.indeed.com/cmp/Circulee?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7aa04hdhg802&fromjk=79fce93d3eb788c9',
#         'https://de.indeed.com/cmp/Escapio-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7aaoqip9j802&fromjk=4f37ce67b3761108',
#         'https://de.indeed.com/cmp/Merantix?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7abp6kojo800&fromjk=8bc140309ac56efb',
#         'https://de.indeed.com/cmp/The-Bike-Club?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7acr1i3rg803&fromjk=97578766a74f4a37',
#         'https://de.indeed.com/cmp/Verlag-Der-Tagesspiegel-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7adg9k2mg802&fromjk=325d68b564b1e738',
#         'https://de.indeed.com/cmp/Easypark-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7ae4qjgap800&fromjk=be8b7030f15b6648',
#         'https://de.indeed.com/cmp/Subtel-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7aeq8k7bn802&fromjk=a549dd2ad57c9881',
#         'https://de.indeed.com/cmp/Rydes?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bi6ul21j802&fromjk=e8c7d8eb6c290a74',
#         'https://de.indeed.com/cmp/Everyone-Energy?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bj9ck7ts801&fromjk=4d6614d8e4dcc872',
#         'https://de.indeed.com/cmp/Craft-Circus-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bkcmjjik802&fromjk=4929dc4287901f83',
#         'https://de.indeed.com/cmp/In-Pact-Media-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bli4j3vv801&fromjk=1731105eeb0962d3',
#         'https://de.indeed.com/cmp/Incred-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bmnnjjiu803&fromjk=25fdd1c44654ff0c',
#         'https://de.indeed.com/cmp/Cloudinary?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bnnijksu802&fromjk=c695b893cef4b284',
#         'https://de.indeed.com/cmp/Also-Energy?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7boqgkkfc802&fromjk=8c287bce4377d212',
#         'https://de.indeed.com/cmp/Adsquare-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bq4ck7cg801&fromjk=9e109c0d0d1fc4eb',
#         'https://de.indeed.com/cmp/Entyre-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7br1piqv3802&fromjk=77de329afdb9e9d3',
#         'https://de.indeed.com/cmp/Sendinblue?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bs63jqvd802&fromjk=953cea5bb44670dc',
#         'https://de.indeed.com/cmp/Vaayu-Tech-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bta7hdhg800&fromjk=61ef53d12505b993',
#         'https://de.indeed.com/cmp/Eqolot?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7buarhdhg802&fromjk=f18c867167df71e1',
#         'https://de.indeed.com/cmp/Singularitysales-Beteiligungsges.-Mbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bvf8jkvo802&fromjk=02704f1d0fd6615d',
#         'https://de.indeed.com/cmp/Primal-State-Performance-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7c0h9ikrh802&fromjk=5dbdb877e58ccc60',
#         'https://de.indeed.com/cmp/Hartmann-Tresore?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7c1jcjjjs800&fromjk=706f21512a350405',
#         'https://de.indeed.com/cmp/Madvertise-2?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7d74ljg9n800&fromjk=bf736bca49cd89cd',
#         'https://de.indeed.com/cmp/Enpal-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7d8fm2fbv003&fromjk=74615c24ba07dd6f',
#         'https://de.indeed.com/cmp/Ebuero-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7d9jrjqvi800&fromjk=33b67b24279136ff',
#         'https://de.indeed.com/cmp/Matthias-Pianezezr?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7dammjkv6800&fromjk=2f4d3ed8541424db',
#         'https://de.indeed.com/cmp/First-Berlin-Equity-Research-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7dbpcjg9b800&fromjk=ec7445c02260be55',
#         'https://de.indeed.com/cmp/Eclipse-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7dcrolhdn802&fromjk=9e49b1bcd02940eb',
#         'https://de.indeed.com/cmp/Sellerx-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7ddu3lhej802&fromjk=de58e2b7a4f58ceb',
#         'https://de.indeed.com/cmp/Easylivestream?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7dtrnip9j802&fromjk=d5071b1589294ef2',
#         'https://de.indeed.com/cmp/Nyn-Consulting?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7duvfl237801&fromjk=7c22957bdbdce7a4',
#         'https://de.indeed.com/cmp/Magaloop-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e01el21j802&fromjk=e8e7981f2c5f2b67',
#         'https://de.indeed.com/cmp/Dertaler-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e14bjqvi802&fromjk=a2cf468ec571ef25',
#         'https://de.indeed.com/cmp/Keyence?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e275l21j801&fromjk=5e88e985e7c160c4',
#         'https://de.indeed.com/cmp/Egroup?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e39tjqvd800&fromjk=96a05ce9675c211c',
#         'https://de.indeed.com/cmp/Codept-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e4c3lhei800&fromjk=8d7a43a24d6f9f0f',
#         'https://de.indeed.com/cmp/Cloudinary?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fhobikre802&fromjk=c695b893cef4b284',
#         'https://de.indeed.com/cmp/Matthias-Pianezezr?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fipihdi6802&fromjk=2f4d3ed8541424db',
#         'https://de.indeed.com/cmp/Apoll-On-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fjfo2e11002&fromjk=5a73c29bd37b2297',
#         'https://de.indeed.com/cmp/Audience-Serv-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fkilk7cg800&fromjk=abea09427d2ca136',
#         'https://de.indeed.com/cmp/The-Recruitment-2.0-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fl84ikd9802&fromjk=18fe84a8212babb5',
#         'https://de.indeed.com/cmp/Berliner-Brandstifter?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7flurikdg802&fromjk=d868ffd821a56d07',
#         'https://de.indeed.com/cmp/United-Internet-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fmkvk7rk802&fromjk=38b49b4f812ec32a',
#         'https://de.indeed.com/cmp/Estrategy-Consulting-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fnbql210802&fromjk=30cb08585c128ac8',
#         'https://de.indeed.com/cmp/Magaloop-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fo2el22k803&fromjk=e8e7981f2c5f2b67',
#         'https://de.indeed.com/cmp/In-Pact-Media-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fp4kk7ej800&fromjk=1731105eeb0962d3',
#         'https://de.indeed.com/cmp/Sense-Electra-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fq6njkv6802&fromjk=b734bb3347c04a3a',
#         'https://de.indeed.com/cmp/Flexperto-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fqtcirp1801&fromjk=ec91669cc4841e0b',
#         'https://de.indeed.com/cmp/Primal-State-Performance-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7gpn62fbr002&fromjk=5dbdb877e58ccc60',
#         'https://de.indeed.com/cmp/Bewerbungscode-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7hv80jg90800&fromjk=ce84e2ab99147fcd',
#         'https://de.indeed.com/cmp/Sense-Electra-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i09ljjik800&fromjk=b734bb3347c04a3a',
#         'https://de.indeed.com/cmp/Sendinblue?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i0v8k7bn802&fromjk=8007da5f0107a98f',
#         'https://de.indeed.com/cmp/Lions-&-Gazelles-International-Recruitment-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i1kuir2n804&fromjk=acff33b4255d5c67',
#         'https://de.indeed.com/cmp/Workbees-Gmbh-(part-of-Netgo-Group)?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i298jkv6800&fromjk=95b26f252138d5c1',
#         'https://de.indeed.com/cmp/Valsight-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i3bkl21j802&fromjk=6502fa20aa20cfbd',
#         'https://de.indeed.com/cmp/Ticketmaster?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i4ffjjjs802&fromjk=bb02c87334de177b',
#         'https://de.indeed.com/cmp/Wunderpen-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i5h6ikre802&fromjk=1171319b530ee5fb',
#         'https://de.indeed.com/cmp/Valsight-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i6jmlhdn802&fromjk=ca3bf3b411c9ea14',
#         'https://de.indeed.com/cmp/Eurofins?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i7acj3ut800&fromjk=0709a6d9225fdd7e',
#         'https://de.indeed.com/cmp/21.finance?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i826lhdh802&fromjk=fbbefefe1cf31079',
#         'https://de.indeed.com/cmp/Weroad?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i98pjg9b800&fromjk=153ae7c7a5bd1342',
#         'https://de.indeed.com/cmp/Ds-Event-Lobby-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7ia58je1l800&fromjk=91f1f3b7500db573',
#         'https://de.indeed.com/cmp/Nico-Europe-Gmbh-4?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7iplaje36802&fromjk=d111c1c4ab3a2785',
#         'https://de.indeed.com/cmp/Workbees-Gmbh-(part-of-Netgo-Group)?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7jtnbi46f802&fromjk=95b26f252138d5c1',
#         'https://de.indeed.com/cmp/Ds-Event-Lobby-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7julrikcj800&fromjk=91f1f3b7500db573',
#         'https://de.indeed.com/cmp/Bewerbungscode-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7jvc8lhdn802&fromjk=ce84e2ab99147fcd',
#         'https://de.indeed.com/cmp/Twinwin?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k01llhdh802&fromjk=5f31e4fbb4340b4e',
#         'https://de.indeed.com/cmp/Bauer-Gruppe-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k0lvlhed800&fromjk=4ab2b121d6551fa5',
#         'https://de.indeed.com/cmp/Meetsales?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k1dpjgap802&fromjk=b1796f142df77949',
#         'https://de.indeed.com/cmp/Wunderpen-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k222k7cg803&fromjk=1171319b530ee5fb',
#         'https://de.indeed.com/cmp/Product-People?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k2n8k7ts800&fromjk=dc46c00a42a3907e',
#         'https://de.indeed.com/cmp/Verve-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k3crk6r3800&fromjk=59c8a19c12c6609c',
#         'https://de.indeed.com/cmp/Nico-Europe-Gmbh-4?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k426k6r3803&fromjk=d111c1c4ab3a2785',
#         'https://de.indeed.com/cmp/G2k-Group-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k4nvikre801&fromjk=fdb62f6de6d29d92',
#         'https://de.indeed.com/cmp/Matthias-Pianezezr?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k5ghl21j802&fromjk=cd1bd8efde516f42',
#         'https://de.indeed.com/cmp/Multitude?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k67tje0p802&fromjk=16ae832ec933f1f3',
#         'https://de.indeed.com/cmp/Sellerx-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7km29k7ej800&fromjk=e66fd59a12be6ca9',
#         'https://de.indeed.com/cmp/Audience-Serv-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7lsrjlhdd800&fromjk=abea09427d2ca136',
#         'https://de.indeed.com/cmp/Twinwin?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7lttcjqun803&fromjk=5f31e4fbb4340b4e',
#         'https://de.indeed.com/cmp/Talent--valet?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7luiskkfc800&fromjk=f8f5bf4b8e3d9252',
#         'https://de.indeed.com/cmp/Sellerx-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7mej1jjj7802&fromjk=e66fd59a12be6ca9',
#         'https://de.indeed.com/cmp/Pixtunes-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7muinir3o801&fromjk=c40063d4d90c0f71',
#         'https://de.indeed.com/cmp/Meetsales?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7mvltlheg802&fromjk=b1796f142df77949',
#         'https://de.indeed.com/cmp/Blu-Die-Agentur-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n0ngjjj7802&fromjk=0da7d44f8093fd0a',
#         'https://de.indeed.com/cmp/Therme-Art-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n1e8lhei801&fromjk=d008f2c20e3fa9a6',
#         'https://de.indeed.com/cmp/Ka-Resources?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n27jhdi6802&fromjk=821cd8312fde7b69',
#         'https://de.indeed.com/cmp/Verve-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n37ak7t1802&fromjk=59c8a19c12c6609c',
#         'https://de.indeed.com/cmp/International-People-Solutions?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n3u7kojo802&fromjk=4dbebdc94480ef71',
#         'https://de.indeed.com/cmp/Usu-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7njs5k6r3801&fromjk=36546e92994cda67',
#         'https://de.indeed.com/cmp/International-People-Solutions?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7p79kk7ej800&fromjk=4dbebdc94480ef71',
#         'https://de.indeed.com/cmp/Usu-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7p8cjjksu802&fromjk=2a3068fdacc4c138',
#         'https://de.indeed.com/cmp/Infoverity?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7p90mjkv6802&fromjk=78a88ea6a54ad36a',
#         'https://de.indeed.com/cmp/Ka-Resources?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7p9m0l210801&fromjk=cc688392582a650b',
#         'https://de.indeed.com/cmp/Usu-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7pabnj3ut800&fromjk=b4e39bd53d849b69',
#         'https://de.indeed.com/cmp/Ka-Resources?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7pb1il22p802&fromjk=82258bec8c2d83d9',
#         'https://de.indeed.com/cmp/Ka-Resources?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7pc3pl233801&fromjk=3b4472da888797c9',
#         'https://de.indeed.com/cmp/Black-Pen-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7pd5r2fbr002&fromjk=4e80b09daa8fba4d']

@dataclass
class Company:
    name: str
    website: str
    linkedin: str

def to_csv(data, filename):
    file_exists = path.isfile(filename)

    with open(filename, 'a', encoding='utf-16') as f:
        headers = ['name', 'website', 'linkedin']
        writer = csv.DictWriter(f, delimiter=',', lineterminator='\n', fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def webdriver_setup(proxy = None):
    ip, port = proxy.split(sep=':')
    ua = UserAgent()
    useragent = ua.firefox
    firefox_options = Options()

    firefox_options.add_argument('-headless')
    firefox_options.add_argument('--no-sandbox')
    firefox_options.page_load_strategy = "eager"

    firefox_options.set_preference("general.useragent.override", useragent)
    firefox_options.set_preference('network.proxy.type', 1)
    firefox_options.set_preference('network.proxy.socks', ip)
    firefox_options.set_preference('network.proxy.socks_port', int(port))
    firefox_options.set_preference('network.proxy.socks_version', 4)
    firefox_options.set_preference('network.proxy.socks_remote_dns', True)
    firefox_options.set_preference('network.proxy.http', ip)
    firefox_options.set_preference('network.proxy.http_port', int(port))
    firefox_options.set_preference('network.proxy.ssl', ip)
    firefox_options.set_preference('network.proxy.ssl_port', int(port))

    driver = webdriver.Firefox(options=firefox_options)
    return driver

def job_result_url(proxies, url, term):
    print('Get job list...')
    proxy = choice(proxies)
    driver = webdriver_setup(proxy)
    driver.get(url)
    cookies = driver.get_cookies()
    ua = driver.execute_script("return navigator.userAgent")
    driver.maximize_window()
    driver.set_page_load_timeout(90)
    wait = WebDriverWait(driver, 90)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.jobsearch-Yosegi')))
    parent = driver.find_element(By.CSS_SELECTOR, 'div.jobsearch-Yosegi')
    input_term = parent.find_element(By.ID,'text-input-what')
    # input_term.send_keys(term + Keys.TAB + location + Keys.RETURN)
    input_term.send_keys(term + Keys.RETURN)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.jobsearch-LeftPane')))
    result = driver.current_url.rsplit('&', 1)[0] + '&sort=date&start=0'
    print(result)
    driver.quit()
    return result, cookies, ua

def get_company_url(url, proxies):
    print('Get company url...')
    next_url = url
    notendpage = True
    company_urls = list()
    while notendpage:
        proxy = choice(proxies)
        print(proxy)
        driver = webdriver_setup(proxy)
        driver.get(next_url)
        driver.maximize_window()
        driver.set_page_load_timeout(90)
        wait = WebDriverWait(driver, 90)

        try:
            # Accept all cookies
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,'div.otFlat.bottom.ot-wo-title.vertical-align-content>div>div.ot-sdk-container>div.ot-sdk-row>div#onetrust-button-group-parent.ot-sdk-three.ot-sdk-columns.has-reject-all-button>div#onetrust-button-group>button#onetrust-accept-btn-handler')))
            driver.find_element(By.CSS_SELECTOR, 'div.otFlat.bottom.ot-wo-title.vertical-align-content>div>div.ot-sdk-container>div.ot-sdk-row>div#onetrust-button-group-parent.ot-sdk-three.ot-sdk-columns.has-reject-all-button>div#onetrust-button-group>button#onetrust-accept-btn-handler').click()
        except (NoSuchElementException, TimeoutException):
            pass

        try:
            next_url = driver.find_element(By.CSS_SELECTOR,'a[data-testid="pagination-page-next"]').get_attribute('href')
        except NoSuchElementException:
            notendpage = False

        clicking_objects = driver.find_elements(By.CSS_SELECTOR, 'div.mosaic-provider-jobcards.mosaic.mosaic-provider-jobcards.mosaic-provider-hydrated>ul.jobsearch-ResultsList.css-0>li>div>div.slider_container.css-g7s71f.eu4oa1w0')
        for object in clicking_objects:
            # Scroll until element found
            js_code = "arguments[0].scrollIntoView();"
            element = object.find_element(By.CSS_SELECTOR, 'a.jcs-JobTitle.css-jspxzf.eu4oa1w0')
            driver.execute_script(js_code, element)

            # Click job element
            object.find_element(By.CSS_SELECTOR, 'a.jcs-JobTitle.css-jspxzf.eu4oa1w0').click()

            # Get company url
            try:
                wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.jobsearch-InlineCompanyRating.icl-u-xs-mt--xs.icl-u-xs-mb--md.css-11s8wkw.eu4oa1w0>div:nth-child(2)>div.css-czdse3.eu4oa1w0>a')))
                company_url = driver.find_element(By.CSS_SELECTOR, 'div.jobsearch-InlineCompanyRating.icl-u-xs-mt--xs.icl-u-xs-mb--md.css-11s8wkw.eu4oa1w0>div:nth-child(2)>div.css-czdse3.eu4oa1w0>a').get_attribute('href')
                company_urls.append(company_url)
            except TimeoutException:
                pass

        driver.quit()
        print(f'{len(company_urls)} company(s) are collected')
    return company_urls

def get_linkedin(search_term, proxy):
    print("Searching for linkedin url...")
    formated_proxy = {
        "http://": f"http://{proxy}",
        "https://": f"http://{proxy}",
    }
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"
    }

    if search_term != None:
        url = f"https://html.duckduckgo.com/html/?q={re.sub('[^A-Za-z0-9]+', '+', search_term)}+linkedin"
        with requests.Session() as session:
            response = session.get(url, proxies=formated_proxy, headers=header, timeout=(30, 90))
        tree = HTMLParser(response.text)
        result = tree.css_first("div.serp__results > div#links.results > div.result.results_links.results_links_deep.web-result > div.links_main.links_deep.result__body > div.result__extras > div.result__extras__url > a.result__url").text().strip()
    else:
        result = None
    return result

def get_website(search_term, proxy):
    print("Searching for company website...")
    formated_proxy = {
        "http://": f"http://{proxy}",
        "https://": f"http://{proxy}",
    }
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"
    }
    if search_term != None:
        url = f"https://html.duckduckgo.com/html/?q={re.sub('[^A-Za-z0-9]+', '+', search_term)}"
        with requests.Session() as session:
            response = session.get(url, proxies=formated_proxy, headers=header, timeout=(30, 90))
        tree = HTMLParser(response.text)
        result = tree.css_first("div.serp__results > div#links.results > div.result.results_links.results_links_deep.web-result > div.links_main.links_deep.result__body > div.result__extras > div.result__extras__url > a.result__url").text().strip()
    else:
        result = None
    return result

def company_parser(html, proxies):
    print('Parse HTML...')
    proxy = choice(proxies)
    tree = HTMLParser(html)

    company_name = None
    website_link = None
    linkedin_link = None

    # Get Company name
    try:
        company_name = tree.css_first('div[itemprop="name"]').text()
    except:
        company_name = None

    # Get Company URL
    try:
        parent = tree.css('ul.css-1jgykzt.e37uo190 > li')
        for i in parent:
            try:
                if 'ebs' in i.css_first('a').text().strip():
                    website_link = (i.css_first('a').attributes['href'])
                    break
                else:
                    website_link = None
                    continue
            except:
                website_link = None
                continue
        if website_link == None:
            proxy = choice(proxies)
            website_link = get_website(company_name, proxy)

    except NoSuchElementException:
        proxy = choice(proxies)
        linkedin_link = get_website(company_name, proxy)

    # Get Company linkedin
    try:
        parent = tree.css('ul.css-1jgykzt.e37uo190 > li')
        for i in parent:
            try:
                if 'inked' in i.css_first('a').text().strip():
                    linkedin_link = (i.css_first('a').attributes['href'])
                    break
                else:
                    linkedin_link = None
                    continue
            except:
                linkedin_link = None
                continue
        if linkedin_link == None:
            proxy = choice(proxies)
            linkedin_link = get_linkedin(company_name, proxy)

    except NoSuchElementException:
        proxy = choice(proxies)
        linkedin_link = get_linkedin(company_name, proxy)

    new_item = Company(name=company_name, website=website_link, linkedin=linkedin_link)
    return asdict(new_item)

def fetch(url, ua, cookies_list, proxies):
    cookies = dict()
    for item in cookies_list:
        cookies[item['name']] = item['value']

    proxy = choice(proxies)
    formated_proxy = {
        "http://": f"http://{proxy}",
        "https://": f"http://{proxy}",
    }

    header = {
        "User-Agent": ua
    }

    with httpx.Client(headers=header, cookies=cookies, proxies=formated_proxy, follow_redirects=True) as client:
        response = client.get(url, timeout=(30,90))
    return response.text, response.status_code

def get_data(url, ua, cookies, proxies):
    print('Get data...')
    html, status_code = fetch(url, ua=ua, cookies_list=cookies, proxies=proxies)
    result = company_parser(html, proxies)
    return result, status_code

def main():
    url = 'https://de.indeed.com/'
    term = 'Sales Representative'

    search_result_url, cookies, ua = job_result_url(proxies, url, term)

    # company_urls = get_company_url(search_result_url, proxies=proxies)

    company_urls = [
        'https://de.indeed.com/cmp/Monotype?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9slgvciqvq800&fromjk=35df2fbe97512fba',
        'https://de.indeed.com/cmp/First-Solar,-Inc.?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sligr28gm002&fromjk=39b69ec099799866',
        'https://de.indeed.com/cmp/Trends-&-Brands.ruhr-Gmbh-&-Co.-Kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sljmvki9e801&fromjk=d2995e2c2898375a',
        'https://de.indeed.com/cmp/Eurofins?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sllpajg8h802&fromjk=8b53e0a2c1010fcc',
        'https://de.indeed.com/cmp/Shiji-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9slnddl21s802&fromjk=f402b7358d3aac7c',
        'https://de.indeed.com/cmp/Sebia-Labordiagnostische-Systeme-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9slpfairpo802&fromjk=5522ebc2df39b479',
        'https://de.indeed.com/cmp/Scewo-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9slrghiqti802&fromjk=e6377c1878563bed',
        'https://de.indeed.com/cmp/Talent360-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9slum72cc9000&fromjk=b7202dd43625a8ce',
        'https://de.indeed.com/cmp/Reteach?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sm0g9je14802&fromjk=cf4863b586fa16a2',
        'https://de.indeed.com/cmp/Procept-Biorobotics-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sm1ntikdl801&fromjk=d2b3740f03da956d',
        'https://de.indeed.com/cmp/Sosafe-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sm30djqus802&fromjk=9443ecbf86af21d8',
        'https://de.indeed.com/cmp/Arwa-Personaldienstleistungen-Gmbh-9?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sm432ki9g802&fromjk=59e8de09f7612bf1',
        'https://de.indeed.com/cmp/Beckman-Coulter-Life-Sciences-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sm55r2hpo001&fromjk=87c024a36e50bad0',
        'https://de.indeed.com/cmp/Makerverse?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sm7172hpo002&fromjk=6414f088cab4587c',
        'https://de.indeed.com/cmp/Medbelle?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sm8iikojv802&fromjk=359f6732ddb5690b',
        'https://de.indeed.com/cmp/Makerverse?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9spn05ih16804&fromjk=6414f088cab4587c',
        'https://de.indeed.com/cmp/Unsere-Gr%C3%BCne-Glasfaser?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9spohsk6qj802&fromjk=0f6bb567271714ea',
        'https://de.indeed.com/cmp/Mackenzie-Stuart-PLC?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9spq4dk6qj802&fromjk=151c61bb50591992',
        'https://de.indeed.com/cmp/Hivebuy?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sprmu2gve004&fromjk=ec277ea36589677c',
        'https://de.indeed.com/cmp/Edit-Systems-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9spt8oirpp801&fromjk=39fe259c30df5803',
        'https://de.indeed.com/cmp/02100-Digital-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9spuqdkkf7802&fromjk=08168060ad1e863a',
        'https://de.indeed.com/cmp/Zaubar?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sq1fei453800&fromjk=8b36218e3e613661',
        'https://de.indeed.com/cmp/Clous-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sq4h2irqn800&fromjk=970dd64b21a9283e',
        'https://de.indeed.com/cmp/Global-Changer?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sq66ig0kk802&fromjk=2f1bd17b3326b475',
        'https://de.indeed.com/cmp/Limbiq-System-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sq88ijjh5802&fromjk=1b5ff7cd7add125d',
        'https://de.indeed.com/cmp/Oculai-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sq9r3jgao801&fromjk=7c97cd8525d99321',
        'https://de.indeed.com/cmp/Smartblick?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sqatkk7jo802&fromjk=61b8f234b58a422e',
        'https://de.indeed.com/cmp/Samedi-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sqdgckkfu802&fromjk=ac0a5480f984baea',
        'https://de.indeed.com/cmp/Dr.-F%C3%B6disch-Umweltmesstechnik-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sqg27iqtl800&fromjk=f1864053bd152222',
        "https://de.indeed.com/cmp/Sotheby's?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9sqi4cikdl800&fromjk=36af0262bb0990d1",
        'https://de.indeed.com/cmp/Wolfspeed-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9stt8o2ejr000&fromjk=1f94fda68d24ba13',
        'https://de.indeed.com/cmp/Brambles-7?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9stumtip9m802&fromjk=fe5e023583971ac6',
        'https://de.indeed.com/cmp/Nonstop-Consulting?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t0nssjgaf805&fromjk=8787204a298eea17',
        'https://de.indeed.com/cmp/Altair-Engineering?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t0otnkkfc802&fromjk=9c21b39cc05806f4',
        'https://de.indeed.com/cmp/Medtronic?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t0qfkk7ef800&fromjk=6a1303dc50598896',
        'https://de.indeed.com/cmp/Specialty-Coating-Systems?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t0t8bk7ji802&fromjk=29f2137953fb5942',
        'https://de.indeed.com/cmp/Productsup?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t0ujjikf4800&fromjk=fd5a74413bff1b15',
        'https://de.indeed.com/cmp/Parloa?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t10lgi45p800&fromjk=223d9a09726ff8f1',
        'https://de.indeed.com/cmp/Texas-Instruments?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t12a3iqtl800&fromjk=c38d6b5faa07f78a',
        'https://de.indeed.com/cmp/Jcdecaux?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t14bfk7dd800&fromjk=7d9268252227be30',
        'https://de.indeed.com/cmp/Sykes-Enterprises,-Incorporated?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t15tgk5po802&fromjk=bcbacadac03308c4',
        'https://de.indeed.com/cmp/Hays?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t172skojv802&fromjk=cdcbb25754387c60',
        'https://de.indeed.com/cmp/Transcool-Leisure-Ltd-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t19jok7f7800&fromjk=07ec9fa53e6fdda8',
        'https://de.indeed.com/cmp/The-Recruitment-Specialist-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t1blljjhl800&fromjk=f9d45fb66366abfd',
        'https://de.indeed.com/cmp/Spreaducation-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t4igkih23802&fromjk=0565745fab107750',
        'https://de.indeed.com/cmp/Chip-Germany?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t4jmfje1v800&fromjk=3603b515781834f7',
        'https://de.indeed.com/cmp/Finally-Freelancing-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t4kqdk7f7802&fromjk=92102799917d89c7',
        'https://de.indeed.com/cmp/Clearlight-Saunas-Europe-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t4lsbk7e5802&fromjk=2e71f7fbecd8434c',
        'https://de.indeed.com/cmp/Starline-Computer-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t4n1a2gvu002&fromjk=e1a8e6aafef6980c',
        'https://de.indeed.com/cmp/Nuvisan-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t4o192e15000&fromjk=4e47dcacae46f694',
        'https://de.indeed.com/cmp/Teamviewer?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t4pjgjqus803&fromjk=6122412404295b8a',
        'https://de.indeed.com/cmp/Azelis-UK-Limited?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t4qonk6qj801&fromjk=77e5d5a6e44840f4',
        'https://de.indeed.com/cmp/Sandvik?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t4rsnkoh7800&fromjk=58b3ddef5d30b710',
        'https://de.indeed.com/cmp/Wattfox-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t4t4k2gve002&fromjk=49635a7fe272106a',
        'https://de.indeed.com/cmp/Thermo-Fisher-Scientific?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t4u9nirr6800&fromjk=3e5c458e03fbe8f0',
        'https://de.indeed.com/cmp/Joblift-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t4vd2jqus802&fromjk=9b7557454f80c207',
        'https://de.indeed.com/cmp/Henkel?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t50ut2e1b003&fromjk=1ec7a46d3aa19d2c',
        'https://de.indeed.com/cmp/Michael-Page?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t53072a46000&fromjk=44fef7a49ce16615',
        'https://de.indeed.com/cmp/Hewlett-Packard-Enterprise-Hpe-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t54olk7q4800&fromjk=6ac6dd908441cdd2',
        'https://de.indeed.com/cmp/Siemens?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t8fjgjktd802&fromjk=52e76f35ee65772b',
        'https://de.indeed.com/cmp/Inovyn?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t8gie21cn002&fromjk=4713ed4c0c5bc27d',
        'https://de.indeed.com/cmp/Collect-Ai?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t8hls2gvu000&fromjk=20046b8da0ac4904',
        'https://de.indeed.com/cmp/Eventmobi?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t8iodk7hr802&fromjk=b1de4fd2aae65136',
        'https://de.indeed.com/cmp/Pasara-Health?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t8jrak7dd802&fromjk=0d721a88fd7e50eb',
        'https://de.indeed.com/cmp/Rydes?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t8ldbih35801&fromjk=0102a345e86fc976',
        'https://de.indeed.com/cmp/United-Planet-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t8nfjjksg800&fromjk=ffe8eb7d83daaeff',
        'https://de.indeed.com/cmp/Grainpro-2?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t8ph42gvu002&fromjk=e6e0c22b56cb72b6',
        'https://de.indeed.com/cmp/Pasara-Health?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t8r4jk7qb800&fromjk=417bbbfe0e2d762b',
        'https://de.indeed.com/cmp/Container-Xchange?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t8unp2hpo002&fromjk=9fc0ea22b7eb7cd7',
        'https://de.indeed.com/cmp/Solua-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t90puiqvq802&fromjk=4b89f44a0cf33004',
        'https://de.indeed.com/cmp/Acrolinx?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t920mk7ql800&fromjk=ae99a1318f1eef4f',
        'https://de.indeed.com/cmp/Gumgum?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t93krk7bm802&fromjk=adb1b0ac70d9b3c6',
        'https://de.indeed.com/cmp/Dabbel---Automation-Intelligence-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t959lje1e802&fromjk=dd72ffc6523690cf',
        'https://de.indeed.com/cmp/Cargobase-Pte-Ltd?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9t97d2k7p4800&fromjk=00d6f989f71e41d8',
        'https://de.indeed.com/cmp/Saxoprint-Gmbh-2?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tcgnhi3r2802&fromjk=93ec47ef77c21b8c',
        'https://de.indeed.com/cmp/Tritec-HR-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tcio9jg8h802&fromjk=3282d27407ee3ae6',
        'https://de.indeed.com/cmp/Dabbel---Automation-Intelligence-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tcnaaih35800&fromjk=dd72ffc6523690cf',
        'https://de.indeed.com/cmp/Gumgum?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tcp0pjji5802&fromjk=adb1b0ac70d9b3c6',
        'https://de.indeed.com/cmp/Grainpro-2?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tcqjgk7ii802&fromjk=e6e0c22b56cb72b6',
        'https://de.indeed.com/cmp/Ryte-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tct53k7ef800&fromjk=bb82e5cd32e416b7',
        'https://de.indeed.com/cmp/Laba-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tcvn5j4ov803&fromjk=33e736996b186b5a',
        'https://de.indeed.com/cmp/Salespotentials?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9td2r028gm000&fromjk=97d063d8c77a9912',
        'https://de.indeed.com/cmp/Sensorfact-5?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9td6f4k7d5802&fromjk=aef967ec856ea22a',
        'https://de.indeed.com/cmp/Vectorbuilder,-Inc.?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9td87j2guc000&fromjk=e0a20fe21961b740',
        'https://de.indeed.com/cmp/Vilo-Personal-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9td9pok7ii801&fromjk=0884aef3cfedc20b',
        'https://de.indeed.com/cmp/Jotec-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tdbs12gag000&fromjk=25bca68d2c402922',
        'https://de.indeed.com/cmp/Operations1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tddjnk7fq802&fromjk=223ccf0a758bfb38',
        'https://de.indeed.com/cmp/Zadego-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tdfllk7h4802&fromjk=ae93edc82a2649ed',
        'https://de.indeed.com/cmp/Yolawo?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tdgrvip9m802&fromjk=9190b7963ecabc73',
        'https://de.indeed.com/cmp/Tradeview-Markets-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tgvg2je1e803&fromjk=ea54d392075e559c',
        'https://de.indeed.com/cmp/Adesta?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9th4alk7e5800&fromjk=036ecab90f9af2c6',
        'https://de.indeed.com/cmp/Delicious-Data-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9th6hhirpp802&fromjk=1dcfbf752511eb6f',
        'https://de.indeed.com/cmp/Team-Expert?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9th8mgjksg800&fromjk=691a74b62844073f',
        'https://de.indeed.com/cmp/Nyris-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tha92k7bm800&fromjk=c66685c02d90eda5',
        'https://de.indeed.com/cmp/Thomann-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tk3t1k7p4802&fromjk=239ef08605ecefb6',
        'https://de.indeed.com/cmp/Validatis-I-Bundesanzeiger-Verlag-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tk5fvk7dg802&fromjk=ef5cb50cdf4a5005',
        'https://de.indeed.com/cmp/Enersys?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tk77uip9m801&fromjk=64687ddbc1387aa8',
        'https://de.indeed.com/cmp/Enersys?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tk8lok7hr800&fromjk=be4a43fe5b1e7112',
        'https://de.indeed.com/cmp/Goodhabitz-Germany-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tka67jjjd802&fromjk=1c1d675cab4d952b',
        'https://de.indeed.com/cmp/Coloplast-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tkbne28gm002&fromjk=2262d6c161db9e05',
        'https://de.indeed.com/cmp/Zimvie?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tkcr6jkva800&fromjk=ea0d0b1680425a57',
        'https://de.indeed.com/cmp/Stryker-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tkdu6i453800&fromjk=d066209ce08c00dd',
        'https://de.indeed.com/cmp/Meggle-Gmbh-&-Co.-Kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tkf4r2guc000&fromjk=e9a41d2870958d59',
        'https://de.indeed.com/cmp/Fyrfeed?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tnoagirpp802&fromjk=48a0bfd87f1c3fba',
        'https://de.indeed.com/cmp/Thefork?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tnqp5iqtl800&fromjk=adaf63c744c83c3e',
        'https://de.indeed.com/cmp/Choosemycompany?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tnstjk7sl800&fromjk=a1921b118ce2996e',
        'https://de.indeed.com/cmp/Upslide?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9to0egk7p4802&fromjk=91ecda6f043a37df',
        'https://de.indeed.com/cmp/Veeva-Systems?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9to34rk7hh802&fromjk=0701d550e0697afc',
        'https://de.indeed.com/cmp/Barbrain?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9to6puk7hh800&fromjk=f58fa0c9aaf20069',
        'https://de.indeed.com/cmp/Lieferando?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9to9sqk7io802&fromjk=9cefee5f546dabbe',
        'https://de.indeed.com/cmp/Trivago?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tocfkj3tv802&fromjk=fb5a5b1f6fe5efb0',
        'https://de.indeed.com/cmp/Whistleblower-Software?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9toe1dk7hr802&fromjk=84b0390541d865a6',
        'https://de.indeed.com/cmp/Andela---Third-Party-Job-Board-Only-Postings?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tof45i3r9800&fromjk=4c082417a05f71b2',
        'https://de.indeed.com/cmp/Shell?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9togmu2dof000&fromjk=c09691b1a83b0a25',
        'https://de.indeed.com/cmp/Acronis-International-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9toinok7hh802&fromjk=1408818ee3ba1fe4',
        'https://de.indeed.com/cmp/Gr%C3%A4bert-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tojs5k7tg800&fromjk=3c718703651276cd',
        'https://de.indeed.com/cmp/Cryptomathic?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9toluf2gve002&fromjk=a0a3fbff76713707',
        'https://de.indeed.com/cmp/Arrow-Electronics?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9topvbk7e5802&fromjk=c94ee7ad0b4e8061',
        'https://de.indeed.com/cmp/Whistleblower-Software?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ts2ugje3h800&fromjk=42697586ea68bd38',
        'https://de.indeed.com/cmp/Gr%C3%A4bert-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ts50fk7ej803&fromjk=3c718703651276cd',
        'https://de.indeed.com/cmp/Yfood-Labs-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ts7ibjg91802&fromjk=f8cbf6c2b7dad610',
        'https://de.indeed.com/cmp/Csg-Talent?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ts98c21cn002&fromjk=282a17fd7f1de985',
        'https://de.indeed.com/cmp/A.t.z.?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tsbp22gve001&fromjk=de593cb4f0862f66',
        'https://de.indeed.com/cmp/Johnson-Controls?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tsdfejji5801&fromjk=0a8cdf73752ebc1f',
        'https://de.indeed.com/cmp/Cobus-Concept-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tsfgpirpo800&fromjk=45f46860b0a7a6ea',
        'https://de.indeed.com/cmp/Sandvik?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tsh982cc6002&fromjk=5c20437fbfde4235',
        'https://de.indeed.com/cmp/A.t.z.?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tsjaik7ej802&fromjk=06f85d5f91c10c83',
        'https://de.indeed.com/cmp/Project-People-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tsklr2gag004&fromjk=7019b98c0e0d6f1e',
        'https://de.indeed.com/cmp/Nonstop-Consulting?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tsm8a28gm002&fromjk=eda694a449cccb9f',
        'https://de.indeed.com/cmp/Oxygen-Digital-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tsnt7k7u4802&fromjk=f5443d251448c5dc',
        'https://de.indeed.com/cmp/Hipeople?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tspg5k7hh800&fromjk=2a07e5a8270fbae2',
        'https://de.indeed.com/cmp/Synogate?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tss2dk7ji800&fromjk=89e4f129c7bcfbd7',
        'https://de.indeed.com/cmp/Arviem-Ag-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9tsuknk7sl800&fromjk=43e0198dab665a8c',
        'https://de.indeed.com/cmp/Dimpact?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u07ugj3tv800&fromjk=22f8903611bdd0b3',
        'https://de.indeed.com/cmp/Sales-Perfect?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u09j5jjjd802&fromjk=a7aa5a842ac52c71',
        'https://de.indeed.com/cmp/Monotype-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u0b92jg8h802&fromjk=eb06dc2fa7b9d3bb',
        'https://de.indeed.com/cmp/Penumbra,-Inc.?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u0dclk7dd802&fromjk=11bc44920ff1593c',
        'https://de.indeed.com/cmp/Fastech?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u0f0nk7ql800&fromjk=3387261052aff944',
        'https://de.indeed.com/cmp/Aexus?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u0j0dk7qb800&fromjk=b6f085028ded57aa',
        'https://de.indeed.com/cmp/Impower?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u0llgjjh5800&fromjk=c4b22e7a5c2876fb',
        'https://de.indeed.com/cmp/Additive-Marking-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u0oomi3pi800&fromjk=f9c211e7427d1c23',
        'https://de.indeed.com/cmp/Hero-Software?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u0qrcih23802&fromjk=612fa3d4a6ecdeb0',
        'https://de.indeed.com/cmp/Playvox?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u0stqjg8h801&fromjk=0417e312388c86f0',
        'https://de.indeed.com/cmp/Tulip-Interfaces-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u0v0vjg9s803&fromjk=238806b0e6f689f7',
        'https://de.indeed.com/cmp/Egroup?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u111rk7tm802&fromjk=7a2008c61e94be61',
        'https://de.indeed.com/cmp/Objective-Platform?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u129g2doe002&fromjk=fab12ddb4cc31c4f',
        'https://de.indeed.com/cmp/Ebuero-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u13ptj310800&fromjk=743fa61f48a61b9b',
        'https://de.indeed.com/cmp/Hanfried-Personaldienstleistungen-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u14up28f4002&fromjk=7d8e6b7f072c431f',
        'https://de.indeed.com/cmp/VP-Verbund-Pflegehilfe-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u4ea9k7tm802&fromjk=7e862ad708d2ea8b',
        'https://de.indeed.com/cmp/Worknow-Germany-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u4lkg2cc6002&fromjk=5c6f1f9119ebdc45',
        'https://de.indeed.com/cmp/Jobactive-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u4napk7dd802&fromjk=a2b2c8e6e1b524bc',
        'https://de.indeed.com/cmp/Quad-Europe?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u4otbk7d5802&fromjk=2e37488b2d54faeb',
        'https://de.indeed.com/cmp/Peak-Performance?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u4q0jk7tm802&fromjk=0a45464bed38f208',
        'https://de.indeed.com/cmp/Zimmer-Biomet?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u4rl6jqub800&fromjk=63a5c1c6802a3215',
        'https://de.indeed.com/cmp/Syneos-Health-c7687b23?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u4t9qirp1800&fromjk=3f8cd00e2bc97aa9',
        'https://de.indeed.com/cmp/Ecoonline?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u4ut52gag000&fromjk=acfbb6b1f0dec5dc',
        'https://de.indeed.com/cmp/Tecalliance-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u512kje28800&fromjk=1ae6f5022df48d72',
        'https://de.indeed.com/cmp/Aspire-Software?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u54a42e1b000&fromjk=8e2d39bef6430c0d',
        'https://de.indeed.com/cmp/Oracle?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u578ak5ro802&fromjk=043043dc5d8bdbab',
        'https://de.indeed.com/cmp/Nonstop-Consulting?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u5b98k7sv802&fromjk=3e93a3825310c67d',
        'https://de.indeed.com/cmp/Boston-Scientific?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u5db6jjh5802&fromjk=7bb0d7c963c7aff5',
        'https://de.indeed.com/cmp/Circula?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u5fsjiqvq800&fromjk=865ca8476f23c15c',
        'https://de.indeed.com/cmp/Hugo-Boss?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u5if02cc6000&fromjk=36e28b899f52a52f',
        'https://de.indeed.com/cmp/Wattfox-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u96tsirpv800&fromjk=87a4ffb532ea8ef2',
        'https://de.indeed.com/cmp/Nonstop-Consulting?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u98jrje28802&fromjk=3e93a3825310c67d',
        'https://de.indeed.com/cmp/Rapid7?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u9aopk7fq802&fromjk=a3f68cc36814b91c',
        'https://de.indeed.com/cmp/Puma?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u9eb2i453800&fromjk=ace9f66e962fa06f',
        'https://de.indeed.com/cmp/Boston-Scientific?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u9gd8k7q4802&fromjk=7bb0d7c963c7aff5',
        'https://de.indeed.com/cmp/Casafari?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u9idki453803&fromjk=f085ab3fbd79c9c4',
        'https://de.indeed.com/cmp/Lewa-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u9jvak7d5802&fromjk=22c5d78f47cb5645',
        'https://de.indeed.com/cmp/Syneos-Health-c7687b23?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u9l4ik7dd801&fromjk=3f8cd00e2bc97aa9',
        'https://de.indeed.com/cmp/Circula?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u9mnsk7dg803&fromjk=865ca8476f23c15c',
        'https://de.indeed.com/cmp/Framos?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u9o98j310801&fromjk=d5439e65eeb2a9f4',
        'https://de.indeed.com/cmp/Lhh-Knightsbridge?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u9pqojg91800&fromjk=2c03ff689352c6cf',
        "https://de.indeed.com/cmp/O'farrell-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u9st52guc000&fromjk=849da9cd90bf4c1b",
        'https://de.indeed.com/cmp/Actindo-Ag-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9u9ufp2cc9000&fromjk=080edf0f21743a14',
        'https://de.indeed.com/cmp/Exodus-Jobs?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ua0hl2ejr000&fromjk=a5450bc90edc6d25',
        'https://de.indeed.com/cmp/Essenzmedia?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ua24fk7ef802&fromjk=0c98aaeaba28df28',
        'https://de.indeed.com/cmp/Navan-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9udeqhk7dg800&fromjk=95632e32d5924e37',
        'https://de.indeed.com/cmp/Lindner-Hotels-&-Resorts-2?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9udhs2jgah800&fromjk=3fb332b23cb545d1',
        'https://de.indeed.com/cmp/Cos-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9udljsje28800&fromjk=6fd9dc07cb595c97',
        'https://de.indeed.com/cmp/Smartlane-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9udnfak7dd801&fromjk=02cc636ba6b2a6e2',
        'https://de.indeed.com/cmp/Jobvalley-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9udt6hk7h4802&fromjk=6463f3f6de6a5491',
        'https://de.indeed.com/cmp/Likeminded-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9udvjkikqa802&fromjk=07883b6c20fe34b6',
        'https://de.indeed.com/cmp/Exodus-Jobs?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ue1p8iqti802&fromjk=a5450bc90edc6d25',
        'https://de.indeed.com/cmp/The-Pitch-Corporation?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ue3ui21cn002&fromjk=31e3f017a88424ee',
        'https://de.indeed.com/cmp/Pongs-Technical-Textiles-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ue5tpk7ql803&fromjk=6666602c1722381e',
        'https://de.indeed.com/cmp/Evermood?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ue7fck7tm802&fromjk=91aff40c02566199',
        'https://de.indeed.com/cmp/Clous-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ue9h9k7qb802&fromjk=653db3df521ac9d7',
        'https://de.indeed.com/cmp/Charisma--tec-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uebj5j3tv800&fromjk=46dc0293cb5fbd26',
        'https://de.indeed.com/cmp/Workist-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uedokk7bm802&fromjk=a61ad0158719b39e',
        'https://de.indeed.com/cmp/Maui-Jim-Sunglasses?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uegouk7ql806&fromjk=6e3ea6ad1e4b056f',
        'https://de.indeed.com/cmp/H--tec-Systems?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ueiaj28fe000&fromjk=8891ce81aa986373',
        'https://de.indeed.com/cmp/Advastore-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uhtipih35802&fromjk=7146bb470a291da2',
        'https://de.indeed.com/cmp/Meshcloud-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uhv3ek7ql802&fromjk=e26f79b775a8c537',
        'https://de.indeed.com/cmp/Metso-Outotec?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uicv8i3r9804&fromjk=4d374f8051e763fa',
        'https://de.indeed.com/cmp/Coloplast?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uig0i2dof000&fromjk=f46fc18aa92fcddf',
        'https://de.indeed.com/cmp/Arla-Foods?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uij24jjjd800&fromjk=97c812668fae3a95',
        'https://de.indeed.com/cmp/Tdk-Corporation-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uin59j4ov802&fromjk=2e9af49f75199cda',
        'https://de.indeed.com/cmp/Md7-International-(communications)?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uipkqk7hh804&fromjk=6bc5bdd9ef3a104e',
        'https://de.indeed.com/cmp/Arla-Foods?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uirmejksg802&fromjk=1a24523876a18b9b',
        'https://de.indeed.com/cmp/Altair-Engineering?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uj073ih35802&fromjk=99ca48afb487a797',
        'https://de.indeed.com/cmp/SAP?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uj294jjjd809&fromjk=f7f4631c993787d3',
        'https://de.indeed.com/cmp/Nonstop-Consulting?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uj3qsjkt4803&fromjk=e4c73fdca8399c03',
        'https://de.indeed.com/cmp/On-Ag-5?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uj6e728f4000&fromjk=a8eeb2e250bd4620',
        'https://de.indeed.com/cmp/Rs-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uj8g3jji5807&fromjk=bb388ee719c1ca84',
        'https://de.indeed.com/cmp/Candela-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uja4t2e15000&fromjk=c8b84a884a662ec3',
        'https://de.indeed.com/cmp/State-Street?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ujc6v28gm002&fromjk=b77bb061444f52e8',
        'https://de.indeed.com/cmp/Predium?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9umj1fiqti800&fromjk=dbfaffdf15c5bd46',
        'https://de.indeed.com/cmp/Project-A-Ventures?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9umkhpi3pi802&fromjk=c8140ae70e492dc0',
        'https://de.indeed.com/cmp/Project-A-Services-Gmbh-&-Co.-Kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9umm5u2cc9000&fromjk=1988794015d848f0',
        'https://de.indeed.com/cmp/Nezasa-Travel?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9umno7i3pi802&fromjk=a9af08b8d1e2078f',
        'https://de.indeed.com/cmp/Asics?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9umpa62cc9001&fromjk=d24ffebcd0b2d7dc',
        'https://de.indeed.com/cmp/Project-A-Ventures?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9umql0k7e5803&fromjk=8aaa9572ae75713f',
        'https://de.indeed.com/cmp/Finally-Freelancing?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ums11je1v802&fromjk=cfc12f6bf6f11483',
        'https://de.indeed.com/cmp/Jazz-Pharmaceuticals?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9umtn2k7tm804&fromjk=15eb637a6832dc5e',
        'https://de.indeed.com/cmp/Applause-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9umv8tjkt4802&fromjk=0b7f2fe8c2166124',
        'https://de.indeed.com/cmp/Peckwaterbrands?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9un0fck5ro800&fromjk=51fc34d58638307a',
        'https://de.indeed.com/cmp/Skill--fisher-Deutschland-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9un24vjqub802&fromjk=0bf7af2c01fdf2f3',
        'https://de.indeed.com/cmp/Planex-Gmbh-2?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9un4cpjgah800&fromjk=cb7f1a5f4bfed724',
        'https://de.indeed.com/cmp/Personalisten-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9un5fbk7f7802&fromjk=3ea1c470d225d93f',
        'https://de.indeed.com/cmp/Ingredion?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9un71dk7u1800&fromjk=68707a86f4462022',
        'https://de.indeed.com/cmp/Liebwein-Personalmanagement-Und---service-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9un925irr6802&fromjk=ccb4ab82eb62a070',
        'https://de.indeed.com/cmp/Centre-People-Appointments-Ltd.?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uqi6vjqub802&fromjk=61d2856de1942534',
        'https://de.indeed.com/cmp/Topsort?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uqktj2a46000&fromjk=8c90c62f982b8028',
        'https://de.indeed.com/cmp/%EF%BC%AD%EF%BD%89%EF%BD%93%EF%BD%95%EF%BD%8D%EF%BD%89?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uqmjc2gve002&fromjk=e4ae73b0d3cf9f0e',
        'https://de.indeed.com/cmp/Hiab?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uqol1k7tg800&fromjk=4988c3406ce0f17c',
        'https://de.indeed.com/cmp/Tis?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uqr64k7sl800&fromjk=f67abb7436171f8b',
        'https://de.indeed.com/cmp/Stokke-2?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uqsq0k7ef802&fromjk=af2eaa6b84a71f8e',
        'https://de.indeed.com/cmp/Solita?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uqubtirpp800&fromjk=ffd95b69055c0cbb',
        'https://de.indeed.com/cmp/Complero-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ur0cv2ejr002&fromjk=79c3959f206d672b',
        'https://de.indeed.com/cmp/Shure?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ur2072e15002&fromjk=af54a35810b05b20',
        'https://de.indeed.com/cmp/Brambles-7?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ur3hq2doe002&fromjk=03c5d17f1e068069',
        'https://de.indeed.com/cmp/Hugo-Boss?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ur57ck7qb800&fromjk=e58c5bd92aaf9161',
        'https://de.indeed.com/cmp/Landa?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ur782jktd802&fromjk=0173cba9e53113ad',
        'https://de.indeed.com/cmp/Statista-Ltd.?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ur906iqvq802&fromjk=842d3d7eaa6a4fd0',
        'https://de.indeed.com/cmp/Stackpole-International?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9urb802cc6002&fromjk=aa702822e6c9afb3',
        'https://de.indeed.com/cmp/Rocket-Software?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9urdqnk7sv802&fromjk=ac276c58fc02029f',
        'https://de.indeed.com/cmp/Multipharma,-Inc.-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uurnhih23802&fromjk=1a10befc4d6d20ec',
        'https://de.indeed.com/cmp/Bofest-Consult?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uutd0k7h4802&fromjk=886aa1149f9ce5ee',
        'https://de.indeed.com/cmp/Foodji-Marketplace-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uv0hc2a46000&fromjk=0a8983a555c88f3f',
        'https://de.indeed.com/cmp/Displayce?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uv453k7hh800&fromjk=21066970871dab4d',
        'https://de.indeed.com/cmp/Arrow-Electronics?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uv7mii453800&fromjk=b72ee4642f0f29fe',
        'https://de.indeed.com/cmp/Hugo-Boss?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uv9nik7sl800&fromjk=4d0920b67fa90def',
        'https://de.indeed.com/cmp/Alcon?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uvftsk7dd803&fromjk=ebdb48cf04e3ce0b',
        'https://de.indeed.com/cmp/Harkort-Consulting-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uvinmj4ov800&fromjk=d53e0fca2dd7ffa2',
        'https://de.indeed.com/cmp/Honeywell?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uvlr22e15002&fromjk=6f5579bb3a22e55d',
        'https://de.indeed.com/cmp/Meetago-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uvpb5jqub801&fromjk=33b0eb0397775544',
        'https://de.indeed.com/cmp/Firstweld?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uvrd1i3r9800&fromjk=40854e72eb2a125f',
        'https://de.indeed.com/cmp/Movexm-Ttr-Group-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uvsun2e1b002&fromjk=d3b2b7bc84216a44',
        'https://de.indeed.com/cmp/Nobel-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9uvuhck7dg802&fromjk=2d7b56680d658283',
        'https://de.indeed.com/cmp/Bd?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v003hikqa802&fromjk=8e2a879780b129fa',
        'https://de.indeed.com/cmp/Tsi-Incorporated?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v01nbirr6802&fromjk=ddbb03f60f2bca4b',
        'https://de.indeed.com/cmp/Johnson-Electric?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v3a2ak5ro802&fromjk=6e77e1426774d8ba',
        'https://de.indeed.com/cmp/Advanced-Nutrients?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v3h46jgah800&fromjk=d86250ebbeda6f57',
        'https://de.indeed.com/cmp/Hugo-Boss?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v3m4v21cn003&fromjk=a567db028a7e47bc',
        'https://de.indeed.com/cmp/HR-in-Kraft-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v3nm9jkva802&fromjk=c144b99ae57ab71d',
        'https://de.indeed.com/cmp/Alaiko?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v3orkjjh5803&fromjk=100b2787b4ad4cea',
        'https://de.indeed.com/cmp/Armacell?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v6jf62guc000&fromjk=59de97311a82ebf3',
        'https://de.indeed.com/cmp/Packmatic-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v6oliirpo807&fromjk=cecfeedb100e1858',
        'https://de.indeed.com/cmp/Advanced-Nutrients?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v6q6928f4006&fromjk=851aa8e35e4e2586',
        'https://de.indeed.com/cmp/Essilor?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v6snsj3v6800&fromjk=05ce4e13bc8af524',
        'https://de.indeed.com/cmp/Novartis?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v6uppirr6802&fromjk=b21e97aae3e2eab2',
        'https://de.indeed.com/cmp/Inspire-Technologies-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v70qj28fe000&fromjk=9b508b3825513eb5',
        'https://de.indeed.com/cmp/Radware?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v72cdk7tm802&fromjk=a89be77adcaab889',
        'https://de.indeed.com/cmp/Charles-River-Laboratories?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v75ekk7qb800&fromjk=734da22a738a8adc',
        'https://de.indeed.com/cmp/Rehau-b6d24f0e?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9v76iki3ru800&fromjk=d3f5666c3a8d10d8',
        'https://de.indeed.com/cmp/Rehau-b6d24f0e?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vafll2dof002&fromjk=d3f5666c3a8d10d8',
        'https://de.indeed.com/cmp/Studydrive-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vaim1irpv802&fromjk=775c506224f3885b',
        'https://de.indeed.com/cmp/Essilor?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vam80ih3f801&fromjk=05ce4e13bc8af524',
        'https://de.indeed.com/cmp/Thermo-Fisher-Scientific?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vdhtp2doe002&fromjk=77b8b9de7addb860',
        'https://de.indeed.com/cmp/Hugo-Boss?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vdjbkk7u1800&fromjk=e58c5bd92aaf9161',
        'https://de.indeed.com/cmp/Novartis?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vdkv0k7hh800&fromjk=eeb6ddc7eb8a2f9b',
        'https://de.indeed.com/cmp/Heraeus?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vdmgjiqvq801&fromjk=b03c87837985c624',
        'https://de.indeed.com/cmp/Advanced-Nutrients?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vdo2m2gag000&fromjk=851aa8e35e4e2586',
        'https://de.indeed.com/cmp/Relx-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vdq48ip9m802&fromjk=74721658719b8630',
        'https://de.indeed.com/cmp/Sage?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vds5rk7ji800&fromjk=4246d775d46fc2c4',
        'https://de.indeed.com/cmp/Civey-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vdtr8je28800&fromjk=3304ea1ad489cb1b',
        'https://de.indeed.com/cmp/Dentsply-Sirona?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ve0dn28gm000&fromjk=4a982000397ba1d6',
        'https://de.indeed.com/cmp/Nonstop-Consulting?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ve20pirp1800&fromjk=7af588ba4a0179bf',
        'https://de.indeed.com/cmp/Honeywell?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9ve36jjjhl802&fromjk=9881eb5d344c6eda',
        'https://de.indeed.com/cmp/Truecommerce?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vhbu0k7dg800&fromjk=eb7f0c4d2e5b617c',
        'https://de.indeed.com/cmp/Guided-Solutions-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vhdvtjji5802&fromjk=c5f66adde6a5b611',
        'https://de.indeed.com/cmp/Epunkt-Talentor-International-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vhfb0ih23802&fromjk=a31bbaf9b86ee2d3',
        'https://de.indeed.com/cmp/Talentor-Sweden-Ab?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vhgfck7f7800&fromjk=07b0fa5da1d92a2f',
        'https://de.indeed.com/cmp/Borgwarner?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vhhke2cc9002&fromjk=ae5cc9157a0ba2e8',
        'https://de.indeed.com/cmp/Global-Asc?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vhjatk7ef801&fromjk=18294581e4337348',
        'https://de.indeed.com/cmp/Keysight-Technologies?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vhksek7t7800&fromjk=e24fae8905472379',
        'https://de.indeed.com/cmp/Groupe-Lvmh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vhmdsj310804&fromjk=51b679b932632aa8',
        'https://de.indeed.com/cmp/Allianz?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vho032cc6002&fromjk=a9fab90daf2d27d6',
        'https://de.indeed.com/cmp/Academic-Work?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vhq3kj4ov802&fromjk=05c306a863e7474f',
        'https://de.indeed.com/cmp/Kyndryl?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vhs65k7tg802&fromjk=42e5931283901e1a',
        'https://de.indeed.com/cmp/Sportbusinessjobs?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vhtp8jksg802&fromjk=43cc715522420e25',
        'https://de.indeed.com/cmp/Tdk-Corporation-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vi1b4k7tg802&fromjk=738b54e35f66013b',
        'https://de.indeed.com/cmp/Canonical?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vi4cvirp1800&fromjk=ae91585fddd1ed68',
        'https://de.indeed.com/cmp/Thermo-Fisher-Scientific?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vi71pje28800&fromjk=77b8b9de7addb860',
        'https://de.indeed.com/cmp/Overlack-Ag-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vlfqajkva802&fromjk=4415e98f977c8120',
        'https://de.indeed.com/cmp/Celonis-7?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vljaaiqvq802&fromjk=c3767b1aab69dc10',
        'https://de.indeed.com/cmp/Peter-Park?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vllcm21cn000&fromjk=e65630a9afaf142c',
        'https://de.indeed.com/cmp/Sportbusinessjobs?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vln1jk7qb800&fromjk=43cc715522420e25',
        'https://de.indeed.com/cmp/City-Job-Offers?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vlq4ek7tg802&fromjk=49f7ea5b1a38d361',
        'https://de.indeed.com/cmp/Acronis-International-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vlt3miqti802&fromjk=e88f02ba7156f702',
        'https://de.indeed.com/cmp/Epunkt-Talentor-International-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vlulpk7q4800&fromjk=a31bbaf9b86ee2d3',
        'https://de.indeed.com/cmp/Talentor-Sweden-Ab?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vm07nk5ro800&fromjk=07b0fa5da1d92a2f',
        'https://de.indeed.com/cmp/Freudenberg-Real-Estate-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vm29hk7fq802&fromjk=eed441823008f5d9',
        'https://de.indeed.com/cmp/Arrow-Electronics?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vm4a4je1e802&fromjk=b1daa071d93cbe4e',
        "https://de.indeed.com/cmp/Moody's-Corporation?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vm6bsje28802&fromjk=adaa65790a16cac8",
        'https://de.indeed.com/cmp/Allianz?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vm8cijg9s800&fromjk=a9fab90daf2d27d6',
        'https://de.indeed.com/cmp/Masterplan.com-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vm9urip9m803&fromjk=845ac6ffc2fa0537',
        'https://de.indeed.com/cmp/Keysight-Technologies?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vmbmjirpo802&fromjk=e24fae8905472379',
        'https://de.indeed.com/cmp/Tdk-Corporation-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vmdr3k7h4800&fromjk=58bbeff9ff3ff057',
        'https://de.indeed.com/cmp/Keysight-Technologies?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vpscpi3r2800&fromjk=d1e4549b58f5e311',
        'https://de.indeed.com/cmp/Inveox-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vpuvq2dof002&fromjk=4ad7c7b7c0e4cb42',
        'https://de.indeed.com/cmp/Charles-River-Laboratories?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vq210k7fq802&fromjk=734da22a738a8adc',
        'https://de.indeed.com/cmp/Groupe-Lvmh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vq54qk7u4802&fromjk=51b679b932632aa8',
        'https://de.indeed.com/cmp/Tdk-Corporation-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vq7m7k7d5800&fromjk=a2f4a99f9dcd85bc',
        'https://de.indeed.com/cmp/Glen-Callum-Associates-Ltd?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vqa73k7dd801&fromjk=5a8d5a58685649ff',
        'https://de.indeed.com/cmp/Randstad?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vqc8bjg9s800&fromjk=733893ae569e3163',
        'https://de.indeed.com/cmp/Nexthink?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vqfq8j3tv802&fromjk=038b5798c7afc4f8',
        'https://de.indeed.com/cmp/Tdk-Corporation-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vqj97k7f7802&fromjk=bea0313a9d0b6227',
        'https://de.indeed.com/cmp/The-Sansin-Corporation-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vqlbbih35800&fromjk=f930b48258370201',
        'https://de.indeed.com/cmp/Simscale-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vqmshj3tv803&fromjk=5dd9ebbc9c1f33c0',
        'https://de.indeed.com/cmp/The-Qt-Company?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vqou8k7ef802&fromjk=2cfeda33f881a7d2',
        'https://de.indeed.com/cmp/Startyoursales?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vqrv8k7ql802&fromjk=99c3f928ca47f02b',
        'https://de.indeed.com/cmp/Navan-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vqth9irpo800&fromjk=5c63defe2561ca3b',
        'https://de.indeed.com/cmp/Landa-Corporation?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vquj7k7qb802&fromjk=3013035709432680',
        'https://de.indeed.com/cmp/Xeotek?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vugmhjg9s800&fromjk=5ec85f2391bbc9c5',
        'https://de.indeed.com/cmp/Sentinelone?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vumkq2e1b000&fromjk=c389062638ccf2d5',
        'https://de.indeed.com/cmp/Pipa-Engagement?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vup7pk7st801&fromjk=f4d18e1d5eee5706',
        'https://de.indeed.com/cmp/Lumiform?campaignid=mobvjcmp&from=mobviewjob&tk=1gp9vur9tk7io802&fromjk=ba350d4758f620aa',
        'https://de.indeed.com/cmp/Peter-Park-System-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa01krpk7q4800&fromjk=9d4415a5492f67fe',
        'https://de.indeed.com/cmp/Legal-Os?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa01m3aikoh800&fromjk=c32f81c2108eb5c6',
        'https://de.indeed.com/cmp/Planted-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa01npt21cn000&fromjk=78b4570aff0222d0',
        'https://de.indeed.com/cmp/Valuecase?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa01pcnj3v6802&fromjk=fe4cb95115d69523',
        'https://de.indeed.com/cmp/Navan-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa01qffk7f7802&fromjk=5c973656b981ac8e',
        'https://de.indeed.com/cmp/Virtuagym?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa01rh5je28800&fromjk=e7a964fa00034bc0',
        'https://de.indeed.com/cmp/Neobrain?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa01smg2guc002&fromjk=c0351cf0cd33afe9',
        'https://de.indeed.com/cmp/Aucta?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa04mdmjg9s802&fromjk=0f06f572062c4c3a',
        'https://de.indeed.com/cmp/Next-Big-Thing-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa04nfl2gag002&fromjk=1b97b298e00fdd1d',
        'https://de.indeed.com/cmp/Aucta?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0aq66ikoh800&fromjk=0f06f572062c4c3a',
        'https://de.indeed.com/cmp/Emil-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0aro8j310802&fromjk=23848e2fdc11b6b5',
        'https://de.indeed.com/cmp/Sosafe-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0ata5k7t7802&fromjk=02d210b596c861ae',
        'https://de.indeed.com/cmp/Openproject-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0ausmjjh5802&fromjk=c7fda4fbc4166a11',
        'https://de.indeed.com/cmp/Pentagon-International-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0b0dkiqti800&fromjk=c048948d5682d0e4',
        'https://de.indeed.com/cmp/Smartblick?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0b1gi21cn000&fromjk=30b74990e345c05d',
        'https://de.indeed.com/cmp/Wealthpilot-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0b3262gag002&fromjk=f4aa26ffd312109a',
        'https://de.indeed.com/cmp/Peloton?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0b5qiirpv801&fromjk=8244e41ad9683f0f',
        'https://de.indeed.com/cmp/Smith-c210cb62?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0b7nc2a46000&fromjk=0c2fc42a6bc5b9c2',
        'https://de.indeed.com/cmp/Flinker?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0b9ad2cc9000&fromjk=421c36317b91bbde',
        'https://de.indeed.com/cmp/M%C3%BChlbauer-Gmbh-&-Co.-Kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0bah42doe002&fromjk=dad23487708897fc',
        'https://de.indeed.com/cmp/Caiz-Development-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0bckkk7q4800&fromjk=89cc5375cc2f63f7',
        'https://de.indeed.com/cmp/Everphone-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0benkje3h800&fromjk=48db057a58f03e2e',
        'https://de.indeed.com/cmp/Ecm-Sales-Solutions-Ltd?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0bg8ujktd800&fromjk=0ea92fac28952545',
        'https://de.indeed.com/cmp/Yoffix?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0epp4ih23800&fromjk=543a004fcb8f01d1',
        'https://de.indeed.com/cmp/Gerresheimer?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0esa7k7sl802&fromjk=b70a64bc29b439cd',
        'https://de.indeed.com/cmp/Valueworks-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0etgfk7ii802&fromjk=e5406cd9687e9f34',
        'https://de.indeed.com/cmp/Synctive?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0evldk7t7800&fromjk=47413cbd85b0958b',
        'https://de.indeed.com/cmp/Art-News-Agency?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0f1f0k7ii800&fromjk=2b14b5e3c4648048',
        'https://de.indeed.com/cmp/Sosafe-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0f2r22a46002&fromjk=02d210b596c861ae',
        'https://de.indeed.com/cmp/Voquz-Labs-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0f42dje1v800&fromjk=1a6c9f3c42f3836a',
        'https://de.indeed.com/cmp/Beyondtrust?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0f5lkk7qb802&fromjk=d9db5606236bd5d3',
        'https://de.indeed.com/cmp/Vytruve?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0f78dj310802&fromjk=5aed4099a5e97dfd',
        'https://de.indeed.com/cmp/Doit-International-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0f919irpp802&fromjk=aff46c5fbac7774d',
        'https://de.indeed.com/cmp/Smith-c210cb62?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0fag82dof002&fromjk=0c2fc42a6bc5b9c2',
        'https://de.indeed.com/cmp/Energieweit-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0fc2njktd802&fromjk=7afe4c49ea7fb10e',
        'https://de.indeed.com/cmp/Mate?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0fdnh2ejr000&fromjk=b67c9dbb4f45faba',
        'https://de.indeed.com/cmp/Cloudflare-6?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0fg93k7e5802&fromjk=d9cd1139eba50205',
        'https://de.indeed.com/cmp/Openproject-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0ficrk7ji801&fromjk=c7fda4fbc4166a11',
        'https://de.indeed.com/cmp/Octopus-Energy?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0iqkik7tm802&fromjk=d93d9962d0e00bd0',
        'https://de.indeed.com/cmp/Cargo.one?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0j38ti3pi804&fromjk=efe1e1c6729a52a4',
        'https://de.indeed.com/cmp/Bots-and-People-Product-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0j579jji5803&fromjk=d947e38dbf63f364',
        'https://de.indeed.com/cmp/Coachhub-2?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0j6q2irr6802&fromjk=77ec7252418ff62b',
        'https://de.indeed.com/cmp/Actano-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0j8rsjg91801&fromjk=deede5f64187143f',
        'https://de.indeed.com/cmp/Inuru?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0jaep28gm002&fromjk=117dab48a1bdc8a6',
        'https://de.indeed.com/cmp/Container-Xchange?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0jd07k7e5800&fromjk=d81bdc36f6c1827a',
        'https://de.indeed.com/cmp/Hornetsecurity?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0jf33jjhl801&fromjk=ffeace3d75bfe21b',
        'https://de.indeed.com/cmp/Flinker?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0jgl7iqvq802&fromjk=421c36317b91bbde',
        'https://de.indeed.com/cmp/Lx-Hausys-Europe-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0jinki3r2800&fromjk=1cf26c57271c50c8',
        'https://de.indeed.com/cmp/Everphone-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0jk9o2gag000&fromjk=48db057a58f03e2e',
        'https://de.indeed.com/cmp/X--nrw-Gmbh---Xerox-Premier-Production-Reseller-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0jlrije28800&fromjk=632376785a08515d',
        'https://de.indeed.com/cmp/Dracoon-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0jnt3k7sl802&fromjk=ece34ade58276787',
        'https://de.indeed.com/cmp/Cross-Alm?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0jpf7k7fq802&fromjk=4e71e7366f6e0a6b',
        'https://de.indeed.com/cmp/Sep-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0jqhmk7qb800&fromjk=79d11a1897cb394b',
        'https://de.indeed.com/cmp/Appinio-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0n4o4ip9m800&fromjk=10c4abe26233f0a8',
        'https://de.indeed.com/cmp/Lawlift-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0n6auirpo802&fromjk=324a3f9a00d45119',
        'https://de.indeed.com/cmp/Doit-International-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0n8d9k7e5802&fromjk=aff46c5fbac7774d',
        'https://de.indeed.com/cmp/Valsight-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0najok7ql802&fromjk=ca3bf3b411c9ea14',
        'https://de.indeed.com/cmp/Energieweit-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0ncks2guc002&fromjk=7afe4c49ea7fb10e',
        'https://de.indeed.com/cmp/Cross-Alm?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0nf9g2gve002&fromjk=4e71e7366f6e0a6b',
        'https://de.indeed.com/cmp/Roomhero-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa0nialk7tg800&fromjk=f050490b02532760',
        'https://de.indeed.com/cmp/Mate?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1gti02cc6000&fromjk=85885a6be0f0e03d',
        'https://de.indeed.com/cmp/Sep-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1gv3kk7f7800&fromjk=79d11a1897cb394b',
        'https://de.indeed.com/cmp/Notchdelta-Executive-Search?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1h06hjg9s802&fromjk=2c0c80cd6c275bbb',
        'https://de.indeed.com/cmp/Lx-Hausys-Europe-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1h1tc2e15005&fromjk=1cf26c57271c50c8',
        'https://de.indeed.com/cmp/Lanes-&-Planes-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1h3cjk7q4800&fromjk=1880c6cf6e8e8297',
        'https://de.indeed.com/cmp/Planex-Gmbh-Die-Jobstrategen?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1jt2hikoh804&fromjk=66698b92654e2b47',
        'https://de.indeed.com/cmp/Oculai-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1k0gok7fq802&fromjk=6087312761521c7a',
        'https://de.indeed.com/cmp/Agicap-Deutschland?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1k472jkt4800&fromjk=f677b0e409fcd77f',
        'https://de.indeed.com/cmp/Virtuagym?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1k67g2guc002&fromjk=6737bfe2fd2664e4',
        'https://de.indeed.com/cmp/Proemion-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1k8sfipau800&fromjk=45f74a1c883e7f19',
        'https://de.indeed.com/cmp/Concentrix?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1kauiih23803&fromjk=d3c4826a283b7512',
        'https://de.indeed.com/cmp/Deel?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1kdfrk7ej802&fromjk=077cd3d0d437f23c',
        'https://de.indeed.com/cmp/Workist-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1kf4mk7dd800&fromjk=86dbc809e17c4ab0',
        'https://de.indeed.com/cmp/Alaiko-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1kgmk28gm002&fromjk=f2ee1dbd17716afd',
        'https://de.indeed.com/cmp/Pure-Storage?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1o8eli3ru804&fromjk=a189364dabc6ffca',
        'https://de.indeed.com/cmp/Coachhub-2?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1oc0jjqub802&fromjk=0b7496d31eb09f28',
        'https://de.indeed.com/cmp/Actief-Personalmanagement-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1oe4vk7e5802&fromjk=a25c7ac9daba7b1c',
        'https://de.indeed.com/cmp/Hrpeople?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1og6njg8h802&fromjk=6702cb276abe1b71',
        'https://de.indeed.com/cmp/Joblogistik-Personal-Partner-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1oj8a2gve002&fromjk=949869cf83677efa',
        'https://de.indeed.com/cmp/Deel?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1olbuiqvq802&fromjk=ef82c6bff480d859',
        'https://de.indeed.com/cmp/Careforce-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1onf721cn000&fromjk=be9ae65e3db8f971',
        'https://de.indeed.com/cmp/Mate?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1oph6k7sv802&fromjk=383116f776de638e',
        'https://de.indeed.com/cmp/Deel?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1osj62a46002&fromjk=1c588a6835641418',
        'https://de.indeed.com/cmp/Deel?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1oumcih23802&fromjk=7620f243804dc910',
        'https://de.indeed.com/cmp/Black-Pen-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1p0npk7io802&fromjk=635bfd3732dff1aa',
        'https://de.indeed.com/cmp/Dropsuite?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1p2q6k7io802&fromjk=8ae8104de7210d91',
        'https://de.indeed.com/cmp/Europcell-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1p5gj2gve002&fromjk=24a45e92366b4db1',
        'https://de.indeed.com/cmp/Leanix?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1p7pfk7ql800&fromjk=061e84187c635320',
        'https://de.indeed.com/cmp/Knowunity-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1pcjvk7d5803&fromjk=f4008bdb66bc7ee0',
        'https://de.indeed.com/cmp/Totalenergies?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1ti7p2a46002&fromjk=7bcc0ad2202d49a0',
        'https://de.indeed.com/cmp/Leanix?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1tlo5ikqa802&fromjk=061e84187c635320',
        'https://de.indeed.com/cmp/Capmo-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1tp9kk7sv800&fromjk=97b2c83e899ad791',
        'https://de.indeed.com/cmp/7learnings?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1tsqpk7u4800&fromjk=3d285ecbaa68468c',
        'https://de.indeed.com/cmp/Zeiss-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1tvrqk7tg802&fromjk=cc8f6f9bfee80f1a',
        'https://de.indeed.com/cmp/Mars?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1u1t8je1v800&fromjk=67c990b4f0bdf372',
        'https://de.indeed.com/cmp/Exfo?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1u5tvi453802&fromjk=61daf978576df841',
        'https://de.indeed.com/cmp/Spacefill-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1u7g12e1b002&fromjk=90dcbcc016987445',
        'https://de.indeed.com/cmp/Drsmile?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1u9htj310803&fromjk=3a43d94e7f8f046d',
        'https://de.indeed.com/cmp/Givaudan?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1uditjg8h800&fromjk=65e301c3e9d56325',
        'https://de.indeed.com/cmp/Buffalo-Boots-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1uhi8k5ro803&fromjk=67353f660578a1d0',
        'https://de.indeed.com/cmp/Wenzel-Metrology-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1ujkbje1v802&fromjk=d67e3ad31f4b4425',
        'https://de.indeed.com/cmp/Abercrombie-&-Fitch?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1um4l2gag003&fromjk=92937e25029d7bb9',
        'https://de.indeed.com/cmp/Abbott?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1ur51k7t7800&fromjk=8b5e5d9b88f83d49',
        'https://de.indeed.com/cmp/Check-Point-Software-Technologies?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa1uv5f2ejr004&fromjk=e40fc884052d004f',
        'https://de.indeed.com/cmp/U.S.-Army?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa229sik5ro800&fromjk=59682cea67d2042b',
        'https://de.indeed.com/cmp/Wenzel-Metrology-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa22bt3jjjd800&fromjk=d67e3ad31f4b4425',
        'https://de.indeed.com/cmp/Gilly-Hicks?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa22did21cn002&fromjk=de65a373e7cec0d3',
        'https://de.indeed.com/cmp/Coboc-Gmbh-&-Co.-Kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa22f4ek7ef803&fromjk=9e44d56c1796e928',
        'https://de.indeed.com/cmp/Buffalo-Boots-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa22h5hk7d5802&fromjk=67353f660578a1d0',
        'https://de.indeed.com/cmp/U.S.-Air-Force?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa22konk7sv802&fromjk=da3d54e6b74756d9',
        'https://de.indeed.com/cmp/Abercrombie-&-Fitch?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa22mf5ip9m802&fromjk=92937e25029d7bb9',
        'https://de.indeed.com/cmp/Onboard-Crm?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa22o0e2a46002&fromjk=8f8319e5fffc5638',
        'https://de.indeed.com/cmp/7learnings?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa22pj7k7tm802&fromjk=3d285ecbaa68468c',
        'https://de.indeed.com/cmp/Capmo-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa22ujjje28802&fromjk=97b2c83e899ad791',
        'https://de.indeed.com/cmp/Psg-A-Dover-Company?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa2327kirpp802&fromjk=c76f2324f4547fcc',
        'https://de.indeed.com/cmp/Hollister-Co?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa23688ip9m800&fromjk=6be6b48fe9dc2eae',
        'https://de.indeed.com/cmp/Prosolution?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa238aojkt4802&fromjk=53fd291c03655512',
        'https://de.indeed.com/cmp/Hugo-Boss?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa239fkk7bm802&fromjk=ab7173585569529b',
        'https://de.indeed.com/cmp/Check-Point-Software-Technologies?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa23b3kjkva802&fromjk=e40fc884052d004f',
        'https://de.indeed.com/cmp/Pvh-Corp.?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa26i732guc002&fromjk=ccf1120c3f010495',
        'https://de.indeed.com/cmp/Drsmile?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa26jq5irp1802&fromjk=3a43d94e7f8f046d',
        'https://de.indeed.com/cmp/Convatec?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa26lt5jji5802&fromjk=98466f4df57d17a2',
        'https://de.indeed.com/cmp/Tdk-Corporation-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa26nf3k7ef800&fromjk=4b849e1b4a2d8784',
        'https://de.indeed.com/cmp/Infineon-Technologies?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa26p0u2ejr002&fromjk=c196b40b5ca2e18c',
        'https://de.indeed.com/cmp/Bny-Mellon?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa26r2fk7tg800&fromjk=f689471ddc3f1d9a',
        'https://de.indeed.com/cmp/Shell?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa26to7jji5802&fromjk=c1f89c820c713dc6',
        'https://de.indeed.com/cmp/Career-Management-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa271nqk7dd802&fromjk=14ca6c6bc3e15478',
        'https://de.indeed.com/cmp/Msd?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa273pdk7f7802&fromjk=d42ef8cb329be6f9',
        'https://de.indeed.com/cmp/Meltwater?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa274v128gm002&fromjk=34e609a5f3f8142d',
        'https://de.indeed.com/cmp/Orion-Engineered-Carbons-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa276d7k7tm802&fromjk=6739dad3a6bc546c',
        'https://de.indeed.com/cmp/Tacto-Technology-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa277fik7dg800&fromjk=f0f73dc0c77098bd',
        'https://de.indeed.com/cmp/Loftware,-Inc.-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa278rgk7q4803&fromjk=a37cd1a31d2d9606',
        'https://de.indeed.com/cmp/Servicenow?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa27a7a2e1b002&fromjk=3cecc2c4f0036e32',
        'https://de.indeed.com/cmp/Tdk-Corporation-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gpa27cb0k7st803&fromjk=3644c7b062f0b6fb']

    # print(company_urls)
    # with ThreadPoolExecutor() as executor:
    #     worker = partial(get_data, ua=ua, cookies=cookies, proxies=proxies)
    #     for result in executor.map(worker, company_urls):
    #         print(result)
    #         to_csv(result, 'junior sales.csv')


    for url in company_urls:
        try:
            result, status_code= get_data(url, ua=ua, cookies=cookies, proxies=proxies)
            if status_code == 200:
                print(result)
                print(status_code)

            else:
                print(result)
                print(status_code)
                search_result_url, cookies, ua = job_result_url(proxies, url, term)
                result, status_code = get_data(url, ua=ua, cookies=cookies, proxies=proxies)

        except (ConnectionRefusedError, ConnectError, RemoteProtocolError) as e:
            print(e)
            time.sleep(30)
            search_result_url, cookies, ua = job_result_url(proxies, url, term)
            result, status_code = get_data(url, ua=ua, cookies=cookies, proxies=proxies)
            print(result)
            print(status_code)

        to_csv(result, 'Sales Representative Indeed.csv')

if __name__ == '__main__':
    start = time.perf_counter()
    main()
    print(f'Processing Time: {time.perf_counter() - start} second(s)')