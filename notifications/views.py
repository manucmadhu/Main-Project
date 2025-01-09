# notifications/views.py
from django.http import HttpResponse

def notification_list(request):
    return HttpResponse("List of Notifications")

def create_notification(request):
    return HttpResponse("Create a New Notification")
from django.shortcuts import render

# Create the notification_home view
def notification_home(request):
    # Implement the logic for this view, e.g., fetching notifications
    return render(request, 'notifications/home.html')
