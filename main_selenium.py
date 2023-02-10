import asyncio
import csv
import time
from fake_useragent import UserAgent
from random import choice
from selectolax.parser import HTMLParser
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
import httpx
from dataclasses import dataclass
import re

proxies = [#'154.12.198.179:8800',
           '192.126.253.48:8800',
           '192.126.250.22:8800',
           #'154.38.30.117:8800',
           '192.126.253.197:8800',
           '192.126.253.59:8800',
           #'154.38.30.196:8800',
           '192.126.253.134:8800',
           #'154.12.198.69:8800',
           '192.126.250.223:8800'
           ]

@dataclass
class Company:
    name:str
    website:str
    linkedin:str

def to_csv(data):
    with open('result.csv', 'a+') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def webdriver_setup(proxy = None):
    ip, port = proxy.split(sep=':')
    ua = UserAgent()
    useragent = ua.firefox
    firefox_options = Options()

    firefox_options.add_argument('-headless')
    firefox_options.add_argument('--no-sandbox')

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

def job_result_url(proxies, url, term, location):
    print('Get job list...')
    proxy = choice(proxies)
    driver = webdriver_setup(proxy)
    driver.get(url)
    cookies = driver.get_cookies()
    ua = driver.execute_script("return navigator.userAgent")
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.jobsearch-Yosegi')))
    parent = driver.find_element(By.CSS_SELECTOR, 'div.jobsearch-Yosegi')
    input_term = parent.find_element(By.ID,'text-input-what')
    input_term.send_keys(term + Keys.TAB + location + Keys.RETURN)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.mosaic-provider-jobcards.mosaic.mosaic-provider-jobcards.mosaic-provider-hydrated')))
    result = driver.current_url.rsplit('&', 1)[0] + '&start=0'
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
        wait = WebDriverWait(driver, 15)

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
    return company_urls

def get_data_httpx(url, cookies_list, ua, proxies):
    print('get_company_url...')
    cookies = dict()
    header = {"user-agent":ua}
    for item in cookies_list:
        cookies[item['name']] = item['value']


def get_linkedin(search_term, proxy):
    print("Searching for linkedin url...")
    formated_proxy = {
        "http://": f"http://{proxy}",
        "https://": f"http://{proxy}",
    }
    header = {
        "User-Agent": "Mozilla/5.0(Windows NT 6.1;Win64;x64;rv:109.0)Gecko/20100101Firefox/109.0"
    }

    url = f"https://html.duckduckgo.com/html/?q={re.sub('[^A-Za-z0-9]+', '+', search_term)}+linkedin"
    with httpx.Client(proxies=formated_proxy, headers=header, timeout=(3,27)) as client:
        response = client.post(url)
    tree = HTMLParser(response.text)
    result = tree.css_first("div#links.results > div.result.results_links.results_links_deep.web-result > div.links_main.links_deep.result__body > h2.result__title > a.result__a").attributes['href']
    return result

def get_data(driver, url, proxy):
    print('Get data...')
    driver.get(url)
    wait = WebDriverWait(driver, 15)

    # Get Company name
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'body.turnstileInfo')))
    Company.name = driver.find_element(By.CSS_SELECTOR, 'div[itemprop="name"]').text

    # Get Company URL
    try:
        parent = driver.find_element(By.CSS_SELECTOR, 'ul.css-1jgykzt.e37uo190')
        Company.website = parent.find_element(By.PARTIAL_LINK_TEXT, 'ebs').get_attribute('href')
    except NoSuchElementException:
        Company.website = None

    # Get Company linkedin
    try:
        parent = driver.find_element(By.CSS_SELECTOR, 'ul.css-1jgykzt.e37uo190')
        Company.linkedin = parent.find_element(By.PARTIAL_LINK_TEXT, 'inked').get_attribute('href')
    except NoSuchElementException:
        Company.linkedin = get_linkedin(Company.name, proxy)

    driver.quit()
    return Company

