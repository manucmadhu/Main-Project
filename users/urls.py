# power_grid_management/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.login_view, name='login'),
    #  path('', views.dashboard_view, name='dashboard'),
    path('/signup', views.signup_view, name='signup'),
]
