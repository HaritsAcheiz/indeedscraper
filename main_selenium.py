from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from random import choice

from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

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

    firefox_options.set_capability("acceptSslCerts", True)
    firefox_options.set_capability("acceptInsecureCerts", True)
    firefox_options.set_capability("ignore-certificate-errors", False)

    driver = webdriver.Firefox(options=firefox_options)
    return driver

def search_job(driver, url, term, location):
    driver.get(url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.jobsearch-Yosegi')))
    parent = driver.find_element(By.CSS_SELECTOR, 'div.jobsearch-Yosegi')
    input_term = parent.find_element(By.ID,'text-input-what')
    input_term.send_keys(term + Keys.TAB + location + Keys.RETURN)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.mosaic-provider-jobcards.mosaic.mosaic-provider-jobcards.mosaic-provider-hydrated')))
    parent = driver.find_elements(By.CSS_SELECTOR, 'div.mosaic-provider-jobcards.mosaic.mosaic-provider-jobcards.mosaic-provider-hydrated>ul.jobsearch-ResultsList.css-0>li>div>div.slider_container.css-g7s71f.eu4oa1w0')
    []

def main():
    url = 'https://de.indeed.com/'
    term = 'junior sales'
    location = 'Berlin'

    proxy = choice(proxies)
    driver = webdriver_setup(proxy)
    search_job(driver, url, term, location)


if __name__ == '__main__':
    main()
