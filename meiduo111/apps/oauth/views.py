from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .qq_sdk import OAuthQQ


class QQurlView(APIView):
    def get(self,request):
        #接收登录后的地址
        state = request.query_params.get('next')
        #创建工具类对象
        oauthqq= OAuthQQ(state = state)
        #获取授权地址
        url=oauthqq.get_qq_login_url()
        #响应
        return Response({
            'login_url':url
        })

class QQLoginView(APIView):
    def get(self,request):
        #获取code
        code=request.query_params.get('get')

        #根据code获取token
        oauthqq = OAuthQQ()
        token = oauthqq.get_access_token(code)

        #根据token获取openid
        openid = oauthqq.get_openid(token)

        #查询openid是否存在,如果存在则状态保持,登录成功
        #如果不存在,则通知客户端转到绑定页面
        pass