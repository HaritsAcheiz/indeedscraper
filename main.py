import httpx
from selectolax.parser import HTMLParser
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

def webdriver_setup(proxy=None,useragent=None):
    if proxy != None:
        split_proxy = proxy.split(':')
        ip = split_proxy[0]
        port = split_proxy[1]

        ff_opt = Options()

        # ff_opt.add_argument("--headless")
        ff_opt.add_argument("--no-sandbox")
        # ff_opt.set_preference("general.useragent.override", useragent)
        ff_opt.set_preference('network.proxy.type', 1)
        ff_opt.set_preference('network.proxy.socks', ip)
        ff_opt.set_preference('network.proxy.socks_port', int(port))
        ff_opt.set_preference('network.proxy.socks_version', 5)
        ff_opt.set_preference('network.proxy.socks_remote_dns', True)
        ff_opt.set_preference('network.proxy.http', ip)
        ff_opt.set_preference('network.proxy.http_port', int(port))
        ff_opt.set_preference('network.proxy.ssl', ip)
        ff_opt.set_preference('network.proxy.ssl_port', int(port))

    else:
        ff_opt = Options()

        ff_opt.add_argument("--no-sandbox")

    driver = Firefox(options=ff_opt)

    return driver

def get_cookies(driver, url):
    driver.get(url)
    driver.maximize_window()

    result = {'ua':None, 'cookies':None}
    # get cookies and useragent
    brCookies = driver.get_cookies()
    ua = driver.execute_script('return navigator.userAgent')
    result['ua'] = {"user-agent": ua}

    # driver.quit()

    # filter out the cf_clearance cookie
    cf_cookies = [cookie for cookie in brCookies if cookie['name'] in ('__cf_bm', '_cfuvid')]
    result['cookies'] = {"__cf_bm": cf_cookies[0]['value'],
               "_cfuvid": cf_cookies[1]['value']
               }
    return result

def get_pages(url, user_agent, cookies, proxy):
    proxies = {
        "http://": f"http://{proxy}",
        "https://": f"http://{proxy}"
    }
    with httpx.Client(headers=user_agent, cookies=cookies, proxies=proxies) as client:
        html_pages = client.get(url).text
    return html_pages

# def get_pages_cs(url):
#     with cloudscraper.create_scraper() as scraper:
#         html_pages = scraper.get(url).text
#     return html_pages
def main():
    url = 'https://de.indeed.com/jobs?q=Junior+Sales&l=Berlin&start=0'
    driver = webdriver_setup(proxy='192.126.253.59:8800')
    cookies = get_cookies(driver=driver, url=url)
    result = get_pages(url=url, user_agent=cookies['ua'], cookies=cookies['cookies'], proxy='192.126.253.59:8800')
    # result2 = get_pages_cs(url=url)
    print('=======================result============================')
    print(result)
    # print('=======================result2============================')
    # print(result2)

if __name__ == '__main__':
    main()