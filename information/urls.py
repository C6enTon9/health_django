# information/urls.py

from django.urls import path
from . import views

app_name = 'information'

urlpatterns = [
    # 新版通用接口
    path('update/<str:attribute_name>/', views.update_attribute_view, name='update_attribute'),
    path('get/<str:attribute_name>/', views.get_attribute_view, name='get_attribute'),
    path('health-metrics/', views.get_health_metrics_view, name='get_health_metrics'),

    # 旧版兼容接口 - 向后兼容
    path('upd_height/', views.upd_height_view, name='upd_height'),
    path('get_height/', views.get_height_view, name='get_height'),
    path('upd_weight/', views.upd_weight_view, name='upd_weight'),
    path('get_weight/', views.get_weight_view, name='get_weight'),
    path('upd_age/', views.upd_age_view, name='upd_age'),
    path('get_age/', views.get_age_view, name='get_age'),
    path('upd_information/', views.upd_information_view, name='upd_information'),
    path('get_information/', views.get_information_view, name='get_information'),
    path('upd_target/', views.upd_target_view, name='upd_target'),
    path('get_target/', views.get_target_view, name='get_target'),
]