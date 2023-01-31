import httpx
import asyncio
import time
from selectolax.parser import HTMLParser
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

def scrape_cookies():
    url = 'https://de.indeed.com/jobs?q=Junior+Sales&l=Berlin&start=0'

    ip = '154.12.198.179'
    port = '8800'
    useragent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"

    ff_opt = Options()
    ff_opt.add_argument("--headless")
    ff_opt.add_argument("--no-sandbox")
    ff_opt.set_preference("general.useragent.override", useragent)
    ff_opt.set_preference('network.proxy.type', 1)
    ff_opt.set_preference('network.proxy.socks', ip)
    ff_opt.set_preference('network.proxy.socks_port', int(port))
    ff_opt.set_preference('network.proxy.socks_version', 4)
    ff_opt.set_preference('network.proxy.socks_remote_dns', True)
    ff_opt.set_preference('network.proxy.http', ip)
    ff_opt.set_preference('network.proxy.http_port', int(port))
    ff_opt.set_preference('network.proxy.ssl', ip)
    ff_opt.set_preference('network.proxy.ssl_port', int(port))

    driver = Firefox(options=ff_opt)
    driver.get(url)
    time.sleep(1)
    brCookies = driver.get_cookies()
    cf_cookies = [cookie for cookie in brCookies if cookie['name'] == 'cf_clearance'][0]['value']
    cookies = {'cf_clearance': cf_cookies}
    return cookies

if __name__ == '__main__':
    cookies = scrape_cookies()
    print(cookies)