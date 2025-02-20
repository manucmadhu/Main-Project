from django.urls import path
from . import views

urlpatterns = [
     path('chabot/<int:user_id>',views.chatbot_api,name='chatbot_api')
]
