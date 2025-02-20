import requests
import json

# API endpoint URL (adjust if your host/port are different)
url = "http://127.0.0.1:8000/api/update-usage-bill/"

# Sample JSON payload
payload = {
    "uuid": "1",        # Replace with a valid user uuid from your bear model
    "current_usage": 150,
    "past_usage": 200,
    "avg_usage": 175,
    "bill_amount": 50,
    "load": 80,
    "section_id": "1"
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code in (200, 201):
        print("Success:", response.json())
    else:
        print(f"Error: Status code {response.status_code}")
        print("Response:", response.text)
except Exception as e:
    print("An error occurred:", e)
