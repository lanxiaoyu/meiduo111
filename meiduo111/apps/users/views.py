from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from rest_framework.generics import CreateAPIView
from .serializers import UserCreateSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.backends import ModelBackend
from rest_framework_jwt.utils import jwt_response_payload_handler


class UsernameCountView(APIView):
    def get(self,request,username):
        """查询用户名个数"""
        count = User.objects.filter(username=username).count()

        #响应
        return Response({
            'username':username,
            'count':count

        })


class MobileCountView(APIView):
    def get(self,request,mobile):
        """查询手机个数"""
        count = User.objects.filter(mobile=mobile).count()

        #响应
        return Response({
            'mobile':mobile,
            'count':count
        })

class UserCreateView(CreateAPIView):
    """创建用户对象"""
   # queryset = 当前进行创建操作,不需要查询
    serializer_class = UserCreateSerializer