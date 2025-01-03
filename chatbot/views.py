from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
import random

SUGGESTIONS = [
    "Switch to energy-efficient appliances.",
    "Turn off lights when not in use.",
    "Unplug devices to save energy.",
]

def chatbot_view(request):
    query = request.GET.get('query', '')
    response = random.choice(SUGGESTIONS) if "save energy" in query else "How can I assist you?"
    return JsonResponse({"response": response})
