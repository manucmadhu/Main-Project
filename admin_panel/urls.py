
from django.contrib import admin
from django.urls import path
from . import views
from users import views as user_views
from chatbot import views as chatbot_views
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
    path('make_maintenance/<str:obj>', views.make_maintenance, name='make_maintenance'),
    path('completedmaintenances/', views.completed_maintenance, name='completedmaintenances'),
    path('powerusage/<int:user_id>',user_views.power_usage,name='powerusage'),
    path('billpay/<int:user_id>',user_views.bill_collec,name='billpay'),
    path('payment/process/<str:uuid>/', user_views.process_payment, name='process_payment'),
    path("rankings/", views.rankings, name="rankings"),
    path("gross-power-data/", views.gross_power_data, name="gross-power-data"),
    path('maintenance/', views.gross_maintenance, name='gross_maintenance'),
    path('api/update-usage-bill/', views.update_usage_and_bill, name='update_usage_and_bill'),
    path('chabot/<int:user_id>',chatbot_views.chatbot_api,name='chatbot_api'),

]
