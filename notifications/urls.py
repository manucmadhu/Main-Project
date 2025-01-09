from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_home'),
    path('details/<int:id>/', views.notification_list, name='notification_details'),
]
