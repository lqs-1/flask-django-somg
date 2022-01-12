import json

from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.generic import View
from django.db import transaction
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from .models import User
import logging
import re
from utils import statusCode
from itsdangerous import TimedJSONWebSignatureSerializer as Ter
from dfresh import settings
from celery_tasks import tasks
# Create your views here.


logger = logging.getLogger()

class UserRegisterView(View):
    def post(self, request):
        get_json_data = json.loads(request.body)
        username = get_json_data.get('user_name')
        password = get_json_data.get('pwd')
        cpassword = get_json_data.get('cpwd')
        email = get_json_data.get('email')
        allow = get_json_data.get('allow')
        print(username, password, cpassword, email,allow)

        if not all([username, password, cpassword, email]):
            return JsonResponse({'errno': statusCode.INCOMPLETE_DATA, 'errmsg': '数据不完整'})

        if allow != 'on':
            return JsonResponse({'errno': statusCode.ALLOW_STATUS, 'errmsg': '请勾选协议'})

        if cpassword != password:
            return JsonResponse({'errno': statusCode.DATA_ERROR, 'errmsg': '两次密码不一致'})

        if not re.match(r'^\w+@\w+\.[a-z]+', email):
            return JsonResponse({'errno': statusCode.EMAIL_ERROR, 'errmsg': '邮箱格式错误'})

        try:
            user = User.objects.filter(username=username)
        except Exception as e:
            logger.error(e)
            # user = None

        if user:
            return JsonResponse({'errno': statusCode.USER_EXIST, 'errmsg': '用户已存在'})

        user = User.objects.create_user(username=username, password=password, email=email)
        user.is_active = 0
        user.save()

        # 生成加密信息
        ter = Ter(settings.SECRET_KEY, 300)
        token = ter.dumps({'user_id': user.id})
        token = token.decode('utf-8')

        # 发邮件
        # tasks.send_mail_tasks.delay(username=username, email=email, token=token)
        object = '电商项目测试'  # 主题
        message = ''  # 必填， 没有也要填，不能写html代码，因为不能转意
        from_email = settings.EMAIL_HOST_USER  # 谁发
        recipient_list = [email]  # 发给谁
        html_message = '<h1>好</h1>'  # 写html代码， 可以转意
        send_mail(object, message, from_email, recipient_list,html_message=html_message)
        return JsonResponse({'errmsg': '6666'})
