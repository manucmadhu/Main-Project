from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def dashboard_view(request):
    data = {
        "current_usage": "190 kWh",
        "predicted_usage": "180 kWh",
        "bill_details": [
            {"appliance": "Refrigerator", "bill": 500},
            {"appliance": "AC", "bill": 1000},
        ],
    }
    return JsonResponse(data)