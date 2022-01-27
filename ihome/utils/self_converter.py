from werkzeug.routing import BaseConverter

# 自定义万能转换器
class ReConverter(BaseConverter):
    def __init__(self, url_map, regex):
        # 调用父类
        super().__init__(url_map)
        #  保存正则表达式
        self.regex = regex