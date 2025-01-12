from django.shortcuts import render, redirect

# Create your views here.
from django.http import JsonResponse

def manage_generators(request):
    data = {
        'generators': [
            {'id': 1, 'status': 'ON', 'capacity': '100 MW'},
            {'id': 2, 'status': 'OFF', 'capacity': '150 MW'},
        ]
    }
    return JsonResponse(data)

def update_generator(request, generator_id):
    if request.method == 'POST':
        # Update the generator data here
        # Fetch data using generator_id and save the form data to the database
        fuel = request.POST.get('fuel')
        status = request.POST.get('status')
        power_produced = request.POST.get('power_produced')
        peak_capacity = request.POST.get('peak_capacity')
        
        # Save these values to the database (pseudo-code)
        # generator = Generator.objects.get(id=generator_id)
        # generator.fuel = fuel
        # generator.status = status
        # generator.power_produced = power_produced
        # generator.peak_capacity = peak_capacity
        # generator.save()

        return redirect('generators')  # Redirect to the generators page
    return render(request, 'generators.html')