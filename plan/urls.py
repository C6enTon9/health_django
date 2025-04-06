from django.urls import path
from . import views

urlpatterns = [
    path('get_plan/', views.get_plan),
    path('upd_plan/', views.upd_plan),
]