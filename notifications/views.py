from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def notifications_view(request):
    data = {
        "notifications": [
            {"user": "User 92", "message": "Power failure in your area"},
            {"grid": "Grid 8", "message": "Maintenance scheduled"},
        ]
    }
    return JsonResponse(data)
