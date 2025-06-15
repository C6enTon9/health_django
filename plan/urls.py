# plan/urls.py

from django.urls import path
from . import views

app_name = 'plan'

urlpatterns = [
    # 一个端点处理所有创建和更新操作
    path('manage/', views.manage_plans_view, name='manage_plans'),

    # 一个端点处理所有查询操作
    path('list/', views.list_plans_view, name='list_plans'),
    path('recent/', views.recent_plans_view, name='recent_plans'),
    path('over/', views.get_over_num_view, name='get_over_num'),
    path('workout/', views.get_workout_view, name='get_workout'),
]