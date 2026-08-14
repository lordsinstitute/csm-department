import pickle
from django.shortcuts import render
from django.contrib import messages
from sklearn.svm import SVC
from .forms import UserRegistrationForm
from .models import UserRegistrationModel
from django.conf import settings
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    roc_curve,
    auc,
    log_loss
)

# Load and preprocess dataset once
df = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'railway_powerline_fault_data_balanced_5000.csv'))
label_encoder = LabelEncoder()
df["Fault_Type"] = label_encoder.fit_transform(df["Fault_Type"])
class_names = label_encoder.classes_  # Extract class names from the dataset
x = df[['Voltage', 'Current', 'Temperature', 'Vibration', 'Load', 'Speed']]  # Updated feature columns
y = df['Fault_Type']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=39)

# Initialize and fit scaler globally
scaler = StandardScaler()
scaler.fit(x_train)

def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        else:
            messages.success(request, 'Email or Mobile Already Existed')
            print("Invalid form")
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})

def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHomePage.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})

def UserHome(request):
    return render(request, 'users/UserHomePage.html', {})

def DatasetView(request):
    path = os.path.join(settings.MEDIA_ROOT, 'railway_powerline_fault_data_balanced_5000.csv')
    df = pd.read_csv(path)
    df_html = df.to_html(classes='table table-striped', index=False)
    return render(request, 'users/viewdataset.html', {'data': df_html})

def Training(request):
    # Ensure media directory exists and is writable
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    # Train the model
    model = RandomForestClassifier(random_state=42, class_weight="balanced")
    model.fit(x_train, y_train)  # Use unscaled data for consistency with prediction
    output_path = os.path.join(settings.MEDIA_ROOT, 'rfc.pkl')

    # open in binary-write mode
    with open(output_path, 'wb') as f:
        pickle.dump(model, f)
    y_train_pred = model.predict(x_train)
    y_test_pred = model.predict(x_test)
    y_pred = y_test_pred  # Define y_pred after model is trained

    # Calculate metrics
    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    train_loss = log_loss(y_train, model.predict_proba(x_train))
    test_loss = log_loss(y_test, model.predict_proba(x_test))

    # Save plots with high DPI for clarity
    def save_plot(fig, filename):
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        fig.savefig(filepath, dpi=100, bbox_inches='tight')
        fig.clear()  # Clear figure to free memory
        print(f"Saved plot to: {filepath}")

    # Accuracy Plot
    plt.figure(figsize=(6, 4))
    plt.bar(['Train Accuracy', 'Test Accuracy'], [train_acc, test_acc], color=['green', 'blue'])
    plt.ylim(0, 1)
    plt.title('Train vs Test Accuracy')
    plt.ylabel('Accuracy')
    plt.grid(True)
    save_plot(plt.gcf(), 'accuracy_plot.png')

    # Loss Plot
    plt.figure(figsize=(6, 4))
    plt.bar(['Train Loss', 'Test Loss'], [train_loss, test_loss], color=['red', 'orange'])
    plt.title('Train vs Test Log Loss')
    plt.ylabel('Log Loss')
    plt.grid(True)
    save_plot(plt.gcf(), 'loss_plot.png')

    # ROC Curve (for binary classification)
    roc_plot_path = None
    roc_auc = None
    if len(np.unique(y_test)) == 2:
        y_score = model.predict_proba(x_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_score)
        roc_auc = auc(fpr, tpr)
        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.2f}", color="darkblue")
        plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve")
        plt.legend()
        plt.grid(True)
        save_plot(plt.gcf(), 'roc_plot.png')
        roc_plot_path = os.path.join(settings.MEDIA_ROOT, 'roc_plot.png')

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_test_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted Class")
    plt.ylabel("True Class")
    save_plot(plt.gcf(), 'confusion_matrix.png')

    # Context with full media URLs
    context = {
        'train_acc': train_acc,
        'test_acc': test_acc,
        'train_loss': train_loss,
        'test_loss': test_loss,
        'roc_auc': roc_auc,
        'accuracy_plot': f"{settings.MEDIA_URL}accuracy_plot.png",
        'loss_plot': f"{settings.MEDIA_URL}loss_plot.png",
        'roc_plot': f"{settings.MEDIA_URL}roc_plot.png" if roc_plot_path else None,
        'confusion_matrix': f"{settings.MEDIA_URL}confusion_matrix.png",
    }
    print(f"✅ Test Accuracy: {test_acc * 100:.2f}%")
    return render(request, 'users/training.html', context)

def Prediction(request):
    
    # Simulated training data (replace with your actual x_train and y_train)
    x_train = np.array([
        [230.0, 14.0, 45.0, 0.55, 106.0, 61.0],  # overloading
        [240.0, 15.0, 50.0, 0.60, 110.0, 65.0],  # flctuation
        [200.0, 12.0, 40.0, 0.50, 100.0, 55.0],  # no fault
        [235.0, 13.5, 47.0, 0.58, 108.0, 63.0],  # risk
        [225.0, 13.0, 43.0, 0.53, 104.0, 59.0],  # overloading
        [245.0, 16.0, 52.0, 0.62, 112.0, 67.0]   # flctuation
    ])
    y_train = np.array([0, 1, 2, 3, 0, 1])

    # Define class names
    class_names = ["Overload", "Fluctuation", "No Fault", "Derailment Risk"]

    # Initialize and fit the scaler
    scaler = StandardScaler()
    scaler.fit(x_train)

    # Train the model
    model = RandomForestClassifier(random_state=42, class_weight="balanced")
    model.fit(scaler.transform(x_train), y_train)


    if request.method == 'POST':
        # Get input from form (updated to new fields)
        try:
            voltage = float(request.POST.get('voltage', 0.0))
            current = float(request.POST.get('current', 0.0))
            temperature = float(request.POST.get('temperature', 0.0))
            vibration = float(request.POST.get('vibration', 0.0))
            load = float(request.POST.get('load', 0.0))
            speed = float(request.POST.get('speed', 0.0))

            # Create sample input array with the new fields
            sample_input_raw = np.array([[voltage, current, temperature, vibration, load, speed]])

            # Scale the input using the global scaler
            sample_input_scaled = scaler.transform(sample_input_raw)

            # Predict
            class_names = ["Overload", "Fluctuation", "No Fault", "Derailment Risk"]

            predicted_class_idx = model.predict(sample_input_scaled)[0]
            predicted_class = class_names[predicted_class_idx]
            probability = model.predict_proba(sample_input_scaled).max() * 100  # Confidence percentage

            context = {
                'predicted_class': predicted_class,
                'probability': probability,
                'voltage': voltage,
                'current': current,
                'temperature': temperature,
                'vibration': vibration,
                'load': load,
                'speed': speed,
            }
            return render(request, 'users/predict_form.html', context)
        except ValueError as e:
            messages.error(request, 'Please enter valid numerical values for all fields.')
            return render(request, 'users/predict_form.html', {'error': 'Invalid input'})

    return render(request, 'users/predict_form.html')