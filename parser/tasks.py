import asyncio
from sellout.arqconfig import redis_settings
from arq import create_pool
from sellout.products.models import Product


async def update_product_info(product_id):
    await asyncio.sleep(5)  # Simulate long-running task
    print(f"Product {product_id} updated.")


async def update_full_info():
    pass