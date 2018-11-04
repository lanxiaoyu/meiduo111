from rest_framework.views import APIView
from rest_framework.response import Response
from . import serializers
from meiduo111.utils import myjson
from goods.models import SKU


class CartView(APIView):
    def perform_authentication(self, request):
        # 在执行视图函数前，不进行身份检查
        pass

    def post(self, request):
        # 判断用户是否登录
        try:
            # 如果用户认证信息不存在则抛异常
            user = request.user
        except:
            user = None

        # 接收请求数据，进行验证
        serializer = serializers.CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 验证通过后获取数据
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']

        # 构造响应对象
        response = Response(serializer.validated_data)

        if user is None:
            # 如果未登录，则存入cookie
            # 读取cookies中的数据
            cart_str = request.COOKIES.get('cart')
            if cart_str is None:
                cart_dict = {}
            else:
                cart_dict = myjson.loads(cart_str)
            # 取出原数量
            if sku_id in cart_dict:
                count_cart = cart_dict[sku_id]['count']
            else:
                count_cart = 0
            # 修改数据
            cart_dict[sku_id] = {
                'count': count + count_cart,
                'selected': True
            }
            # 写cookie
            cart_str = myjson.dumps(cart_dict)
            response.set_cookie('cart', cart_str, max_age=60 * 60 * 24 * 14)
        else:
            # 如果已登录，则存入redis
            pass

        return response

    def get(self, request):
        try:
            user = request.user
        except:
            user = None

        if user is None:
            # 未登录，读cookie
            # 获取cookie中购物车信息
            cart_str = request.COOKIES.get('cart')
            cart_dict = myjson.loads(cart_str)
            # 根据商品编号查询对象，并添加数量、选中属性
            skus = []
            for key, value in cart_dict.items():
                sku = SKU.objects.get(pk=key)
                sku.count = value['count']
                sku.selected = value['selected']
                skus.append(sku)
            # 序列化输出
            serializer = serializers.CartSerializer(skus, many=True)
            return Response(serializer.data)
        else:
            # 已登录，读redis
            pass