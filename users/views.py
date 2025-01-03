# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({"status": "success", "role": user.role})
        return JsonResponse({"status": "failure", "message": "Invalid credentials"})
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
