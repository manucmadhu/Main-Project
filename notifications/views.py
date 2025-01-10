from django.http import JsonResponse

def notifications_view(request):
    data = {
        'notifications': [
            {'user': 'User 1', 'message': 'Scheduled maintenance tomorrow'},
            {'user': 'User 2', 'message': 'High power consumption detected'},
        ]
    }
    return JsonResponse(data)
