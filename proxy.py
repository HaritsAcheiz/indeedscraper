import httpx
import asyncio
from selectolax.parser import HTMLParser

def get_proxy():
    print("Collecting proxies...")
    with httpx.Client() as s:
        response = s.get('https://free-proxy-list.net/')
    s.close()
    soup = HTMLParser(response.content)
    list_data = soup.css('table.table.table-striped.table-bordered > tbody > tr')
    scraped_proxies = []
    blocked_cc = ['IR', 'RU']
    for i in list_data:
        ip = i.css_first('tr > td:nth-child(1)').text()
        port = i.css_first('tr > td:nth-child(2)').text()
        cc = i.css_first('tr > td:nth-child(3)').text()
        if cc in blocked_cc:
            continue
        else:
            scraped_proxies.append(f'{ip}:{port}')
    print(f"{len(scraped_proxies)} proxies collected")
    return scraped_proxies

def choose_proxy(scraped_proxies):
    working_proxies = []
    for i, item in enumerate(scraped_proxies):
        if i < len(scraped_proxies) and len(working_proxies) < 5:
            formated_proxy = {
                "http://": f"http://{item}",
                "https://": f"http://{item}"
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            }
            print(f'checking {formated_proxy}')
            try:
                with httpx.Client(proxies=formated_proxy, headers=headers, timeout=(3,27)) as session:
                    response = session.get(url='https://www.google.com')
                if response.status_code == 200:
                    working_proxies.append(item)
                    print(f'{item} selected')
                else:
                    print(f"not working with status code: {response.status_code}")
                response.close()
            except Exception as e:
                print(f"not working with {e}")
                pass
        else:
            break
    return working_proxies

async def fetch(url):
    async with httpx.AsyncClient(timeout=None) as client:
        return await client.get(url)

async def main(urls):

    responses = await asyncio.gather(*map(fetch, urls))
    htmls = [response.text for response in responses]
    return htmls

def parsing(html):
    tree = HTMLParser.css_first()

if __name__ == '__main__':
    # scraped_proxies = get_proxy()
    # proxies = choose_proxy(scraped_proxies)
    # print(proxies)

    scraped_proxies = ['117.251.103.186:8080', '8.219.97.248:80', '15.207.146.140:3128', '13.126.231.63:3128', '135.181.14.45:5959']
    #
    formated_proxy = {"http://": f"http://{scraped_proxies[3]}",
                      "https://": f"http://{scraped_proxies[3]}"}
    urls = ['https://de.indeed.com/cmp/Hotel-Mssngr?campaignid=mobvjcmp&from=mobviewjob&tk=1gof8d8ekje0t800&fromjk=b047ef9a275f692a','https://de.indeed.com/cmp/Sonnen?campaignid=mobvjcmp&from=mobviewjob&tk=1gou6joj1jqvi802&fromjk=e846fde655293c2e']
    # # url2 = 'https://www.google.com'
    # with httpx.Client(proxies=formated_proxy) as client:
    #     response = client.get(url)
    # print(response)
    # print(response.text)

    result = asyncio.run(main(urls))
    print(result)