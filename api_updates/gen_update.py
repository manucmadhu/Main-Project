import requests
import json

# Define the API endpoint
API_URL = "http://127.0.0.1:8000/api/update_generator/"  # Update if needed

# Sample test data
payload = {
    "uuid": "1",  # Replace with an existing generator UUID
    "current_production": 120.5,
    "efficiency": 85.3,
    "fuel_cost": 10.5,
    "emissions": 5.2,
    "free": False,
    
}

# Set headers for JSON request
headers = {"Content-Type": "application/json"}

# Send POST request
response = requests.post(API_URL, data=json.dumps(payload), headers=headers)

# Print the response
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
