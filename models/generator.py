import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv("models/generator_ranking_dataset.csv")

# Encode categorical variables
df["Generator_Type"] = df["Generator_Type"].astype("category").cat.codes

# Features (X) and Target (y)
X = df.drop(columns=["Generator_ID", "Overall_Rank"])
y = df["Overall_Rank"].astype(int)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate performance
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save model in a common location
joblib.dump(model, "models/generator_ranking_model.pkl")  # Save inside 'models/' directory

print("Model trained and saved successfully!")
