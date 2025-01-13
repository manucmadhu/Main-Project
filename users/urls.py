# power_grid_management/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views
from admin_panel import views as admin_views
urlpatterns = [
    path('', views.cauthenticate, name='cauthenticate'),
    #  path('', views.dashboard_view, name='dashboard'),
    path('signup', views.signup_view, name='signup'),
    path('ad',views.login_view,name='login_view'),
    path('generators/<int:generator_id>', admin_views.view_generator, name='view_generator'),  # Corrected URL pattern
    path('generators/<str:generator_id>/update/', admin_views.update_generator, name='update_generator'),
    path('sections/<int:section_id>', admin_views.view_section, name='view_section'), 
    path('sections/<str:section_id>/update/', admin_views.update_section, name='update_section'),
    path('grids/<int:grid_id>', admin_views.view_grid, name='view_grid'), 
    path('grids/<str:grid_id>/update/', admin_views.update_grid, name='update_grid'),
]   
