import asyncio
import aiohttp
from fake_useragent import UserAgent
import cfscrape
import re
import json
import numpy as np
import aiofiles
from aiocsv import AsyncReader, AsyncDictReader, AsyncWriter, AsyncDictWriter


async def Set_Headers():  # set user agent and headers
    headers = {
        "User-Agent": UserAgent().random,
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }
    return headers


async def parsing(cookies, headers, pages_list):  # start parsing
    try:
        async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:  # set cookie ,headers
            for i in pages_list:
                async with session.get(
                        f'https://www.stadiumgoods.com/en-us/shopping?pageindex={i}') as response:  # parse pages by index
                    regex = re.compile('{([^<]*)window.__BUILD')
                    text = await response.text()

                    match_result = re.findall(regex, text)  # regex for find json in html
                    pagedata = json.loads(match_result[0].replace('window.__BUILD', '').replace(
                        '"entities"', '{"entities"').replace(';', ''))

                for product_id in pagedata['entities']['products']:

                    slug = pagedata['entities']['products'][product_id]['slug']

                    async with session.get(
                            f'https://www.stadiumgoods.com/en-us/shopping/{slug}') as productresponse:  # parse every product

                        async with aiofiles.open(f"text/{slug}.json", mode="w+", encoding="utf-8", newline="") as afp:
                            await afp.write(await productresponse.text())
                            exit(0)

                        regex = re.compile('{([^<]*)window.__BUILD')
                        prod_match_result = re.findall(regex, await productresponse.text())
                        jsonproduct = json.loads(prod_match_result[0].replace(
                            'window.__BUILD', '').replace('"entities"', '{"entities"').replace(';', ''))
                        sku = str(jsonproduct['entities']['products'][product_id]['brandStyleId'])
                        prices = []
                        sizes = []
                        for size in jsonproduct['entities']['products'][product_id][
                            'sizes']:  # desirialiase json and get price , size
                            sizename = size['name']
                            stock = dict(size['stock'][0])
                            price = stock['price']['formatted']['includingTaxes']
                            prices.append(price)
                            sizes.append(sizename)

                        async with aiofiles.open(f"jsons/{slug}.json", mode="w+", encoding="utf-8", newline="") as afp:
                            await afp.write(json.dumps(jsonproduct))
    except Exception as e:
        print(e)


async def checkresponse(cookies, headers):  # func for check cloudflare bypass
    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
        async with session.get(f'https://www.stadiumgoods.com/en-us/shopping?pageindex=1') as response:
            print("Check Status:", response.status)

            return response.status


async def main():
    headers = await Set_Headers()  # set headers
    scraper = cfscrape.create_scraper()

    login = scraper.get("https://www.stadiumgoods.com/en-us/", headers=headers)  # get cloudflare bypass
    print(login)
    print(login.cookies.get_dict())

    cookies = login.cookies.get_dict()

    checkstatus = await checkresponse(cookies, headers)
    max_retries = 20
    retries = 0
    while checkstatus == 403 and retries < max_retries:
        headers = await Set_Headers()
        login = scraper.get(
            "https://www.stadiumgoods.com/en-us/", headers=headers)  # if not bypass try more
        cookies = login.cookies.get_dict()
        checkstatus = await checkresponse(cookies, headers)

    pages = [i for i in range(1, 150)]  # parse form 1 page to 148 need to change if pages more then 148
    pages_lists = np.array_split(pages,
                                 20)  # arrays split on 20 arrays => create 20 tasks (maybe you need to put a little
    # less for improve perfomance )
    print(pages_lists)
    print(cookies)
    tasks = []
    for i in pages_lists:
        task = asyncio.create_task(parsing(cookies, headers, i))  # crete task for every array
        tasks.append(task)
    await asyncio.gather(*tasks)  # info from tasks , for debugging if something wrong


loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())  # create main loop for parsing
