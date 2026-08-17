import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor # Changed to Regressor
import joblib
import numpy as np

# --- 1. Load Data ---
print("1. Loading and Cleaning Data for Regression...")
try:
    df = pd.read_csv('ckd_data.csv')
except FileNotFoundError:
    print("Error: ckd_data.csv not found. Please ensure the file is in the same directory.")
    exit()

# --- 2. Data Cleaning and Preprocessing ---
df.replace('?', np.nan, inplace=True)
df.replace('\t?', np.nan, inplace=True) 
df.replace('\tyes', 'yes', inplace=True) 
df.replace('\tno', 'no', inplace=True)
df.replace('ckd\t', 'ckd', inplace=True)

# Convert all columns to numeric type where possible
for col in ['age', 'bp', 'sg', 'al', 'su', 'pcv', 'hemo', 'sc']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Handle categorical data
le = LabelEncoder()
df['rbc'] = le.fit_transform(df['rbc'].astype(str))
df['bact'] = le.fit_transform(df['bact'].astype(str))

# Drop classification and unused columns
df.drop(['class', 'wbc', 'rbcc'], axis=1, errors='ignore', inplace=True)

# Fill remaining NaN values using the mean
df.fillna(df.mean(), inplace=True)

# --- 3. Feature Selection: Target is HEMOGLOBIN (Hemo) ---
target = 'hemo' # Predict Hemoglobin level over time
features = [col for col in df.columns if col != target] 
X = df[features]
y = df[target]

# --- 4. Model Training (Random Forest Regressor) ---
print("2. Training Random Forest Regressor Model...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Use Regressor for predicting continuous values
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# --- 5. Evaluation (R-squared score is used for regression) ---
r2_score = model.score(X_test, y_test)
print(f"3. Model R-squared Score: {r2_score:.2f} (Close to 1.0 is good)")

# --- 6. Save Model and Features ---
model_filename = 'ckd_regressor.pkl' # New filename
joblib.dump(model, model_filename)

# Save the feature names for consistent input mapping in Django
joblib.dump(features, 'regressor_features.pkl')

print(f"4. Success! Regression Model saved as {model_filename}")

