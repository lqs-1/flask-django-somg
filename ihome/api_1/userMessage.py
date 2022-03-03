from . import api
from flask import request, g, jsonify
from ihome.utils import fdfs_storage, statusCode
from ihome.utils import login_check
from ihome.models import User
from ihome import db
from config import fdfs_config


@api.route('/avatar', methods=['POST'])
@login_check.login_required
def user_avatar():
    user_id = g.user_id
    avatar = request.files.get('avatar')
    file_id = fdfs_storage.save(avatar.read())

    user = User.query.get(user_id)
    user.avatar_url = file_id

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(errno=statusCode.MYSQL_CONNECTION_ERROR, errmsg='数据库链接错误')

    return jsonify(errno=statusCode.OK, errmsg='上传头像成功')


@api.route('/name', methods=['POST'])
@login_check.login_required
def user_name():
    user_id = g.user_id
    name = request.form.get('name')

    try:
        User.query.filter_by(id=user_id).update({"name": name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(errno=statusCode.MYSQL_CONNECTION_ERROR, errmsg='数据库链接错误')

    return jsonify(errno=statusCode.OK, errmsg='用户名修改成功')


@api.route('/user', methods=['GET'])
@login_check.login_required
def get_avatar():
    user_id = g.user_id
    user = User.query.get(user_id)
    if user is None:
        return jsonify(errno=statusCode.DATA_UN_EXISTS, errmsg='数据不存在')

    avatar = user.avatar_url
    avatar = fdfs_config.BASE_URL + avatar
    return  jsonify(errno=statusCode.OK, errmsg='头像获取成功', data={'avatar': avatar, 'name': user.name, 'mobile': user.mobile})

