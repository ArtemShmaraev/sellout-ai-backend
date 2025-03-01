from celery import shared_task
import aiohttp
import asyncio


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


@shared_task
def my_async_task(url):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    session = aiohttp.ClientSession()
    try:
        result = loop.run_until_complete(fetch(session, url))
    finally:
        loop.run_until_complete(session.close())
        loop.close()
    return result
