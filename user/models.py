from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password, check_password
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
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, password=None):
        user = self.create_user(user_id, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """
    用户模型
    """
    
    user_id = models.CharField('用户ID', max_length=20, unique=True)
    is_active = models.BooleanField('是否激活', default=True)
    is_staff = models.BooleanField('是否为工作人员', default=False)

    objects = UserManager()
    
    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.user_id

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
