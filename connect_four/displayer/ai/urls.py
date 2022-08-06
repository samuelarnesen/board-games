from django.urls import path, include
from django.contrib import admin
from . import views
app_name = 'ai'

urlpatterns = [
    path('', views.get_move, name="index"),
]
