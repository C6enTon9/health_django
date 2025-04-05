from django.db import models

class Information(models.Model):
    user_id = models.CharField(max_length=100)
    information = models.TextField()
    target = models.TextField()
    height = models.IntegerField()
    weight = models.IntegerField()
    age = models.IntegerField()