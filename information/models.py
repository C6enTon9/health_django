from django.db import models

class Information(models.Model):
    username = models.CharField(max_length=100)
    information = models.TextField()
    height = models.IntegerField()
    weight = models.IntegerField()
    age = models.IntegerField()
    
    def get_age(self):
        return self.age

    def get_height(self):
        return self.height  
    
    def get_weight(self):  
        return self.weight
    
    def __str__(self):
        return self.username