from django.shortcuts import render, redirect,get_object_or_404
from users import models as user_model
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

# def update_generator(request, generator_id):
#     if request.method == 'POST':
#         # Update the generator data here
#         # Fetch data using generator_id and save the form data to the database
#         fuel = request.POST.get('fuel')
#         status = request.POST.get('status')
#         power_produced = request.POST.get('power_produced')
#         peak_capacity = request.POST.get('peak_capacity')
        
#         # Save these values to the database (pseudo-code)
#         # generator = Generator.objects.get(id=generator_id)
#         # generator.fuel = fuel
#         # generator.status = status
#         # generator.power_produced = power_produced
#         # generator.peak_capacity = peak_capacity
#         # generator.save()

#         return redirect('generators')  # Redirect to the generators page
#     return render(request, 'generators.html')

def view_generator(request,generator_id):
    generator = None
    generator_id = request.GET.get('generator_id', None)  # Get generator_id from query parameter

    if generator_id:
        generator = get_object_or_404(user_model.generator, uuid=generator_id)

    return render(request, 'generators.html', {'generator': generator})

def update_generator(request, generator_id):
    generator = get_object_or_404(user_model.generator, uuid=generator_id)

    if request.method == 'POST':
        # Update generator fields with form data
        generator.fuel = request.POST.get('fuel', generator.fuel)
        activity_status = request.POST.get('status', generator.activity_status)
        if activity_status =="on" or activity_status=='ON':
            generator.activity_status = True
        else :
            generator.activity_status = False
        generator.current_production = request.POST.get('current_production', generator.current_production)
        generator.peak_capacity = request.POST.get('peak_capacity', generator.peak_capacity)
        generator.save()

        # Redirect back to the view page after saving
        return redirect('view_generator', generator_id=generator.uuid)

    return render(request, 'update_generator.html', {'generator': generator})