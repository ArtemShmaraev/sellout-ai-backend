from django.urls import re_path

from .consumers import ProductUpdatePlatformConsumer

websocket_urlpatterns = [
    re_path(r'product/update_platform/(?P<room_name>\w+)/$', ProductUpdatePlatformConsumer.as_asgi()),
]
