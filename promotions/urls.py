from django.urls import path
from .views import PromocodeView


urlpatterns = [path('check/<int:user_id>', PromocodeView.as_view())]