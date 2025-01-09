from django.shortcuts import render

# Home view
def home(request):
    return render(request, 'core/home.html')

# About view
def about(request):
    return render(request, 'core/about.html')
