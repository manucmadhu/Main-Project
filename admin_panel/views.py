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
    for user in user_model.bear.objects.filter(section_id=section.uuid):
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
        for user in user_model.bear.objects.filter(section_id=section.uuid):
            send_error_message(user.uuid,now(),now()+timedelta(hours=2))
            user_off(user_id=user.uuid)
    except Exception as e:
        print(e)
    section.activity_status=False
    section.save()
    return

from django.core.mail import send_mail
from users.models import bear  # Import the user model
from django.conf import settings

def send_error_message(user_id, start, end):
    """Send an email to notify the user of a power outage."""
    user = bear.objects.filter(uuid=user_id).first()
    
    if not user or not user.email:
        print("User not found or email not provided")
        return

    subject = "Power Outage Notification"
    message = (
        f"Dear {user.name},\n\n"
        "We would like to inform you about a power outage in your area.\n"
        f"Outage Start Time: {start}\n"
        f"Estimated Restoration Time: {end}\n\n"
        "We apologize for the inconvenience and appreciate your patience.\n"
        "Thank you,\nPower Grid Management Team"
    )

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        print(f"Power outage notification sent to {user.email}")
    except Exception as e:
        print(f"Error sending email: {e}")

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
        section_id=request.POST.get('section',user.section_id)
        if user.section_id!= section_id:
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
        user.section_id=request.POST.get('section',user.section_id)
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
    
    try:
        for user in bear.objects.all():
            send_error_message(user.uuid,start_time,end_time)
    except Exception as e:
        print(e)
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
MODEL_PATH = "train\generator_ranking_model.pkl"
FEATURES_PATH = "train/feature_names.pkl"

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

import os
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from users.models import generator  # Import model to avoid circular import issues

MODEL_PATH = "train/isolation_forest_model.pkl"
FEATURES_PATH = "train/user_features.pkl"
ENCODER_PATH = "train/user_scaler.pkl"

label_encoder = LabelEncoder()

def update_generator_rankings():
    """Fetches data from the database, predicts rankings, and updates the records."""
    generators = generator.objects.all()

    if not os.path.exists(MODEL_PATH) or not os.path.exists(FEATURES_PATH):
        print("⚠️ Model or feature names file is missing! Train and save the model first.")
        return

    # Load the model and feature names
    model = joblib.load(MODEL_PATH)
    FEATURE_NAMES = joblib.load(FEATURES_PATH)

    data = []
    generator_instances = []

    # Collect data from each generator instance
    for gen in generators:
        data.append([gen.generator_type, gen.efficiency, gen.fuel_cost, gen.emissions, gen.current_production])
        generator_instances.append(gen)

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data, columns=["Generator_Type", "Efficiency", "Fuel_Cost", "Emissions", "Power_Output"])

    # **Encode the categorical "Generator_Type" column**
    if "Generator_Type" in df.columns:
        df["Generator_Type"] = label_encoder.fit_transform(df["Generator_Type"])  # Convert text to numbers
        joblib.dump(label_encoder, ENCODER_PATH)  # Save encoder for future use

    # Ensure feature names match the model
    for col in FEATURE_NAMES:
        if isinstance(col, str) and col not in list(df.columns):
            df[col] = 0  # Add missing columns

    # Reorder the columns to match the model's expected feature names
    df = df[FEATURE_NAMES]  # Reorder columns

    # Predict rankings using the loaded model
    predictions = model.predict(df)

    # Update the generator records with the predicted rankings
    for i, gen in enumerate(generator_instances):
        gen.overall_rank = int(predictions[i])
        gen.save()

import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import os
from django.shortcuts import render
# from .models import Generator, Bear  # Ensure correct model imports

# Paths to model files
MODEL_PATH = "train/isolation_forest_model.pkl"
SCALER_PATH = "train/user_scaler.pkl"
FEATURES_PATH = "train/user_features.pkl"
CSV_PATH = "train/user_dataset.csv"

def rankings(request):
    """Admin view to display generator rankings after prediction."""
    update_anomalous_users()  # Ensure anomalies are updated
    generators = user_model.generator.objects.all().order_by("overall_rank")
    anomalies = detect_anomalies()
    predictions =maintenance_predictions()  # Get predictions
    # return render(request, "maintenance.html", {"predictions": predictions})
    return render(request, "rankings.html", {"generators": generators, "anomalies": anomalies,"predictions": predictions})

