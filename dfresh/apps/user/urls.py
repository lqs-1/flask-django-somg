from django.urls import path
from .views import UserRegisterView, UserActiveView, UserActiveGetView, UserLoginView, UserLogoutView, UserCenterView, UserOrderView, UserAddressView, UserAlterPwdView
app_name = 'user'
urlpatterns = [
    path('register', UserRegisterView.as_view(), name='register'),
    path('active/<str:token>', UserActiveView.as_view(), name='active'),
    path('reactive', UserActiveGetView.as_view(), name='reactive'),
    path('login', UserLoginView.as_view(), name='login'),
    path('logout', UserLogoutView. as_view(), name='logout'),

    path('user', UserCenterView.as_view(), name='user'),
    path('order', UserOrderView.as_view(), name='order'),
    path('address', UserAddressView.as_view(), name='address'),

    # path('getalter', GetUserAlterPwdView.as_view(), name='pwd'),
    # path('alterpwd/<str:mig_id>', UserAlterPwdView.as_view(), name='alterpwd'),
    path('alterpwd', UserAlterPwdView.as_view(), name='alterpwd'),

    # path('imgcode/<str:img_id>', GetImageCodeApi.as_view(), name='getcode')
]

