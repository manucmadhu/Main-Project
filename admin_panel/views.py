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

def view_generator(request):
    generator_uuid = request.GET.get('generator_id', None)
    generator = None
    if generator_uuid:
        generator = get_object_or_404(user_model.generator, uuid=generator_uuid)
    return render(request, 'your_template.html', {'generator': generator})

def update_generator(request, id):
    generator = get_object_or_404(user_model.generator, id=id)
    if request.method == 'POST':
        generator.fuel = request.POST.get('fuel')
        generator.status = request.POST.get('status')
        generator.power_produced = request.POST.get('power_produced')
        generator.peak_capacity = request.POST.get('peak_capacity')
        generator.save()
        return redirect('view_generator')  # Redirect to the view generator page