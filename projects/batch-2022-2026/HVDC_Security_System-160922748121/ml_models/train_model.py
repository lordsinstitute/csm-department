"""
HVDC CyberSec - Random Forest Model Trainer
Run: python ml_models/train_model.py
Saves: ml_models/hvdc_rf_model.pkl
       ml_models/scaler.pkl
"""
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (classification_report, confusion_matrix,
                             accuracy_score, precision_score,
                             recall_score, f1_score)

# ── Load Dataset ──────────────────────────────────────────────────────
print('Loading dataset...')
df = pd.read_csv('datasets/hvdc_cyber_dataset.csv')
print(f'Shape: {df.shape}')

FEATURES = [
    'dc_voltage', 'dc_current', 'ac_voltage_rectifier',
    'ac_voltage_inverter', 'active_power', 'reactive_power',
    'firing_angle_rectifier', 'extinction_angle_inverter',
    'network_packet_rate', 'communication_latency'
]
TARGET = 'label'

X = df[FEATURES]
y = df[TARGET]

# ── Split ─────────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f'Train: {len(X_train)} | Test: {len(X_test)}')

# ── Scale Features ────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# ── Train Model ───────────────────────────────────────────────────────
print('Training Random Forest...')
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)
model.fit(X_train_sc, y_train)

# ── Evaluate ──────────────────────────────────────────────────────────
y_pred = model.predict(X_test_sc)
acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, average='weighted')
rec  = recall_score(y_test, y_pred, average='weighted')
f1   = f1_score(y_test, y_pred, average='weighted')

print('\n=== Model Evaluation ===')
print(f'Accuracy:  {acc:.4f}')
print(f'Precision: {prec:.4f}')
print(f'Recall:    {rec:.4f}')
print(f'F1 Score:  {f1:.4f}')
print('\nClassification Report:')
label_names = ['Normal','DoS','FDI','Cmd Manip','Replay']
print(classification_report(y_test, y_pred, target_names=label_names))

print('\nConfusion Matrix:')
print(confusion_matrix(y_test, y_pred))

# Cross-validation
cv_scores = cross_val_score(model, X_train_sc, y_train, cv=5, scoring='accuracy')
print(f'\nCross-Val Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})')

# Feature importance
print('\nFeature Importances:')
for feat, imp in sorted(zip(FEATURES, model.feature_importances_),
                         key=lambda x: x[1], reverse=True):
    print(f'  {feat:35s}: {imp:.4f}')

# ── Save Model ────────────────────────────────────────────────────────
os.makedirs('ml_models', exist_ok=True)
joblib.dump(model,  'ml_models/hvdc_rf_model.pkl')
joblib.dump(scaler, 'ml_models/scaler.pkl')
print('\nModel saved: ml_models/hvdc_rf_model.pkl')
print('Scaler saved: ml_models/scaler.pkl')
print('Training complete!')
