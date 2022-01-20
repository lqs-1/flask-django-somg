from django.views.generic import View
from django.shortcuts import redirect, render, reverse
from .models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner, GoodsSKU
from apps.order.models import OrderGoods
# from dfresh import settings
from django.core.cache import cache

from django.core.paginator import Paginator


class GetAndSetIndexView(View):
    """商品促销活动先不管"""
    def get(self, request):
        # 获取商品分类
        goods_type_list = GoodsType.objects.all().order_by("logo")[:6]
        # 获取banner轮播
        goods_index_goods_banner = IndexGoodsBanner.objects.all().order_by("index")
        # 获取活动
        active_goods_list = IndexPromotionBanner.objects.all()[:2]


        #  获取分类商品
        for goods_type in goods_type_list:
            image_banners = IndexTypeGoodsBanner.objects.filter(type=goods_type, display_type=1).order_by('index')[:4]
            text_banners = IndexTypeGoodsBanner.objects.filter(type=goods_type, display_type=1).order_by('index')[:4]

        #       动态添加属性
            goods_type.image_banners = image_banners
            goods_type.text_banners = text_banners

        context = {
            "goods_type_list": goods_type_list,
            "goods_index_goods_banner": goods_index_goods_banner,
            "active_goods_list": active_goods_list

        }

        return render(request, 'index.html', context)

class GetGoodsDetailView(View):
    def get(self, request, goods_id):
        goods = GoodsSKU.objects.get(id=goods_id)
        # 展示同类商品
        show_goods_list = GoodsSKU.objects.filter(type=goods.type).order_by("-sales")[:2]
        # 获取评论信息
        comments = OrderGoods.objects.filter(sku=goods.id)

        context = {
            'goods': goods,
            'show_goods_list': show_goods_list,
            'comments': comments
        }
        return render(request, 'detail.html', context)

class GetGoodsListView(View):
    def get(self, request, goods_type_id):
        # print(goods_type_id)
        goods_type = GoodsType.objects.get(id=goods_type_id)
        goods_list = GoodsSKU.objects.filter(type=goods_type)
        goods_list_tj = goods_list[:2]

        paginator = Paginator(goods_list, 2)

        pages = paginator.num_pages


        goods_list = paginator.get_page(2)
        # goods_list.has_previous()

        context = {
            'goods_list': goods_list,
            'goods_list_tj': goods_list_tj,
            'pages': pages,
        }
        # goods_list.has_previous()
        # # 是否有后一页
        # goods_list.has_next()
        # # 是否是当前页
        # goods_list.number()
        # # 便利页码
        # goods_list.paginator.page_range()
        # 获取第n页
        # paginator.get_page(2)

        return render(request, 'list.html', context)# # 是否有前一页
