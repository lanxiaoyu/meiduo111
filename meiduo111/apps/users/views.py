from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User


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