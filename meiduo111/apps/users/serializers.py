from rest_framework import serializers
from django_redis import get_redis_connection
import re
from rest_framework_jwt.settings import api_settings
from .models import User
from celery_tasks.email.tasks import send_verify_mail
from meiduo111.utils import tjws
from . import constants

class UserCreateSerializer(serializers.Serializer):
    # 定义属性
    id=serializers.IntegerField(read_only=True)#不接收客户端的数据，只向客户端输出
    token=serializers.CharField(read_only=True)
    username = serializers.CharField(
        min_length=5,
        max_length=20,
        error_messages={
            'min_length': '用户名包含5-20个字符',
            'max_length': '用户名包含5-20个字符',
        }
    )
    password = serializers.CharField(
        min_length=8,
        max_length=20,
        error_messages={
            'min_length': '密码包含8-20个字符',
            'max_length': '密码包含8-20个字符',
        },
        write_only=True#只接收客户端的数据，不向客户端输出数据
    )
    password2 = serializers.CharField(
        min_length=8,
        max_length=20,
        error_messages={
            'min_length': '密码包含8-20个字符',
            'max_length': '密码包含8-20个字符',
        },
        write_only=True
    )
    sms_code = serializers.IntegerField(write_only=True)
    mobile = serializers.CharField()
    allow = serializers.BooleanField(write_only=True)

    # 验证
    def validate_username(self, value):
        # 验证用户名是否重复
        count = User.objects.filter(username=value).count()
        if count > 0:
            raise serializers.ValidationError('用户名已经存在')
        return value

    def validate_mobile(self, value):
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        # 验证手机号是否重复
        count = User.objects.filter(mobile=value).count()
        if count > 0:
            raise serializers.ValidationError('手机号已经存在')
        return value

    def validate_allow(self, value):
        # 是否同意协议
        if not value:
            raise serializers.ValidationError('请先阅读协议并同意')
        return value

    # 2.多属性判断
    def validate(self, attrs):
        # 判断两个密码是否一致
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError('两个密码不一致')

        # 短信验证码是否正确
        # 1.获取请求报文中的短信验证码、手机号
        sms_code_request = attrs.get('sms_code')
        mobile = attrs.get('mobile')
        # 2.获取redis中的短信验证码
        redis_cli = get_redis_connection('sms_code')
        sms_code_redis = redis_cli.get('sms_code_' + mobile)  # None
        # 3判断是否过期
        if sms_code_redis is None:
            raise serializers.ValidationError('短信验证码已经过期')
        # 4.强制立即过期
        redis_cli.delete('sms_code_' + mobile)
        # 5.判断两个验证码是否相等
        if int(sms_code_request) != int(sms_code_redis):
            raise serializers.ValidationError('短信验证码错误')

        return attrs

    # 保存
    def create(self, validated_data):
        user = User()
        user.username = validated_data.get('username')
        user.set_password(validated_data.get('password'))
        user.mobile = validated_data.get('mobile')
        user.save()

        #需要生成token
        jwt_payload_handler=api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler=api_settings.JWT_ENCODE_HANDLER
        payload=jwt_payload_handler(user)
        token=jwt_encode_handler(payload)#header.payload.signature

        #将token输出到客户端
        user.token=token

        return user

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','mobile','email','email_active']

class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=['email']

#重写修改方法,在修改属性后,需要想邮箱发送邮件
    def update(self, instance, validated_data):
        email=validated_data.get('email')
        instance.email = email
        instance.save()

        url=instance.generate_verify_url()
        #发送激活邮箱:发出邮件即可给出提示,发的过程比较耗时,可以在一个新进程中执行
        send_verify_mail.delay(email,url)


        return instance

class EmailActiveSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=200)

    def validate(self, attrs):
        #获取加密字符中
        token = attrs.get('token')
        #解密
        data_dict = tjws.loads(token,constants.VERIFY_EMAIL_EXPIRES)
        #判断是否过期
        if data_dict is None:
            raise serializers.ValidationError('激活链接过期')
        #将获取到的user_id加入验证后的数据字典中
        attrs['user_id'] = data_dict.get('user_id')

        return attrs