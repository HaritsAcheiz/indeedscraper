from fake_useragent import UserAgent
from random import choice

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from selectolax import parser

import httpx

proxies = ['154.38.30.117:8800',
           '192.126.253.59:8800',
           '154.12.198.69:8800',
           '192.126.253.48:8800',
           # '192.126.250.223:8800',
           '192.126.250.22:8800',
           '154.12.198.179:8800',
           '192.126.253.134:8800',
           '192.126.253.197:8800',
           '154.38.30.196:8800'
           ]

scraped_proxies = ['35.154.32.37:3128', '51.79.50.31:9300', '115.96.208.124:8080', '151.80.95.161:8080', '51.159.115.233:3128']

def webdriver_setup(proxy = None):
    ip, port = proxy.split(sep=':')
    ua = UserAgent()
    useragent = ua.firefox
    firefox_options = Options()

    # firefox_options.headless = True
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
    driver.get(url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.jobsearch-Yosegi')))
    parent = driver.find_element(By.CSS_SELECTOR, 'div.jobsearch-Yosegi')
    input_term = parent.find_element(By.ID,'text-input-what')
    input_term.send_keys(term + Keys.TAB + location + Keys.RETURN)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.mosaic-provider-jobcards.mosaic.mosaic-provider-jobcards.mosaic-provider-hydrated')))
    result = driver.current_url.rsplit('&', 1)[0] + '&start=0'
    driver.quit()
    return result

def get_company_url(driver, url):
    driver.get(url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    try:
        # Accept all cookies
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,'div.otFlat.bottom.ot-wo-title.vertical-align-content>div>div.ot-sdk-container>div.ot-sdk-row>div#onetrust-button-group-parent.ot-sdk-three.ot-sdk-columns.has-reject-all-button>div#onetrust-button-group>button#onetrust-accept-btn-handler')))
        driver.find_element(By.CSS_SELECTOR, 'div.otFlat.bottom.ot-wo-title.vertical-align-content>div>div.ot-sdk-container>div.ot-sdk-row>div#onetrust-button-group-parent.ot-sdk-three.ot-sdk-columns.has-reject-all-button>div#onetrust-button-group>button#onetrust-accept-btn-handler').click()
        print('All Cookies accepted')
    except (NoSuchElementException, TimeoutException):
        print('No Cookies Banner')
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


if __name__ == '__main__':
    main()
