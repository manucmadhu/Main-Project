
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('generators/<int:generator_id>/', views.update_generator, name='update_generator'),
]
