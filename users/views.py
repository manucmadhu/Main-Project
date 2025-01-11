# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib import admin
from .models import User,appliance,generator,section,grid,bill

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)  # Log in the user
            # Redirect based on role
            if user.role.lower() == 'admin':
                return render(request, "admin_panel.html")  # Render admin dashboard
            else:
                return render(request, "dashboard.html")  # Render user dashboard
        else:
            # Add error message for invalid credentials
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    
    # Render the login page for GET request
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

def dashboard_view(request):
    data = {
        'current_usage': '180 kWh',
        'predicted_usage': '170 kWh',
        'bill_details': [
            {'appliance': 'Fridge', 'bill': 500},
            {'appliance': 'AC', 'bill': 1200},
        ],
    }
    return JsonResponse(data)

def signup_view(request):
    if request.method == 'POST':
        user_password = request.POST['password']
         
        User(uuid=request.POST['userid'],name=request.POST['username'],email=request.POST,password=hash_password(user_password),role ='user').save()
        return render(request,'login.html')
    return render(request,'signup.html')

    