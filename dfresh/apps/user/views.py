import json
from django.shortcuts import render, redirect, HttpResponse, reverse
from django.http import JsonResponse
from django.views.generic import View
from django.db import transaction
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import User
from .models import User
import logging
import re
from utils import statusCode
from itsdangerous import TimedJSONWebSignatureSerializer as Ter
from dfresh import settings
from celery_tasks import tasks
# Create your views here.


logger = logging.getLogger('lqs')

class UserRegisterView(View):

    def get(self, request):
        return render(request=request, template_name='register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        cpassword = request.POST.get('cpwd')
        email = request.POST.get('email')
        # print(username, password, cpassword, email,allow)

        if not all([username, password, cpassword, email]):
            return render(request=request, template_name='register.html', context={'errno': statusCode.INCOMPLETE_DATA, 'errmsg': '数据不完整'})

        if cpassword != password:
            return render(request=request, template_name='register.html', context={'errno': statusCode.DATA_ERROR, 'errmsg': '两次密码不一致'})

        if not re.match(r'^\w+@\w+\.[a-z]+', email):
            return render(request=request, template_name='register.html', context={'errno': statusCode.EMAIL_ERROR, 'errmsg': '邮箱格式错误'})

        try:
            user = User.objects.get(username=username)
        except Exception as e:
            logger.error(e)
            user = None

        if user:
            return render(request=request, template_name='register.html', context={'errno': statusCode.USER_EXIST, 'errmsg': '用户已存在'})

        user = User.objects.create_user(username=username, password=password, email=email)
        user.is_active = 0
        user.save()

        # 生成加密信息
        ter = Ter(settings.SECRET_KEY, 300)
        token = ter.dumps({'user_id': user.id})
        token = token.decode('utf-8')
        # 发邮件
        tasks.send_mail_tasks.delay(username=username, email=email, token=token)

        return redirect(reverse('goods:index'))

class UserActiveView(View):
    '''激活用户'''
    def get(self, request, token):
        ter = Ter(settings.SECRET_KEY, 300)
        try:
            with transaction.atomic():
                info = ter.loads(token)
                user_id = info.get('user_id')

                user = User.objects.get(id=user_id)
                user.is_active = 1
                user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'errno': statusCode.ACTIVE_EXPIRED, 'errmsg': '激活链接过期'})

        return JsonResponse({'errno': statusCode.OK, 'errmsg': '激活成功可以登录了'})


class UserGetActiveLink(View):
    def post(self, request):
        get_json_data = json.loads(request.body)

        username = get_json_data.get('user_name')
        email = get_json_data.get('email')

        if not all([username, email]):
            return JsonResponse({'errno': statusCode.INCOMPLETE_DATA, 'errmsg': '数据不完整'})

        if not re.match(r'^\w+@\w+\.[a-z]+', email):
            return JsonResponse({'errno': statusCode.EMAIL_ERROR, 'errmsg': '邮箱格式错误'})

        try:
            user = User.objects.get(username=username, email=email)
        except Exception as e:
            logger.error(e)
            user = None

        if user is None:
            return JsonResponse({'errno': statusCode.NON_USER, 'errmsg': '没有此用户，快去注册吧'})

        ter = Ter(settings.SECRET_KEY, 300)
        token = ter.dumps({'user_id': user.id})
        token = token.decode('utf-8')

        tasks.send_mail_tasks.delay(username=username, email=email, token=token)
        return JsonResponse({'errno': statusCode.OK, 'errmsg': '已发送激活链接请及时激活'})


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

        content = {
            'username': username,
            'password': password,
            'checked': checked
        }
        return JsonResponse(content)


    def post(self, request):
        get_json_data = json.loads(request.body)
        username = get_json_data.get('user_name')
        password = get_json_data.get('pwd')

        remenber = get_json_data.get('remember')

        if not all([username, password]):
            return JsonResponse({'errno': statusCode.INCOMPLETE_DATA, 'errmsg': '数据不完整'})

        # 验证用户
        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({'errno': statusCode.NON_USER, 'errmsg': '用户不存在，请先注册'})

        if user.is_active != 1:
            return JsonResponse({'errno': statusCode.NO_ACTIVE, 'errmsg': '用户未激活，请先激活'})

        login(user)
        response = JsonResponse({'errno': statusCode.OK, 'errmsg': '登录成功'})
        if remenber == 'on':
            response.set_cookie('username', username, max_age=7*24*60*60)
            response.set_cookie('password', password, max_age=7*24*60*60)
        return response