def detect_anomalies():
    """Detect anomalies in user data using the trained model."""
    try:
        # Load trained model and scaler
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        feature_names = joblib.load(FEATURES_PATH)

        # Ensure user data is saved before analysis
        save_users_to_csv()

        # Fetch user data
        users = user_model.bear.objects.all()
        anomalies = []

        for user in users:
            # Prepare the input data
            data = [
                user.current_usage,
                user.past_usage,
                user.avg_usage,
                user.bill_amount,
                user.load,
                user.section,
                int(user.activity_status)  # Convert Boolean to int (0 or 1)
            ]

            # Scale the data
            data_scaled = scaler.transform([data])[0]  # Ensure 1D array

            # Predict anomaly
            prediction = model.predict([data_scaled])

            if prediction[0] == -1:
                # Extract the scalar anomaly score
                anomaly_score = model.decision_function([data_scaled])[0]
                
                anomalies.append({
                    "user": user.username,
                    "anomaly_score": anomaly_score
                })
        
        return anomalies
    except Exception as e:
        print(f"Error detecting anomalies: {e}")
        return []

def update_anomalous_users():
    """Check for users showing anomalies and mark them as inactive."""
    anomalies = detect_anomalies()
    
    if anomalies:
        for anomaly in anomalies:
            try:
                user = user_model.bear.objects.get(username=anomaly['user'])
                user.activity_status = False  # Flagging user as inactive
                user.save()
                print(f"Anomaly detected for {user.username}, flagged as inactive.")
            except user_model.bearear.DoesNotExist:
                print(f"User {anomaly['user']} not found.")
    else:
        print("No anomalies detected.")

def save_users_to_csv():
    """Fetch all user data from the database and append it to a CSV file."""
    try:
        users = user_model.bear.objects.all()
        
        data = [[
            user.username,
            user.current_usage,
            user.past_usage,
            user.avg_usage,
            user.bill_amount,
            user.load,
            user.section,
            int(user.activity_status)
        ] for user in users]
        
        df = pd.DataFrame(data, columns=["Username", "Current_Usage", "Past_Usage", "Avg_Usage", "Bill_Amount", "Load", "Section", "Activity_Status"])
        df.to_csv(CSV_PATH, mode='a', header=not os.path.exists(CSV_PATH), index=False)
        print("User data appended to CSV file.")
    except Exception as e:
        print(f"Error saving user data to CSV: {e}")
from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd
import joblib
import os

# 📌 Define file paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "train", "maintenance_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "train", "maintenance_scaler.pkl")
DATA_PATH = os.path.join(BASE_DIR, "train", "maintenance_data.csv")

# 📌 Load model and scaler with error handling
try:
    if not (os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH)):
        raise FileNotFoundError("❌ Model or scaler file missing!")

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

except Exception as e:
    raise FileNotFoundError(f"❌ Error loading model/scaler: {e}")

def maintenance_predictions():
    # 📌 Load data safely
    try:
        df = pd.read_csv(DATA_PATH)
    except Exception as e:
        return JsonResponse({"error": f"❌ Error loading data: {e}"}, status=500)

    # 📌 Ensure only valid columns are used
    feature_columns = ["Generator_ID", "Runtime_Hours", "Fuel_Consumption", 
                       "Temperature", "Vibration_Level", "Last_Maintenance_Days"]
    
    if not all(col in df.columns for col in feature_columns):
        return JsonResponse({"error": "❌ Required columns missing in dataset!"}, status=400)

    # 📌 Preprocess input
    df_filtered = df[feature_columns]

    # 📌 Convert categorical column 'Generator_ID' if necessary
    df_filtered["Generator_ID"] = df_filtered["Generator_ID"].astype("category").cat.codes

    # 📌 Scale data and predict
    try:
        scaled_data = scaler.transform(df_filtered)
        predictions = model.predict(scaled_data)
        df["prediction"] = ["Maintenance Required" if p == -1 else "Normal" for p in predictions]
    except Exception as e:
        return JsonResponse({"error": f"❌ Prediction error: {e}"}, status=500)

    # 📌 Return predictions as JSON
    return JsonResponse({"predictions": df.to_dict(orient="records")}, safe=False)

from django.shortcuts import render
import pandas as pd
import os
from users.models import generator
from users.models import section  # Assuming correct import path

# 📌 Path to power data CSV file
DATA_PATH = "train/household_power_consumption.csv"

def gross_power_data(request):
    if not os.path.exists(DATA_PATH):
        return render(request, "error.html", {"message": "Data file not found!"})

    # Load required data
    df = pd.read_csv(DATA_PATH, usecols=["Date", "Time", "Global_active_power", "Global_reactive_power", 
                                         "Voltage", "Global_intensity", "Sub_metering_1", 
                                         "Sub_metering_2", "Sub_metering_3"], nrows=100)

    # Compute Total Power
    df["Total_Power"] = df["Global_active_power"] + df["Global_reactive_power"]
    
    # Predicted Total Power (sum of all rows)
    predicted_total = df["Total_Power"].sum()

    # Fetch database values
    total_power_generated = sum(gen.current_production for gen in generator.objects.all())
    total_usage = sum(sec.load for sec in section.objects.all())

    # Section-wise Power Data
    section_data = [
        {
            "uuid": sec.uuid,
            "usage": sec.load,
            "users": sec.users
        }
        for sec in section.objects.all()
    ]

    context = {
        "power_data": df.to_dict(orient="records"),
        "total_power": total_power_generated,
        "total_usage": total_usage,
        "section_data": section_data,  # Pass section-wise data
        "predicted_total": predicted_total  # Ensure predicted value is passed
    }
    
    return render(request, 'gross.html', context)



