
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('generators/<int:generator_id>', views.view_generator, name='view_generator'),  # Corrected URL pattern
    path('generators/<str:generator_id>/update/', views.update_generator, name='update_generator'),
    path('sections/<int:section_id>', views.view_section, name='view_sections'), 
    path('sections/<str:section_id>/update/', views.update_section, name='update_section'),
    path('admin_panel/<int:user_id>',views.admin_view,name='admin_panel'),
    path('grids/<int:grid_id>', views.view_grid, name='view_grid'), 
    path('grids/<str:grid_id>/update/', views.update_grid, name='update_grid'),
    path('users/<int:user_id>',views.view_user,name='view_user'),
    path('users/<str:user_id>/update/', views.update_user, name='update_user'),
    path('maintenances/', views.show_maintenance, name='show_maintenance'),
    path('maintenances/<int:id>/update', views.update_maintenance, name='update_maintenance'),
]
