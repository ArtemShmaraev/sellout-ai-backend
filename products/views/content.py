import hashlib
import json
from time import time

from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.main_page import get_header_photo, get_photo_text, get_selection, get_sellout_photo_text
from sellout.settings import CACHE_TIME
from users.models import User
from wishlist.models import Wishlist

from products.models import FooterText
from products.product_page import count_queryset, get_product_page_header
from products.serializers import ProductMainPageSerializer
from products.tools import get_queryset_from_list_id


class MainPageBlocks2GetBlock(APIView):
    def get(self, request, block_id):
        gender = request.query_params.get('gender')
        n = int(request.query_params.get("n"))
        if gender == "F":
            with open("main_women_desktop_2.json", encoding="utf-8") as file:
                json_data = json.load(file)
        else:
            with open("main_men_desktop_2.json", encoding="utf-8") as file:
                json_data = json.load(file)

        filtered_data = []
        for block in json_data:
            if block.get('blockId') == block_id:
                filtered_data = block['products'][n]
                break
        return Response(filtered_data, status=status.HTTP_200_OK)




class MainPageBlocks2(APIView):

    def get(self, request):
        # Шаг 1: Получить cookies из запроса
        cookies = dict(request.COOKIES) # это словарь, где ключ - имя куки, а значение - ее содержимое
        gender = request.query_params.get('gender')


        # Шаг 2: Прочитать JSON из запроса
        # Предположим, что JSON передается в теле запроса, например:
        if gender == "F":
            with open("main_women_desktop_2.json", encoding="utf-8") as file:
                json_data = json.load(file)
        else:
            with open("main_men_desktop_2.json", encoding="utf-8") as file:
                json_data = json.load(file)


        # Шаг 3: Пройтись по элементам JSON и извлечь id
        filtered_data = []
        for block in json_data:
            if block['type'] in ['popularBrands', 'multiSectionCircles', 'multiSectionRecs', 'multiSectionImages']:
                print("len", len(block['products']))
                block_id = block.get("blockId")
                if block_id:
                    # Шаг 4: Получить куку по id блока
                    # print(block_id)
                    cookie_value = cookies.get(f"{block_id}-Ind")

                    # print(cookie_value)

                    if not (cookie_value and cookie_value.isdigit()):
                        cookie_value = 0
                        # Преобразуем куку в индекс (целое число)


                    product_index = int(cookie_value)
                    # print("index", product_index)

                    # Сохраняем только нужный продукт, остальные делаем пустыми
                    filtered_products = [
                        block["products"][i] if i == product_index else []
                        for i in range(len(block["products"]))
                    ]
                    # print(len(block["products"]))

                    # Обновляем блок с фильтрованными продуктами
                    block["products"] = filtered_products
                    # filtered_data.append(block)
            filtered_data.append(block)

        # Шаг 6: Возвращаем отфильтрованный JSON
        # print(filtered_data)
        # file_path="data_men.json"
        # with open(file_path, 'w') as json_file:
        #     # Сохраняем словарь в файл в формате JSON
        #     json.dump(filtered_data, json_file, indent=4)
        return Response(filtered_data, status=status.HTTP_200_OK)


