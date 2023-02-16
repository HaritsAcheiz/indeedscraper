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
    driver.delete_all_cookies()
    driver.get(url)
    cookies = driver.get_cookies()
    ua = driver.execute_script("return navigator.userAgent")
    driver.maximize_window()
    driver.set_page_load_timeout(20)
    wait = WebDriverWait(driver, 15)
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
        driver.set_page_load_timeout(95)
        wait = WebDriverWait(driver, 90)

        # try:
        #     # Accept all cookies
        #     wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,'div.otFlat.bottom.ot-wo-title.vertical-align-content>div>div.ot-sdk-container>div.ot-sdk-row>div#onetrust-button-group-parent.ot-sdk-three.ot-sdk-columns.has-reject-all-button>div#onetrust-button-group>button#onetrust-accept-btn-handler')))
        #     # wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]')))
        #     driver.find_element(By.CSS_SELECTOR, 'div.otFlat.bottom.ot-wo-title.vertical-align-content>div>div.ot-sdk-container>div.ot-sdk-row>div#onetrust-button-group-parent.ot-sdk-three.ot-sdk-columns.has-reject-all-button>div#onetrust-button-group>button#onetrust-accept-btn-handler').click()
        # except (NoSuchElementException, TimeoutException):
        #     print('no cookies banner')
        #     pass

        try:
            # next_url = driver.find_element(By.CSS_SELECTOR,'a[data-testid="pagination-page-next"]').get_attribute('href')
            next_url = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]'))).get_attribute('href')
        except (NoSuchElementException, TimeoutException) as e:
            print(e)
            notendpage = False

        clicking_objects = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.mosaic-provider-jobcards.mosaic.mosaic-provider-jobcards.mosaic-provider-hydrated>ul.jobsearch-ResultsList.css-0>li>div>div.slider_container.css-g7s71f.eu4oa1w0')))

        # clicking_objects = driver.find_elements(By.CSS_SELECTOR, 'div.mosaic-provider-jobcards.mosaic.mosaic-provider-jobcards.mosaic-provider-hydrated>ul.jobsearch-ResultsList.css-0>li>div>div.slider_container.css-g7s71f.eu4oa1w0')

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
    base_url = 'https://de.indeed.com/'
    term = 'Account Executive'

    search_result_url, cookies, ua = job_result_url(proxies, base_url, term)

    company_urls = get_company_url(search_result_url, proxies=proxies)

    print(company_urls)

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
                search_result_url, cookies, ua = job_result_url(proxies, base_url, term)
                result, status_code = get_data(url, ua=ua, cookies=cookies, proxies=proxies)

        except (ConnectionRefusedError, ConnectError, RemoteProtocolError) as e:
            print(e)
            time.sleep(30)
            search_result_url, cookies, ua = job_result_url(proxies, url, term)
            result, status_code = get_data(url, ua=ua, cookies=cookies, proxies=proxies)
            print(result)
            print(status_code)

        to_csv(result, 'Account Executive.csv')

if __name__ == '__main__':
    start = time.perf_counter()
    main()
    print(f'Processing Time: {time.perf_counter() - start} second(s)')