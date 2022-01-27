from ronglian_sms_sdk import SmsSDK
from ihome.utils import controllerCode

accId = '8a216da87ca23458017cd12b56d008d1'
accToken = 'a4837f29b26d4a9380c516e5e0320e0b'
appId = '8a216da87ca23458017cd12b57ce08d8'

def send_message(mobile, smscode):
    sdk = SmsSDK(accId, accToken, appId)
    tid = '1'
    mobile = mobile
    datas = (smscode, controllerCode.RONG_LIAN_EXPIRED/60)
    sdk.sendMessage(tid, mobile, datas)
