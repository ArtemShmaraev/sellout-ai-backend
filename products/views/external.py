from datetime import datetime
import json
import math
import os

import boto3
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import (
    DewuInfo,
    RansomRequest,
    SGInfo,
)
from products.serializers import (
    DewuInfoSerializer,
    SGInfoSerializer,
)


class DewuInfoCount(APIView):
    def get(self, request):
        count = DewuInfo.objects.values_list("id", flat=True).count()
        return Response({"count": count, "page": math.ceil(count / 30)})


class DewuInfoListSpuIdView(APIView):
    def get(self, request):
        dewu_infos = DewuInfo.objects.values_list('spu_id', flat=True)
        return Response(dewu_infos, status=status.HTTP_200_OK)


# Create your views here.
class DewuInfoListView(APIView):
    def get(self, request):
        web_data = request.query_params.get("web_data")
        if web_data is not None:
            # Параметр был передан, теперь вы можете проверить его значение
            web_data = web_data.lower() == 'true'

            if not web_data:
                dewu_infos = DewuInfo.objects.filter(web_data={})
            else:
                dewu_infos = DewuInfo.objects.all()
        else:
            dewu_infos = DewuInfo.objects.all().order_by('spu_id')
        # count = dewu_infos.count()
        count = 1
        page_number = request.query_params.get("page")
        page_number = int(page_number if page_number else 1)
        start_index = (page_number - 1) * 30
        queryset = dewu_infos[start_index:start_index + 30]
        serializer = DewuInfoSerializer(queryset, many=True)
        res = {'count': count, "results": serializer.data}  # Замените на вашу сериализацию
        return Response(res, status=status.HTTP_200_OK)


class DewuInfoView(APIView):
    def get(self, request, spu_id):
        dewu_info = DewuInfo.objects.filter(spu_id=spu_id)
        # print(dewu_info.web_data['size_table'])
        serializer = DewuInfoSerializer(dewu_info, many=True)
        # Замените на вашу сериализацию
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, spu_id):
        data = json.loads(request.body)
        if DewuInfo.objects.filter(spu_id=spu_id).exists():
            dewu_info = DewuInfo.objects.get(spu_id=spu_id)
        else:
            dewu_info = DewuInfo(spu_id=spu_id)

        if "api_data" in data:
            dewu_info.api_data = data['api_data']
        if "preprocessed_data" in data:
            dewu_info.preprocessed_data = data['preprocessed_data']
        if "web_data" in data:
            dewu_info.web_data = data['web_data']
        # if "processed_data" in data:
        #     dewu_info.processed_data = data["processed_data"]
        if "formatted_manufacturer_sku" in data:
            dewu_info.formatted_manufacturer_sku = data["formatted_manufacturer_sku"]
        dewu_info.save()
        return Response(DewuInfoSerializer(dewu_info).data)

    def delete(self, request, spu_id):
        try:
            dewu_info = DewuInfo.objects.filter(spu_id=spu_id)
            dewu_info.delete()

            return Response("Удален", status=status.HTTP_200_OK)
        except DewuInfo.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class SGInfoListSkuView(APIView):
    def get(self, request):
        sg_infos = SGInfo.objects.values_list('manufacturer_sku', flat=True)
        return Response(sg_infos, status=status.HTTP_200_OK)


# Create your views here.
class SGInfoListView(APIView):
    def get(self, request):
        sg_infos = SGInfo.objects.all()
        # count = dewu_infos.count()
        count = 1
        page_number = request.query_params.get("page")
        page_number = int(page_number if page_number else 1)
        start_index = (page_number - 1) * 100
        queryset = sg_infos[start_index:start_index + 100]
        serializer = SGInfoSerializer(queryset, many=True)
        res = {'count': count, "results": serializer.data}  # Замените на вашу сериализацию
        return Response(res, status=status.HTTP_200_OK)


class SGInfoView(APIView):
    def get(self, request, sku):
        sg_info = SGInfo.objects.filter(manufacturer_sku=sku)
        serializer = SGInfoSerializer(sg_info, many=True)
        # Замените на вашу сериализацию
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, sku):
        data = json.loads(request.body)
        if SGInfo.objects.filter(manufacturer_sku=sku).exists():
            sg_info = SGInfo.objects.get(manufacturer_sku=sku)
        else:
            sg_info = SGInfo(manufacturer_sku=sku)
        if "data" in data:
            sg_info.data = data['data']
        if "formatted_manufacturer_sku" in data:
            sg_info.formatted_manufacturer_sku = data["formatted_manufacturer_sku"]
        if "relevant_number" in data:
            sg_info.relevant_number = int(data['relevant_number'])
        if "novelty_number" in data:
            sg_info.novelty_number = int(data["novelty_number"])
        # sg_info.save()
        return Response(SGInfoSerializer(sg_info).data)

    def delete(self, request, sku):
        try:
            sg_info = SGInfo.objects.filter(manufacturer_sku=sku)
            sg_info.delete()

            return Response("Удален", status=status.HTTP_200_OK)
        except DewuInfo.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class MakeRansomRequest(APIView):
    def post(self, request):
        data = request.data
        name = data.get('name', "")
        tg_name = data.get('tg_name', "")
        phone_number = data.get('phone_number', "")
        email = data.get('email', "")
        url = data.get('url', "")
        info = data.get('info', "")

        file_obj = data['file']

        file_path = 'ransom_photos'  # указываем путь к папке на сервере

        if not os.path.exists(file_path):  # проверяем, существует ли папка
            os.makedirs(file_path)  # если не существует, создаем ее

        file_name = file_obj.name + datetime.now().strftime('%Y%m%d%H%M%S')  # получаем имя файла
        full_file_path = os.path.join(file_path, file_name)  # создаем полный путь к файлу

        with open(full_file_path, 'wb+') as destination:  # открываем файл для записи
            for chunk in file_obj.chunks():  # записываем содержимое файла
                destination.write(chunk)


        access_id = 'YCAJE0F2sIDFNPfcTqknCFtoY'
        access_key = 'YCNRvyqXPhlTbZ8vdAhDA6wAhxZCZ8KlRKjTPIDV'
        bucket_name = 'sellout-photos'  # Укажите название бакета
        s3_client = boto3.client(
            service_name='s3',
            endpoint_url='https://sellout.su',
            aws_access_key_id=access_id,
            aws_secret_access_key=access_key
        )


        full_cloud_path = os.path.join("ransom_photo", file_name)
        path = full_cloud_path.replace("\\", "/")

        if file_path.endswith(".png"):
            content_type = "image/png"
        else:
            content_type = "image/jpeg"

        s3_client.upload_file(
            full_file_path,
            bucket_name,
            path,
            ExtraArgs={'ContentType': content_type}
        )
        url_photo = f'https://sellout.su/sellout-photos/{path}'


        ransom_request = RansomRequest.objects.create(
            name=name,
            tg_name=tg_name,
            phone_number=phone_number,
            email=email,
            url=url,
            photo=url_photo,
            info=info
        )


        return Response(url_photo)
