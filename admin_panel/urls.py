
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('generators/<int:generator_id>/', views.update_generator, name='update_generator'),
    path('generators/<int:generator_id>', views.view_generator, name='view_generator'),  # Corrected URL pattern
    path('generators/<str:generator_id>/update/', views.update_generator, name='update_generator'),
]
