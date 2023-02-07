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

scraped_proxies = ['110.34.3.229:3128', '173.249.198.244:8080', '3.7.132.202:3128', '154.236.189.19:8080', '65.1.75.38:3128']

@dataclass
class Company:
    name:str
    website:str
    linkedin:str

def webdriver_setup(proxy = None):
    ip, port = proxy.split(sep=':')
    ua = UserAgent()
    useragent = ua.firefox
    firefox_options = Options()

    # firefox_options.headless = True
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

def job_result_url(driver, url, term, location):
    print('Get job list...')
    driver.get(url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.jobsearch-Yosegi')))
    parent = driver.find_element(By.CSS_SELECTOR, 'div.jobsearch-Yosegi')
    input_term = parent.find_element(By.ID,'text-input-what')
    input_term.send_keys(term + Keys.TAB + location + Keys.RETURN)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.mosaic-provider-jobcards.mosaic.mosaic-provider-jobcards.mosaic-provider-hydrated')))
    result = driver.current_url.rsplit('&', 1)[0] + '&start=0'
    driver.quit()
    return result

def get_company_url(driver, url):
    print('Get company url...')
    driver.get(url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)

    try:
        # Accept all cookies
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,'div.otFlat.bottom.ot-wo-title.vertical-align-content>div>div.ot-sdk-container>div.ot-sdk-row>div#onetrust-button-group-parent.ot-sdk-three.ot-sdk-columns.has-reject-all-button>div#onetrust-button-group>button#onetrust-accept-btn-handler')))
        driver.find_element(By.CSS_SELECTOR, 'div.otFlat.bottom.ot-wo-title.vertical-align-content>div>div.ot-sdk-container>div.ot-sdk-row>div#onetrust-button-group-parent.ot-sdk-three.ot-sdk-columns.has-reject-all-button>div#onetrust-button-group>button#onetrust-accept-btn-handler').click()
    except (NoSuchElementException, TimeoutException):
        pass

    clicking_objects = driver.find_elements(By.CSS_SELECTOR, 'div.mosaic-provider-jobcards.mosaic.mosaic-provider-jobcards.mosaic-provider-hydrated>ul.jobsearch-ResultsList.css-0>li>div>div.slider_container.css-g7s71f.eu4oa1w0')
    company_urls = list()
    for object in clicking_objects:
        # Scroll until element found
        js_code = "arguments[0].scrollIntoView();"
        element = object.find_element(By.CSS_SELECTOR, 'a.jcs-JobTitle.css-jspxzf.eu4oa1w0')
        driver.execute_script(js_code, element)

        # Click job element
        object.find_element(By.CSS_SELECTOR, 'a.jcs-JobTitle.css-jspxzf.eu4oa1w0').click()

        # Get company url
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.jobsearch-InlineCompanyRating.icl-u-xs-mt--xs.icl-u-xs-mb--md.css-11s8wkw.eu4oa1w0>div:nth-child(2)>div.css-czdse3.eu4oa1w0>a')))
        company_url = driver.find_element(By.CSS_SELECTOR, 'div.jobsearch-InlineCompanyRating.icl-u-xs-mt--xs.icl-u-xs-mb--md.css-11s8wkw.eu4oa1w0>div:nth-child(2)>div.css-czdse3.eu4oa1w0>a').get_attribute('href')
        company_urls.append(company_url)
    driver.quit()
    return company_urls

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
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'ul.css-1jgykzt.e37uo190')))
    Company.name = driver.find_element(By.CSS_SELECTOR, 'div[itemprop="name"]').text

    # Get Company URL
    parent = driver.find_element(By.CSS_SELECTOR, 'ul.css-1jgykzt.e37uo190')
    try:
        Company.website = parent.find_element(By.PARTIAL_LINK_TEXT, 'ebs').get_attribute('href')
    except NoSuchElementException:
        Company.website = None

    # Get Company linkedin
    try:
        Company.linkedin = parent.find_element(By.PARTIAL_LINK_TEXT, 'inked').get_attribute('href')
    except NoSuchElementException:
        Company.linkedin = get_linkedin(Company.name, proxy)
    driver.quit()
    return Company

def main():
    url = 'https://de.indeed.com/'
    term = 'junior sales'
    location = 'Berlin'

    proxy = choice(proxies)
    driver = webdriver_setup(proxy)
    search_result_url = job_result_url(driver, url, term, location)

    print(search_result_url)

    proxy = choice(proxies)
    driver = webdriver_setup(proxy)
    company_urls = get_company_url(driver, search_result_url)
    print(company_urls)

    # company_urls = ['https://de.indeed.com/cmp/Hotel-Mssngr?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5ab3ki9a800&fromjk=b047ef9a275f692a', 'https://de.indeed.com/cmp/Nh-8adc4d2a?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5bd62cfo002&fromjk=cc7dd09f67a7720d', 'https://de.indeed.com/cmp/Make-IT-Fix-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5cg5kibj803&fromjk=d7da040a0c4e08ad', 'https://de.indeed.com/cmp/Instinct3?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5dhvj3sp800&fromjk=dc8355820312c198', 'https://de.indeed.com/cmp/Targomo?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5eksk7gm802&fromjk=f7ff39626cd0f56f', 'https://de.indeed.com/cmp/Tts-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5fmvj3sp800&fromjk=c662129170711dba', 'https://de.indeed.com/cmp/Trakken-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5gogi3rn800&fromjk=3c9e429cd64ad558', 'https://de.indeed.com/cmp/Homburg-&-Partner?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5hrbk2lj800&fromjk=fd87426e320e2a3b', 'https://de.indeed.com/cmp/Highcoordination-Gmbh-1?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5it5keee800&fromjk=e4374dd769afabe7', 'https://de.indeed.com/cmp/Sonnen?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5k0lk7q0800&fromjk=e846fde655293c2e', 'https://de.indeed.com/cmp/Kreuzwerker-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5l7vkibj802&fromjk=e6b45259b1d839d6', 'https://de.indeed.com/cmp/A.-Lange-&-S%C3%B6hne?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5midk7q0802&fromjk=41a8cddcc5a80de1', 'https://de.indeed.com/cmp/Precise-Hotels-&-Resorts-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5nnhi3q6802&fromjk=0cb3375933f69c8b', 'https://de.indeed.com/cmp/Orbitvu?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5oqvk7jn802&fromjk=d48d9cb347c5aea9', 'https://de.indeed.com/cmp/Likeminded-Gmbh?campaignid=mobvjcmp&from=mobviewjob&tk=1gomb5psljqtv802&fromjk=2861be7ef9dd894a']
    for url in company_urls:
        proxy = choice(proxies)
        print(proxy)
        driver = webdriver_setup(proxy)
        result = get_data(driver, url, proxy)
        print(f'Company name: {result.name}')
        print(f'Company website: {result.website}')
        print(f'Company linkedin: {result.linkedin}')
        print('====================================================================')

if __name__ == '__main__':
    start = time.perf_counter()
    main()
    print(f'Processing Time for 15 company: {time.perf_counter() - start} second(s)')