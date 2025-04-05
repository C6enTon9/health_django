from django.db import models

class User(models.Model):
    # 基本字段
    user_id = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)