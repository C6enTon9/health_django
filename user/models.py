from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    """
    用户管理器
    只提供创建普通用户的功能
    """
    
    def create_user(self, user_id, password=None):
        """
        创建普通用户
        :param user_id: 用户ID，作为用户的唯一标识
        :param password: 用户密码
        :return: 创建的用户实例
        """
        if not user_id:
            raise ValueError('用户ID不能为空')
        user = self.model(user_id=user_id)
        user.set_password(password)  # 设置密码，会自动进行加密
        user.save()
        return user

class User(AbstractBaseUser):
    """
    简单用户模型
    继承自AbstractBaseUser，自动包含以下字段：
    - password: 存储加密后的密码
    - last_login: 最后登录时间
    """
    
    # 自定义字段
    user_id = models.CharField('用户ID', max_length=20, unique=True)

    # 指定用户管理器
    objects = UserManager()

    # 设置用户名字段
    USERNAME_FIELD = 'user_id'

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user_id
