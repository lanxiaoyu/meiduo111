from django.db import models
from django.contrib.auth.models import AbstractUser
from . import constants
from meiduo111.utils import tjws


class User(AbstractUser):
    # 默认拥有了用户名、密码、邮箱等属性
    # 扩展属性：定义
    mobile = models.CharField(max_length=11, unique=True)
    email_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'tb_users'

    def generate_verify_url(self):
        #构造有效数据
        data = {'user_id':self.id}
        #加密
        token = tjws.dumps(data,constants.VERIFY_EMAIL_EXPIRES)
        #构造激活链接
        return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token