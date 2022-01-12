from django.urls import path
from .views import UserRegisterView, UserActiveView

app_name = 'user'
urlpatterns = [
    path('register', UserRegisterView.as_view(), name='register'),
    path('active/<str:token>', UserActiveView.as_view(), name='active'),
]
