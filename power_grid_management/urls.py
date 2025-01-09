from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel URL
    path('', include('core.urls')),   # Main core app routing
    path('notifications/', include('notifications.urls')),  # Notifications app routing
]
