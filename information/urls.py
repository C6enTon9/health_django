from django.urls import path
from . import views

urlpatterns = [
    path('upd_weight/', views.upd_weight),
    path('get_weight/', views.get_weight),
    path('upd_age/', views.upd_age),
    path('get_age/', views.get_age),
    path('upd_information/', views.upd_information),
    path('get_information/', views.get_information),
    path('upd_target/', views.upd_target),
    path('get_target/', views.get_target),
]