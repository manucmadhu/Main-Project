# power_grid_management/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.cauthenticate, name='cauthenticate'),
    #  path('', views.dashboard_view, name='dashboard'),
    path('signup', views.signup_view, name='signup'),
    path('ad',views.login_view,name='login_view'),
]