def main():
    url = 'https://de.indeed.com/'
    term = 'junior sales'
    location = 'Berlin'

    search_result_url, cookies, ua = job_result_url(proxies, url, term, location)
    #
    print(search_result_url, cookies, ua)
    #
    # company_urls = get_company_url(search_result_url, proxies=proxies)
    # print(company_urls)
    # to_csv(company_urls)

    company_urls = ['https://de.indeed.com/cmp/Hotel-Mssngr?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jnhgjjiv802&fromjk=2626f305ad399745', 'https://de.indeed.com/cmp/Sonnen?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6joj1jqvi802&fromjk=e846fde655293c2e', 'https://de.indeed.com/cmp/Nh-8adc4d2a?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jpa32e11003&fromjk=cc7dd09f67a7720d', 'https://de.indeed.com/cmp/Highcoordination-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jpupl22k801&fromjk=e4374dd769afabe7', 'https://de.indeed.com/cmp/Instinct3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jqj5k5ro803&fromjk=dc8355820312c198', 'https://de.indeed.com/cmp/Svarmony?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jr9rkkd7801&fromjk=c0f24575b0cdd119', 'https://de.indeed.com/cmp/Varc-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jrv0k7sn805&fromjk=17fb64f24bbd28b3', 'https://de.indeed.com/cmp/Trakken-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jskr2m5n000&fromjk=3c9e429cd64ad558', 'https://de.indeed.com/cmp/Berry-Global,-Inc?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jtn4ir3o802&fromjk=2f307529e5e74403', 'https://de.indeed.com/cmp/All-For-One-Group-Se?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6juc6ikd9800&fromjk=6fb8710cc3cb1be1', 'https://de.indeed.com/cmp/Targomo?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jv0qj3vv800&fromjk=f7ff39626cd0f56f', 'https://de.indeed.com/cmp/Kreuzwerker-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jvlskkfn802&fromjk=e6b45259b1d839d6', 'https://de.indeed.com/cmp/Coffee-Circle-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6k0ccjjgs802&fromjk=da42d794164550f8', 'https://de.indeed.com/cmp/Pair-Finance-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6k11ojqun802&fromjk=7849b844150895fb', 'https://de.indeed.com/cmp/Make-IT-Fix-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6k234jjgs802&fromjk=d7da040a0c4e08ad', 'https://de.indeed.com/cmp/Park-&-Control-Pac-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l5kok7t1802&fromjk=e6571b36e8743b24', 'https://de.indeed.com/cmp/Hrworks-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l6mbirp1802&fromjk=340238d4d02a7f0d', 'https://de.indeed.com/cmp/Adevinta-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l7bijqvd802&fromjk=b69ad2d7b20d6203', 'https://de.indeed.com/cmp/A.-Lange-&-S%C3%B6hne?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l80pk7ej802&fromjk=41a8cddcc5a80de1', 'https://de.indeed.com/cmp/Likeminded-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l93jj3v7801&fromjk=2861be7ef9dd894a', 'https://de.indeed.com/cmp/Tts-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6la53ikrh801&fromjk=c662129170711dba', 'https://de.indeed.com/cmp/Unzer?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lpmek7qa802&fromjk=f70c0e03a8bfa532', 'https://de.indeed.com/cmp/Johnson-Controls?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lqotl237802&fromjk=4fe8ab8f7185c97c', 'https://de.indeed.com/cmp/Dream-Broker-Oy?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lrf4je0n800&fromjk=d7d4136101cd0fce', 'https://de.indeed.com/cmp/Precise-Hotels-&-Resorts-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ls56ki8k802&fromjk=9f43f92aa33b57cd', 'https://de.indeed.com/cmp/Krongaard-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lsqe2m5n000&fromjk=54e865d43a169ce2', 'https://de.indeed.com/cmp/Vinci?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lu3fk7rk802&fromjk=21df39ebdc36181b', 'https://de.indeed.com/cmp/Powercloud-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lv55ikd9802&fromjk=896be62c6754a5b7', 'https://de.indeed.com/cmp/Lieferando?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lvqnk7qa800&fromjk=2f92467356626881', 'https://de.indeed.com/cmp/Easypark-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n027k7bn802&fromjk=d0267431f6b2811b', "https://de.indeed.com/cmp/Marc-O'polo?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n13vi3rg800&fromjk=85c6bfc5f1bc6731", 'https://de.indeed.com/cmp/Mediamarktsaturn?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n1q7lhed802&fromjk=279cda594803afaf', 'https://de.indeed.com/cmp/E--vendo-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n2h3k5og802&fromjk=e7c274e6f22afd19', 'https://de.indeed.com/cmp/Too-Good-to-Go?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n377lhdn800&fromjk=e22657761c6117c1', 'https://de.indeed.com/cmp/Codary?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n49fjjj7802&fromjk=e3f800e120c62399', 'https://de.indeed.com/cmp/Youngcapital?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n4tllhdn802&fromjk=4df7dbf10035ae1b', 'https://de.indeed.com/cmp/Vialytics?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n609ip9j800&fromjk=aab9e83cc1d680cd', 'https://de.indeed.com/cmp/Quadriga-Media-Berlin-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n714k7ej800&fromjk=4d620a04147eb20b', 'https://de.indeed.com/cmp/Sanofi?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n7nqk7qa802&fromjk=456e0fe674084f28', 'https://de.indeed.com/cmp/Homburg-&-Partner?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n8d5lhej800&fromjk=fd87426e320e2a3b', 'https://de.indeed.com/cmp/Inmediasp?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n939jjiu804&fromjk=b0779e787e8ec359', 'https://de.indeed.com/cmp/Nextcoder-Softwareentwicklungs-Ug?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6na43lhdn802&fromjk=02291b4c35c12bf0', 'https://de.indeed.com/cmp/Berger?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6nao3k7fs802&fromjk=eeea07a54876f9eb', 'https://de.indeed.com/cmp/Anschutz-Entertainment-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6nbpilhdk800&fromjk=d316a4fce5584139', 'https://de.indeed.com/cmp/Inmediasp?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ocaij3ut802&fromjk=b0779e787e8ec359', "https://de.indeed.com/cmp/Marc-O'polo?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6odcbjqvd800&fromjk=85c6bfc5f1bc6731", 'https://de.indeed.com/cmp/Lieferando?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oe4gjkv6802&fromjk=2f92467356626881', 'https://de.indeed.com/cmp/Hewlett-Packard-Enterprise-Hpe-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oer1ki8k800&fromjk=848a90d1ab19907b', 'https://de.indeed.com/cmp/Anschutz-Entertainment-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ofg0l22k800&fromjk=d316a4fce5584139', 'https://de.indeed.com/cmp/Eat-Happy-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6og6kje1l800&fromjk=41ac10034fc16733', 'https://de.indeed.com/cmp/Powercloud-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oh6okkfn800&fromjk=896be62c6754a5b7', 'https://de.indeed.com/cmp/Precise-Hotels-&-Resorts-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ohrtk7ts800&fromjk=9f43f92aa33b57cd', 'https://de.indeed.com/cmp/Fanpage-Karma?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oifajgap802&fromjk=3b4e9ec705c22ba7', 'https://de.indeed.com/cmp/Berger?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oj3jlhdg802&fromjk=eeea07a54876f9eb', 'https://de.indeed.com/cmp/Ivu-Traffic-Technologies-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ojp3ip9j802&fromjk=7c99bdec2fa15359', 'https://de.indeed.com/cmp/Capmo-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6okf5k7bn804&fromjk=97b2c83e899ad791', 'https://de.indeed.com/cmp/Http-Www.trendence.com-Karriere-Stellenangebote.html?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ol52jjgs800&fromjk=f88aa90f55260d15', 'https://de.indeed.com/cmp/Quadriga-Media-Berlin-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6om6ok7ej800&fromjk=4d620a04147eb20b', 'https://de.indeed.com/cmp/U--blox?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6on9glhdk802&fromjk=f0df3e68d6a93836', 'https://de.indeed.com/cmp/Scout24-Se-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6pqldikd9802&fromjk=d3327c7ee79328e2', 'https://de.indeed.com/cmp/Primal-State?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6prmtkkfc804&fromjk=6ad12bdfd5d8e9fb', 'https://de.indeed.com/cmp/Adsquare-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6psppk7d4800&fromjk=51f958aab5f7e873', 'https://de.indeed.com/cmp/Berlin-Cuisine-Metzger-&-Jensen-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ptsdlhdn800&fromjk=a5ce09402fddc001', 'https://de.indeed.com/cmp/Hewlett-Packard-Enterprise-Hpe-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6puutlhdd801&fromjk=848a90d1ab19907b', 'https://de.indeed.com/cmp/Herm%C3%A8s-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q017je36800&fromjk=63df9a9e254f26f0', 'https://de.indeed.com/cmp/Vattenfall?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q136j3v7802&fromjk=2d1da6110893f134', 'https://de.indeed.com/cmp/Online-Birds-Hotel-Marketing-Solutions?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q255je1l800&fromjk=3daaa833ecd47e51', 'https://de.indeed.com/cmp/Accenture?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q36skkfc800&fromjk=01fbc74f6bce501f', 'https://de.indeed.com/cmp/Nia-Health-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q499jjgs800&fromjk=2e2e962ef4cf606e', 'https://de.indeed.com/cmp/IBM-Ix-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q5b0jg9b800&fromjk=9994c25c7c874823', 'https://de.indeed.com/cmp/Unzer?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q6d5k7ts803&fromjk=81d7138283eda9bf', 'https://de.indeed.com/cmp/Deloitte?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q7f82bc4003&fromjk=75d3a0743bcbd1ae', 'https://de.indeed.com/cmp/Giga.green?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q8hdkojo802&fromjk=aa5ca76412181b7f', 'https://de.indeed.com/cmp/Saatchi-&-Saatchi?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q9jqk7sn802&fromjk=db07fe2a39c17491', 'https://de.indeed.com/cmp/Dataguard-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6rjr8lhdd802&fromjk=37066ac8ee53e985', 'https://de.indeed.com/cmp/Diconium-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6rks5jjjs802&fromjk=f9afb40cd075124e', 'https://de.indeed.com/cmp/Smarketer-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6rlj7k7sn802&fromjk=15f6d88298624e90', 'https://de.indeed.com/cmp/Berlin-Brands-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s567l22k802&fromjk=50f4744cd5754274', 'https://de.indeed.com/cmp/Care-With-Care?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s66rl22o807&fromjk=be82878656ef7cec', 'https://de.indeed.com/cmp/Smartclip-Europe-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s6tplheg805&fromjk=00ef1c15bf5b5939', 'https://de.indeed.com/cmp/Bonial?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s7tdki8k800&fromjk=24d158ec1fd24ec9', 'https://de.indeed.com/cmp/Re-Cap?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s8km2m5n002&fromjk=514faab177900060', 'https://de.indeed.com/cmp/Schindler-59cfe7ee?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s99ajqvi800&fromjk=1619b0e0ab6a2b5b', 'https://de.indeed.com/cmp/Sonnen?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s9uc2fbr002&fromjk=be1fd61011ef7e08', 'https://de.indeed.com/cmp/Angel-Last-Mile-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6saltk5og803&fromjk=afae896c15b4b92b', 'https://de.indeed.com/cmp/Capgemini?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6sbe1j3v7802&fromjk=a9e76fa7d7d568f9', 'https://de.indeed.com/cmp/Hrlab-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6sc1uip9j800&fromjk=ee2ed6b1d8a3a033', 'https://de.indeed.com/cmp/Sabienzia-Technologies-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6scnol233802&fromjk=e901abc02f6d3bad', 'https://de.indeed.com/cmp/Adsquare-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tga1ir2n800&fromjk=0946d72d5f01ee6b', 'https://de.indeed.com/cmp/Alstom?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6thj9k7bn802&fromjk=7c59e0e5cc24defc', 'https://de.indeed.com/cmp/Vodafone?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tiluikcj800&fromjk=c2d9b4fe54366208', 'https://de.indeed.com/cmp/Cenit?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tjo7k7bn802&fromjk=6505e394e293cc72', 'https://de.indeed.com/cmp/The-Social-Chain-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tkp7k7fs802&fromjk=6e94fb9ac295feba', 'https://de.indeed.com/cmp/Dataguard-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tlsvjjik804&fromjk=a3e7e16e164c6094', 'https://de.indeed.com/cmp/Spendesk?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tn08k6r3800&fromjk=0715219702bf2ad2', 'https://de.indeed.com/cmp/Humanoo-Etherapists-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6to1jjjiu802&fromjk=e4b92fad1ac40cd1', 'https://de.indeed.com/cmp/U--blox?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tp3ik7fs801&fromjk=f0df3e68d6a93836', 'https://de.indeed.com/cmp/Deutsche-Bank?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tqabikcj803&fromjk=5748085de433fa25', 'https://de.indeed.com/cmp/Live-Nation?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6trrt2m5n005&fromjk=3cd1ed52272f1b5c', 'https://de.indeed.com/cmp/Krongaard-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tt7ij326802&fromjk=3fccdb4eace9bf64', 'https://de.indeed.com/cmp/Michael-Page?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tu9jir3o800&fromjk=22f72c1aaf7608ea', 'https://de.indeed.com/cmp/Yoc-France?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tvafk7cg801&fromjk=98c98956530df48c', 'https://de.indeed.com/cmp/Smartbroker?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6u010ir2n802&fromjk=12eb3afd69bcb4b1', 'https://de.indeed.com/cmp/Deutsche-Bank?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v21dl22p800&fromjk=5748085de433fa25', 'https://de.indeed.com/cmp/Humanoo-Etherapists-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v33e2fbv000&fromjk=e4b92fad1ac40cd1', 'https://de.indeed.com/cmp/Avart-Personal-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v3oekojo802&fromjk=914685aa3e3d3f81', 'https://de.indeed.com/cmp/Capgemini?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v4dbl237802&fromjk=371a49fb77b100cb', 'https://de.indeed.com/cmp/Smartbroker?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v5f9kkd7802&fromjk=12eb3afd69bcb4b1', 'https://de.indeed.com/cmp/Michael-Page?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v672ikcj802&fromjk=22f72c1aaf7608ea', 'https://de.indeed.com/cmp/Bilendi?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v6tvjjiu802&fromjk=86393400f2b96819', 'https://de.indeed.com/cmp/Kranus-Health-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v800lhdh802&fromjk=46c69764204b3c61', 'https://de.indeed.com/cmp/Humanoo?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v8mki46f803&fromjk=7699949131a89839', 'https://de.indeed.com/cmp/Steinbeis-School-of-International-Business-and-Entrepreneurship-(sibe)-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v9brl22k802&fromjk=5d0b0708bbce7955', 'https://de.indeed.com/cmp/Youngcapital?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vadjlhej802&fromjk=6cb7dfc77311fc22', 'https://de.indeed.com/cmp/Hewlett-Packard-Enterprise-Hpe-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vb2jj3ut801&fromjk=609757da0649b591', 'https://de.indeed.com/cmp/Headmatch-Gmbh-&-Co.kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vbo4k7rk802&fromjk=e6a4a905c6e092d8', 'https://de.indeed.com/cmp/Krongaard-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vck5jjiv800&fromjk=3fccdb4eace9bf64', 'https://de.indeed.com/cmp/Dps-Business-Solutions-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vdg02m5n002&fromjk=7ec5e1d8620690ae', 'https://de.indeed.com/cmp/Gkm-Recruitment-Services?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70eeejg9n800&fromjk=648749532e95b692', 'https://de.indeed.com/cmp/Bilendi?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70fmmikrh801&fromjk=86393400f2b96819', 'https://de.indeed.com/cmp/Just-Spices-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70gk0ikcj807&fromjk=85e469b5ebcb7c4c', 'https://de.indeed.com/cmp/Noris-Network?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70hmh2bc4003&fromjk=c05495fbcebba4e4', 'https://de.indeed.com/cmp/Headmatch-Gmbh-&-Co.kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70iovl22p801&fromjk=e6a4a905c6e092d8', 'https://de.indeed.com/cmp/Avart-Personal-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70jr3l21j802&fromjk=914685aa3e3d3f81', 'https://de.indeed.com/cmp/Kranus-Health-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70ktuj3ut802&fromjk=46c69764204b3c61', 'https://de.indeed.com/cmp/Comsysto-Reply-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70qt3k5ro805&fromjk=63bcf919b26239a3', 'https://de.indeed.com/cmp/Bearingpoint?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70rjqje36802&fromjk=095c85169a38d8f9', 'https://de.indeed.com/cmp/Hoppecke-Batterien?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70slvlheg802&fromjk=ef8d22ff0e30d255', 'https://de.indeed.com/cmp/Steinbeis-School-of-International-Business-and-Entrepreneurship-(sibe)-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70to32fbv002&fromjk=5d0b0708bbce7955', 'https://de.indeed.com/cmp/Dps-Business-Solutions-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70upvjgap802&fromjk=7ec5e1d8620690ae', 'https://de.indeed.com/cmp/Michael-Page?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70vsal210802&fromjk=5de951a85fcd8738', 'https://de.indeed.com/cmp/Robert-Half?campaignid=mobvjcmp&from=mobviewjob&tk=1gou710ujl22k800&fromjk=8d57969b3839fb6b', 'https://de.indeed.com/cmp/Hays?campaignid=mobvjcmp&from=mobviewjob&tk=1gou71205jjiu800&fromjk=e4dc737964d8b1c9', 'https://de.indeed.com/cmp/Noris-Network?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7226qir3o800&fromjk=1b324c8ac18fc90e', 'https://de.indeed.com/cmp/Zalando?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7236tki8k803&fromjk=085baa86ea598d78', 'https://de.indeed.com/cmp/Deutsche-Bank?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7249ql22o802&fromjk=24598c474fdc87a0', 'https://de.indeed.com/cmp/Solique-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7251rikd9802&fromjk=e5d9af519388ea3b', 'https://de.indeed.com/cmp/Tesvolt-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou725oa2fbv000&fromjk=752e32e80fbf8f02', 'https://de.indeed.com/cmp/Floris-Catering-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou726gbikdg802&fromjk=88e644be36905113', 'https://de.indeed.com/cmp/Michael-Page?campaignid=mobvjcmp&from=mobviewjob&tk=1gou727gqjjjs802&fromjk=247325277bdef0d5', 'https://de.indeed.com/cmp/Capgemini?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72882ikdg803&fromjk=371a49fb77b100cb', 'https://de.indeed.com/cmp/Broadgate-Search?campaignid=mobvjcmp&from=mobviewjob&tk=1gou728u6l22p802&fromjk=48c95cae49a33de5', 'https://de.indeed.com/cmp/Connected-Gs-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou729hjjkvo803&fromjk=f8178e2ab395f8b1', 'https://de.indeed.com/cmp/Kuehne+nagel?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72a62k7qa802&fromjk=15060a73d20ce616', 'https://de.indeed.com/cmp/Spendesk?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72b8lk5ro800&fromjk=eae533cf0cccd9f5', 'https://de.indeed.com/cmp/Apcoa-Parking-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72bv7jqvd802&fromjk=381396175176161a', 'https://de.indeed.com/cmp/Aemtec-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72ckdl210802&fromjk=d668c4faa81606e2', 'https://de.indeed.com/cmp/Alogis-Ag-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72daukkd7802&fromjk=f0baff0610131fe2', 'https://de.indeed.com/cmp/Fischerappelt?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73errjg9n802&fromjk=a0808e7270c93486', 'https://de.indeed.com/cmp/Hoppecke-Batterien?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73fr2j3v7802&fromjk=ab829ff6a51ef812', 'https://de.indeed.com/cmp/Ib-Vogt-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73gi4kkfn802&fromjk=2fd275f557831d51', 'https://de.indeed.com/cmp/Deutsche-Bank?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73h7tlhdh802&fromjk=2690f5c402dc43a2', 'https://de.indeed.com/cmp/Studydrive-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73httjqvd801&fromjk=b14d5c0ba161ab7e', 'https://de.indeed.com/cmp/Nobel-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73iiuikrh800&fromjk=af3b3a0bac211aec', 'https://de.indeed.com/cmp/Oliver-Wyman-Group-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7420pk7bn802&fromjk=e9a47934c2050555', 'https://de.indeed.com/cmp/Hubject-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7433hk7cg800&fromjk=41cb640230fe52bd', 'https://de.indeed.com/cmp/Usu-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou743o3k7ej802&fromjk=6b23fceb8ef2859c', 'https://de.indeed.com/cmp/Software-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou744qeje36802&fromjk=ce7a9d00b5e453cb', 'https://de.indeed.com/cmp/Nobel-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gou745fgjjiv802&fromjk=5ac57abcdbe2ba13', 'https://de.indeed.com/cmp/Lingoda-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7465nkkfc803&fromjk=31ac7e7d0960a35b', 'https://de.indeed.com/cmp/Ey?campaignid=mobvjcmp&from=mobviewjob&tk=1gou746t9jksu800&fromjk=2d1b5a0d8bfbb466', 'https://de.indeed.com/cmp/Strategy&?campaignid=mobvjcmp&from=mobviewjob&tk=1gou747jjlhdh802&fromjk=e35ae750d842c7df', 'https://de.indeed.com/cmp/Usu-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75hnjjjj7802&fromjk=6b23fceb8ef2859c', 'https://de.indeed.com/cmp/Studydrive-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75imul233800&fromjk=b14d5c0ba161ab7e', 'https://de.indeed.com/cmp/Lingoda-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75joml21j800&fromjk=31ac7e7d0960a35b', 'https://de.indeed.com/cmp/Software-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75krfiqv3800&fromjk=ce7a9d00b5e453cb', 'https://de.indeed.com/cmp/Kuehne+nagel?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75lgv2m5n002&fromjk=15060a73d20ce616', 'https://de.indeed.com/cmp/Spendesk?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75mivl21j800&fromjk=a6426709248c7dfe', 'https://de.indeed.com/cmp/Thermo-Fisher-Scientific?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75n9fk7ts804&fromjk=b85e4519093e889d', 'https://de.indeed.com/cmp/Spendesk?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75o0rir2n802&fromjk=344c94ba993dfc79', 'https://de.indeed.com/cmp/Ib-Vogt-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75on1lhed800&fromjk=2fd275f557831d51', 'https://de.indeed.com/cmp/Alstom?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75pffje1l800&fromjk=dccd8a1400aae357', 'https://de.indeed.com/cmp/Avantgarde-Experts?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75qg4irp1800&fromjk=581cc252f3c405f8', 'https://de.indeed.com/cmp/Orange-Quarter?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75r5fk5og802&fromjk=d3a2efd4549cea35', 'https://de.indeed.com/cmp/Realworld-One-Gmbh-&-Co.-Kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75rqok7d4803&fromjk=60042adbeda42da5', 'https://de.indeed.com/cmp/Frg-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75sf5k7ts802&fromjk=c734f98e71b6dc59', 'https://de.indeed.com/cmp/Veeva-Systems?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75t56lheg803&fromjk=8785c08cfd511493', 'https://de.indeed.com/cmp/Usu-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou76v6fi46f800&fromjk=16bd223191897413', 'https://de.indeed.com/cmp/Avantgarde-Experts?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7707s2e11002&fromjk=de3ed4dca6c3473a', 'https://de.indeed.com/cmp/Deutsche-Telekom?campaignid=mobvjcmp&from=mobviewjob&tk=1gou770unj3vv802&fromjk=e2849bddec87183f', 'https://de.indeed.com/cmp/Workstreams.ai-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou771mgkkfd800&fromjk=8615a4952d2ebb65', 'https://de.indeed.com/cmp/Yara-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou772o5i46f803&fromjk=eaeedfd9a3eff58b', 'https://de.indeed.com/cmp/Flaconi-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou773e6jjiu802&fromjk=7d34dcbd390c4335', 'https://de.indeed.com/cmp/Ml6?campaignid=mobvjcmp&from=mobviewjob&tk=1gou774h2jg9n800&fromjk=fc9f30ea8c5a197a', 'https://de.indeed.com/cmp/Vanilla-Steel-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou775imk7qa800&fromjk=1be83b54ce988bd6', 'https://de.indeed.com/cmp/Br%C3%B6er-&-Partner-Gmbh-&-Co-Kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7768hje1l801&fromjk=36d392cb282a5926', 'https://de.indeed.com/cmp/Bunch?campaignid=mobvjcmp&from=mobviewjob&tk=1gou77737ikrh800&fromjk=caf1e55ecbcdadda', 'https://de.indeed.com/cmp/Trinckle-3d-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou777vel233801&fromjk=20ff3807007d5057', 'https://de.indeed.com/cmp/Leanlancer-Ug?campaignid=mobvjcmp&from=mobviewjob&tk=1gou778nli46f802&fromjk=737a3c699338a650', 'https://de.indeed.com/cmp/Leanlancer-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou779qvjg9n800&fromjk=6e6f8019d8d34a7c', 'https://de.indeed.com/cmp/Clariness?campaignid=mobvjcmp&from=mobviewjob&tk=1gou77atglhdd800&fromjk=c489e6cf51e209d7', 'https://de.indeed.com/cmp/Mindbody?campaignid=mobvjcmp&from=mobviewjob&tk=1gou77bihhdhg802&fromjk=971f5370df68a00f', 'https://de.indeed.com/cmp/Masterplan.com-4?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78hbdjg90802&fromjk=33fb2fa9cb4db6db', 'https://de.indeed.com/cmp/Picture-Tree-International-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78id8ikd9803&fromjk=7e8045daf4f3b4df', 'https://de.indeed.com/cmp/Enpal-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78ja2jg9n802&fromjk=74615c24ba07dd6f', 'https://de.indeed.com/cmp/Fairsenden-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78k7ukkfn802&fromjk=13669fae46359423', 'https://de.indeed.com/cmp/Centrovital-Berlin?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78laqje1l80h&fromjk=75c37f2f66027ec0', 'https://de.indeed.com/cmp/Dedo-Media-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78mcklhej802&fromjk=7bea898030156603', 'https://de.indeed.com/cmp/Briink?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78n2ik7dg802&fromjk=518b11ae627b2710', 'https://de.indeed.com/cmp/First-Berlin-Equity-Research-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78nnqlhdh802&fromjk=8bc298f3503e47ce', 'https://de.indeed.com/cmp/Merantix?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78odejqun801&fromjk=8bc140309ac56efb', 'https://de.indeed.com/cmp/Delphai?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78p36jqvd802&fromjk=dcf4c5badc1e6163', 'https://de.indeed.com/cmp/Contentbird-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78pp2lhdg800&fromjk=6f311172db2ca662', 'https://de.indeed.com/cmp/Easylivestream?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78qeoje0n801&fromjk=d5071b1589294ef2', 'https://de.indeed.com/cmp/Bvdw-Services-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78r5rk7fs800&fromjk=e0364340a38c6258', 'https://de.indeed.com/cmp/Cytosorbents-Europe-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78s7flhdk802&fromjk=75ecae871b101e8b', 'https://de.indeed.com/cmp/Oceansapart?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78ta4kkfd800&fromjk=9a3f148ea2272336', 'https://de.indeed.com/cmp/K&K-Handelsgesellschaft-Mbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a3dj2fbr000&fromjk=d8c368565350162e', 'https://de.indeed.com/cmp/Leanlancer-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a4etjkvj802&fromjk=6e6f8019d8d34a7c', 'https://de.indeed.com/cmp/Circulee-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a547k7t1801&fromjk=8020ce1d27ab81cc', 'https://de.indeed.com/cmp/Briink?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a5q4jjgs800&fromjk=518b11ae627b2710', 'https://de.indeed.com/cmp/Equeo-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a6rkl22p802&fromjk=c1e9440d1854d634', 'https://de.indeed.com/cmp/Clariness?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a7htl22k802&fromjk=c489e6cf51e209d7', 'https://de.indeed.com/cmp/Heyrecruit?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a8k8kkd7802&fromjk=65f8dc6dcbaaa512', 'https://de.indeed.com/cmp/Weroad-4?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a9all22o802&fromjk=2e551c5f448515c0', 'https://de.indeed.com/cmp/Circulee?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7aa04hdhg802&fromjk=79fce93d3eb788c9', 'https://de.indeed.com/cmp/Escapio-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7aaoqip9j802&fromjk=4f37ce67b3761108', 'https://de.indeed.com/cmp/Merantix?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7abp6kojo800&fromjk=8bc140309ac56efb', 'https://de.indeed.com/cmp/The-Bike-Club?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7acr1i3rg803&fromjk=97578766a74f4a37', 'https://de.indeed.com/cmp/Verlag-Der-Tagesspiegel-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7adg9k2mg802&fromjk=325d68b564b1e738', 'https://de.indeed.com/cmp/Easypark-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7ae4qjgap800&fromjk=be8b7030f15b6648', 'https://de.indeed.com/cmp/Subtel-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7aeq8k7bn802&fromjk=a549dd2ad57c9881', 'https://de.indeed.com/cmp/Rydes?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bi6ul21j802&fromjk=e8c7d8eb6c290a74', 'https://de.indeed.com/cmp/Everyone-Energy?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bj9ck7ts801&fromjk=4d6614d8e4dcc872', 'https://de.indeed.com/cmp/Craft-Circus-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bkcmjjik802&fromjk=4929dc4287901f83', 'https://de.indeed.com/cmp/In-Pact-Media-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bli4j3vv801&fromjk=1731105eeb0962d3', 'https://de.indeed.com/cmp/Incred-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bmnnjjiu803&fromjk=25fdd1c44654ff0c', 'https://de.indeed.com/cmp/Cloudinary?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bnnijksu802&fromjk=c695b893cef4b284', 'https://de.indeed.com/cmp/Also-Energy?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7boqgkkfc802&fromjk=8c287bce4377d212', 'https://de.indeed.com/cmp/Adsquare-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bq4ck7cg801&fromjk=9e109c0d0d1fc4eb', 'https://de.indeed.com/cmp/Entyre-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7br1piqv3802&fromjk=77de329afdb9e9d3', 'https://de.indeed.com/cmp/Sendinblue?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bs63jqvd802&fromjk=953cea5bb44670dc', 'https://de.indeed.com/cmp/Vaayu-Tech-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bta7hdhg800&fromjk=61ef53d12505b993', 'https://de.indeed.com/cmp/Eqolot?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7buarhdhg802&fromjk=f18c867167df71e1', 'https://de.indeed.com/cmp/Singularitysales-Beteiligungsges.-Mbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bvf8jkvo802&fromjk=02704f1d0fd6615d', 'https://de.indeed.com/cmp/Primal-State-Performance-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7c0h9ikrh802&fromjk=5dbdb877e58ccc60', 'https://de.indeed.com/cmp/Hartmann-Tresore?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7c1jcjjjs800&fromjk=706f21512a350405', 'https://de.indeed.com/cmp/Madvertise-2?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7d74ljg9n800&fromjk=bf736bca49cd89cd', 'https://de.indeed.com/cmp/Enpal-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7d8fm2fbv003&fromjk=74615c24ba07dd6f', 'https://de.indeed.com/cmp/Ebuero-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7d9jrjqvi800&fromjk=33b67b24279136ff', 'https://de.indeed.com/cmp/Matthias-Pianezezr?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7dammjkv6800&fromjk=2f4d3ed8541424db', 'https://de.indeed.com/cmp/First-Berlin-Equity-Research-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7dbpcjg9b800&fromjk=ec7445c02260be55', 'https://de.indeed.com/cmp/Eclipse-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7dcrolhdn802&fromjk=9e49b1bcd02940eb', 'https://de.indeed.com/cmp/Sellerx-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7ddu3lhej802&fromjk=de58e2b7a4f58ceb', 'https://de.indeed.com/cmp/Easylivestream?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7dtrnip9j802&fromjk=d5071b1589294ef2', 'https://de.indeed.com/cmp/Nyn-Consulting?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7duvfl237801&fromjk=7c22957bdbdce7a4', 'https://de.indeed.com/cmp/Magaloop-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e01el21j802&fromjk=e8e7981f2c5f2b67', 'https://de.indeed.com/cmp/Dertaler-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e14bjqvi802&fromjk=a2cf468ec571ef25', 'https://de.indeed.com/cmp/Keyence?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e275l21j801&fromjk=5e88e985e7c160c4', 'https://de.indeed.com/cmp/Egroup?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e39tjqvd800&fromjk=96a05ce9675c211c', 'https://de.indeed.com/cmp/Codept-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e4c3lhei800&fromjk=8d7a43a24d6f9f0f', 'https://de.indeed.com/cmp/Cloudinary?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fhobikre802&fromjk=c695b893cef4b284', 'https://de.indeed.com/cmp/Matthias-Pianezezr?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fipihdi6802&fromjk=2f4d3ed8541424db', 'https://de.indeed.com/cmp/Apoll-On-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fjfo2e11002&fromjk=5a73c29bd37b2297', 'https://de.indeed.com/cmp/Audience-Serv-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fkilk7cg800&fromjk=abea09427d2ca136', 'https://de.indeed.com/cmp/The-Recruitment-2.0-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fl84ikd9802&fromjk=18fe84a8212babb5', 'https://de.indeed.com/cmp/Berliner-Brandstifter?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7flurikdg802&fromjk=d868ffd821a56d07', 'https://de.indeed.com/cmp/United-Internet-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fmkvk7rk802&fromjk=38b49b4f812ec32a', 'https://de.indeed.com/cmp/Estrategy-Consulting-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fnbql210802&fromjk=30cb08585c128ac8', 'https://de.indeed.com/cmp/Magaloop-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fo2el22k803&fromjk=e8e7981f2c5f2b67', 'https://de.indeed.com/cmp/In-Pact-Media-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fp4kk7ej800&fromjk=1731105eeb0962d3', 'https://de.indeed.com/cmp/Sense-Electra-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fq6njkv6802&fromjk=b734bb3347c04a3a', 'https://de.indeed.com/cmp/Flexperto-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fqtcirp1801&fromjk=ec91669cc4841e0b', 'https://de.indeed.com/cmp/Primal-State-Performance-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7gpn62fbr002&fromjk=5dbdb877e58ccc60', 'https://de.indeed.com/cmp/Bewerbungscode-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7hv80jg90800&fromjk=ce84e2ab99147fcd', 'https://de.indeed.com/cmp/Sense-Electra-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i09ljjik800&fromjk=b734bb3347c04a3a', 'https://de.indeed.com/cmp/Sendinblue?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i0v8k7bn802&fromjk=8007da5f0107a98f', 'https://de.indeed.com/cmp/Lions-&-Gazelles-International-Recruitment-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i1kuir2n804&fromjk=acff33b4255d5c67', 'https://de.indeed.com/cmp/Workbees-Gmbh-(part-of-Netgo-Group)?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i298jkv6800&fromjk=95b26f252138d5c1', 'https://de.indeed.com/cmp/Valsight-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i3bkl21j802&fromjk=6502fa20aa20cfbd', 'https://de.indeed.com/cmp/Ticketmaster?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i4ffjjjs802&fromjk=bb02c87334de177b', 'https://de.indeed.com/cmp/Wunderpen-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i5h6ikre802&fromjk=1171319b530ee5fb', 'https://de.indeed.com/cmp/Valsight-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i6jmlhdn802&fromjk=ca3bf3b411c9ea14', 'https://de.indeed.com/cmp/Eurofins?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i7acj3ut800&fromjk=0709a6d9225fdd7e', 'https://de.indeed.com/cmp/21.finance?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i826lhdh802&fromjk=fbbefefe1cf31079', 'https://de.indeed.com/cmp/Weroad?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i98pjg9b800&fromjk=153ae7c7a5bd1342', 'https://de.indeed.com/cmp/Ds-Event-Lobby-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7ia58je1l800&fromjk=91f1f3b7500db573', 'https://de.indeed.com/cmp/Nico-Europe-Gmbh-4?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7iplaje36802&fromjk=d111c1c4ab3a2785', 'https://de.indeed.com/cmp/Workbees-Gmbh-(part-of-Netgo-Group)?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7jtnbi46f802&fromjk=95b26f252138d5c1', 'https://de.indeed.com/cmp/Ds-Event-Lobby-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7julrikcj800&fromjk=91f1f3b7500db573', 'https://de.indeed.com/cmp/Bewerbungscode-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7jvc8lhdn802&fromjk=ce84e2ab99147fcd', 'https://de.indeed.com/cmp/Twinwin?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k01llhdh802&fromjk=5f31e4fbb4340b4e', 'https://de.indeed.com/cmp/Bauer-Gruppe-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k0lvlhed800&fromjk=4ab2b121d6551fa5', 'https://de.indeed.com/cmp/Meetsales?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k1dpjgap802&fromjk=b1796f142df77949', 'https://de.indeed.com/cmp/Wunderpen-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k222k7cg803&fromjk=1171319b530ee5fb', 'https://de.indeed.com/cmp/Product-People?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k2n8k7ts800&fromjk=dc46c00a42a3907e', 'https://de.indeed.com/cmp/Verve-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k3crk6r3800&fromjk=59c8a19c12c6609c', 'https://de.indeed.com/cmp/Nico-Europe-Gmbh-4?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k426k6r3803&fromjk=d111c1c4ab3a2785', 'https://de.indeed.com/cmp/G2k-Group-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k4nvikre801&fromjk=fdb62f6de6d29d92', 'https://de.indeed.com/cmp/Matthias-Pianezezr?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k5ghl21j802&fromjk=cd1bd8efde516f42', 'https://de.indeed.com/cmp/Multitude?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k67tje0p802&fromjk=16ae832ec933f1f3', 'https://de.indeed.com/cmp/Sellerx-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7km29k7ej800&fromjk=e66fd59a12be6ca9', 'https://de.indeed.com/cmp/Audience-Serv-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7lsrjlhdd800&fromjk=abea09427d2ca136', 'https://de.indeed.com/cmp/Twinwin?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7lttcjqun803&fromjk=5f31e4fbb4340b4e', 'https://de.indeed.com/cmp/Talent--valet?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7luiskkfc800&fromjk=f8f5bf4b8e3d9252', 'https://de.indeed.com/cmp/Sellerx-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7mej1jjj7802&fromjk=e66fd59a12be6ca9', 'https://de.indeed.com/cmp/Pixtunes-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7muinir3o801&fromjk=c40063d4d90c0f71', 'https://de.indeed.com/cmp/Meetsales?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7mvltlheg802&fromjk=b1796f142df77949', 'https://de.indeed.com/cmp/Blu-Die-Agentur-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n0ngjjj7802&fromjk=0da7d44f8093fd0a', 'https://de.indeed.com/cmp/Therme-Art-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n1e8lhei801&fromjk=d008f2c20e3fa9a6', 'https://de.indeed.com/cmp/Ka-Resources?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n27jhdi6802&fromjk=821cd8312fde7b69', 'https://de.indeed.com/cmp/Verve-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n37ak7t1802&fromjk=59c8a19c12c6609c', 'https://de.indeed.com/cmp/International-People-Solutions?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n3u7kojo802&fromjk=4dbebdc94480ef71', 'https://de.indeed.com/cmp/Usu-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7njs5k6r3801&fromjk=36546e92994cda67', 'https://de.indeed.com/cmp/International-People-Solutions?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7p79kk7ej800&fromjk=4dbebdc94480ef71', 'https://de.indeed.com/cmp/Usu-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7p8cjjksu802&fromjk=2a3068fdacc4c138', 'https://de.indeed.com/cmp/Infoverity?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7p90mjkv6802&fromjk=78a88ea6a54ad36a', 'https://de.indeed.com/cmp/Ka-Resources?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7p9m0l210801&fromjk=cc688392582a650b', 'https://de.indeed.com/cmp/Usu-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7pabnj3ut800&fromjk=b4e39bd53d849b69', 'https://de.indeed.com/cmp/Ka-Resources?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7pb1il22p802&fromjk=82258bec8c2d83d9', 'https://de.indeed.com/cmp/Ka-Resources?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7pc3pl233801&fromjk=3b4472da888797c9', 'https://de.indeed.com/cmp/Black-Pen-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7pd5r2fbr002&fromjk=4e80b09daa8fba4d']



    # proxy = choice(proxies)
    # driver = webdriver_setup(proxy)
    # company_urls = get_company_url(driver, search_result_url)
    # print(company_urls)
    #
    # for url in company_urls:
    #     proxy = choice(proxies)
    #     print(proxy)
    #     driver = webdriver_setup(proxy)
    #     result = get_data(driver, url, proxy)
    #     print(f'Company name: {result.name}')
    #     print(f'Company website: {result.website}')
    #     print(f'Company linkedin: {result.linkedin}')
    #     print('====================================================================')

