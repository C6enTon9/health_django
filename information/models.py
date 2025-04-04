from django.db import models

class Information(models.Model):
    username = models.CharField(max_length=100)
    information = models.TextField()

    def __str__(self):
        return self.username