import json
import subprocess
import threading
from collections import OrderedDict
from datetime import datetime, timedelta

from django.db import transaction
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import (
    Photo, Product, Tag,
)


class UpdateProductTagsView(APIView):
    def post(self, request, slug):
        """
        Обновление тегов продукта.
        Добавляет новые теги из списка или удаляет все теги, если указан флаг `delete`.
        """
        try:
            product_id = int(slug.split("-")[-1])
            # Получаем продукт по ID
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # Получаем данные из запроса
        data = request.data
        delete = data.get('delete', False)  # Флаг удаления тегов (по умолчанию False)
        tags = data.get('tags', [])  # Список новых тегов для добавления

        if delete:
            # Если установлен флаг `delete`, очищаем все теги
            # product.tags.clear()
            return Response({"message": "Tags cleared successfully."}, status=status.HTTP_200_OK)

        if tags:
            # Добавляем теги из списка
            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name)  # Создаем тег, если его нет
                # product.tags.add(tag)

            return Response({"message": "Tags updated successfully."}, status=status.HTTP_200_OK)

        # Если запрос некорректный
        return Response({"error": "Invalid request. Provide 'tags' or 'delete'."}, status=status.HTTP_400_BAD_REQUEST)


class ProductUpdatePerHour(APIView):
    def get(self, request, hour):
        twelve_hours_ago = datetime.now() - timedelta(hours=hour)
        products_added = Product.objects.filter(last_upd__gt=twelve_hours_ago).count()
        return Response(f"Количество товаров, добавленных за последние {hour} часов: {products_added}")