def parser(html):
    print('Parse HTML...')
    tree = HTMLParser(html)

    # Get Company name
    Company.name = tree.css_first('div[itemprop="name"]').text

    # Get Company URL
    try:
        parent = tree.css_first('ul.css-1jgykzt.e37uo190')
        Company.website = parent.css_first("a[text()*='ebs']").attrs['href']
    except NoSuchElementException:
        Company.website = None

    # Get Company linkedin
    try:
        parent = tree.css_first('ul.css-1jgykzt.e37uo190')
        Company.linkedin = parent.parent.css_first("a[text()*='inked']").attrs['href']
    except NoSuchElementException:
        Company.linkedin = get_linkedin(Company.name, proxy)

    return Company

# async def fetch(url, ua, cookies):
#     async with httpx.AsyncClient(timeout=None) as client:
#         return await client.get(url)

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

    with httpx.Client(headers=header, cookies=cookies, proxies=formated_proxy) as client:
        response = client.get(url)
    print(response.text)

# async def mainAsyncio(company_urls):
def mainAsyncio(company_urls, proxies):
    url = 'https://de.indeed.com/'
    term = 'junior sales'
    location = 'Berlin'

    search_result_url, cookies, ua = job_result_url(proxies, url, term, location)
    print(search_result_url, cookies, ua)

    result = fetch(company_urls[0], ua=ua, cookies_list=cookies, proxies=proxies[5])
    print(result)


    # responses = await asyncio.gather(*map(fetch, company_urls))
    # htmls = [response.text for response in responses]
    # return htmls

