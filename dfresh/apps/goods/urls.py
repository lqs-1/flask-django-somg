from django.urls import path
from .views import GetAndSetIndexView

app_name = 'goods'
urlpatterns = [
    path('', GetAndSetIndexView.as_view(), name='index')
]