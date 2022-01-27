from flask import Flask
from config import config_mapper
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session  # 可以通过这个拓展自定义session存储
from flask_wtf import CSRFProtect  # 添加csrf防护
import logging
from logging.handlers import RotatingFileHandler
from .utils.self_converter import ReConverter
import time

# 数据库对象
db = SQLAlchemy()
# 创建redis链接对象
redis_store = None

# 配置日志信息
# 设置日志记录等级
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# 配置日志记录器,指明日志保存的路径,每个日志文件的最大大小,保存的日志文件的个数上限
file_log_handler = RotatingFileHandler(f"logs/error_{time.strftime('%Y-%m-%d')}.log", maxBytes=1024*1024*100, backupCount=10)
# 配置写入等级
file_log_handler.setLevel(logging.WARNING)
# 创建日志记录格式
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
logger.addHandler(file_log_handler)


# 工厂模式
def create_app(config_name):
    app = Flask(__name__)
    # 添加配置
    config_class = config_mapper.get(config_name)
    app.config.from_object(config_class)
    # 初始化数据库
    db.init_app(app)
    # 初始化redis
    global redis_store
    redis_store = StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)
    # 利用flask-session，将session数据保存到redis中
    Session(app)
    # 为flask填充csrf防护
    CSRFProtect(app)
    # 注册转换器
    app.url_map.converters['re'] = ReConverter
    # 注册蓝图
    from .api_1 import api
    app.register_blueprint(api, url_prefix='/api_1')
    from .webhtml import webhtml
    app.register_blueprint(webhtml)
    return app
