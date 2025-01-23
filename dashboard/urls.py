from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('notifications/', include('notifications.urls')),
    
    # Handle root URL (redirect to dashboard or another view)
    path('', lambda request: redirect('dashboard/')),  # Redirect to 'dashboard/'
]
