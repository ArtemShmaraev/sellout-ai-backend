from django.urls import path
from .views import PromocodeView, PromocodeAnonView


urlpatterns = [path('check/<int:user_id>', PromocodeView.as_view()),
               path('anon_check', PromocodeAnonView.as_view())]