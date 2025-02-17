from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from admin_panel import views as admin_views
from dashboard import views as dashboard_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', user_views.login_view, name='logout'),
    path('', user_views.cauthenticate, name='authenticate'),
    path('ad',user_views.login_view,name='login'),
    path('admin_panel/<int:user_id>',user_views.admin_view,name='admin_panel'),
    path('dash',dashboard_views.dashboard_view, name='dashboard'),
    path('chatbot/', include('chatbot.urls')),
    path('notifications/', include('notifications.urls')),
    path('signup',user_views.signup_view,name='signup'),
    path('generators/<int:generator_id>', admin_views.view_generator, name='view_generator'),  # Corrected URL pattern
    path('generators/<str:generator_id>/update/', admin_views.update_generator, name='update_generator'),
    path('sections/<int:section_id>', admin_views.view_section, name='view_sections'), 
    path('sections/<str:section_id>/update/', admin_views.update_section, name='update_section'),
    path('grids/<int:grid_id>', admin_views.view_grid, name='view_grid'), 
    path('grids/<str:grid_id>/update/', admin_views.update_grid, name='update_grid'),
    path('users/<int:user_id>',admin_views.view_user,name='view_user'),
    path('users/<str:user_id>/update/', admin_views.update_user, name='update_user'),
    path('maintenances/', admin_views.show_maintenance, name='show_maintenance'),
    path('maintenances/<int:id>/update', admin_views.update_maintenance, name='update_maintenance'),
    path('make_maintenance/<str:obj>', admin_views.make_maintenance, name='make_maintenance'),
    path('completedmaintenances/', admin_views.completed_maintenance, name='completedmaintenances'),
    path('powerusage/<int:user_id>',user_views.power_usage,name='powerusage'),
    path('billpay/<int:user_id>',user_views.bill_collec,name='billpay'),
    path('payment/process/<str:uuid>/', user_views.process_payment, name='process_payment'),
    path("rankings/", admin_views.rankings, name="rankings"),
    path("rankings/", admin_views.rankings, name="rankings")
]