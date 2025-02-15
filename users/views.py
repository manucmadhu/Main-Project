from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, bear, bill # Corrected capitalization of Bear model
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
                return redirect('admin_panel',user_id=user.uuid)
            else :
                return render(request,'dashboard.html')
        return JsonResponse({"status": "failure", "message": "Invalid credentials"})
    return render(request, 'login.html')
def admin_view(request,user_id):
    user=get_object_or_404(User,uuid=user_id)
    # user=request.POST('user_id',user.uuid)
    return render(request,'admin_panel.html',{'user':user})
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
            context = {'user': user}
            # Redirect based on role
            if user.role.lower() == 'admin':
                return render(request, "admin_panel.html",context)  # Render admin dashboard
            else:
                return render(request, "dashboard.html",context)  # Render user dashboard
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

def power_usage(request,user_id):
    user=get_object_or_404(bear,uuid=user_id)
    
    return render(request, 'power_usage.html', {'user': user})
def bill_collec(request,user_id):
    bill_id=get_object_or_404(bill,user=user_id)
    # if request.method == "POST":
    return render(request, 'bill.html', {'bill': bill_id})

def process_payment(request, uuid):
    try:
        user_bill = bill.objects.get(uuid=uuid)
        user_bill.paid = True  # Mark as paid
        user_bill.pending_amount = 0.0
        user_bill.save()
        return redirect('billpay', user_id=uuid)
    except bill.DoesNotExist:
        return redirect('dashboard')  # Redirect if bill not found