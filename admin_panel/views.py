from django.shortcuts import render, redirect,get_object_or_404
from users import models as user_model
from users.views import check,hashed
from django.db.models import F,Sum
# Create your views here.
from django.http import JsonResponse
from datetime import datetime
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
    user=request.user
    return render(request, 'sections.html', {'section': section,'user':user})


def update_section(request, section_id):
    section = get_object_or_404(user_model.section, uuid=section_id)

    if request.method == 'POST':
        # Update fields with data from the form
        if section.activity_status:
            activity_status = request.POST.get('activity_status', 'on')
        else:
            activity_status = request.POST.get('activity_status', 'off')  # Default to 'off' if not provided
        # section.grids = request.POST.get('grids', section.grids)
        # section.users = int(request.POST.get('users', section.users))  # Convert to int
        # section.load = int(request.POST.get('load', section.load))  # Convert to int
        section.max_load = int(request.POST.get('max_load', section.max_load))  # Convert to int
        section.users=user_model.bear.objects.filter(section=section.uuid).count()
        total_usage_difference = user_model.bear.objects.filter(section=section.uuid).annotate(usage_diff=F('current_usage') - F('past_usage')).aggregate(total_usage_diff=Sum('usage_diff'))['total_usage_diff']

# Assign the calculated value to the section's load
        section.load = total_usage_difference if total_usage_difference is not None else 0
        # Logic for updating activity status and related fields
        if activity_status.lower() == 'off':
            section.activity_status = False
            section.users = 0
            section.load = 0
            section.grids = None
            sec_off(section_id=section.uuid)
        else:
            if section.activity_status is False:
                sec_on(section_id)
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

def sec_on(section_id):
    section=get_object_or_404(user_model.section_id,uuid=section_id)
    for user in user_model.bear.objects.filter(section=section.uuid):
        user_on(user_id=user.uuid)
    section.activity_status=True
    section.save()
    return

def view_generator(request,generator_id):
    generator = None
    generator_id = request.GET.get('generator_id', None)  # Get generator_id from query parameter
    user=request.user
    if generator_id:
        generator = get_object_or_404(user_model.generator, uuid=generator_id)

    return render(request, 'generators.html', {'generator': generator,'user':user})

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
            grid_off(grid1)
            newgrid=get_object_or_404(user_model.grid,uuid=grid1)
            generator.grid1=grid1
            generator.grid1power=newgrid.load
        if generator.grid2 != grid2 :
            grid_off(grid2)
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
    user=request.user

    return render(request, 'grid.html',{'grid':grid,'user':user})

def update_grid(request, grid_id):
    grid = get_object_or_404(user_model.grid, uuid=grid_id)

    if request.method == 'POST':
        # Handle activity status
        if grid.activity_status:
            activity_status = request.POST.get('activity_status','on')
        else:
            activity_status = request.POST.get('activity_status','off')
        grid.activity_status = activity_status == 'on'

        # Update other fields with form data

        # Adjust fields based on logic
        if not grid.activity_status :
            grid.activity_status = False
            grid_off(grid.uuid)
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
        user_off(user_id=user.uuid)
    section.activity_status=False
    section.save()
    return

def send_error_message(user_id,start,end):
    # Send error message to user
    return

def view_user(request,user_id):
    user=get_object_or_404(user_model.bear,uuid=user_id)
    return render(request,'users.html',{'bear':user})

def update_user(request,user_id):
    user = get_object_or_404(user_model.bear, uuid=user_id)

    if request.method == 'POST':
        # Handle activity status
        if user.activity_status:
            activity_status = request.POST.get('activity_status','on') 
        else:
            activity_status = request.POST.get('activity_status','off')
        user.activity_status = activity_status == 'on'
        if user.activity_status == False:
            user_off(user)
        user.username=request.POST.get('user_name',user.username)
        user.email=request.POST.get('user_email',user.email)
        user.name=request.POST.get('name',user.name)
        section_id=request.POST.get('section',user.section)
        if user.section!= section_id:
            section=get_object_or_404(user_model.section,uuid=section_id)
            section.load+=user.load
            if section.load>section.max_load:
                return JsonResponse("error Section load exceeded")
            else:
                section.save()
        user.bill_amount=request.POST.get('bill_amount',user.bill_amount)
        bill=get_object_or_404(user_model.bill,user=user.uuid)
        bill.pending_amount=user.bill_amount
        bill.save()
        user.save()
        # Save updates
        return redirect('view_user',user_id=user.uuid)

    return render(request, 'update_user.html', {'bear': user})

