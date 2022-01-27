from flask import Blueprint

# 创建蓝图对象
api = Blueprint('api_1', __name__)
# 验证码模块
from .checkUser import *