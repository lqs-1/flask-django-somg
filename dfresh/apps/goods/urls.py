from django.urls import path
from .views import GetIndexView

app_name = 'goods'
urlpatterns = [
    path('', GetIndexView.as_view(), name="index")
]