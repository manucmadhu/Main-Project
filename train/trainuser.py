import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Read the dataset into a DataFrame (Ensure the correct path is provided)
df = pd.read_csv('train/user_dataset.csv')

# Drop rows where the target variable has missing values (for the target 'load')
df = df.dropna(subset=['load'])

# Identify numeric and categorical features
numeric_features = ['current_usage', 'past_usage', 'avg_usage', 'bill_amount', 'load']
categorical_features = ['section', 'activity_status']

# Custom transformer for LabelEncoder to apply on each column individually
class CustomLabelEncoder(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        # Apply LabelEncoder on each column individually
        self.encoders = [LabelEncoder().fit(X[:, i]) for i in range(X.shape[1])]
        return self

    def transform(self, X):
        # Apply the transformation and return the encoded result
        return np.column_stack([encoder.transform(X[:, i]) for i, encoder in enumerate(self.encoders)])

# Create transformers for each type of feature

# Numeric transformer - Impute missing values with mean and standardize the data
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),  # Use mean for numeric columns
    ('scaler', StandardScaler())  # Standardize the numeric features (optional)
])

# Categorical transformer - Impute missing values with most frequent value and encode labels
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),  # Use most frequent for categorical columns
    ('encoder', CustomLabelEncoder())  # Encode categorical features using custom LabelEncoder
])

# Combine transformers into a column transformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Apply the preprocessor to the dataset
X = df[numeric_features + categorical_features]  # Select only the required features
X_transformed = preprocessor.fit_transform(X)

# Optional: Convert the transformed data back to a DataFrame for further processing
transformed_df = pd.DataFrame(X_transformed)

# Save the transformed features as 'user_features.pkl'
joblib.dump(X_transformed, 'train/user_features.pkl')

# Split the data into features and target (For demonstration, the target is 'load')
X = df[numeric_features + categorical_features]
y = df['load']  # Replace with your actual target column

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Apply the preprocessing pipeline to the training data
X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)  # Apply the same transformation to the test set

# Train a RandomForest model (replace with any model you'd like)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_transformed, y_train)

# Save the preprocessing pipeline
joblib.dump(preprocessor, 'preprocessor.pkl')

# Save the scaler separately
scaler = numeric_transformer.named_steps['scaler']
joblib.dump(scaler, 'train/user_scaler.pkl')

# Save the trained model
joblib.dump(model, 'model.pkl')

print("Preprocessing pipeline, scaler, features, and model saved successfully!")