def gross_maintenance(request):
    schedules = Schedule.objects.all()

    total_schedules = schedules.count()
    completed_count = schedules.filter(completed=True).count()
    pending_count = total_schedules - completed_count
    total_est_cost = sum(schedule.est_cost for schedule in schedules)
    total_act_cost = sum(schedule.act_cost for schedule in schedules)

    context = {
        "schedules": schedules,
        "total_schedules": total_schedules,
        "completed_count": completed_count,
        "pending_count": pending_count,
        "total_est_cost": total_est_cost,
        "total_act_cost": total_act_cost
    }
    return render(request, 'gross_maintenance.html', context)


from django.views.decorators.csrf import csrf_exempt


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
# from api_updates import user_model  # Import your models

@csrf_exempt
def update_usage_and_bill(request):
    """
    API endpoint to update usage details, bill amount, and section load for a user.
    Expects a POST request with a JSON payload.

    Example payload:
    {
        "uuid": "user123",
        "current_usage": 150,
        "past_usage": 200,
        "avg_usage": 175,
        "bill_amount": 50,
        "load": 80,
        "section": "A"
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid HTTP method. Use POST."}, status=405)

    # Parse JSON data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    # Validate required field
    user_uuid = data.get("uuid")
    if not user_uuid:
        return JsonResponse({"error": "User UUID is required."}, status=400)

    # Get the user instance
    try:
        user_instance = user_model.bear.objects.get(uuid=user_uuid)
    except user_model.bear.DoesNotExist:
        return JsonResponse({"error": f"User with UUID '{user_uuid}' not found."}, status=404)

    # Store previous section and load for adjustment
    previous_section_uuid = user_instance.section_id
    previous_load = user_instance.load

    # Update user fields if provided
    if "current_usage" in data:
        user_instance.current_usage = data["current_usage"]
    if "past_usage" in data:
        user_instance.past_usage = data["past_usage"]
    if "avg_usage" in data:
        user_instance.avg_usage = data["avg_usage"]
    if "load" in data:
        user_instance.load = data["load"]
    if "section_id" in data:
        user_instance.section_id = data["section_id"]

    # Save user updates
    try:
        user_instance.save()
    except Exception as e:
        return JsonResponse({"error": f"Error saving user data: {e}"}, status=500)

    # Update or create the bill record for this user
    try:
        bill_instance, created = user_model.bill.objects.get_or_create(user=user_uuid, defaults={"pending_amount": 0.0})
        if "bill_amount" in data:
            bill_instance.pending_amount = data["bill_amount"]
            bill_instance.save()
    except Exception as e:
        return JsonResponse({"error": f"Error updating bill data: {e}"}, status=500)

    # Update section load if "load" or "section" has changed
    if "load" in data or "section" in data:
        try:
            new_section_uuid = user_instance.section_id
            new_load = user_instance.load

            # Reduce load from previous section
            if previous_section_uuid and previous_section_uuid != new_section_uuid:
                user_model.section.objects.filter(uuid=previous_section_uuid).update(load=F("load") - previous_load)

            # Increase load for the new section
            if new_section_uuid:
                new=user_model.section.objects.filter(uuid=new_section_uuid).first()
                
                new.load=min(new.max_load,new.load+new_load)
                new.save()
        except Exception as e:
            return JsonResponse({"error": f"Error updating section load: {e}"}, status=500)
    
    update_section(user_instance.section_id)
    return JsonResponse({"message": "Usage, bill, and section load updated successfully."})

@csrf_exempt
def update_generator(request):
    """
    API endpoint to update generator details.
    Expects a POST request with a JSON payload.

    Example payload:
    {
        "uuid": "gen_001",
        "current_production": 120.5,
        "efficiency": 85.3,
        "fuel_cost": 10.5,
        "emissions": 5.2,
        "free": false,
        "canserve": 500
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid HTTP method. Use POST."}, status=405)

    # Parse JSON data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    # Validate required field
    generator_uuid = data.get("uuid")
    if not generator_uuid:
        return JsonResponse({"error": "Generator UUID is required."}, status=400)

    # Get the generator instance
    try:
        generator_instance = user_model.generator.objects.get(uuid=generator_uuid)
    except user_model.generator.DoesNotExist:
        return JsonResponse({"error": f"Generator with UUID '{generator_uuid}' not found."}, status=404)

    # Update generator fields if provided
    if "current_production" in data:
        generator_instance.current_production = data["current_production"]
    if "efficiency" in data:
        generator_instance.efficiency = data["efficiency"]
    if "fuel_cost" in data:
        generator_instance.fuel_cost = data["fuel_cost"]
    if "emissions" in data:
        generator_instance.emissions = data["emissions"]
    if "free" in data:
        generator_instance.free = data["free"]
    if "canserve" in data:
        generator_instance.canserve = data["canserve"]

    # Save generator updates
    try:
        generator_instance.save()
    except Exception as e:
        return JsonResponse({"error": f"Error saving generator data: {e}"}, status=500)

    return JsonResponse({"message": "Generator details updated successfully."})

def update_section(id):
    section = user_model.section.objects.filter(uuid=id).first()
    
    if not section:
        print(f"Grid with UUID {id} not found.")
        return
    
    try:
        # Summing up the `load` values of all users in the given section
        section.load = sum(user.load for user in user_model.bear.objects.filter(section_id=section.uuid))
        section.save()  # Save changes to the database
        update_grid(section.grids)
    except Exception as e:
        print(f"Error updating grid: {e}")
def update_grid(id):
    grid = user_model.grid.objects.filter(uuid=id).first()
    
    if not grid:
        print(f"Grid with UUID {id} not found.")
        return
    
    try:
        # Retrieve sections safely, handling missing sections
        sec1 = user_model.section.objects.filter(uuid=grid.sec1).first()
        sec2 = user_model.section.objects.filter(uuid=grid.sec2).first()
        sec3 = user_model.section.objects.filter(uuid=grid.sec3).first()

        # Initialize sum and add only existing sections
        total_load = 0
        if sec1:
            total_load += sec1.load
        else:
            print(f"Warning: Section {grid.sec1} not found.")

        if sec2:
            total_load += sec2.load
        else:
            print(f"Warning: Section {grid.sec2} not found.")

        if sec3:
            total_load += sec3.load
        else:
            print(f"Warning: Section {grid.sec3} not found.")

        # Update grid load
        grid.load = total_load
        grid.save()  # Save changes to the database
        print(f"Grid {id} load updated successfully: {total_load} kW")

    except Exception as e:
        print(f"Error updating grid {id}: {e}")

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from users.models import Complaint  # Import Complaint model
from django.views.decorators.csrf import csrf_exempt

def manage_complaints(request):
    """Admin view to manage user complaints"""
    complaints = Complaint.objects.all()

    if request.method == "POST":
        if "save_changes" in request.POST:  # Save button clicked
            complaint_id = request.POST.get("complaint_id")
            new_status = request.POST.get("status")

            if complaint_id and new_status:
                complaint = Complaint.objects.filter(id=complaint_id).first()
                if complaint:
                    complaint.status = new_status
                    complaint.save()
                    messages.success(request, f"Complaint #{complaint.id} updated to {new_status}.")

        elif "delete_complaint" in request.POST:  # Delete button clicked
            complaint_id = request.POST.get("complaint_id")
            complaint = Complaint.objects.filter(id=complaint_id).first()
            if complaint:
                complaint.delete()
                messages.success(request, f"Complaint #{complaint_id} deleted successfully.")

        return redirect("manage_complaints")

    return render(request, "manage_complaints.html", {"complaints": complaints})

from django.shortcuts import redirect
from django.contrib import messages
from users.models import bear, bill
from django.core.mail import send_mail
from django.conf import settings


def send_bill_reminder(request, user_id):
    """Send an email reminder for pending bill payment."""
    user = bear.objects.filter(uuid=user_id).first()  # Fetch user details
    if not user:
        return JsonResponse({"error": "User not found."}, status=404)

    bill = user_model.bill.objects.filter(user=user_id).first()  # Fetch the user's bill
    if not bill:
        return JsonResponse({"error": "No bill found for this user."}, status=404)

    # Email details
    subject = "Electricity Bill Payment Reminder"
    message = f"Dear {user.name},\n\nYour pending bill amount is ₹{bill.pending_amount}.\nPlease make the payment at your earliest convenience.\n\nThank you!"
    recipient_email = user.email  # Ensure email exists in `bear` model

    # Send email
    send_mail(
        subject,
        message,
        "admin@powergrid.com",  # Replace with your actual sender email
        [recipient_email],
        fail_silently=False,
    )

    return redirect("admin_panel", user_id=user_id)  # Redirect back to admin panel
