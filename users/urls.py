# power_grid_management/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views
from users import views as user_views
from admin_panel import views as admin_views
urlpatterns = [
    path('', views.cauthenticate, name='cauthenticate'),
    path('signup', views.signup_view, name='signup'),
    path('ad',views.login_view,name='login_view'),
    path('generators/<int:generator_id>', admin_views.view_generator, name='view_generator'),  # Corrected URL pattern
    path('generators/<str:generator_id>/update/', admin_views.update_generator, name='update_generator'),
    path('sections/<int:section_id>', admin_views.view_section, name='view_section'), 
    path('sections/<str:section_id>/update/', admin_views.update_section, name='update_section'),
    path('grids/<int:grid_id>', admin_views.view_grid, name='view_grid'), 
    path('admin_panel/<int:user_id>',user_views.admin_view,name='admin_panel'),
    path('grids/<str:grid_id>/update/', admin_views.update_grid, name='update_grid'),
    path('users/<int:user_id>',admin_views.view_user,name='view_user'),
    path('users/<str:user_id>/update/', admin_views.update_user, name='update_user'),
   path('maintenances/', admin_views.show_maintenance, name='show_maintenance'),
   path('make_maintenance/<str:obj>', admin_views.make_maintenance, name='make_maintenance'),
   path('powerusage/<int:user_id>',views.power_usage,name='powerusage'),
   path('billpay/<int:user_id>',views.bill_collec,name='billpay'),
   path('payment/process/<str:uuid>/', views.process_payment, name='process_payment'),
   path("rankings/", admin_views.rankings, name="rankings"),
   path("gross-power-data/", admin_views.gross_power_data, name="gross-power-data"),
   path('api/update-usage-bill/', admin_views.update_usage_and_bill, name='update_usage_and_bill'),
]