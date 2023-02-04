import httpx
import asyncio
from selectolax import parser

def get_proxy():
    print("Collecting proxies...")
    with httpx.Client() as s:
        response = s.get('https://free-proxy-list.net/')
    s.close()
    soup = parser.HTMLParser(response.content)
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
                with httpx.Client(proxies=formated_proxy, headers=headers, timeout=(7,10)) as session:
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

if __name__ == '__main__':
    # asyncio.run(main(urls))
    # scraped_proxies = get_proxy()
    # proxies = choose_proxy(scraped_proxies)
    # print(proxies)

    scraped_proxies = ['35.154.32.37:3128', '51.79.50.31:9300', '115.96.208.124:8080', '151.80.95.161:8080',
                       '51.159.115.233:3128']

    formated_proxy = {"http://": f"http://{scraped_proxies[0]}",
                      "https://": f"http://{scraped_proxies[0]}"}
    url = 'https://de.indeed.com/cmp/Hotel-Mssngr?campaignid=mobvjcmp&from=mobviewjob&tk=1gof8d8ekje0t800&fromjk=b047ef9a275f692a'
    with httpx.Client(proxies=formated_proxy) as client:
        response = client.get(url)
    print(response)
    print(response.text)