from django.shortcuts import render, redirect,get_object_or_404
from users import models as user_model
from django.db.models import F
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
        grid1 = request.POST.get('grid1',generator.grid1)
        grid2 = request.POST.get('grid2',generator.grid2)
        if generator.grid1 != grid1 :
            newgrid=get_object_or_404(user_model.grid,uuid=grid1)
            generator.grid1=grid1
            generator.grid1power=newgrid.load
        if generator.grid2 != grid2 :
            newgrid=get_object_or_404(user_model.grid,uuid=grid2)
            generator.grid2=grid2
            generator.grid2power=newgrid.load
        if generator.current_production == 0 :
            generator.activity_status=False
            generator_off(generator.uuid)
        if generator.activity_status is False :
            generator.current_production = 0
            generator_off(generator.uuid)
        if generator.current_production >=generator.peak_capacity:
            generator.current_production=generator.peak_capacity
            generator.free=False
        if generator.grid1power>0 and generator.grid2power >0:
            generator.free=False
        else:
            generator.free=True
        generator.save()

        # Redirect back to the view page after saving
        return redirect('view_generator', generator_id=generator.uuid)

    return render(request, 'update_generator.html', {'generator': generator})

def generator_off(generator_id):
    generator = get_object_or_404(user_model.generator, uuid=generator_id)
    if generator.grid1!=0:
        free_generator = generator.objects.filter(activity_status=False,peak_capacity__gt=F('current_production') + grid1.load).first()
        if free_generator is None:
            grid_off(generator.grid1)
        if free_generator.grid1 ==0 and generator.grid1!=0 :
            grid1=get_object_or_404(user_model.grid,uuid=generator.grid1)
            free_generator.grid1 = grid1.uuid
            free_generator.grid1power=grid1.load
            free_generator.current_production+=grid1.load
        elif free_generator.grid2 ==0 and generator.grid1!=0 :
            grid1=get_object_or_404(user_model.grid,uuid=generator.grid1)
            free_generator.grid2 = grid1.uuid
            free_generator.grid2power=grid1.load
            free_generator.current_production+=grid1.load
        generator.save()
        grid1.save()
        free_generator.save()
    elif generator.grid2 !=0 :
        free_generator = generator.objects.filter(activity_status=False,peak_capacity__gt=F('current_production') + grid2.load).first()
        if free_generator is None:
            grid_off(generator.grid2)
        if free_generator.grid1 == 0 and generator.grid2 != 0 :
            grid2=get_object_or_404(user_model.grid,uuid=generator.grid2)
            free_generator.grid1 = grid2.uuid
            free_generator.current_production+=grid2.load
        elif free_generator.grid2 ==0 and generator.grid2!=0 :
            grid1=get_object_or_404(user_model.grid,uuid=generator.grid1)
            free_generator.grid2 = grid1.uuid
            free_generator.grid2power=grid1.load
            free_generator.current_production+=grid1.load
        generator.save()
        grid2.save()
        free_generator.save()
    return

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
            grid.users = request.POST.get('users', grid.users)
            grid.load = request.POST.get('load', grid.load)
        except ValueError:
            # Handle invalid numeric input
            # messages.error(request, "Invalid input for users or load. Please provide valid numbers.")
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

def grid_off(grid_id):
    grid = get_object_or_404(user_model.grid, uuid=grid_id)
    if grid.sec1:
        sec_off(grid.sec1)
    if grid.sec2:
        sec_off(grid.sec2)
    if grid.sec3:
        sec_off(grid.sec3)
    return
from django.utils.timezone import now
from datetime import timedelta
def sec_off(section_id):
    section=get_object_or_404(user_model.section_id,uuid=section_id)
    for user in user_model.bear.objects.filter(section=section.uuid):
        send_error_message(user.uuid,now(),now()+timedelta(hours=2))
    return

def send_error_message(user_id,start,end):
    # Send error message to user
    return