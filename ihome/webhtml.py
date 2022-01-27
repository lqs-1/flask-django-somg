from flask import Blueprint
from flask import make_response, current_app
from flask_wtf import csrf

webhtml = Blueprint('webhtml', __name__)


'''
前后端分离的时候，静态资源需要跑一个服务器环境，所有就在项目中直接跑出来，通过找静态文件的方式
    make_response,current_app.send_static_file(xxx)
添加csrf口令
    flask-wtf模块中，csrf.generate_csrf()可以自动生成
'''

@webhtml.route("/<re(r'.*'):html_page_name>")
def get_html_page(html_page_name):
    # '''提供html代码'''
    # # 如果html_file_name 表示访问的路径是/,请求的是主页
    # if not html_page_name:
    #     html_page_name = "index.html"
    #
    # # 如果资源名不是favicon.ico
    # if html_page_name != "favicon.ico":
    #     html_page_name = "html/" + html_page_name
    #
    # # 创建一个csrf_token值,这个方法自动生成值
    # csrf_token = csrf.generate_csrf()
    #
    # # flask提供的返回静态文件的方法app.send_static_file()可以找到对应的静态文件,make_response()可以生成响应体
    # resp = make_response(current_app.send_static_file(html_page_name))
    #
    # # 设置cookie
    # resp.set_cookie("csrf_token", csrf_token)
    # return resp

    # 判断是否有页面的传入
    if not html_page_name:
        html_page_name = 'index.html'
    if html_page_name != 'favicon.ico':
        # 文件static下面中直接有的可以直接找到，如果没有就拼接字符串
        html_page_name = 'html/' + html_page_name

    # 添加csrf，自动产生，也可以自定义
    csrf_token = csrf.generate_csrf()
    # 全局上下文中有个寻找静态文件的方法send_static_file找静态文件
    resp = make_response(current_app.send_static_file(html_page_name))
    # 存入cookie，每次请求都会带上
    resp.set_cookie("csrf_token", csrf_token)
    return resp