# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse

# views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return render(request,"admin_panel.html")  # Redirect admin users to an admin dashboard
                else:
                    return render(request,"dashboard.html")  # Redirect regular users to their dashboard
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})
# In your views.py
# def signup_view(request):
#     if request.method == 'POST':
#         form = SignupForm(request.POST)
#         if form.is_valid():
#             # Handle form saving here
#             return redirect('login')  # Redirect to login after successful signup
#     else:
#         form = SignupForm()
#     return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
def dashboard_view(request):
    data = {
        'current_usage': '150 kWh',
        'predicted_usage': '170 kWh',
        'bill_details': [
            {'appliance': 'Fridge', 'bill': 500},
            {'appliance': 'AC', 'bill': 1200},
        ],
    }
    return JsonResponse(data)
def signup_view(request):
    return render(request,'signup.html')