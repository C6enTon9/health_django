# 项目主urls.py
from django.urls import path
from . import views
app_name = 'nutrition'

urlpatterns = [
    # ...其他路由
    path('analyze/', views.FoodRecognitionView.as_view(), name='food-analysis'),
    path('analyze/recognize-base64/', views.FoodRecognitionBase64View.as_view(), name='food-recognition-base64'),
    path('calculate/', views.NutritionCalculationView.as_view(), name='nutrition-calculate'),

]