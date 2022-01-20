from django.urls import path
from .views import GetGoodsPayView


app_name = 'order'
urlpatterns = [
    path('pay', GetGoodsPayView.as_view(), name='pay'),
]