# -*- coding: utf-8 -*-
"""model_training and evaluation.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1St9eP6y2rFDNOBFVw7tUS2Ts1LJ26GKw
"""

# Model Training and Cross-Validation

import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
import joblib  # For saving models
import warnings
import os
import json  # For saving model accuracies

# Suppress warnings for cleaner output (optional)
warnings.filterwarnings('ignore')

# Load the dataset
df = pd.read_csv('feature_engineered_dataset.csv')
print(f"Dataset Loaded. Shape: {df.shape}")

# Define feature columns and target
feature_cols = [
    'temperature', 'longitude', 'latitude',
    'traffic_high', 'traffic_low', 'traffic_moderate',
    'weather_cloudy', 'weather_rain', 'weather_sunny',
    'gp_combined', 'robi_combined', 'bl_combined'
]
X = df[feature_cols]
y = df['best_provider_encoded']

# Stratified K-Fold Cross-Validation
n_splits = 5
skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

# Initialize models
models = {
    'Random Forest': RandomForestClassifier(random_state=42),
    'Extra Trees': ExtraTreesClassifier(random_state=42),
    'SVM': SVC(probability=True, random_state=42),
    'XGBoost': XGBClassifier(eval_metric='mlogloss', random_state=42)  # Removed use_label_encoder
}

# Define parameter grids for each model
param_grids = {
    'Random Forest': {
        'n_estimators': [100, 200, 300],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5, 10]
    },
    'Extra Trees': {
        'n_estimators': [100, 200, 300],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5, 10]
    },
    'SVM': {
        'C': [0.1, 1, 10],
        'kernel': ['linear', 'rbf'],
        'gamma': ['scale', 'auto']
    },
    'XGBoost': {
        'n_estimators': [100, 200, 300],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2]
    }
}

# Function to perform Grid Search CV and evaluate models
def evaluate_model(model_name, model, param_grid, X, y, skf):
    print(f"\n=== Training and Evaluating {model_name} ===")
    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=skf,
        scoring='accuracy',
        n_jobs=-1,
        verbose=1  # To monitor progress
    )
    grid_search.fit(X, y)
    best_model = grid_search.best_estimator_
    best_params = grid_search.best_params_
    best_score = grid_search.best_score_
    print(f"Best Parameters for {model_name}: {best_params}")
    print(f"Best Cross-Validation Accuracy for {model_name}: {best_score:.4f}")

    # Evaluate best model with cross-validation
    accuracies = cross_val_score(best_model, X, y, cv=skf, scoring='accuracy')
    mean_accuracy = accuracies.mean()
    print(f"Cross-Validation Accuracies for {model_name}: {accuracies}")
    print(f"Mean CV Accuracy for {model_name}: {mean_accuracy:.4f}")

    # Return the best model and its mean accuracy
    return best_model, mean_accuracy

# Dictionaries to store the best models and their mean accuracies
best_models = {}
model_accuracies = {}

# Create directory to save models if it doesn't exist
os.makedirs('best_models', exist_ok=True)

# Evaluate each model
for model_name in models:
    best_model, mean_accuracy = evaluate_model(
        model_name,
        models[model_name],
        param_grids[model_name],
        X,
        y,
        skf
    )
    best_models[model_name] = best_model
    model_accuracies[model_name] = mean_accuracy

    # Save the best model to disk
    model_filename = f"best_models/best_model_{model_name.replace(' ', '_')}.pkl"
    joblib.dump(best_model, model_filename)
    print(f"Saved {model_name} model to {model_filename}")

# Identify the best model based on mean cross-validation accuracy
best_model_name = max(model_accuracies, key=model_accuracies.get)
best_model = best_models[best_model_name]
best_model_accuracy = model_accuracies[best_model_name]

print(f"\n=== Best Model: {best_model_name} ===")
print(f"Mean CV Accuracy: {best_model_accuracy:.4f}")
print(f"Model saved at: best_models/best_model_{best_model_name.replace(' ', '_')}.pkl")

# Save the best model's name to a text file for easy reference
best_model_name_file = 'best_models/best_model_name.txt'
with open(best_model_name_file, 'w') as f:
    f.write(best_model_name)

print(f"Saved the best model's name to '{best_model_name_file}'.")

# Optionally, save the accuracies dictionary for future reference
accuracies_file = 'best_models/model_accuracies.json'
with open(accuracies_file, 'w') as f:
    json.dump(model_accuracies, f)

print(f"Saved all models' accuracies to '{accuracies_file}'.")