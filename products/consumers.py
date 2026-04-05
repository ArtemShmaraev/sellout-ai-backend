import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ProductUpdatePlatformConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.product_id = self.scope['url_route']['kwargs']['product_id']
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Обработка сообщения и обновление цены продукта
        # Пример: Обновление цены продукта
        # product = Product.objects.get(pk=self.product_id)
        # product.price = новая_цена
        # product.save()

        await self.send(text_data=json.dumps({
            'message': f"Price for product {self.product_id} updated to."
        }))