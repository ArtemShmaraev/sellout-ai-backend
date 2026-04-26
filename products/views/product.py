import hashlib
import json
import os
import subprocess
import threading
from time import time
from urllib.parse import parse_qs, urlparse

from django.contrib.sitemaps import views as sitemaps_views
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Gender, HeaderPhoto, Product
from products.product_page import count_queryset, get_product_page
from products.product_site_map import ProductSitemap
from products.search_tools import similar_product
from products.serializers import (
    ProductAdminSerializer,
    ProductMainPageSerializer,
    ProductSerializer,
    ProductSlugAndPhotoSerializer,
)
from products.tools import get_fid_product, get_queryset_from_list_id
from sellout.settings import CACHE_TIME, HOST, RPS, TIME_RPS
from users.models import User
from wishlist.models import Wishlist


def run_command_async(request):
    def run_command(command):
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        print(result)

    if request.method == 'GET':
        command = request.GET.get('command', '')
        threading.Thread(target=run_command, args=(command,)).start()
        return JsonResponse({'message': 'Command is running in the background.'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def sitemap_view(request):
    sitemaps = {
        'products': ProductSitemap,
    }
    response = sitemaps_views.sitemap(request, sitemaps)
    return render(request, 'sitemap.xml', {'urls': response.content})


def view_photo_for_rate(request):
    photo_id = int(request.GET.get('id', 1))
    t = 1
    next_param = request.GET.get('next', False)
    if next_param:
        t = 1
    last_id = 17290
    first_id = 15434
    print(123121)
    photo = HeaderPhoto.objects.filter(id=photo_id, where="product_page", rating=5).exists()
    while not photo:
        photo_id += t
        if photo_id <= first_id:
            photo = HeaderPhoto.objects.filter(id=first_id, where="product_page", rating=5).exists()
            photo_id = first_id
        elif photo_id >= last_id:
            photo = HeaderPhoto.objects.filter(id=last_id, where="product_page", rating=5).exists()
            photo_id = last_id
        else:
            photo = HeaderPhoto.objects.filter(id=photo_id, where="product_page", rating=5).exists()
        print(photo, photo_id)
    photo = HeaderPhoto.objects.get(id=photo_id)
    return render(request, 'view_photo.html', {'photo': photo, "next_photo": photo.id + 1, "last_photo": photo.id - 1})


def rate_photo(request):
    if request.method == 'POST':
        photo_id = int(request.POST['photo_id'])
        photo = HeaderPhoto.objects.get(id=photo_id)
        rating = request.POST['gender']
        if rating == "М" or rating == "У":
            photo.genders.add(Gender.objects.get(name="M"))
        if rating == "Ж" or rating == "У":
            photo.genders.add(Gender.objects.get(name="F"))
        photo.save()
        if HOST == "sellout.su":
            return redirect(f"https://{HOST}/api/v1/product/pict?id={photo_id + 1}")
        return redirect(f"https://{HOST}/api/v1/product/pict?id={photo_id + 1}")


class ProductSkuView(APIView):
    def get(self, request, sku):
        try:
            params = request.query_params
            if params.get("formatted"):
                product = Product.objects.filter(formatted_manufacturer_sku=sku).values_list("id", flat=True)
            else:
                product = Product.objects.filter(manufacturer_sku=sku).values_list("id", flat=True)
            if not product:
                return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(product, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductSpuIdView(APIView):
    def get(self, request, spu_id):
        product = Product.objects.filter(spu_id=spu_id).first()
        return Response(ProductAdminSerializer(product).data)


class ProductsFid(APIView):
    def get(self, request, page):
        params = request.query_params
        filename = params.get("file_name", False)
        if filename:
            filename = f"fids/{filename}.xml"
            with open(filename, 'rb') as f:
                response = HttpResponse(f, content_type='application/xml')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

        size_page = int(params.get("size_page", 1000))

        url = request.build_absolute_uri()
        parsed_url = urlparse(url)

        file_name = f"fids/{size_page}"

        query_params = parse_qs(parsed_url.query)
        if query_params:
            params_str = '_'.join([f'{key}{value}' for key, value in query_params.items()])
            file_name = f'{file_name}_{params_str}'
        file_name = f"{file_name}.xml"
        print(file_name)
        if not os.path.exists(file_name):
            params = request.query_params
            queryset = Product.objects.all()
            price_max = params.get('price_max')
            price_min = params.get('price_min')
            line = params.getlist('line')
            color = params.getlist('color')
            is_sale = params.get("is_sale")
            category = params.getlist("category")
            material = params.getlist("material")
            gender = params.getlist("gender")
            brand = params.getlist("brand")
            collab = params.getlist("collab")
            collection = params.getlist('collection')

            queryset = queryset.filter(available_flag=True)

            if is_sale:
                queryset = queryset.filter(is_sale=True)
            if collab:
                if "all" in collab:
                    queryset = queryset.filter(is_collab=True)
                else:
                    queryset = queryset.filter(collab__query_name__in=collab)
            if material:
                queryset = queryset.filter(materials__eng_name__in=material)
            if collection:
                queryset = queryset.filter(collections__query_name__in=collection)
            if brand:
                for brand_name in brand:
                    queryset = queryset.filter(brands__query_name=brand_name)
            if line:
                queryset = queryset.filter(lines__full_eng_name__in=line)
            if color:
                queryset = queryset.filter(colors__name__in=color)
            if category:
                queryset = queryset.filter(categories__eng_name__in=category)
            if price_min:
                queryset = queryset.filter(min_price__gte=price_min)
            if price_max:
                queryset = queryset.filter(min_price__lte=price_max)

            products_page = queryset[(page - 1) * size_page:page * size_page]
            print(products_page.count())
            fid = get_fid_product(products_page)
            print("aaa")
            with open(file_name, 'wb') as f:
                f.write(fid)

        with open(file_name, 'rb') as f:
            response = HttpResponse(f, content_type='application/xml')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response


class SlugForSpuId(APIView):
    def get(self, request, spu_id):
        try:
            products = list(map(
                lambda x: f"https://sellout.su/products/{x}",
                Product.objects.filter(spu_id=spu_id).values_list("slug", flat=True)
            ))
            return Response(products)
        except ObjectDoesNotExist:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductSlugAndPhoto(APIView):
    def get(self, request):
        params = request.query_params
        queryset = Product.objects.all()
        page_number = int(params.get("page", 1))
        categories = params.getlist("category", "")
        lines = params.getlist("line", "")

        if categories:
            queryset = queryset.filter(categories__eng_name__in=categories)
        if lines:
            queryset = queryset.filter(lines__full_eng_name__in=lines)

        res = {}

        queryset = queryset.values_list("id", flat=True)
        cache_count_key = f"productcount_{request.build_absolute_uri()}"
        cached_count = cache.get(cache_count_key)
        if cached_count is not None:
            count = cached_count
        else:
            count = queryset.count()
            cache.set(cache_count_key, count, CACHE_TIME)

        res['count'] = count

        start_index = (page_number - 1) * 100
        queryset = queryset[start_index:start_index + 100]
        queryset = get_queryset_from_list_id(list(queryset.values_list("id", flat=True)))
        queryset = ProductSlugAndPhotoSerializer(queryset, many=True).data
        res['results'] = queryset
        return Response(res)


class ProductSimilarView(APIView):
    def get(self, request, product_id):
        context = {"wishlist": Wishlist.objects.get(user=User(id=self.request.user.id)) if request.user.id else None}
        res = []
        try:
            product = Product.objects.get(id=product_id)
            if Product.objects.filter(spu_id=product.spu_id).exists():
                another_configuration = Product.objects.filter(
                    spu_id=product.spu_id, available_flag=True
                ).exclude(id=product.id).order_by("min_price")
                if another_configuration.count() > 0:
                    name = "Другие конфигурации" if not product.has_many_colors else "Другие цвета"
                    res.append({"name": name,
                                "products": ProductMainPageSerializer(another_configuration, many=True,
                                                                      context=context).data})
            similar = similar_product(product)
            print(similar)
            if similar[1]:
                if similar[0].exists():
                    res.append({"name": "Похожие товары",
                                "products": ProductMainPageSerializer(similar[0], many=True, context=context).data})
            return Response(res)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductsCountView(APIView):
    def get(self, request):
        count = count_queryset(request)
        return Response({"count": count})


class ProductView(APIView):
    def get(self, request):
        t0 = time()

        # Загружаем wishlist_ids один раз — множество ID, без N+1 в сериализаторе
        wishlist_ids = set()
        user_status = None
        if request.user.id:
            try:
                wl = Wishlist.objects.get(user=User(id=request.user.id))
                wishlist_ids = set(wl.products.values_list("id", flat=True))
            except Wishlist.DoesNotExist:
                pass
            user_status = request.user.user_status

        size = self.request.query_params.getlist('size')
        if size:
            size = list(map(lambda x: x.split("_")[1], size))
        price_max = self.request.query_params.get('price_max')
        price_min = self.request.query_params.get('price_min')
        ordering = self.request.query_params.get('ordering')
        adminka = self.request.query_params.get('adminka')

        context = {
            "wishlist": None,
            "wishlist_ids": wishlist_ids,
            "user_status": user_status,
            "size": size if size else None,
            "price_max": price_max if price_max else None,
            "price_min": price_min if price_min else None,
            "ordering": ordering if ordering else None,
        }

        url = request.build_absolute_uri()
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_product_key = f"product_page:{url_hash}_{f'{request.user.id}_{request.user.user_status.id}' if request.user.id else 0}"
        cached_data = cache.get(cache_product_key)
        if cached_data is None:
            queryset, res = get_product_page(request, context)
            t_new = time()
            if adminka:
                queryset = ProductAdminSerializer(queryset, many=True, context=context).data
            else:
                queryset = ProductMainPageSerializer(queryset, many=True, context=context).data
            cache.set(cache_product_key, (queryset, res), CACHE_TIME)
            t_old = time()
            print(f"no cache: {t_old - t_new}")
        else:
            t_new = time()
            queryset, res = cached_data
            t_old = time()
            print(f"cache: {t_old - t_new}")

        # Обновляем in_wishlist без мутации кэшированного объекта
        if request.user.id:
            queryset = [{**p, "in_wishlist": p["id"] in wishlist_ids} for p in queryset]

        serializer = queryset
        res["results"] = serializer
        t10 = time()
        res['time'] = t10 - t0
        return Response(res)


class ProductFullSlugView(APIView):
    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            serializer = ProductAdminSerializer(product, context={
                "list_lines": True,
                "wishlist": Wishlist.objects.get(user=User(id=request.user.id)) if request.user.id else None,
            })
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductSlugView(APIView):
    def get(self, request, slug):
        try:
            t1 = time()
            data_ip = self.request.query_params.get('ip')
            is_update = self.request.query_params.get('is_update')
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            print("мой ip", ip, data_ip, request.build_absolute_uri())

            cache_key = f'request_count_{ip}'
            request_count = cache.get(cache_key, 0)
            is_valid = True
            if request_count > RPS:
                is_valid = False
            is_valid = True

            if is_valid:
                product = Product.objects.get(slug=slug)
            else:
                product = Product.objects.first()

            if product.is_custom:
                return Response("Товар не найден")

            if not is_update:
                request_count += 1
                cache.set(cache_key, request_count, timeout=TIME_RPS)
                print(f"request_count {request_count}")
                print("Пошла")
                product.rel_num += 1
                product.save()

            serializer = ProductSerializer(product, context={
                "list_lines": True,
                "wishlist": Wishlist.objects.get(user=User(id=request.user.id)) if request.user.id else None,
            })
            t3 = time()
            data = serializer.data
            print(is_valid, "ну вот сука", self.request.query_params.get('captcha'))
            data['is_valid_captcha_token'] = is_valid
            data['ip'] = ip
            data['request'] = {'count': request_count, "RPS": RPS}
            return Response(data)
        except Product.DoesNotExist:
            return Response("Товар не найден")


class ProductIdView(APIView):
    def get(self, request, id):
        try:
            product = Product.objects.get(id=id)
            serializer = ProductSerializer(product, context={
                "list_lines": True,
                "wishlist": Wishlist.objects.get(
                    user=User(id=self.request.user.id) if request.user.id else None),
            })
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductUpdateView(APIView):
    def delete(self, request, product_id):
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response("Товар успешно удален")

    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)
        data = json.loads(request.body)
        if 'categories' in data:
            categories = data.get('categories', [])
            product.categories.clear()
            product.categories.add(*categories)
        if 'lines' in data:
            lines = data.get('lines', [])
            product.lines.clear()
            product.lines.add(*lines)
        if 'colors' in data:
            colors = data.get('colors', [])
            product.lines.add(*colors)
        if 'brands' in data:
            brands = data.get('brands', [])
            product.brands.clear()
            product.brands.add(*brands)
        if 'tags' in data:
            tags = data.get('tags', [])
            product.tags.clear()
            product.tags.add(*tags)
        if 'model' in data:
            product.model = data.get('model', product.model)
        if 'colorway' in data:
            product.colorway = data.get('colorway', product.colorway)
        if 'russian_name' in data:
            product.russian_name = data.get('russian_name', product.russian_name)
        if 'manufacturer_sku' in data:
            product.manufacturer_sku = data.get('manufacturer_sku', product.manufacturer_sku)
        if 'description' in data:
            product.description = data.get('description', product.description)
        if 'bucket_link' in data:
            product.bucket_link = data.get('bucket_link', product.bucket_link)
        if 'main_color' in data:
            product.main_color_id = data.get('main_color', product.main_color_id)
        product.slug = ""
        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)


class ListProductView(APIView):
    def post(self, request):
        try:
            t = time()
            s_products = json.loads(request.body)["products"]
            product_list_string = json.dumps(s_products, sort_keys=True)
            product_list_hash = hashlib.sha256(product_list_string.encode('utf-8')).hexdigest()

            cache_product_key = f"product_list_{product_list_hash}"
            cached_data = cache.get(cache_product_key)

            if cached_data is not None:
                products = cached_data
            else:
                products = Product.objects.filter(id__in=s_products).order_by(
                    models.Case(*[models.When(id=id, then=index) for index, id in enumerate(s_products)])
                )
                cache.set(cache_product_key, products, CACHE_TIME)

            print("лист ", time() - t)

            return Response(ProductMainPageSerializer(products, many=True, context={
                "wishlist": Wishlist.objects.get(user=User(id=self.request.user.id)) if request.user.id else None,
            }).data)
        except json.JSONDecodeError:
            return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response("One or more product do not exist", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