class MainPageBlocks(APIView):

    def get(self, request):
        # number_page = int(request.COOKIES.get('number_main_page', '1'))
        number_page = int(request.query_params.get("page", 1))

        next = request.query_params.get("next", False)
        new = request.query_params.get("new", False)
        selected_gender = request.query_params.get('selected_gender', False)
        # print(self.request.COOKIES)
        # print(number_page)
        context = {"wishlist": Wishlist.objects.get(user=User(id=self.request.user.id)) if request.user.id else None}
        res = []
        # 1 подборка
        # 0 фото
        print(selected_gender)
        gender = ["M", "F"]
        if selected_gender in ['M', 'F', 'K']:
            gender = [selected_gender]

        # gender = ["M", "F"]
        if request.user.id:
            # gender = [request.user.gender.name]
            for page in range(0 if not next else number_page - 1, number_page):
                if page == 0:
                    if "M" in gender:
                        file_path = 'temp_main_men_withproducts.json'

                    else:
                        file_path = 'temp_main_women_withproducts.json'
                    with open(file_path, encoding='utf-8') as file:
                        json_data = json.load(file)[:20]
                        res.extend(json_data)

                    s = []
                elif page == 1:
                    if "M" in gender:
                        file_path = 'temp_main_men_withproducts.json'
                    else:
                        file_path = 'temp_main_women_withproducts.json'
                    with open(file_path, encoding='utf-8') as file:
                        json_data = json.load(file)[20:]
                        res.extend(json_data)
                    s = []


                else:
                    s = [0, 1, 0, 1, 1]
                    # s = [0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0]

                t1 = time()
                last = "any"
                for i in range(len(s)):
                    type = s[i]
                    if type == 0:
                        cache_photo_key = f"main_page:{i}_{page}_{request.user.id if request.user.id else ''}_{''.join(gender)}"  # Уникальный ключ для каждой URL
                        cached_data = cache.get(cache_photo_key)

                        if cached_data is not None and not new:
                            photo, last, list_id = cached_data
                        else:
                            photo, last, list_id = get_photo_text(last, gender)

                            cache.set(cache_photo_key, (photo, last, list_id), CACHE_TIME)

                        queryset = get_queryset_from_list_id(list_id)
                        if queryset.exists():
                            res.append(photo)
                            selection = {"type": "selection_without_title", "title": photo['mobile']['title'],
                                         "url": photo['mobile']['url'],
                                         'products': ProductMainPageSerializer(queryset, many=True, context=context).data}
                            res.append(selection)

                    elif type == 1:
                        cache_sellection_key = f"main_page:{i}_{page}_{request.user.id if request.user.id else None}_{''.join(gender)}"  # Уникальный ключ для каждой URL
                        cached_data = cache.get(cache_sellection_key)

                        if cached_data is not None and not new:
                            list_id, selection = cached_data
                        else:

                            list_id, selection = get_selection(gender)

                            cache.set(cache_sellection_key, (list_id, selection), CACHE_TIME)

                        queryset = get_queryset_from_list_id(list_id)

                        selection['products'] = ProductMainPageSerializer(queryset, many=True, context=context).data

                        res.append(selection)
                    else:
                        cache_photo_key = f"main_page:{i}_{page}_{request.user.id if request.user.id else None}_{''.join(gender)}"  # Уникальный ключ для каждой URL
                        cached_data = cache.get(cache_photo_key)
                        if cached_data is not None and not new:
                            photo, last = cached_data
                        else:

                            photo, last = get_sellout_photo_text(last)
                            cache.set(cache_photo_key, (photo, last), CACHE_TIME)
                        res.append(photo)
            response = Response(res)
            response.set_cookie('number_main_page', str(number_page + 1),
                                max_age=3600)  # Установка нового значения куки (истечет через 1 час)
            # print(len(res))

            return response
        else:
            for page in range(0 if not next else number_page - 1, number_page):
                anon_cache = f"main_page_anon_{page}_{''.join(gender)}"
                cached_data = cache.get(anon_cache)
                if cached_data is not None and not new:
                    res = cached_data
                else:
                    if page == 0:
                        if "M" in gender:
                            file_path = 'temp_main_men_withproducts.json'

                        else:
                            file_path = 'temp_main_women_withproducts.json'
                        with open(file_path, encoding='utf-8') as file:
                            json_data = json.load(file)[:20]
                            res.extend(json_data)
                        s = []
                    elif page == 1:
                        if "M" in gender:
                            file_path = 'temp_main_men_withproducts.json'
                        else:
                            file_path = 'temp_main_women_withproducts.json'
                        with open(file_path, encoding='utf-8') as file:
                            json_data = json.load(file)[20:]
                            res.extend(json_data)
                        s = []



                    else:
                        s = [0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0]
                    t1 = time()
                    last = "any"
                    for i in range(len(s)):
                        type = s[i]
                        if type == 0:
                            photo, last, list_id = get_photo_text(last, gender)
                            queryset = get_queryset_from_list_id(list_id)
                            if queryset.exists():
                                res.append(photo)
                                selection = {"type": "selection", "title": photo['mobile']['title'],
                                             "url": photo['mobile']['url'],
                                             'products': ProductMainPageSerializer(queryset, many=True,
                                                                                   context=context).data}
                                res.append(selection)

                        elif type == 1:

                            list_id, selection = get_selection(gender)
                            queryset = get_queryset_from_list_id(list_id)
                            selection['products'] = ProductMainPageSerializer(queryset, many=True, context=context).data
                            res.append(selection)
                        else:
                            photo, last = get_sellout_photo_text(last)
                            res.append(photo)
                cache.set(anon_cache, res, CACHE_TIME)
            # print(res)
            response = Response(res)
            return response


class GetHeaderPhoto(APIView):

    def get(self, request):
        cache_photo_key = "header_photo"  # Уникальный ключ для каждой URL
        cached_data = cache.get(cache_photo_key)

        if cached_data is not None:
            res = cached_data
        else:
            res = get_header_photo()
            cache.set(cache_photo_key, (res), CACHE_TIME)

        return Response(res)


class ProductHeaderTextView(APIView):
    def get(self, request):
        url = request.build_absolute_uri()

        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_header_key = f"product_header:{url_hash}"  # Уникальный ключ для каждой URL
        cached_header = cache.get(cache_header_key)
        if cached_header is not None:
            photos = cached_header
        else:
            photos = get_product_page_header(request)
            cache.set(cache_header_key, (photos), CACHE_TIME)
        res = {}
        res["mobile"] = photos['mobile']
        res["desktop"] = photos['desktop']

        return Response(res)


class ProductFooterTextView(APIView):
    def get(self, request):
        line = request.query_params.getlist('line')
        category = request.query_params.getlist("category")
        gender = request.query_params.getlist("gender")
        collab = request.query_params.getlist("collab")
        data = {"title": "",
                "description": ""}
        if len(line) == 1:
            if FooterText.objects.filter(lines__full_eng_name=line[0]).exists():
                text = FooterText.objects.get(lines__full_eng_name=line[0])
                data['title'] = text.title
                data['description'] = text.text

        return Response(data)


class ProductsCountView(APIView):
    def get(self, request):
        count = count_queryset(request)
        return Response({"count": count})