class MyScoreForProduct(APIView):
    def get(self, request, id):
        try:
            product = Product.objects.get(id=id)
            my_score = product.extra_score
            print(my_score)
            return Response({"my_score": my_score})
        except Product.DoesNotExist:
            return Response({"error": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, id):
        try:
            product = Product.objects.get(id=id)
            data = json.loads(request.body)
            my_score = data['my_score']
            last = product.extra_score
            product.extra_score = my_score
            product.score_product_page += round((my_score - last) * 0.1)
            product.save()

            return Response({"my_score": my_score})
        except Product.DoesNotExist:
            return Response({"error": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HideProductView(APIView):
    def get(self, request, spu_id, property_id):
        product = Product.objects.filter(spu_id=spu_id, property_id=property_id)
        product.update(available_flag=False)
        return Response("Готово")


class HideProductSpiIdView(APIView):
    def get(self, request, spu_id, ):
        product = Product.objects.filter(spu_id=spu_id)
        product.update(available_flag=False)
        return Response("Готово")


class PopularSpuIdView(APIView):
    def get(self, request):
        count = int(request.query_params.get('count', 5000))
        popular_product = list(
            Product.objects.filter(available_flag=True, is_custom=False).values_list("spu_id", flat=True).order_by(
                "-rel_num"))[:count]

        other = list(
            Product.objects.filter(available_flag=False).values_list("spu_id", flat=True).order_by("-rel_num"))[:10000]

        def remove_duplicates(lst):
            return list(OrderedDict.fromkeys(lst))

        popular_product = remove_duplicates(popular_product)
        return Response(popular_product)


class UpdatePrice(APIView):
    def get(self, request):
        page = int(request.query_params.get('page', 1))

        def update_prices(products, start, end):
            for product_id in products[start:end]:
                product = Product.objects.get(id=product_id)
                with transaction.atomic():
                    # product.update_price()
                    pass

        # Получите все продукты, которые вы хотите обновить
        products = Product.objects.filter(available_flag=True).filter(actual_price=False).values_list("id", flat=True)
        part = page
        num_part = products.count() // 4
        products = products[num_part * (part - 1):num_part * part]
        # products = products[105000:210000]
        # products = products[210000:315000]
        # products = products[315000:429000]

        # Укажите количество потоков
        num_threads = 8

        # Разделите список продуктов на равные части для каждого потока
        batch_size = len(products) // num_threads

        # Создайте потоки и запустите их
        threads = []
        for i in range(num_threads):
            start = i * batch_size
            end = start + batch_size if i < num_threads - 1 else len(products)
            thread = threading.Thread(target=update_prices, args=(products, start, end))
            thread.start()
            threads.append(thread)

        # Дождитесь завершения всех потоков
        for thread in threads:
            thread.join()

        return Response("Цены успешно обновлены.")


class PhotoWhiteList(APIView):
    def get(self, request, product_id):
        product = Product.objects.get(id=product_id)
        for photo in product.black_bucket_link.all():
            product.bucket_link.add(photo)
        product.black_bucket_link.clear()
        product.save()
        return Response("Готово")


class AddPhotoBlackList(APIView):
    def get(self, request, product_id, photo_id):
        try:
            product = Product.objects.get(id=product_id)
            photo = Photo.objects.get(id=photo_id)
        except Product.DoesNotExist:
            return Response("Продукт не найден", status=status.HTTP_404_NOT_FOUND)
        except Photo.DoesNotExist:
            return Response("Фото не найдено", status=status.HTTP_404_NOT_FOUND)

        try:
            # Удаляем фото из bucket_link и добавляем в black_bucket_link
            product.bucket_link.remove(photo)
            product.black_bucket_link.add(photo)
            product.save()
            if not product.bucket_link.exists():
                product.available_flag = False
                product.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response("Готово")


class NewSale(APIView):
    def post(self, request):
        data = json.loads(request.body)
        slug = data['slug'].replace("https://sellout.su/products/", "")
        product = Product.objects.get(slug=slug)
        # product.add_sale(data['sale_absolute'], data['sale_percentage'])
        return Response("Готово")


class DelSale(APIView):
    def post(self, request):
        data = json.loads(request.body)
        slug = data['slug'].replace("https://sellout.su/products/", "")
        product = Product.objects.get(slug=slug)
        # product.del_sale()
        return Response("Готово")


class ProductUpdatePriceUrlDewu(APIView):
    def get(self, request):
        import requests
        from urllib.parse import parse_qs, urlparse
        params = request.query_params
        url = params.get("url", False)
        response = requests.head(url, allow_redirects=False)
        if 'location' in response.headers:
            redirect_url = response.headers['location']
            parsed_url = urlparse(redirect_url)

            if 'spuId' in parse_qs(parsed_url.query):
                spu_id = int(parse_qs(parsed_url.query)['spuId'][0])
            else:
                return None
        else:
            return None
        print(spu_id)
        data = requests.get(f"https://sellout.su/sellout-ai-parser-manager/get_data?spu_id={spu_id}").json()
        # s = add_product_hk(data)
        # return Response(s.slug)


class ProductUpdatePricePS(APIView):
    def post(self, request):
        data = json.loads(request.body)
        # add_product_ps_api(data)
        return Response("Ok")


class ProductUpdatePriceHK(APIView):
    def post(self, request):
        data = json.loads(request.body)
        # p = add_product_hk(data)
        # if p.slug:
        #     return Response(f"https://sellout.su/products/{p.slug}")
        # else:
        #     print(p, '1')
        #     return Response(f"Ошибка")
        return Response("Ok")


class AddProductView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        # product = add_product_api(data)
        # return Response(ProductSerializer(product).data)
        return Response("Ok")


class AddListProductsView(APIView):  # список товаров одного spu_id
    def post(self, request):
        data = json.loads(request.body)
        # add_products_spu_id_api(data)
        return Response("Готово")


def run_command_async(request):
    def run_command(command):
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        # здесь вы можете обработать результат, сохранить его или передать куда-то еще
        print(result)
    if request.method == 'GET':
        command = request.GET.get('command', '')
        # Запускаем команду в отдельном потоке
        threading.Thread(target=run_command, args=(command,)).start()
        # Немедленный ответ клиенту
        return JsonResponse({'message': 'Command is running in the background.'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
# class RunCommand(APIView):
#     def get(self, request):
#         params = request.query_params
#         pwd = params.get("pwd", "")
#
#         if pwd == "1qw2":
#             command = params.get('command', '')
#             loop = asyncio.get_event_loop()
#
#             # Запуск команды асинхронно
#             result = await loop.run_in_executor(None, lambda: subprocess.check_output(command, shell=True,
#                                                                                       stderr=subprocess.STDOUT,
#                                                                                       text=True))
#
#             # subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, start_new_session=True)
#             return Response({'message': 'Команда успешно запущена в фоновом режиме'})
#
#         return Response({'error': 'Ошибка'})