def user_off(user_id):
    send_error_message(user_id,now(),now()+timedelta(hours=2))
    user=get_object_or_404(user_model.bear,uuid=user_id)
    user.activity_status=False
    user.save()
    return

def show_user(request,user_id):#for the actual user to see his details
    user=get_object_or_404(user_model.bear,uuid=user_id)
    return redirect('naiveusers.html',user_id=user.uuid)

def user_on(user_id):
    send_restore_message(user_id,now())
    user=get_object_or_404(user_model.bear,uuid=user_id)
    user.activity_status=True
    user.save()
    return

def send_restore_message(user_id,time):
    return
def edit_user(request,user_id):
    user = get_object_or_404(user_model.bear, uuid=user_id)

    if request.method == 'POST':
        # Handle activity status
        user.username=request.POST.get('user_name',user.username)
        user.email=request.POST.get('user_email',user.email)
        user.name=request.POST.get('name',user.name)
        user.section=request.POST.get('section',user.section)
        user.profile_pic=request.POST.get('profile_pic',user.profile_pic)
        user.save()
        # Save updates
        return redirect('naiveusers', user_id=user.uuid)

    return render(request, 'edit_user.html', {'user': user})

def change_password(request,user_id):
    user=get_object_or_404(user_model.bear,uuid=user_id)
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_user=check(user.username,old_password)
    if new_user is None:
        return JsonResponse('error')
    else:
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password != confirm_password:
            return JsonResponse('error')
        else:
            user.password = hashed(new_password)
    return render(request,'change_password.html',user_id=user.uuid)
from users.models import Schedule
def show_maintenance(request):
    # Fetch the 5 most recent maintenance records
    recent_maintenances = Schedule.objects.all().order_by('-start_time')#.filter(completed=False)

    # Pass the records to the template context
    return render(request, 'show_maintenance.html', {'maintenances': recent_maintenances})

def make_maintenance(request,obj):  #front end not created
    if request.method == 'POST':    
        id=request.POST.get('uid')
        start_time=request.POST.get('start_time')
        end_time=request.POST.get('end_time')
        estimated_cost=request.POST.get('est_cost')
        user_model.Schedule(uuid=id,obj=obj,start_time=start_time,end_time=end_time,est_cost=estimated_cost,completed=False).save()
        return redirect('show_maintenance')
    return render(request, 'make_maintenance.html', {'Object': obj})



def update_maintenance(request, id):
    Schedule = get_object_or_404(user_model.Schedule, uuid=id)

    if request.method == 'POST':
        # Handle the 'completed' checkbox
        completed = request.POST.get('completed', 'off')
        if completed == 'on':
            Schedule.completed = True
        else:
            Schedule.completed = False
        # Handle 'act_cost' field
        act_cost = request.POST.get('act_cost')
        Schedule.act_cost = float(act_cost)
        if Schedule.act_cost==0 and Schedule.completed:
            Schedule.act_cost=Schedule.est_cost

        # Handle 'end_time' field
        end_time = request.POST.get('end_time')
        if Schedule.completed:
            # Set the current time as the end time if completed
            Schedule.end_time = now()
        elif end_time:
            try:
                # Parse the datetime-local format from the form
                Schedule.end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
            except ValueError:
                Schedule.end_time = None  # Handle invalid datetime input gracefully

        # Save the updated schedule
        Schedule.save()
        return redirect('show_maintenance')  # Redirect to the maintenances page

    return render(request, 'update_maintenance.html', {'Schedule': Schedule})
