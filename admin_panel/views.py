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


def view_sections(request,section_id):
    section = None
    section_id = request.GET.get('section_id', None)  # Get generator_id from query parameter

    if section_id:
        section = get_object_or_404(user_model.section, uuid=section_id)

    return render(request, 'sections.html', {'section': section})

def update_sections(request, section_id):
    section = get_object_or_404(user_model.section, uuid=section_id)

    if request.method == 'POST':
        activity_status=request.POST.get('activity_status',section.activity_statusactivity_status)
        section.grids=request.POST.get('grids',section.grids)
        section.users=request.POST.get('users',section.users)
        section.load=request.POST.get('load',section.load)
        section.max_load=request.POST.get('max_load',section.max_load)
        if activity_status=='OFF' or activity_status=='off':
            section.activity_status=False
            section.users=0
            section.load=0
            section.grids=None
        else:
            section.activity_status=True
        if section.users ==0 :
            section.load=0
            section.grids=None
            section.activity_status=False
        if section.load>section.max_load :
            section.load=section.max_load
        if section.load == 0:
            section.activity_status=False
            section.users=0
            section.grids=None
        return redirect('view_sections', section_id=section.uuid)

    return render(request, 'update_sections.html', {'section': section})
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
        if generator.current_production == 0 :
            generator.activity_status=False
        if generator.activity_status is False :
            generator.current_production = 0
        generator.save()

        # Redirect back to the view page after saving
        return redirect('view_generator', generator_id=generator.uuid)

    return render(request, 'update_generator.html', {'generator': generator})