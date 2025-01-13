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


def view_section(request, section_id):
    section = get_object_or_404(user_model.section, uuid=section_id)
    return render(request, 'sections.html', {'section': section})


def update_section(request, section_id):
    section = get_object_or_404(user_model.section, uuid=section_id)

    if request.method == 'POST':
        # Update fields with data from the form
        activity_status = request.POST.get('activity_status', 'off')  # Default to 'off' if not provided
        section.grids = request.POST.get('grids', section.grids)
        section.users = int(request.POST.get('users', section.users))  # Convert to int
        section.load = int(request.POST.get('load', section.load))  # Convert to int
        section.max_load = int(request.POST.get('max_load', section.max_load))  # Convert to int

        # Logic for updating activity status and related fields
        if activity_status.lower() == 'off':
            section.activity_status = False
            section.users = 0
            section.load = 0
            section.grids = None
        else:
            section.activity_status = True

        # Ensure consistency between load, max_load, and users
        if section.users == 0:
            section.load = 0
            section.grids = 0
            section.activity_status = False
        elif section.load > section.max_load:
            section.load = section.max_load

        # Handle cases where load is 0
        if section.load == 0:
            section.activity_status = False
            section.users = 0
            section.grids = 0

        # Save the updated section
        section.save()

        return redirect('view_sections',section_id=section.uuid)  # Redirect to the correct view (ensure 'view_sections' is defined in urls)

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
        if generator.activity_status is True:
            activity_status = request.POST.get('activity_status','on')
        else:
            activity_status = request.POST.get('activity_status','off')
        if activity_status =="on":
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

def view_grid(request,grid_id):
    grid = None
    grid_id = request.GET.get('grid_id', None)  # Get generator_id from query parameter

    if grid_id:
        grid = get_object_or_404(user_model.grid, uuid=grid_id)

    return render(request, 'grid.html', {'grid': grid})

def update_grid(request, grid_id):
    grid = get_object_or_404(user_model.grid, uuid=grid_id)

    if request.method == 'POST':
        # Handle activity status
        activity_status = request.POST.get('activity_status', 'off')  # Default to 'off' if not in POST
        grid.activity_status = activity_status == 'on'

        # Update other fields with form data
        try:
            grid.users = int(request.POST.get('users', grid.users))
            grid.load = float(request.POST.get('load', grid.load))
        except ValueError:
            # Handle invalid numeric input
            messages.error(request, "Invalid input for users or load. Please provide valid numbers.")
            return render(request, 'update_grid.html', {'grid': grid})

        # Adjust fields based on logic
        if not grid.activity_status or grid.users == 0 or grid.load == 0:
            grid.activity_status = False
            grid.users = 0
            grid.load = 0

        # Save updates
        grid.save()

        return redirect('view_grid', grid_id=grid.uuid)

    return render(request, 'update_grid.html', {'grid': grid})
