from django.db import models

# Create your models here.
class User (models.Model):
    objects = models.manager
    user_id = models.CharField(max_length=20)
    user_pswd = models.CharField(max_length=20)