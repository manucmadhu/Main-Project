from django.shortcuts import render, redirect,get_object_or_404
from users import models as user_model
from users.views import check,hashed
from django.db.models import F,Sum
# Create your views here.
from django.http import JsonResponse
from datetime import datetime
import os
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
from .forms import AddGridForm, RemoveGridForm  # Import the forms

def view_generator(request, generator_id):
    user = request.user
    generator = get_object_or_404(user_model.generator, uuid=generator_id)

    # Fetch all grids linked to this generator
    served_grids = user_model.serves.objects.filter(gen_id=generator.uuid)

    if request.method == "POST":
        grid_uuid = request.POST.get("grid_uuid")
        
        if not grid_uuid:
            return JsonResponse({"error": "Grid UUID is required"}, status=400)

        print(f"📌 Grid UUID Received: {grid_uuid}")  # Debugging

        # 🟢 Adding a Grid
        if "add_grid" in request.POST:
            grid = user_model.grid.objects.filter(uuid=grid_uuid).first()
            
            if not grid:
                return JsonResponse({"error": "Grid not found"}, status=404)

            if user_model.serves.objects.filter(gen_id=generator.uuid, grid_id=grid.uuid).exists():
                return JsonResponse({"error": "Grid already linked!"}, status=400)

            if grid.load > generator.peak_capacity - generator.current_production:
                return JsonResponse({"error": "Grid capacity can't be fulfilled by generator"}, status=400)

            last_entry = user_model.serves.objects.last()
            uid = int(last_entry.uuid) + 1 if last_entry and last_entry.uuid else 1

            user_model.serves.objects.create(
                gen_id=generator.uuid, 
                grid_id=grid.uuid, 
                uuid=uid, 
                power_usage=grid.load
            )

            return JsonResponse({"message": "Grid added successfully"}, status=200, safe=False)

        # 🔴 Removing a Grid
        elif "remove_grid" in request.POST:
            print(f"📌 Attempting to remove grid {grid_uuid}")

            old_entry = user_model.serves.objects.filter(gen_id=generator.uuid, grid_id=grid_uuid).first()

            if old_entry:
                print(f"✅ Found grid {grid_uuid}, proceeding with deletion.")

                grid_load = old_entry.power_usage
                generator.current_production = max(generator.current_production - grid_load, 0)
                generator.save()

                # ⚠️ Check if `grid_off()` is causing an issue
                try:
                    grid_off(grid_uuid)
                except Exception as e:
                    print(f"⚠️ Error in grid_off(): {e}")  # Debugging
                    return JsonResponse({"error": "Grid removal failed due to grid_off error"}, status=500)

                # ✅ Delete the grid link
                deleted_count, _ = user_model.serves.objects.filter(gen_id=generator.uuid, grid_id=grid_uuid).delete()

                if deleted_count:
                    print(f"✅ Grid {grid_uuid} removed successfully!")
                    return JsonResponse({"message": "Grid removed successfully"}, status=200, safe=False)
                else:
                    print(f"❌ Failed to delete grid {grid_uuid}.")
                    return JsonResponse({"error": "Failed to remove grid"}, status=400)
            else:
                print(f"❌ Grid {grid_uuid} not found in the serves table.")
                return JsonResponse({"error": "Grid not linked to this generator or does not exist"}, status=400)

    return render(
        request,
        "generators.html",
        {
            "generator": generator,
            "user": user,
            "served_grids": served_grids,
        },
    )


def update_generator(request, generator_id):
    generator = get_object_or_404(user_model.generator, uuid=generator_id)
    old_status = generator.activity_status  # Store old status

    if request.method == 'POST':
        generator.fuel = request.POST.get('fuel', generator.fuel)
        generator.current_production = request.POST.get('current_production', generator.current_production)
        generator.peak_capacity = request.POST.get('peak_capacity', generator.peak_capacity)

        # Handle activity_status correctly
        activity_status = request.POST.get('activity_status')  # Returns 'on' if checked, None if unchecked
        generator.activity_status = True if activity_status == "on" else False
        if generator.activity_status is False:
            generator.current_production=0
        # Ensure production doesn't exceed peak capacity
        generator.current_production = min(float(generator.current_production), float(generator.peak_capacity))

        # If production is 0, disable the generator
        if generator.current_production == 0:
            generator.activity_status = False
        # If generator was turned off, trigger generator_off()
        if old_status and not generator.activity_status:
            generator_off(generator.uuid)

        generator.save()
        return redirect('view_generator', generator_id=generator.uuid)

    return render(request, 'update_generator.html', {'generator': generator})
from django.db.models import F

