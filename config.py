from redis import StrictRedis


class Confitg(object):
    '''配置'''
    DEBUG = True
    SECRET_KEY = 'frergtery34ergsetrg'

    # 数据库
    SQLALCHEMY_DATABASE_URI = 'pymysql+mysql://lqs@lqs:127.0.0.1:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # 事务，开启可以手动提交和回滚

    # redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 配置session存储到redis中(flask-session配置)
    SESSION_TYPE = 'redis'  # 指定session使用redis存储
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)   # 指定session存储使用的redis的数据库
    SESSION_USE_SIGNER = True  # 对session中的id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 3600*24  # session数据的有效期



class Product(Confitg):
    '''配置'''
    DEBUG = False
    SECRET_KEY = 'frergtery34ergsetrg'

    # 数据库
    SQLALCHEMY_DATABASE_URI = 'pymysql+mysql://lqs@lqs:127.0.0.1:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # 事务，开启可以手动提交和回滚

    # redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 配置session存储到redis中(flask-session配置)
    SESSION_TYPE = 'redis'  # 指定session使用redis存储
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)   # 指定session存储使用的redis的数据库
    SESSION_USE_SIGNER = True  # 对session中的id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 3600*24  # session数据的有效期


class Development(Confitg):
    '''配置'''
    DEBUG = True
    SECRET_KEY = 'frergtery34ergsetrg'

    # 数据库
    SQLALCHEMY_DATABASE_URI = 'pymysql+mysql://lqs@lqs:127.0.0.1:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # 事务，开启可以手动提交和回滚

    # redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 配置session存储到redis中(flask-session配置)
    SESSION_TYPE = 'redis'  # 指定session使用redis存储
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)   # 指定session存储使用的redis的数据库
    SESSION_USE_SIGNER = True  # 对session中的id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 3600*24  # session数据的有效期


config_mapper = {
    'product': Product,
    'development': Development,
}
