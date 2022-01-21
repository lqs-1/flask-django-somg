from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from utils.loginCheck import LoginRequiredMixin
from utils import alipay, statusCode
from .models import OrderGoods, OrderInfo
from apps.user.models import Address

# 电脑网站支付
alipay.gen_alipay_client().api_alipay_trade_page_pay(
    out_trade_no=1,  # 订单编号
    total_amount=3,  # 总金额
    subject='fsdf',  # 订单主题
    return_url='http',  # 支付成功跳转页面
    notify_url=None,  # 回调地址
)


class GetGoodsPayView(LoginRequiredMixin, View):
    def get(self, request):

        goods_name = request.GET.get('goods_name')
        goods_count = request.GET.get('goods_count')
        goods_totail = request.GET.get('goods_totail')
        print(goods_totail, goods_name, goods_count)



        return render(request, 'place_order.html', {'errno': statusCode.OK, 'errmsg': 'ok'})

