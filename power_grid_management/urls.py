from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from admin_panel import views as admin_views
from dashboard import views as dashboard_views
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('users/', include('users.urls')),
    path('', user_views.cauthenticate, name='authenticate'),
    path('ad',user_views.login_view,name='login'),
    path('dash',dashboard_views.dashboard_view, name='dashboard'),
    path('chatbot/', include('chatbot.urls')),
    path('notifications/', include('notifications.urls')),
    path('signup',user_views.signup_view,name='signup'),
    path('generators/<int:generator_id>/', admin_views.update_generator, name='update_generator'),
]
