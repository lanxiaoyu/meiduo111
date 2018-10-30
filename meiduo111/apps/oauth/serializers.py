from django_redis import get_redis_connection
from rest_framework import serializers
from .models import OAuthQQuser
from users.models import User
from meiduo111.utils import tjws
from . import constants


class QQBindSerializer(serializers.Serializer):
    # 定义属性
    mobile = serializers.CharField()
    password = serializers.CharField()
    sms_code = serializers.CharField()
    access_token = serializers.CharField()

    # 验证
    def validate(self, attrs):
        """
        验证:短信验证码
        1.读取redis中的验证码
        2,读取请求中的验证码
        3.判断是否过期
        4,删除redis中验证码
        5.对比

        """
        sms_code_request = attrs.get('sms_code')
        mobile = attrs.get('mobile')
        #2,获取redis中的短信验证码
        redis_cli = get_redis_connection('sms_code')
        sms_code_redis = redis_cli.get('sms_code_'+mobile)
        #3.判断是否过期
        if sms_code_redis is None:
            raise serializers.ValidationError('短信验证码已经过期')
        #4.强制立即过期
        redis_cli.delete('sms_code' + mobile)
        #5,判断两个验证码是否相等
        if int(sms_code_request) != int(sms_code_redis):
            raise serializers.ValidationError('短信验证码错误')

        # 验证:access_token
        # 1,解密
        data_dict = tjws.loads(attrs.get('access_token'), constants.BIND_TOKEN_EXPIRES)
        # 2.判断是否过期
        if data_dict is None:
            raise serializers.ValidationError('access_token过期')
        # 3.获取openid
        openid = data_dict.get('openid')
        # 4.加入字典
        attrs['openid'] = openid
        return attrs


    def create(self, validated_data):
        # validated_data表示验证后的数据
        mobile = validated_data.get('mobile')
        openid = validated_data.get('openid')
        password = validated_data.get('password')
        # 1.查询手机号是否对应着一个用户
        try:
            user = User.objects.get(mobile=mobile)
        except:
            # 3.如果没有对应着一个用户
            # 3.1 创建用户
            user = User()
            user.username = mobile
            user.mobile = mobile
            user.set_password(password)
            user.save()
        else:
            # 2.如果对应着一个用户,进行密码对比
            # 2.1如果密码错误则抛出异常
            if not user.check_password(password):
                raise serializers.ValidationError('此手机号已经被使用')
        # 绑定 创建OAuthQQuser对象
        qquser = OAuthQQuser()
        qquser.openid = openid
        qquser.user = user
        qquser.save()

        return qquser
