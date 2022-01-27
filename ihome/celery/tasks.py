from celery import Celery
from ihome.libs import send_sms


app = Celery('ihome', broker='redis://127.0.0.1:6379/3')

@app.task
def send_sms_code(mobile, sms_code):
    send_sms.send_message(mobile, sms_code)