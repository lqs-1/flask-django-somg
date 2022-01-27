from . import api
from flask import request, make_response, current_app, jsonify, session
from ihome.utils.captcha import captcha
from ihome import redis_store
from ihome.utils import controllerCode
from ihome.utils import statusCode
from ihome import models
import random
from ihome.celery import tasks
from ihome import db

# 获取图像验证码
@api.route('/image_code/<code_id>', methods=['GET'])
def get_picture_code(code_id):
    # 生成图形验证码
    name, code, image_code = captcha.captcha.generate_captcha()
    # 验证码放入缓存
    try:
        redis_store.setex(f'image_code_{code_id}', controllerCode.REDIS_IMAGE_CODE_EXPIRED, code)
    except Exception as e:
        current_app.logger.error('图像验证码报保存失败')
        return jsonify(errno=statusCode.IMAGE_CODE_SAVE_REDIS_FAIL, errmsg='图形验证码保存失败')
    resp = make_response(image_code)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


# 获取手机验证码
@api.route("/sms_code/<re(r'1[356789]\d{9}'):mobile>", methods=['GET'])
def get_sms_code(mobile):
    image_code = request.args.get('code')
    image_code_id = request.args.get('codeId')

    if not all([image_code_id, image_code]):
        return jsonify(errno=statusCode.INCOMPLETE_DATA, errmsg='数据不完整')

    try:
        real_image_code = redis_store.get(f'image_code_{image_code_id}')
        redis_store.delete(f'image_code_{image_code_id}')
        real_image_code = str(real_image_code, encoding='utf-8')
    except Exception as e:
        current_app.logger.error(f'{e}, {image_code_id}验证码过期')
        return jsonify(errno=statusCode.IMAGE_CODE_SAVE_REDIS_FAIL, errmsg='图形验证码过期')

    if image_code.lower() != real_image_code.lower():
        return jsonify(errno=statusCode.IMAGE_CODE_ERROR, errmsg='图形验证码错误')

    # 判断手机号是否存在了
    try:
        user = models.User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(f'{e},数据库链接错误')
        return jsonify(errno=statusCode.MYSQL_CONNECTION_ERROR, errmsg='数据库链接错误')
    else:
        if user is not None:
            return jsonify(errno=statusCode.DATA_EXISTS, errmsg='用户已存在')

    # 检测是否在60秒内获取过验证码
    try:
        sms_smark = redis_store.get(f'sms_code_{mobile}')
    except Exception as e:
        current_app.logger.error(f'e, redis链接错误')
        return jsonify(errno=statusCode.REDIS_CONNECTION_ERROR, errmsg='redis链接错误')
    else:
        if sms_smark is not None:
            return jsonify(errno=statusCode.DATA_ERROR, errmsg='数据错误，60秒只能发送一次')

    # 发送验证码
    # 组织验证码
    sms_code = random.randint(100000, 999999)
    tasks.send_sms_code.delay(mobile, sms_code)
    # 保存验证码
    try:
        redis_store.setex(f'sms_code_{mobile}', controllerCode.REDIS_SMS_CODE_EXPIRED, sms_code)
    except Exception as e:
        current_app.logger.error(f'{e}, redis链接错误')
        return jsonify(errno=statusCode.REDIS_CONNECTION_ERROR, errmsg='redis链接错误')

    return jsonify(errno=statusCode.OK, errmsg='短信验证码发送成功')


@api.route('/register', methods=['POST'])
def register():
    json_data = request.get_json()
    mobile = json_data.get('mobile')
    sms_code = json_data.get('sms_code')
    pwd = json_data.get('pwd')
    cpwd = json_data.get('cpwd')

    if not all([mobile, sms_code, pwd, cpwd]):
        return jsonify(errno=statusCode.INCOMPLETE_DATA, errmsg='数据不完整')

    if pwd != cpwd:
        return jsonify(errno=statusCode.DATA_ERROR, errmsg='两次密码不一致')

    # 比对验证码
    try:
        real_sms_code = redis_store.get(f'sms_code_{mobile}')
        redis_store.delete(f'sms_code_{mobile}')
        real_sms_code = str(real_sms_code, encoding='utf-8')
    except Exception as e:
        current_app.logger.error(f'{e}, redis链接错误')
        return jsonify(errno=statusCode.REDIS_CONNECTION_ERROR, errmsg='redis链接错误')

    if real_sms_code != sms_code:
        return jsonify(errno=statusCode.DATA_ERROR, errmsg='短信验证码错误')

    # 保存信息
    user = models.User(name=mobile, mobile=mobile)
    user.password = pwd
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f'{e}, 数据库连接错误')
        return jsonify(errno=statusCode.MYSQL_CONNECTION_ERROR, errmsg='数据库链接错误')

    return jsonify(errno=statusCode.OK, errmsg='注册成功')


@api.route('/login', methods=['GET'])
def login():
    mobile = request.args.get('mobile')
    pwd = request.args.get('pwd')

    if not all([mobile, pwd]):
        return jsonify(errno=statusCode.INCOMPLETE_DATA, errmsg='数据不完整')

    # 验证用户
    # 是否错误登录过多
    user_ip = request.remote_addr
    try:
        login_count = redis_store.get(f'login_count_{user_ip}')
    except Exception as e:
        current_app.logger.error(f'{e}, redis连接错误')
        return jsonify(errno=statusCode.REDIS_CONNECTION_ERROR, errmsg="redis链接错误")
    else:
        if login_count is not None and int(login_count) > controllerCode.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=statusCode.LOGIN_MAX_TIMES_ERROR, errmsg="登录受限稍后重试")

    try:
        redis_store.incr(f'login_count_{user_ip}')
        redis_store.expire(f'login_count_{user_ip}', controllerCode.LOGIN_OUT_TIME_ALLOW_TIME)
    except Exception as e:
        current_app.logger.error(f'{e}, redis连接错误')
        return jsonify(errno=statusCode.REDIS_CONNECTION_ERROR, errmsg="redis链接错误")

    user = models.User.query.filter_by(mobile=mobile).first()
    if user is None:
        return jsonify(errno=statusCode.DATA_ERROR, errmsg="登录信息错误，没有此用户")

    if not user.check_password(pwd):
        return jsonify(errno=statusCode.DATA_ERROR, errmsg="密码错误")

    session['user_id'] = user.id
    return jsonify(errno=statusCode.OK, errmsg='登录成功')


@api.route('/session', methods=['GET'])
def login_check():
    user_id = session.get('user_id')

    if user_id is None:
        return jsonify(errno=statusCode.SESSION_ERROR, errmsg="false")
    else:
        user = models.User.query.get(user_id)
        return jsonify(errno=statusCode.OK, errmsg="true", data={"name": user.name})


@api.route('/session', methods=['DELETE'])
def logout():
    session.clear()
    return jsonify(errno=statusCode.OK, errmsg="true")






