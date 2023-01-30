# import httpx
import asyncio
from selectolax.parser import HTMLParser
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

if __name__ == '__main__':

    url = 'https://de.indeed.com/jobs?q=Junior+Sales&l=Berlin&start=0'

    ip = '154.12.198.179'
    port = '8800'
    useragent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"

    header = {#"Host": "de.indeed.com",
              "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
              # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
              # "Accept-Language": "en-US,en;q=0.5",
              # "Accept-Encoding": "gzip, deflate, br",
              # "Alt-Used": "de.indeed.com",
              # "Connection": "keep-alive",
              "Cookie": '__cf_bm=RnnLvi6GZeFGdCfLDuPGPvZXaNUrAiYramx.Bd70Z4M-1675112221-0-ASShsXuGJmVJJTL4j+xgHdozQKaKxHlL6JaCaJCdOwYeujUO2e6aTDRUATKyJMttSO/R9owRFRD8yULaOscOgWw=; _cfuvid=wOSj942v1TUrAfl8KS2ZoUK8R6TJ0Z5GhGDl5Y2BoK0-1675110204040-0-604800000; CTK=1go24a40nmjlk800; RF="QXOA6F_NPhPqwOrnO1efjyOe0CXJrE4IgGyhxIXU9NqQsR8bwun4h4WUCXf66hD8AFFrKkP89Do="; CSRF=mxIMRoRM9Ug5MzqBSxq9V6VU1o8KAl8E; SURF=YH99BIa5dLcjgE2GXNDItk6mL9On12Nx; _ga=GA1.2.1505812215.1675108885; _gid=GA1.2.421615850.1675108885; gonetap=closed; g_state={"i_p":1675116087327,"i_l":1}; _gcl_au=1.1.345893952.1675109241; SHARED_INDEED_CSRF_TOKEN=46GDLXfzK02YgoHniK5qBG9db78McrfS; LC="co=ID"; CO=DE; LOCALE=de; MICRO_CONTENT_CSRF_TOKEN=AzjpvrByVmoEFB9l7JJhhGmsfkHWLgKk; PPID=""; _mkto_trk=id:699-SXJ-715&token:_mch-indeed.com-1675110287086-29309; CO=US; LOCALE=en; indeed_rcc="LOCALE:PREF:LV:CTK:CO:UD"; INDEED_CSRF_TOKEN=zBX53OFWYFJbQi6A5FSVAWzRtCk5llR4; LV="LA=1675112369:CV=1675110308:TS=1675110291"; UD="LA=1675112369:CV=1675110308:TS=1675110308:SG=2749b5e7911f94f8d7238b020d444006"; PREF="TM=1675110308079:LD=de:L=Berlin"; LANG=de; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Jan+31+2023+03%3A59%3A34+GMT%2B0700+(Indochina+Time)&version=202210.1.0&isIABGlobal=false&hosts=&consentId=640cd21f-98b8-40a2-b572-38fecf793323&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0%2CC0004%3A0%2CC0007%3A0&AwaitingReconsent=false; JSESSIONID=F3AA139B4DC7DD029535D62EE369EF59; jaSerpCount=13; RQ="q=Junior+Sales&l=Berlin&ts=1675112369962"; ac=/2KKwKDgEe2Q2lkn+ZIULA#/2NOEKDgEe2Q2lkn+ZIULA',
              # "Upgrade-Insecure-Requests": "1",
              # "Sec-Fetch-Dest": "document",
              # "Sec-Fetch-Mode": "navigate",
              # "Sec-Fetch-Site": "none",
              # "Sec-Fetch-User": "?1",
              # "TE": "trailers"
              }

    # with httpx.Client(proxies=proxies, headers=header, default_encoding='utf-8', verify=False) as client:
    #     html = client.get(url)
    # print(html)

    ff_opt = Options()

    # ff_opt.add_argument("--headless")
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
    driver.maximize_window()
    print(driver.current_url)