if __name__ == '__main__':
    start = time.perf_counter()
    company_urls = [
        'https://de.indeed.com/cmp/Hotel-Mssngr?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jnhgjjiv802&fromjk=2626f305ad399745',
        'https://de.indeed.com/cmp/Sonnen?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6joj1jqvi802&fromjk=e846fde655293c2e',
        'https://de.indeed.com/cmp/Nh-8adc4d2a?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jpa32e11003&fromjk=cc7dd09f67a7720d',
        'https://de.indeed.com/cmp/Highcoordination-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jpupl22k801&fromjk=e4374dd769afabe7',
        'https://de.indeed.com/cmp/Instinct3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jqj5k5ro803&fromjk=dc8355820312c198',
        'https://de.indeed.com/cmp/Svarmony?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jr9rkkd7801&fromjk=c0f24575b0cdd119',
        'https://de.indeed.com/cmp/Varc-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jrv0k7sn805&fromjk=17fb64f24bbd28b3',
        'https://de.indeed.com/cmp/Trakken-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jskr2m5n000&fromjk=3c9e429cd64ad558',
        'https://de.indeed.com/cmp/Berry-Global,-Inc?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jtn4ir3o802&fromjk=2f307529e5e74403',
        'https://de.indeed.com/cmp/All-For-One-Group-Se?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6juc6ikd9800&fromjk=6fb8710cc3cb1be1',
        'https://de.indeed.com/cmp/Targomo?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jv0qj3vv800&fromjk=f7ff39626cd0f56f',
        'https://de.indeed.com/cmp/Kreuzwerker-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6jvlskkfn802&fromjk=e6b45259b1d839d6',
        'https://de.indeed.com/cmp/Coffee-Circle-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6k0ccjjgs802&fromjk=da42d794164550f8',
        'https://de.indeed.com/cmp/Pair-Finance-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6k11ojqun802&fromjk=7849b844150895fb',
        'https://de.indeed.com/cmp/Make-IT-Fix-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6k234jjgs802&fromjk=d7da040a0c4e08ad',
        'https://de.indeed.com/cmp/Park-&-Control-Pac-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l5kok7t1802&fromjk=e6571b36e8743b24',
        'https://de.indeed.com/cmp/Hrworks-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l6mbirp1802&fromjk=340238d4d02a7f0d',
        'https://de.indeed.com/cmp/Adevinta-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l7bijqvd802&fromjk=b69ad2d7b20d6203',
        'https://de.indeed.com/cmp/A.-Lange-&-S%C3%B6hne?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l80pk7ej802&fromjk=41a8cddcc5a80de1',
        'https://de.indeed.com/cmp/Likeminded-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6l93jj3v7801&fromjk=2861be7ef9dd894a',
        'https://de.indeed.com/cmp/Tts-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6la53ikrh801&fromjk=c662129170711dba',
        'https://de.indeed.com/cmp/Unzer?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lpmek7qa802&fromjk=f70c0e03a8bfa532',
        'https://de.indeed.com/cmp/Johnson-Controls?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lqotl237802&fromjk=4fe8ab8f7185c97c',
        'https://de.indeed.com/cmp/Dream-Broker-Oy?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lrf4je0n800&fromjk=d7d4136101cd0fce',
        'https://de.indeed.com/cmp/Precise-Hotels-&-Resorts-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ls56ki8k802&fromjk=9f43f92aa33b57cd',
        'https://de.indeed.com/cmp/Krongaard-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lsqe2m5n000&fromjk=54e865d43a169ce2',
        'https://de.indeed.com/cmp/Vinci?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lu3fk7rk802&fromjk=21df39ebdc36181b',
        'https://de.indeed.com/cmp/Powercloud-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lv55ikd9802&fromjk=896be62c6754a5b7',
        'https://de.indeed.com/cmp/Lieferando?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6lvqnk7qa800&fromjk=2f92467356626881',
        'https://de.indeed.com/cmp/Easypark-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n027k7bn802&fromjk=d0267431f6b2811b',
        "https://de.indeed.com/cmp/Marc-O'polo?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n13vi3rg800&fromjk=85c6bfc5f1bc6731",
        'https://de.indeed.com/cmp/Mediamarktsaturn?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n1q7lhed802&fromjk=279cda594803afaf',
        'https://de.indeed.com/cmp/E--vendo-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n2h3k5og802&fromjk=e7c274e6f22afd19',
        'https://de.indeed.com/cmp/Too-Good-to-Go?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n377lhdn800&fromjk=e22657761c6117c1',
        'https://de.indeed.com/cmp/Codary?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n49fjjj7802&fromjk=e3f800e120c62399',
        'https://de.indeed.com/cmp/Youngcapital?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n4tllhdn802&fromjk=4df7dbf10035ae1b',
        'https://de.indeed.com/cmp/Vialytics?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n609ip9j800&fromjk=aab9e83cc1d680cd',
        'https://de.indeed.com/cmp/Quadriga-Media-Berlin-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n714k7ej800&fromjk=4d620a04147eb20b',
        'https://de.indeed.com/cmp/Sanofi?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n7nqk7qa802&fromjk=456e0fe674084f28',
        'https://de.indeed.com/cmp/Homburg-&-Partner?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n8d5lhej800&fromjk=fd87426e320e2a3b',
        'https://de.indeed.com/cmp/Inmediasp?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6n939jjiu804&fromjk=b0779e787e8ec359',
        'https://de.indeed.com/cmp/Nextcoder-Softwareentwicklungs-Ug?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6na43lhdn802&fromjk=02291b4c35c12bf0',
        'https://de.indeed.com/cmp/Berger?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6nao3k7fs802&fromjk=eeea07a54876f9eb',
        'https://de.indeed.com/cmp/Anschutz-Entertainment-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6nbpilhdk800&fromjk=d316a4fce5584139',
        'https://de.indeed.com/cmp/Inmediasp?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ocaij3ut802&fromjk=b0779e787e8ec359',
        "https://de.indeed.com/cmp/Marc-O'polo?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6odcbjqvd800&fromjk=85c6bfc5f1bc6731",
        'https://de.indeed.com/cmp/Lieferando?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oe4gjkv6802&fromjk=2f92467356626881',
        'https://de.indeed.com/cmp/Hewlett-Packard-Enterprise-Hpe-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oer1ki8k800&fromjk=848a90d1ab19907b',
        'https://de.indeed.com/cmp/Anschutz-Entertainment-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ofg0l22k800&fromjk=d316a4fce5584139',
        'https://de.indeed.com/cmp/Eat-Happy-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6og6kje1l800&fromjk=41ac10034fc16733',
        'https://de.indeed.com/cmp/Powercloud-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oh6okkfn800&fromjk=896be62c6754a5b7',
        'https://de.indeed.com/cmp/Precise-Hotels-&-Resorts-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ohrtk7ts800&fromjk=9f43f92aa33b57cd',
        'https://de.indeed.com/cmp/Fanpage-Karma?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oifajgap802&fromjk=3b4e9ec705c22ba7',
        'https://de.indeed.com/cmp/Berger?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6oj3jlhdg802&fromjk=eeea07a54876f9eb',
        'https://de.indeed.com/cmp/Ivu-Traffic-Technologies-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ojp3ip9j802&fromjk=7c99bdec2fa15359',
        'https://de.indeed.com/cmp/Capmo-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6okf5k7bn804&fromjk=97b2c83e899ad791',
        'https://de.indeed.com/cmp/Http-Www.trendence.com-Karriere-Stellenangebote.html?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ol52jjgs800&fromjk=f88aa90f55260d15',
        'https://de.indeed.com/cmp/Quadriga-Media-Berlin-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6om6ok7ej800&fromjk=4d620a04147eb20b',
        'https://de.indeed.com/cmp/U--blox?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6on9glhdk802&fromjk=f0df3e68d6a93836',
        'https://de.indeed.com/cmp/Scout24-Se-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6pqldikd9802&fromjk=d3327c7ee79328e2',
        'https://de.indeed.com/cmp/Primal-State?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6prmtkkfc804&fromjk=6ad12bdfd5d8e9fb',
        'https://de.indeed.com/cmp/Adsquare-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6psppk7d4800&fromjk=51f958aab5f7e873',
        'https://de.indeed.com/cmp/Berlin-Cuisine-Metzger-&-Jensen-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6ptsdlhdn800&fromjk=a5ce09402fddc001',
        'https://de.indeed.com/cmp/Hewlett-Packard-Enterprise-Hpe-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6puutlhdd801&fromjk=848a90d1ab19907b',
        'https://de.indeed.com/cmp/Herm%C3%A8s-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q017je36800&fromjk=63df9a9e254f26f0',
        'https://de.indeed.com/cmp/Vattenfall?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q136j3v7802&fromjk=2d1da6110893f134',
        'https://de.indeed.com/cmp/Online-Birds-Hotel-Marketing-Solutions?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q255je1l800&fromjk=3daaa833ecd47e51',
        'https://de.indeed.com/cmp/Accenture?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q36skkfc800&fromjk=01fbc74f6bce501f',
        'https://de.indeed.com/cmp/Nia-Health-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q499jjgs800&fromjk=2e2e962ef4cf606e',
        'https://de.indeed.com/cmp/IBM-Ix-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q5b0jg9b800&fromjk=9994c25c7c874823',
        'https://de.indeed.com/cmp/Unzer?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q6d5k7ts803&fromjk=81d7138283eda9bf',
        'https://de.indeed.com/cmp/Deloitte?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q7f82bc4003&fromjk=75d3a0743bcbd1ae',
        'https://de.indeed.com/cmp/Giga.green?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q8hdkojo802&fromjk=aa5ca76412181b7f',
        'https://de.indeed.com/cmp/Saatchi-&-Saatchi?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6q9jqk7sn802&fromjk=db07fe2a39c17491',
        'https://de.indeed.com/cmp/Dataguard-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6rjr8lhdd802&fromjk=37066ac8ee53e985',
        'https://de.indeed.com/cmp/Diconium-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6rks5jjjs802&fromjk=f9afb40cd075124e',
        'https://de.indeed.com/cmp/Smarketer-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6rlj7k7sn802&fromjk=15f6d88298624e90',
        'https://de.indeed.com/cmp/Berlin-Brands-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s567l22k802&fromjk=50f4744cd5754274',
        'https://de.indeed.com/cmp/Care-With-Care?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s66rl22o807&fromjk=be82878656ef7cec',
        'https://de.indeed.com/cmp/Smartclip-Europe-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s6tplheg805&fromjk=00ef1c15bf5b5939',
        'https://de.indeed.com/cmp/Bonial?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s7tdki8k800&fromjk=24d158ec1fd24ec9',
        'https://de.indeed.com/cmp/Re-Cap?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s8km2m5n002&fromjk=514faab177900060',
        'https://de.indeed.com/cmp/Schindler-59cfe7ee?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s99ajqvi800&fromjk=1619b0e0ab6a2b5b',
        'https://de.indeed.com/cmp/Sonnen?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6s9uc2fbr002&fromjk=be1fd61011ef7e08',
        'https://de.indeed.com/cmp/Angel-Last-Mile-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6saltk5og803&fromjk=afae896c15b4b92b',
        'https://de.indeed.com/cmp/Capgemini?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6sbe1j3v7802&fromjk=a9e76fa7d7d568f9',
        'https://de.indeed.com/cmp/Hrlab-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6sc1uip9j800&fromjk=ee2ed6b1d8a3a033',
        'https://de.indeed.com/cmp/Sabienzia-Technologies-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6scnol233802&fromjk=e901abc02f6d3bad',
        'https://de.indeed.com/cmp/Adsquare-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tga1ir2n800&fromjk=0946d72d5f01ee6b',
        'https://de.indeed.com/cmp/Alstom?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6thj9k7bn802&fromjk=7c59e0e5cc24defc',
        'https://de.indeed.com/cmp/Vodafone?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tiluikcj800&fromjk=c2d9b4fe54366208',
        'https://de.indeed.com/cmp/Cenit?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tjo7k7bn802&fromjk=6505e394e293cc72',
        'https://de.indeed.com/cmp/The-Social-Chain-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tkp7k7fs802&fromjk=6e94fb9ac295feba',
        'https://de.indeed.com/cmp/Dataguard-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tlsvjjik804&fromjk=a3e7e16e164c6094',
        'https://de.indeed.com/cmp/Spendesk?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tn08k6r3800&fromjk=0715219702bf2ad2',
        'https://de.indeed.com/cmp/Humanoo-Etherapists-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6to1jjjiu802&fromjk=e4b92fad1ac40cd1',
        'https://de.indeed.com/cmp/U--blox?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tp3ik7fs801&fromjk=f0df3e68d6a93836',
        'https://de.indeed.com/cmp/Deutsche-Bank?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tqabikcj803&fromjk=5748085de433fa25',
        'https://de.indeed.com/cmp/Live-Nation?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6trrt2m5n005&fromjk=3cd1ed52272f1b5c',
        'https://de.indeed.com/cmp/Krongaard-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tt7ij326802&fromjk=3fccdb4eace9bf64',
        'https://de.indeed.com/cmp/Michael-Page?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tu9jir3o800&fromjk=22f72c1aaf7608ea',
        'https://de.indeed.com/cmp/Yoc-France?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6tvafk7cg801&fromjk=98c98956530df48c',
        'https://de.indeed.com/cmp/Smartbroker?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6u010ir2n802&fromjk=12eb3afd69bcb4b1',
        'https://de.indeed.com/cmp/Deutsche-Bank?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v21dl22p800&fromjk=5748085de433fa25',
        'https://de.indeed.com/cmp/Humanoo-Etherapists-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v33e2fbv000&fromjk=e4b92fad1ac40cd1',
        'https://de.indeed.com/cmp/Avart-Personal-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v3oekojo802&fromjk=914685aa3e3d3f81',
        'https://de.indeed.com/cmp/Capgemini?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v4dbl237802&fromjk=371a49fb77b100cb',
        'https://de.indeed.com/cmp/Smartbroker?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v5f9kkd7802&fromjk=12eb3afd69bcb4b1',
        'https://de.indeed.com/cmp/Michael-Page?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v672ikcj802&fromjk=22f72c1aaf7608ea',
        'https://de.indeed.com/cmp/Bilendi?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v6tvjjiu802&fromjk=86393400f2b96819',
        'https://de.indeed.com/cmp/Kranus-Health-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v800lhdh802&fromjk=46c69764204b3c61',
        'https://de.indeed.com/cmp/Humanoo?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v8mki46f803&fromjk=7699949131a89839',
        'https://de.indeed.com/cmp/Steinbeis-School-of-International-Business-and-Entrepreneurship-(sibe)-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6v9brl22k802&fromjk=5d0b0708bbce7955',
        'https://de.indeed.com/cmp/Youngcapital?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vadjlhej802&fromjk=6cb7dfc77311fc22',
        'https://de.indeed.com/cmp/Hewlett-Packard-Enterprise-Hpe-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vb2jj3ut801&fromjk=609757da0649b591',
        'https://de.indeed.com/cmp/Headmatch-Gmbh-&-Co.kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vbo4k7rk802&fromjk=e6a4a905c6e092d8',
        'https://de.indeed.com/cmp/Krongaard-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vck5jjiv800&fromjk=3fccdb4eace9bf64',
        'https://de.indeed.com/cmp/Dps-Business-Solutions-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6vdg02m5n002&fromjk=7ec5e1d8620690ae',
        'https://de.indeed.com/cmp/Gkm-Recruitment-Services?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70eeejg9n800&fromjk=648749532e95b692',
        'https://de.indeed.com/cmp/Bilendi?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70fmmikrh801&fromjk=86393400f2b96819',
        'https://de.indeed.com/cmp/Just-Spices-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70gk0ikcj807&fromjk=85e469b5ebcb7c4c',
        'https://de.indeed.com/cmp/Noris-Network?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70hmh2bc4003&fromjk=c05495fbcebba4e4',
        'https://de.indeed.com/cmp/Headmatch-Gmbh-&-Co.kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70iovl22p801&fromjk=e6a4a905c6e092d8',
        'https://de.indeed.com/cmp/Avart-Personal-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70jr3l21j802&fromjk=914685aa3e3d3f81',
        'https://de.indeed.com/cmp/Kranus-Health-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70ktuj3ut802&fromjk=46c69764204b3c61',
        'https://de.indeed.com/cmp/Comsysto-Reply-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70qt3k5ro805&fromjk=63bcf919b26239a3',
        'https://de.indeed.com/cmp/Bearingpoint?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70rjqje36802&fromjk=095c85169a38d8f9',
        'https://de.indeed.com/cmp/Hoppecke-Batterien?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70slvlheg802&fromjk=ef8d22ff0e30d255',
        'https://de.indeed.com/cmp/Steinbeis-School-of-International-Business-and-Entrepreneurship-(sibe)-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70to32fbv002&fromjk=5d0b0708bbce7955',
        'https://de.indeed.com/cmp/Dps-Business-Solutions-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70upvjgap802&fromjk=7ec5e1d8620690ae',
        'https://de.indeed.com/cmp/Michael-Page?campaignid=mobvjcmp&from=mobviewjob&tk=1gou70vsal210802&fromjk=5de951a85fcd8738',
        'https://de.indeed.com/cmp/Robert-Half?campaignid=mobvjcmp&from=mobviewjob&tk=1gou710ujl22k800&fromjk=8d57969b3839fb6b',
        'https://de.indeed.com/cmp/Hays?campaignid=mobvjcmp&from=mobviewjob&tk=1gou71205jjiu800&fromjk=e4dc737964d8b1c9',
        'https://de.indeed.com/cmp/Noris-Network?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7226qir3o800&fromjk=1b324c8ac18fc90e',
        'https://de.indeed.com/cmp/Zalando?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7236tki8k803&fromjk=085baa86ea598d78',
        'https://de.indeed.com/cmp/Deutsche-Bank?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7249ql22o802&fromjk=24598c474fdc87a0',
        'https://de.indeed.com/cmp/Solique-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7251rikd9802&fromjk=e5d9af519388ea3b',
        'https://de.indeed.com/cmp/Tesvolt-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou725oa2fbv000&fromjk=752e32e80fbf8f02',
        'https://de.indeed.com/cmp/Floris-Catering-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou726gbikdg802&fromjk=88e644be36905113',
        'https://de.indeed.com/cmp/Michael-Page?campaignid=mobvjcmp&from=mobviewjob&tk=1gou727gqjjjs802&fromjk=247325277bdef0d5',
        'https://de.indeed.com/cmp/Capgemini?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72882ikdg803&fromjk=371a49fb77b100cb',
        'https://de.indeed.com/cmp/Broadgate-Search?campaignid=mobvjcmp&from=mobviewjob&tk=1gou728u6l22p802&fromjk=48c95cae49a33de5',
        'https://de.indeed.com/cmp/Connected-Gs-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou729hjjkvo803&fromjk=f8178e2ab395f8b1',
        'https://de.indeed.com/cmp/Kuehne+nagel?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72a62k7qa802&fromjk=15060a73d20ce616',
        'https://de.indeed.com/cmp/Spendesk?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72b8lk5ro800&fromjk=eae533cf0cccd9f5',
        'https://de.indeed.com/cmp/Apcoa-Parking-3?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72bv7jqvd802&fromjk=381396175176161a',
        'https://de.indeed.com/cmp/Aemtec-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72ckdl210802&fromjk=d668c4faa81606e2',
        'https://de.indeed.com/cmp/Alogis-Ag-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou72daukkd7802&fromjk=f0baff0610131fe2',
        'https://de.indeed.com/cmp/Fischerappelt?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73errjg9n802&fromjk=a0808e7270c93486',
        'https://de.indeed.com/cmp/Hoppecke-Batterien?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73fr2j3v7802&fromjk=ab829ff6a51ef812',
        'https://de.indeed.com/cmp/Ib-Vogt-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73gi4kkfn802&fromjk=2fd275f557831d51',
        'https://de.indeed.com/cmp/Deutsche-Bank?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73h7tlhdh802&fromjk=2690f5c402dc43a2',
        'https://de.indeed.com/cmp/Studydrive-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73httjqvd801&fromjk=b14d5c0ba161ab7e',
        'https://de.indeed.com/cmp/Nobel-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gou73iiuikrh800&fromjk=af3b3a0bac211aec',
        'https://de.indeed.com/cmp/Oliver-Wyman-Group-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7420pk7bn802&fromjk=e9a47934c2050555',
        'https://de.indeed.com/cmp/Hubject-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7433hk7cg800&fromjk=41cb640230fe52bd',
        'https://de.indeed.com/cmp/Usu-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou743o3k7ej802&fromjk=6b23fceb8ef2859c',
        'https://de.indeed.com/cmp/Software-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou744qeje36802&fromjk=ce7a9d00b5e453cb',
        'https://de.indeed.com/cmp/Nobel-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gou745fgjjiv802&fromjk=5ac57abcdbe2ba13',
        'https://de.indeed.com/cmp/Lingoda-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7465nkkfc803&fromjk=31ac7e7d0960a35b',
        'https://de.indeed.com/cmp/Ey?campaignid=mobvjcmp&from=mobviewjob&tk=1gou746t9jksu800&fromjk=2d1b5a0d8bfbb466',
        'https://de.indeed.com/cmp/Strategy&?campaignid=mobvjcmp&from=mobviewjob&tk=1gou747jjlhdh802&fromjk=e35ae750d842c7df',
        'https://de.indeed.com/cmp/Usu-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75hnjjjj7802&fromjk=6b23fceb8ef2859c',
        'https://de.indeed.com/cmp/Studydrive-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75imul233800&fromjk=b14d5c0ba161ab7e',
        'https://de.indeed.com/cmp/Lingoda-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75joml21j800&fromjk=31ac7e7d0960a35b',
        'https://de.indeed.com/cmp/Software-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75krfiqv3800&fromjk=ce7a9d00b5e453cb',
        'https://de.indeed.com/cmp/Kuehne+nagel?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75lgv2m5n002&fromjk=15060a73d20ce616',
        'https://de.indeed.com/cmp/Spendesk?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75mivl21j800&fromjk=a6426709248c7dfe',
        'https://de.indeed.com/cmp/Thermo-Fisher-Scientific?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75n9fk7ts804&fromjk=b85e4519093e889d',
        'https://de.indeed.com/cmp/Spendesk?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75o0rir2n802&fromjk=344c94ba993dfc79',
        'https://de.indeed.com/cmp/Ib-Vogt-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75on1lhed800&fromjk=2fd275f557831d51',
        'https://de.indeed.com/cmp/Alstom?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75pffje1l800&fromjk=dccd8a1400aae357',
        'https://de.indeed.com/cmp/Avantgarde-Experts?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75qg4irp1800&fromjk=581cc252f3c405f8',
        'https://de.indeed.com/cmp/Orange-Quarter?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75r5fk5og802&fromjk=d3a2efd4549cea35',
        'https://de.indeed.com/cmp/Realworld-One-Gmbh-&-Co.-Kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75rqok7d4803&fromjk=60042adbeda42da5',
        'https://de.indeed.com/cmp/Frg-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75sf5k7ts802&fromjk=c734f98e71b6dc59',
        'https://de.indeed.com/cmp/Veeva-Systems?campaignid=mobvjcmp&from=mobviewjob&tk=1gou75t56lheg803&fromjk=8785c08cfd511493',
        'https://de.indeed.com/cmp/Usu-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou76v6fi46f800&fromjk=16bd223191897413',
        'https://de.indeed.com/cmp/Avantgarde-Experts?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7707s2e11002&fromjk=de3ed4dca6c3473a',
        'https://de.indeed.com/cmp/Deutsche-Telekom?campaignid=mobvjcmp&from=mobviewjob&tk=1gou770unj3vv802&fromjk=e2849bddec87183f',
        'https://de.indeed.com/cmp/Workstreams.ai-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou771mgkkfd800&fromjk=8615a4952d2ebb65',
        'https://de.indeed.com/cmp/Yara-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou772o5i46f803&fromjk=eaeedfd9a3eff58b',
        'https://de.indeed.com/cmp/Flaconi-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou773e6jjiu802&fromjk=7d34dcbd390c4335',
        'https://de.indeed.com/cmp/Ml6?campaignid=mobvjcmp&from=mobviewjob&tk=1gou774h2jg9n800&fromjk=fc9f30ea8c5a197a',
        'https://de.indeed.com/cmp/Vanilla-Steel-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou775imk7qa800&fromjk=1be83b54ce988bd6',
        'https://de.indeed.com/cmp/Br%C3%B6er-&-Partner-Gmbh-&-Co-Kg?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7768hje1l801&fromjk=36d392cb282a5926',
        'https://de.indeed.com/cmp/Bunch?campaignid=mobvjcmp&from=mobviewjob&tk=1gou77737ikrh800&fromjk=caf1e55ecbcdadda',
        'https://de.indeed.com/cmp/Trinckle-3d-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou777vel233801&fromjk=20ff3807007d5057',
        'https://de.indeed.com/cmp/Leanlancer-Ug?campaignid=mobvjcmp&from=mobviewjob&tk=1gou778nli46f802&fromjk=737a3c699338a650',
        'https://de.indeed.com/cmp/Leanlancer-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou779qvjg9n800&fromjk=6e6f8019d8d34a7c',
        'https://de.indeed.com/cmp/Clariness?campaignid=mobvjcmp&from=mobviewjob&tk=1gou77atglhdd800&fromjk=c489e6cf51e209d7',
        'https://de.indeed.com/cmp/Mindbody?campaignid=mobvjcmp&from=mobviewjob&tk=1gou77bihhdhg802&fromjk=971f5370df68a00f',
        'https://de.indeed.com/cmp/Masterplan.com-4?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78hbdjg90802&fromjk=33fb2fa9cb4db6db',
        'https://de.indeed.com/cmp/Picture-Tree-International-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78id8ikd9803&fromjk=7e8045daf4f3b4df',
        'https://de.indeed.com/cmp/Enpal-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78ja2jg9n802&fromjk=74615c24ba07dd6f',
        'https://de.indeed.com/cmp/Fairsenden-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78k7ukkfn802&fromjk=13669fae46359423',
        'https://de.indeed.com/cmp/Centrovital-Berlin?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78laqje1l80h&fromjk=75c37f2f66027ec0',
        'https://de.indeed.com/cmp/Dedo-Media-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78mcklhej802&fromjk=7bea898030156603',
        'https://de.indeed.com/cmp/Briink?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78n2ik7dg802&fromjk=518b11ae627b2710',
        'https://de.indeed.com/cmp/First-Berlin-Equity-Research-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78nnqlhdh802&fromjk=8bc298f3503e47ce',
        'https://de.indeed.com/cmp/Merantix?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78odejqun801&fromjk=8bc140309ac56efb',
        'https://de.indeed.com/cmp/Delphai?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78p36jqvd802&fromjk=dcf4c5badc1e6163',
        'https://de.indeed.com/cmp/Contentbird-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78pp2lhdg800&fromjk=6f311172db2ca662',
        'https://de.indeed.com/cmp/Easylivestream?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78qeoje0n801&fromjk=d5071b1589294ef2',
        'https://de.indeed.com/cmp/Bvdw-Services-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78r5rk7fs800&fromjk=e0364340a38c6258',
        'https://de.indeed.com/cmp/Cytosorbents-Europe-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78s7flhdk802&fromjk=75ecae871b101e8b',
        'https://de.indeed.com/cmp/Oceansapart?campaignid=mobvjcmp&from=mobviewjob&tk=1gou78ta4kkfd800&fromjk=9a3f148ea2272336',
        'https://de.indeed.com/cmp/K&K-Handelsgesellschaft-Mbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a3dj2fbr000&fromjk=d8c368565350162e',
        'https://de.indeed.com/cmp/Leanlancer-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a4etjkvj802&fromjk=6e6f8019d8d34a7c',
        'https://de.indeed.com/cmp/Circulee-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a547k7t1801&fromjk=8020ce1d27ab81cc',
        'https://de.indeed.com/cmp/Briink?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a5q4jjgs800&fromjk=518b11ae627b2710',
        'https://de.indeed.com/cmp/Equeo-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a6rkl22p802&fromjk=c1e9440d1854d634',
        'https://de.indeed.com/cmp/Clariness?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a7htl22k802&fromjk=c489e6cf51e209d7',
        'https://de.indeed.com/cmp/Heyrecruit?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a8k8kkd7802&fromjk=65f8dc6dcbaaa512',
        'https://de.indeed.com/cmp/Weroad-4?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7a9all22o802&fromjk=2e551c5f448515c0',
        'https://de.indeed.com/cmp/Circulee?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7aa04hdhg802&fromjk=79fce93d3eb788c9',
        'https://de.indeed.com/cmp/Escapio-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7aaoqip9j802&fromjk=4f37ce67b3761108',
        'https://de.indeed.com/cmp/Merantix?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7abp6kojo800&fromjk=8bc140309ac56efb',
        'https://de.indeed.com/cmp/The-Bike-Club?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7acr1i3rg803&fromjk=97578766a74f4a37',
        'https://de.indeed.com/cmp/Verlag-Der-Tagesspiegel-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7adg9k2mg802&fromjk=325d68b564b1e738',
        'https://de.indeed.com/cmp/Easypark-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7ae4qjgap800&fromjk=be8b7030f15b6648',
        'https://de.indeed.com/cmp/Subtel-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7aeq8k7bn802&fromjk=a549dd2ad57c9881',
        'https://de.indeed.com/cmp/Rydes?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bi6ul21j802&fromjk=e8c7d8eb6c290a74',
        'https://de.indeed.com/cmp/Everyone-Energy?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bj9ck7ts801&fromjk=4d6614d8e4dcc872',
        'https://de.indeed.com/cmp/Craft-Circus-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bkcmjjik802&fromjk=4929dc4287901f83',
        'https://de.indeed.com/cmp/In-Pact-Media-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bli4j3vv801&fromjk=1731105eeb0962d3',
        'https://de.indeed.com/cmp/Incred-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bmnnjjiu803&fromjk=25fdd1c44654ff0c',
        'https://de.indeed.com/cmp/Cloudinary?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bnnijksu802&fromjk=c695b893cef4b284',
        'https://de.indeed.com/cmp/Also-Energy?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7boqgkkfc802&fromjk=8c287bce4377d212',
        'https://de.indeed.com/cmp/Adsquare-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bq4ck7cg801&fromjk=9e109c0d0d1fc4eb',
        'https://de.indeed.com/cmp/Entyre-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7br1piqv3802&fromjk=77de329afdb9e9d3',
        'https://de.indeed.com/cmp/Sendinblue?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bs63jqvd802&fromjk=953cea5bb44670dc',
        'https://de.indeed.com/cmp/Vaayu-Tech-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bta7hdhg800&fromjk=61ef53d12505b993',
        'https://de.indeed.com/cmp/Eqolot?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7buarhdhg802&fromjk=f18c867167df71e1',
        'https://de.indeed.com/cmp/Singularitysales-Beteiligungsges.-Mbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7bvf8jkvo802&fromjk=02704f1d0fd6615d',
        'https://de.indeed.com/cmp/Primal-State-Performance-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7c0h9ikrh802&fromjk=5dbdb877e58ccc60',
        'https://de.indeed.com/cmp/Hartmann-Tresore?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7c1jcjjjs800&fromjk=706f21512a350405',
        'https://de.indeed.com/cmp/Madvertise-2?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7d74ljg9n800&fromjk=bf736bca49cd89cd',
        'https://de.indeed.com/cmp/Enpal-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7d8fm2fbv003&fromjk=74615c24ba07dd6f',
        'https://de.indeed.com/cmp/Ebuero-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7d9jrjqvi800&fromjk=33b67b24279136ff',
        'https://de.indeed.com/cmp/Matthias-Pianezezr?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7dammjkv6800&fromjk=2f4d3ed8541424db',
        'https://de.indeed.com/cmp/First-Berlin-Equity-Research-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7dbpcjg9b800&fromjk=ec7445c02260be55',
        'https://de.indeed.com/cmp/Eclipse-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7dcrolhdn802&fromjk=9e49b1bcd02940eb',
        'https://de.indeed.com/cmp/Sellerx-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7ddu3lhej802&fromjk=de58e2b7a4f58ceb',
        'https://de.indeed.com/cmp/Easylivestream?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7dtrnip9j802&fromjk=d5071b1589294ef2',
        'https://de.indeed.com/cmp/Nyn-Consulting?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7duvfl237801&fromjk=7c22957bdbdce7a4',
        'https://de.indeed.com/cmp/Magaloop-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e01el21j802&fromjk=e8e7981f2c5f2b67',
        'https://de.indeed.com/cmp/Dertaler-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e14bjqvi802&fromjk=a2cf468ec571ef25',
        'https://de.indeed.com/cmp/Keyence?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e275l21j801&fromjk=5e88e985e7c160c4',
        'https://de.indeed.com/cmp/Egroup?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e39tjqvd800&fromjk=96a05ce9675c211c',
        'https://de.indeed.com/cmp/Codept-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7e4c3lhei800&fromjk=8d7a43a24d6f9f0f',
        'https://de.indeed.com/cmp/Cloudinary?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fhobikre802&fromjk=c695b893cef4b284',
        'https://de.indeed.com/cmp/Matthias-Pianezezr?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fipihdi6802&fromjk=2f4d3ed8541424db',
        'https://de.indeed.com/cmp/Apoll-On-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fjfo2e11002&fromjk=5a73c29bd37b2297',
        'https://de.indeed.com/cmp/Audience-Serv-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fkilk7cg800&fromjk=abea09427d2ca136',
        'https://de.indeed.com/cmp/The-Recruitment-2.0-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fl84ikd9802&fromjk=18fe84a8212babb5',
        'https://de.indeed.com/cmp/Berliner-Brandstifter?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7flurikdg802&fromjk=d868ffd821a56d07',
        'https://de.indeed.com/cmp/United-Internet-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fmkvk7rk802&fromjk=38b49b4f812ec32a',
        'https://de.indeed.com/cmp/Estrategy-Consulting-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fnbql210802&fromjk=30cb08585c128ac8',
        'https://de.indeed.com/cmp/Magaloop-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fo2el22k803&fromjk=e8e7981f2c5f2b67',
        'https://de.indeed.com/cmp/In-Pact-Media-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fp4kk7ej800&fromjk=1731105eeb0962d3',
        'https://de.indeed.com/cmp/Sense-Electra-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fq6njkv6802&fromjk=b734bb3347c04a3a',
        'https://de.indeed.com/cmp/Flexperto-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7fqtcirp1801&fromjk=ec91669cc4841e0b',
        'https://de.indeed.com/cmp/Primal-State-Performance-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7gpn62fbr002&fromjk=5dbdb877e58ccc60',
        'https://de.indeed.com/cmp/Bewerbungscode-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7hv80jg90800&fromjk=ce84e2ab99147fcd',
        'https://de.indeed.com/cmp/Sense-Electra-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i09ljjik800&fromjk=b734bb3347c04a3a',
        'https://de.indeed.com/cmp/Sendinblue?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i0v8k7bn802&fromjk=8007da5f0107a98f',
        'https://de.indeed.com/cmp/Lions-&-Gazelles-International-Recruitment-Ag?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i1kuir2n804&fromjk=acff33b4255d5c67',
        'https://de.indeed.com/cmp/Workbees-Gmbh-(part-of-Netgo-Group)?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i298jkv6800&fromjk=95b26f252138d5c1',
        'https://de.indeed.com/cmp/Valsight-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i3bkl21j802&fromjk=6502fa20aa20cfbd',
        'https://de.indeed.com/cmp/Ticketmaster?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i4ffjjjs802&fromjk=bb02c87334de177b',
        'https://de.indeed.com/cmp/Wunderpen-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i5h6ikre802&fromjk=1171319b530ee5fb',
        'https://de.indeed.com/cmp/Valsight-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i6jmlhdn802&fromjk=ca3bf3b411c9ea14',
        'https://de.indeed.com/cmp/Eurofins?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i7acj3ut800&fromjk=0709a6d9225fdd7e',
        'https://de.indeed.com/cmp/21.finance?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i826lhdh802&fromjk=fbbefefe1cf31079',
        'https://de.indeed.com/cmp/Weroad?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7i98pjg9b800&fromjk=153ae7c7a5bd1342',
        'https://de.indeed.com/cmp/Ds-Event-Lobby-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7ia58je1l800&fromjk=91f1f3b7500db573',
        'https://de.indeed.com/cmp/Nico-Europe-Gmbh-4?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7iplaje36802&fromjk=d111c1c4ab3a2785',
        'https://de.indeed.com/cmp/Workbees-Gmbh-(part-of-Netgo-Group)?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7jtnbi46f802&fromjk=95b26f252138d5c1',
        'https://de.indeed.com/cmp/Ds-Event-Lobby-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7julrikcj800&fromjk=91f1f3b7500db573',
        'https://de.indeed.com/cmp/Bewerbungscode-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7jvc8lhdn802&fromjk=ce84e2ab99147fcd',
        'https://de.indeed.com/cmp/Twinwin?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k01llhdh802&fromjk=5f31e4fbb4340b4e',
        'https://de.indeed.com/cmp/Bauer-Gruppe-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k0lvlhed800&fromjk=4ab2b121d6551fa5',
        'https://de.indeed.com/cmp/Meetsales?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k1dpjgap802&fromjk=b1796f142df77949',
        'https://de.indeed.com/cmp/Wunderpen-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k222k7cg803&fromjk=1171319b530ee5fb',
        'https://de.indeed.com/cmp/Product-People?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k2n8k7ts800&fromjk=dc46c00a42a3907e',
        'https://de.indeed.com/cmp/Verve-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k3crk6r3800&fromjk=59c8a19c12c6609c',
        'https://de.indeed.com/cmp/Nico-Europe-Gmbh-4?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k426k6r3803&fromjk=d111c1c4ab3a2785',
        'https://de.indeed.com/cmp/G2k-Group-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k4nvikre801&fromjk=fdb62f6de6d29d92',
        'https://de.indeed.com/cmp/Matthias-Pianezezr?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k5ghl21j802&fromjk=cd1bd8efde516f42',
        'https://de.indeed.com/cmp/Multitude?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7k67tje0p802&fromjk=16ae832ec933f1f3',
        'https://de.indeed.com/cmp/Sellerx-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7km29k7ej800&fromjk=e66fd59a12be6ca9',
        'https://de.indeed.com/cmp/Audience-Serv-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7lsrjlhdd800&fromjk=abea09427d2ca136',
        'https://de.indeed.com/cmp/Twinwin?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7lttcjqun803&fromjk=5f31e4fbb4340b4e',
        'https://de.indeed.com/cmp/Talent--valet?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7luiskkfc800&fromjk=f8f5bf4b8e3d9252',
        'https://de.indeed.com/cmp/Sellerx-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7mej1jjj7802&fromjk=e66fd59a12be6ca9',
        'https://de.indeed.com/cmp/Pixtunes-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7muinir3o801&fromjk=c40063d4d90c0f71',
        'https://de.indeed.com/cmp/Meetsales?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7mvltlheg802&fromjk=b1796f142df77949',
        'https://de.indeed.com/cmp/Blu-Die-Agentur-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n0ngjjj7802&fromjk=0da7d44f8093fd0a',
        'https://de.indeed.com/cmp/Therme-Art-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n1e8lhei801&fromjk=d008f2c20e3fa9a6',
        'https://de.indeed.com/cmp/Ka-Resources?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n27jhdi6802&fromjk=821cd8312fde7b69',
        'https://de.indeed.com/cmp/Verve-Group?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n37ak7t1802&fromjk=59c8a19c12c6609c',
        'https://de.indeed.com/cmp/International-People-Solutions?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7n3u7kojo802&fromjk=4dbebdc94480ef71',
        'https://de.indeed.com/cmp/Usu-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7njs5k6r3801&fromjk=36546e92994cda67',
        'https://de.indeed.com/cmp/International-People-Solutions?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7p79kk7ej800&fromjk=4dbebdc94480ef71',
        'https://de.indeed.com/cmp/Usu-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7p8cjjksu802&fromjk=2a3068fdacc4c138',
        'https://de.indeed.com/cmp/Infoverity?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7p90mjkv6802&fromjk=78a88ea6a54ad36a',
        'https://de.indeed.com/cmp/Ka-Resources?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7p9m0l210801&fromjk=cc688392582a650b',
        'https://de.indeed.com/cmp/Usu-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7pabnj3ut800&fromjk=b4e39bd53d849b69',
        'https://de.indeed.com/cmp/Ka-Resources?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7pb1il22p802&fromjk=82258bec8c2d83d9',
        'https://de.indeed.com/cmp/Ka-Resources?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7pc3pl233801&fromjk=3b4472da888797c9',
        'https://de.indeed.com/cmp/Black-Pen-Recruitment?campaignid=mobvjcmp&from=mobviewjob&tk=1gou7pd5r2fbr002&fromjk=4e80b09daa8fba4d']
    # main()
    mainAsyncio(company_urls=company_urls, proxies=proxies)
    print(f'Processing Time for 15 company: {time.perf_counter() - start} second(s)')