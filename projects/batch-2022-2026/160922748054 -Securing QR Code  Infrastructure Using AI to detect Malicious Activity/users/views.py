# views.py

from django.shortcuts import render, HttpResponse
from .forms import UserRegistrationForm
from django.contrib import messages
from .models import UserRegistrationModel
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import pandas as pd
import numpy as np
import cv2
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping

# Globals
global_model = None
vectorizer = None
label_encoder = None
model_path = 'saved_models/url_classifier_rf.pkl'

# Load Dataset
def load_dataset():
    df = pd.read_csv(r'C:\Users\Zubair\Desktop\QR_detection2\media\malicious_phish.csv')
    df.dropna(inplace=True)
    return df

# User Registration
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have been successfully registered')
            return render(request, 'UserRegistrations.html', {'form': UserRegistrationForm()})
        else:
            messages.error(request, 'Email or Mobile already existed.')
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})

# User Login
def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            if check.status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                return render(request, 'users/UserHome.html')
            else:
                messages.warning(request, 'Your account is not activated.')
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, 'Invalid Login ID or Password.')
    return render(request, 'UserLogin.html')

# User Home
def UserHome(request):
    return render(request, 'users/UserHome.html')

# View Dataset
def DatasetView(request):
    try:
        df = load_dataset()
        df_sample = df[['url', 'type']].head(100)  # Only show 100 rows with specific columns
        df_html = df_sample.to_html(classes='table table-striped', index=False)
        return render(request, 'users/viewdataset.html', {'data': df_html})
    except Exception as e:
        return HttpResponse(f"Error loading dataset: {str(e)}")

# Training View (Modified)
def training(request):
    try:
        # Load dataset
        df = load_dataset()
        
        # Optional: Subsample dataset if too large to speed up training
        # Adjust sample_size based on your dataset size and available memory
        sample_size = min(100000, len(df))  # Cap at 100k samples for faster training
        if sample_size < len(df):
            df = df.groupby('type').apply(lambda x: x.sample(frac=sample_size/len(df), random_state=42)).reset_index(drop=True)
        
        X = df['url']
        y = df['type']

        # Encode labels
        global label_encoder
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)

        # Vectorize URLs with optimized TF-IDF
        # Reduced max_features and added n-grams for better feature representation
        global vectorizer
        vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2), sublinear_tf=True)
        X_vectorized = vectorizer.fit_transform(X)

        # Save vectorized data to disk to avoid recomputing in future runs
        vectorized_path = 'saved_models/X_vectorized.npz'
        joblib.dump((X_vectorized, y_encoded), vectorized_path)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

        # Random Forest with parallel processing
        rf_model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)  # Reduced estimators, parallelized
        rf_model.fit(X_train, y_train)
        rf_pred = rf_model.predict(X_test)
        rf_acc = accuracy_score(y_test, rf_pred)
        rf_precision = precision_score(y_test, rf_pred, average='macro')
        rf_recall = recall_score(y_test, rf_pred, average='macro')
        rf_f1 = f1_score(y_test, rf_pred, average='macro')

        # Neural Network with optimized architecture
        # Avoid dense conversion by using a smaller network and batch size
        nn_model = Sequential([
            Dense(64, input_shape=(X_vectorized.shape[1],), activation='relu'),  # Reduced size
            Dense(32, activation='relu'),
            Dense(len(np.unique(y_encoded)), activation='softmax')
        ])
        nn_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        # Adjust batch size and epochs for faster training
        history = nn_model.fit(
            X_train.toarray(),  # Convert to dense only for NN (unavoidable in Keras)
            y_train,
            validation_split=0.2,
            epochs=10,  # Reduced epochs
            batch_size=64,  # Increased batch size for faster processing
            callbacks=[EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True)],
            verbose=0
        )

        # Evaluate Neural Network
        nn_loss, nn_acc = nn_model.evaluate(X_test.toarray(), y_test, verbose=0)

        # Save models
        global global_model
        global_model = rf_model  # Use RF for predictions as it's faster
        os.makedirs('saved_models', exist_ok=True)
        joblib.dump((rf_model, vectorizer, label_encoder), model_path)

        # Save NN model separately if needed for future use
        nn_model.save('saved_models/nn_model.h5')

        return render(request, 'users/training.html', {
            'rf_acc': round(rf_acc, 4),
            'rf_precision': round(rf_precision, 4),
            'rf_recall': round(rf_recall, 4),
            'rf_f1': round(rf_f1, 4),
            'nn_acc': round(nn_acc, 4),
            'nn_loss': round(nn_loss, 4),
        })

    except Exception as e:
        return HttpResponse(f"Error during training: {str(e)}")

# Prediction View
def prediction(request):
    global global_model, vectorizer, label_encoder

    if request.method == 'POST' and request.FILES.get('qr_image'):
        try:
            img_file = request.FILES['qr_image']
            fs = FileSystemStorage()
            filename = fs.save(img_file.name, img_file)
            filepath = fs.path(filename)

            image = cv2.imread(filepath)
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(image)

            if not data:
                raise ValueError("No QR code found in image.")

            qr_data = data.strip()

            if global_model is None:
                if os.path.exists(model_path):
                    global_model, vectorizer, label_encoder = joblib.load(model_path)
                else:
                    raise ValueError("Model not trained yet. Please train the model first.")

            input_vector = vectorizer.transform([qr_data])
            pred = global_model.predict(input_vector)[0]
            predicted_label = label_encoder.inverse_transform([pred])[0]

            return render(request, 'users/predictForm1.html', {
                'output': f'Detected URL: {qr_data}<br>Predicted Type: <strong>{predicted_label}</strong>',
                'features': ['qr_image']
            })

        except Exception as e:
            return render(request, 'users/predictForm1.html', {
                'output': f"Error: {str(e)}",
                'features': ['qr_image']
            })

    return render(request, 'users/predictForm1.html', {
        'features': ['qr_image']
    })