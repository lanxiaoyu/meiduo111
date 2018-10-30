from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from rest_framework import generics
from .serializers import UserCreateSerializer, UserDetailSerializer, EmailSerializer,EmailActiveSerializer,AddressSerializer
from rest_framework.permissions import IsAuthenticated
from  rest_framework.viewsets import ModelViewSet

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

class UserCreateView(generics.CreateAPIView):
    """创建用户对象"""
   # queryset = 当前进行创建操作,不需要查询
    serializer_class = UserCreateSerializer


class UserDetailView(generics.RetrieveAPIView):
    serializer_class =UserDetailSerializer

    #要求登录
    permission_classes = [IsAuthenticated]

    # 视图中封装好的代码，是根据主键查询得到的对象
    # 需求：不根据pk查，而是获取登录的用户
    # 解决：重写get_object()方法


    def get_object(self):
        return self.request.user

class EmailView(generics.UpdateAPIView):
    #要求登录,则request.user才有意义
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    #修改当前登录用户的email属性
    def get_object(self):
        return self.request.user

class EmailActiveView(APIView):
    def get(self,request):
        #接收数据并验证
        serializer =EmailActiveSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors)

        #查询当前用户,并修改属性
        user = User.objects.get(pk=serializer.validated_data.get('user_id'))
        user.email_active = True
        user.save()

        #响应
        return Response({'message':'OK'})

class AddressViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer