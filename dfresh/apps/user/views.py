from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views.generic import View
from utils import statusCode
import re
import logging
from itsdangerous import TimedJSONWebSignatureSerializer
from dfresh import settings
from celery_tasks import tasks
from django.db import transaction
from django.contrib.auth import authenticate, login, logout, get_user_model
from .models import Address
# from utils.captcha import captcha

from django.core.cache import cache

logger = logging.getLogger('django')


class UserRegisterView(View):
    def get(self, request):
        cache.set('hell', 12)
        return render(request, 'register.html')

    def post(self, request):

        User = get_user_model()

        username = request.POST.get('username')
        password = request.POST.get('pwd')
        cpassword = request.POST.get('cpwd')
        email = request.POST.get('email')

        if not all([username, password, cpassword, email]):
            return render(request, 'register.html', {'errno': statusCode.INCOMPLETE_DATA, 'errmsg': '数据不完整'})

        if password != cpassword:
            return render(request, 'register.html', {'errno': statusCode.DATA_ERROR, 'errmsg': '两次密码一致'})

        if re.match(r'\d+@\d+\.\d+', email):
            return render(request, 'register.html', {'errno': statusCode.EMAIL_ERROR, 'errmsg': '邮箱格式不正确'})

        try:
            user = User.objects.get(username=username, password=password)
        except Exception as e:
            logger.error(e)
            user = None

        if user:
            return render(request, 'register.html', {'errno': statusCode.USER_EXIST, 'errmsg': '用户已经存在'})

        try:
            with transaction.atomic():
                user = User.objects.create_user(username=username, password=password, email=email)
                user.is_active = 0
                user.save()
        except Exception as e:
            logger.error(f'{e},{user.username}在存库的时候链接出错')

        ter = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
        token = ter.dumps({'user_id': user.id}).decode('utf-8')

        tasks.send_mail_tasks.delay(username=username, email=email, token=token)

        return redirect('goods:index')


class UserActiveView(View):
    def get(self, request, token):

        User = get_user_model()

        ter = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
        try:
            info = ter.loads(token)
            user_id = info.get('user_id')
            with transaction.atomic():
                user = User.objects.get(id=user_id)
                user.is_active = 1
                user.save()
        except Exception as e:
            logger.error(f'{e}, 激活链接过期')

        return redirect('user:login')

class UserActiveGetView(View):
    def get(self, request):
        return render(request, 'reactive.html')

    def post(self, request):

        User = get_user_model()

        username = request.POST.get('username')

        if not username:
            return render(request, 'reactive.html', {'errno': statusCode.INCOMPLETE_DATA, 'errmsg': '数据不完整'})

        try:
            user = User.objects.get(username=username)
        except Exception as e:
            logger.error(f'{e}, {username}不存在')
            user = None

        if user is None:
            return render(request, 'reactive.html', {'errno': statusCode.NON_USER, 'errmsg': '数据错误'})
        try:
            user = User.objects.get(username=username)
            ter = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
            token = ter.dumps({'user_id': user.id}).decode('utf-8')

            tasks.send_mail_tasks.delay(username=username, email=user.email, token=token)
        except Exception as e:
            logger.error(f'{e}')

        return redirect('user:login')


class UserLoginView(View):
    def get(self, request):
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            password = request.COOKIES.get('password')
            checked = 'checked'
        else:
            username = ''
            password = ''
            checked = ''
        context = {
            'username': username,
            'password': password,
            'checked': checked
        }
        return render(request, 'login.html', context)

    def post(self, request):

        User = get_user_model()

        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remember = request.POST.get('remember')

        if not all([username]):
            return render(request, 'login.html', {'errno': statusCode.INCOMPLETE_DATA, 'errmsg': '数据不完整'})

        try:
            user = User.objects.get(username=username)
        except Exception as e:
            logger.error(e)

        if user.is_active == 0:
            return redirect('user:reactive')

        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'errno': statusCode.NON_USER, 'errmsg': '用户不存在, 或者未激活'})

        login(request, user)
        response = redirect('goods:index')
        if remember == 'on':
            response.set_cookie('username', username, max_age=7*24*3600)
            response.set_cookie('password', password, max_age=7*24*3600)
        else:
            response.set_cookie('username')
            response.set_cookie('password')
        return response


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('goods:index')


class UserAlterPwdView(View):

    def get(self, request):
        return render(request, 'alterpwd.html')

    def post(self, request):

        User = get_user_model()
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not all([username, password]):
            return render(request, 'alterpwd.html', {'errno': statusCode.INCOMPLETE_DATA, 'errmsg': '数据不完整'})

        try:
            with transaction.atomic():
                user = User.objects.get(username=username)
                user.password = password
                user.save()
        except Exception as e:
            logger.error(f'{e}, 修改失败')
            return render(request, 'alterpwd.html', {'errno': statusCode.NON_USER, 'errmsg': '没有此用户，修改失败'})
        return redirect('user:login')


# class GetImageCodeApi(View):
#     def get(self, request, img_id):
#         username = request.GET.get('username')
#         name, text, imgcode = captcha.captcha.generate_captcha()
#         try:
#             cache.setex(f'img_code_{img_id}', text, 120)
#         except Exception as e:
#             logger.error(f'{e}, redis链接错误')
#         resp = HttpResponse(imgcode)
#         resp.headers["Content-Type"] = "image/jpg"
#         return resp






class UserCenterView(View):
    def get(self, request):
        user = request.user
        address = Address.objects.get_default_address(user)
        if address is None:
            try:
                address = user.address_set.all()[0]
            except Exception as e:
                logger.error(f'{e}, {user.username}没有地址信息')
                address = None
        return render(request, 'user_center_info.html', {'active': 'user', 'address': address})




class UserCartView(View):
    def get(self, request):
        return render(request, 'cart.html')

class UserOrderView(View):
    def get(self, request):
        return render(request, 'user_center_order.html', {'active': 'order'})

class UserAddressView(View):
    def get(self, request):
        return render(request, 'user_center_site.html', {'active': 'address'})

