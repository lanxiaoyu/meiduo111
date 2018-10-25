import re
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.serializers import jwt_encode_handler
from rest_framework_jwt.settings import api_settings
from .models import User


class UserCreateSerializer(serializers.Serializer):
        #定义属性
    """
    1.创建用户不需要接收id,也不需要验证--read_only
    2.username:输入 输出 也不要写
    3.password:只输入 write_only
    4.password2:只输入 write_only
    5.allow:只输入 write_only
    6.mobile:输入 输出  不需要写
    7.sms_code: 只输入write_only
    8.token:注册的时候不需要传入,需要输出,read_only
    """
    id = serializers.IntegerField(read_only=True)
    token = serializers.CharField(read_only=True)
    username = serializers.CharField(
        min_length=5,
        max_length=20,
        error_messages={
            "min_length": "用户名包含5-20个字符",
            "max_length": "用户名包含5-20个字符",

        }
    )

    password = serializers.CharField(
        max_length=20,
        min_length=8,
        error_messages={
    "min_length": "用户名包含8-20个字符",
    "max_length": "用户名包含8-20个字符",
        },
        write_only=True

    )

    password2 = serializers.CharField(
        max_length=20,
        min_length=8,
        error_messages={
    "min_length": "用户名包含8-20个字符",
    "max_length": "用户名包含8-20个字符",
        },
        write_only=True

    )

    sms_code = serializers.IntegerField(write_only=True)
    mobile = serializers.CharField()
    allow = serializers.BooleanField(write_only=True)

    #验证
    #1.验证用户名是否重复
    def validata_username(self,value):
        count = User.objects.filter(username=value).count()
        if count >0:
            raise serializers.ValidationError("此用户名已存在")
        return value

    #2.验证两个密码一样
    #3.短信验证码是否正确
    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password != password2:
            raise serializers.ValidationError("两次密码输入不一致")

        #短信验证码是否正确

        sms_code_request = attrs.get("sms_code")
        mobile = attrs.get("mobile")

        redis_cli = get_redis_connection("sms_code")
        sms_code_redis = redis_cli.get("sms_code_" + mobile)
        #判断验证码是否过期
        if sms_code_redis is None:
            raise serializers.ValidationError("短信验证码错误")
        return attrs

    #4.手机号验证
    def validated_mobile(self,value):
        print(value)
        if re.match(r"1[3-9]\d{9}^$", value):
            raise serializers.ValidationError("手机号格式错误")
        count = User.objects.filter(mobile=value).count()
        if count > 0:
            raise serializers.ValidationError("手机号已经注册过了")
        return value

 #5.判断allow
    def validated_allow(self,value):
        print(value)
        if not value:
            raise serializers.ValidationError("请同意注册协议")
        return value

    #保存
    def create(self, validated_data):
        user = User()
        user.name = validated_data.get("username")
        user.mobile = validated_data.get("mobile")
        #密码加密
        user.set_password(validated_data.get("password"))
        user.save()

        # 需要生成token
        from rest_framework_jwt.settings import api_settings
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)


        token = jwt_encode_handler(payload)  # header.payload.signature
        # 为user添加token属性才能输出到客户端
        user.token = token
        return user

