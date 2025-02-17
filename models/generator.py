import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor  # Example model

# Load dataset
df = pd.read_csv("models\generator_ranking_dataset.csv")

# Encode categorical data
label_encoder = LabelEncoder()
df["Generator_Type"] = label_encoder.fit_transform(df["Generator_Type"])

# Train model
X = df.drop(columns=["Overall_Rank"])  # Features
y = df["Overall_Rank"]  # Target

model = RandomForestRegressor()
model.fit(X, y)

# Save model & encoder
joblib.dump(model, "generator_ranking_model.pkl")
joblib.dump(label_encoder, "generator_encoder.pkl")
joblib.dump(list(X.columns), "feature_names.pkl")  # Save feature names
