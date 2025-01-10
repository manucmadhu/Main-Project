from django.http import JsonResponse
import random

SUGGESTIONS = [
    'Switch to LED bulbs.',
    'Turn off appliances when not in use.',
    'Use solar power when possible.',
]

def chatbot_view(request):
    query = request.GET.get('query', '')
    response = random.choice(SUGGESTIONS) if 'save energy' in query else 'How can I assist you?'
    return JsonResponse({'response': response})
