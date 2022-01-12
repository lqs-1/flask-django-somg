from celery import Celery
from django.core.mail import send_mail
from dfresh import settings


app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/0')


@app.task
def send_mail_tasks(username, email, token):
    object = '电商项目测试'  # 主题
    message = ''  # 必填， 没有也要填，不能写html代码，因为不能转意
    from_email = settings.EMAIL_FROM   # 谁发
    recipient_list = [email]   # 发给谁
    html_message = '<h1>好</h1>'  # 写html代码， 可以转意
    send_mail(object=object, message=message, from_email=from_email, recipient_list=recipient_list, html_message=html_message)