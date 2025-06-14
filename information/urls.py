# information/urls.py

from django.urls import path
from . import views

app_name = 'information'

urlpatterns = [
    path('update/<str:attribute_name>/', views.update_attribute_view, name='update_attribute'),
    path('get/<str:attribute_name>/', views.get_attribute_view, name='get_attribute'),
]