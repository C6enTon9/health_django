from django.urls import path
from . import views

urlpatterns = [
    path('',views.QueryUser.as_view())
]