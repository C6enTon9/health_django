from django.db import models

# Create your models here.
class Plan(models.Model):
    user_id = models.CharField(max_length=20)
    thing = models.CharField(max_length=100)
    description = models.TextField()
    day = models.IntegerField()
    start_time = models.DateField()
    end_time = models.DateField()
    is_completed = models.BooleanField(default=False)