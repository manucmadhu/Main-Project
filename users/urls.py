from django.contrib import admin
from django.urls import path, include  # Make sure 'include' is imported
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', include('dashboard.urls')),  # This works if dashboard.urls exists
    path('admin/', admin.site.urls),
    path('notifications/', include('notifications.urls')),  # Include notifications URLs
]
