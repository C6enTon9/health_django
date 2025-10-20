# diet/urls.py

from django.urls import path
from . import views

app_name = 'diet'

urlpatterns = [
    # 获取所有食物列表
    path('foods/', views.get_foods_view, name='get_foods'),

    # 添加食物到餐次
    path('add_food/', views.add_food_view, name='add_food'),

    # 从餐次删除食物
    path('remove_food/', views.remove_food_view, name='remove_food'),

    # 获取每日餐次记录
    path('daily_meals/', views.get_daily_meals_view, name='daily_meals'),

    # 更新食物重量
    path('update_weight/', views.update_food_weight_view, name='update_weight'),
]
