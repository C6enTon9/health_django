from django.db import models

# Create your models here.
class Plan(models.Model):
    user_id = models.CharField(max_length=20)
    thing = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()