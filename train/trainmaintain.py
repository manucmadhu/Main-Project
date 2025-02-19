import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 📌 Load CSV file and handle errors
try:
    df = pd.read_csv("train/maintenance_data.csv", usecols=[
        "Generator_ID", "Runtime_Hours", "Fuel_Consumption",
        "Temperature", "Vibration_Level", "Last_Maintenance_Days", "Failure_Risk"
    ])
    print("✅ Data Loaded Successfully!")
except Exception as e:
    print(f"❌ Error Loading Data: {e}")
    exit()

# 📌 Remove missing values
df.dropna(inplace=True)

# 📌 Convert 'Generator_ID' to numerical encoding
df["Generator_ID"] = df["Generator_ID"].astype("category").cat.codes

# 📌 Separate features (X) and target variable (y)
X = df.drop(columns=["Failure_Risk"])
y = df["Failure_Risk"]

# 📌 Split data into training & testing sets (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 📌 Normalize features using StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 📌 Train a RandomForest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# 📌 Predict and evaluate accuracy
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model Trained Successfully! Accuracy: {accuracy:.2f}")

# 📌 Save trained model & scaler for future use
with open("train/maintenance_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("train/maintenance_scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

print("✅ Model & Scaler Saved Successfully!")
