from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, bear  # Corrected capitalization of Bear model
from django.utils.crypto import salted_hmac

# Constants
SALT = "thisissalt"  # Replace with a secure, unique salt value


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser:
                return render(request,'admin_panel.html')
            else :
                return render(request,'dashboard.html')
        return JsonResponse({"status": "failure", "message": "Invalid credentials"})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# @login_required  # Ensures only authenticated users can access this view
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
        user_id = request.POST['userid']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Save user to the database
        bear(uuid=user_id, name=username, email=email, password=hashed(password), role='user').save()
        return redirect('login')  # Redirect to login page after signup

    return render(request, 'signup.html')

def cauthenticate(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Custom user authentication
        user = check(username, password)
        if user is not None:
            # login(request, user)  # Logs in the user manually

            # Redirect based on role
            if user.role.lower() == 'admin':
                return render(request, "admin_panel.html")  # Render admin dashboard
            else:
                return render(request, "dashboard.html")  # Render user dashboard
        else:
            # Add error message for invalid credentials
            messages.error(request, 'Invalid username or password')
            return render(request, 'login.html')

    # Render the login page for GET request
    return render(request, 'login.html')

def check(username, password):
    try:
        user = bear.objects.get(name=username)  # Query user by username
        if user.password == hashed(password):  # Compare hashed passwords
            return user
    except bear.DoesNotExist:
        return None
    return None

def hashed(password):
    # Securely hash the password using salted_hmac
    return salted_hmac(SALT, password).hexdigest()
