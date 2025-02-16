from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, bear, bill # Corrected capitalization of Bear model
from django.utils.crypto import salted_hmac

# Constants
SALT = "thisissalt"  # Replace with a secure, unique salt value


# def login_view(request):
#     if request.method == "POST":
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user:
#             login(request, user)
#             if user.is_superuser:
#                 return redirect('admin_panel',user_id=user.uuid)
#             else :
#                 return render(request,'dashboard.html')
#         return JsonResponse({"status": "failure", "message": "Invalid credentials"})
#     return render(request, 'login.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .models import User, bear, generator, section, grid, bill, Schedule

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            
            if user.is_superuser:
                # Fetching statistics
                total_generators = generator.objects.count()
                active_generators = generator.objects.filter(activity_status=True).count()
                total_power_generated = sum(gen.current_production for gen in generator.objects.all())

                total_users = bear.objects.count()
                active_users = bear.objects.filter(activity_status=True).count()
                
                total_sections = section.objects.count()
                active_sections = section.objects.filter(activity_status=True).count()

                total_grids = grid.objects.count()
                active_grids = grid.objects.filter(activity_status=True).count()

                total_production = total_power_generated
                total_usage = sum(sec.load for sec in section.objects.all())
                difference = total_production - total_usage

                pending_maintenance = Schedule.objects.filter(completed=False).count()
                lost_hours = sum((sch.end_time - sch.start_time).total_seconds() / 3600 for sch in Schedule.objects.filter(completed=False) if sch.end_time and sch.start_time)
                lost_revenue = sum(sch.est_cost for sch in Schedule.objects.filter(completed=False))

                context = {
                    "user": user,
                    "total_generators": total_generators,
                    "active_generators": active_generators,
                    "total_power_generated": total_power_generated,
                    "total_users": total_users,
                    "active_users": active_users,
                    "total_sections": total_sections,
                    "active_sections": active_sections,
                    "total_grids": total_grids,
                    "active_grids": active_grids,
                    "total_production": total_production,
                    "total_usage": total_usage,
                    "difference": difference,
                    "pending_maintenance": pending_maintenance,
                    "lost_hours": round(lost_hours,2),
                    "lost_revenue": round(lost_revenue,2),
                    "grid_efficiency": round(active_grids*100/total_grids,2),
                    "section_utilization":round(active_sections*100/total_sections),
                    "usage":round(active_users*100/total_users,2)
                
                }

                return render(request, 'admin_panel.html', context)

            else:
                return render(request, 'dashboard.html')

        return JsonResponse({"status": "failure", "message": "Invalid credentials"})

    return render(request, 'login.html')
def admin_view(request,user_id):
    user=get_object_or_404(User,uuid=user_id)
    # user=request.POST('user_id',user.uuid)
    total_generators = generator.objects.count()
    active_generators = generator.objects.filter(activity_status=True).count()
    total_power_generated = sum(gen.current_production for gen in generator.objects.all())

    total_users = bear.objects.count()
    active_users = bear.objects.filter(activity_status=True).count()
                
    total_sections = section.objects.count()
    active_sections = section.objects.filter(activity_status=True).count()

    total_grids = grid.objects.count()
    active_grids = grid.objects.filter(activity_status=True).count()

    total_production = total_power_generated
    total_usage = sum(sec.load for sec in section.objects.all())
    difference = total_production - total_usage

    pending_maintenance = Schedule.objects.filter(completed=False).count()
    lost_hours = sum((sch.end_time - sch.start_time).total_seconds() / 3600 for sch in Schedule.objects.filter(completed=False) if sch.end_time and sch.start_time)
    lost_revenue = sum(sch.est_cost for sch in Schedule.objects.filter(completed=False))

    context = {
                    "user": user,
                    "total_generators": total_generators,
                    "active_generators": active_generators,
                    "total_power_generated": total_power_generated,
                    "total_users": total_users,
                    "active_users": active_users,
                    "total_sections": total_sections,
                    "active_sections": active_sections,
                    "total_grids": total_grids,
                    "active_grids": active_grids,
                    "total_production": total_production,
                    "total_usage": total_usage,
                    "difference": difference,
                    "pending_maintenance": pending_maintenance,
                    "lost_hours": round(lost_hours,2),
                    "lost_revenue": round(lost_revenue,2),
                    "grid_efficiency": round(active_grids*100/total_grids,2),
                    "section_utilization":round(active_sections*100/total_sections),
                    "usage":round(active_users*100/total_users,2)
                }

    return render(request, 'admin_panel.html', context)
    # return render(request,'admin_panel.html',{'user':user})
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