def generator_off(generator_id):
    generator = get_object_or_404(user_model.generator, uuid=generator_id)

    # Get all the grids served by this generator
    served_grids = user_model.serves.objects.filter(gen_id=generator.uuid)

    for serve_entry in served_grids:
        grid = get_object_or_404(user_model.grid, uuid=serve_entry.grid_id)

        # Find an available generator with enough capacity
        free_generator = user_model.generator.objects.filter(
            activity_status=True,
            free=True,
            peak_capacity__gte=F('current_production') + grid.load
        ).first()

        if free_generator:
            # Reassign the grid to the new generator
            serve_entry.gen_id = free_generator.uuid
            serve_entry.save()

            # Update generator's current production
            free_generator.current_production += grid.load
            free_generator.save()
        else:
            # No available generator, so turn off the grid
            grid.activity_status = False
            grid.save()

    # Clear the generator's load and mark it as free
    generator.current_production = 0
    generator.activity_status = False
    generator.free = True
    generator.save()


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
    try:
        if grid.sec1:
            sec_off(grid.sec1)
        if grid.sec2:
            sec_off(grid.sec2)
        if grid.sec3:
            sec_off(grid.sec3)
    except Exception as e:
        print(e)
    return
from django.utils.timezone import now
from datetime import timedelta
def sec_off(section_id):
    section=get_object_or_404(user_model.section,uuid=section_id)
    try:
        for user in user_model.bear.objects.filter(section=section.uuid):
            send_error_message(user.uuid,now(),now()+timedelta(hours=2))
            user_off(user_id=user.uuid)
    except Exception as e:
        print(e)
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
    recent_maintenances = Schedule.objects.all().order_by('-start_time').filter(completed=False)

    # Pass the records to the template context
    return render(request, 'show_maintenance.html', {'maintenances': recent_maintenances})
def completed_maintenance(request):
    # Fetch the 5 most recent maintenance records
    completed_maintenance = Schedule.objects.all().order_by('-start_time').filter(completed=True)

    # Pass the records to the template context
    return render(request, 'completedmaintenances.html', {'completedmaintenances': completed_maintenance})
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

import joblib
import pandas as pd
from django.shortcuts import render


# Load the trained model
MODEL_PATH = "models\generator_ranking_model.pkl"
FEATURES_PATH = "models/feature_names.pkl"

def load_model():
    """Load the ML model if it exists, else raise an error"""
    if os.path.exists(MODEL_PATH) and os.path.exists(FEATURES_PATH):
        model = joblib.load(MODEL_PATH)
        feature_names = joblib.load(FEATURES_PATH)
        return model, feature_names
    else:
        raise FileNotFoundError("Model or feature names file not found! Train the model first.")

# Load model and feature names
model, FEATURE_NAMES = load_model()

def predict_generator_ranking(input_data):
    """Predict generator ranking with correct feature order"""
    # Convert input data to DataFrame
    df = pd.DataFrame([input_data])  

    # Reorder columns to match training set
    df = df.reindex(columns=FEATURE_NAMES, fill_value=0)  

    # Predict ranking
    prediction = model.predict(df)
    return prediction[0]
from django.db import transaction
from sklearn.preprocessing import LabelEncoder
import os
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "generator_ranking_model.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "feature_names.pkl")

# Load the trained encoder (if already saved)
ENCODER_PATH = os.path.join(BASE_DIR, "generator_encoder.pkl")
if os.path.exists(ENCODER_PATH):
    label_encoder = joblib.load(ENCODER_PATH)
else:
    label_encoder = LabelEncoder()  # Create a new one if missing

def update_generator_rankings():
    """Fetches data from the database, predicts rankings, and updates the records."""
    generators = user_model.generator.objects.all()

    if not os.path.exists(MODEL_PATH) or not os.path.exists(FEATURES_PATH):
        print("⚠️ Model or feature names file is missing! Train and save the model first.")
        return

    model = joblib.load(MODEL_PATH)
    FEATURE_NAMES = joblib.load(FEATURES_PATH)

    data = []
    generator_instances = []

    for gen in generators:
        data.append([gen.generator_type, gen.efficiency, gen.fuel_cost, gen.emissions, gen.current_production])
        generator_instances.append(gen)

    df = pd.DataFrame(data, columns=["Generator_Type", "Efficiency", "Fuel_Cost", "Emissions", "Power_Output"])

    # **Encode the categorical "Generator_Type" column**
    if "Generator_Type" in df.columns:
        df["Generator_Type"] = label_encoder.fit_transform(df["Generator_Type"])  # Convert text to numbers
        joblib.dump(label_encoder, ENCODER_PATH)  # Save encoder for future use

    # Ensure feature names match the model
    for col in FEATURE_NAMES:
        if col not in df.columns:
            df[col] = 0  # Add missing columns

    df = df[FEATURE_NAMES]  # Reorder columns

    # Predict rankings
    predictions = model.predict(df)

    # Update each generator record
    for i, gen in enumerate(generator_instances):
        gen.overall_rank = int(predictions[i])
        gen.save()


def rankings(request):
    """Admin view to display generator rankings after prediction"""
    update_generator_rankings()  # Auto-update rankings
    generators = user_model.generator.objects.all().order_by("overall_rank")  # Show sorted rankings
    return render(request, "rankings.html", {"generators": generators})
