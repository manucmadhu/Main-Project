# power_grid_management/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('notifications/', include('notifications.urls')),  # Correctly include notifications app URLs
    path('', include('core.urls')),  # Correctly include core app URLs
]
