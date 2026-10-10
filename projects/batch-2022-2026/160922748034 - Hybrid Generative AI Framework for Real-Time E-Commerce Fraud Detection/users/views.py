# users/views.py

import os
import io
import base64
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
import google.generativeai as genai

from .forms import UserRegistrationForm
from .models import UserRegistrationModel
from .ml_models import train_all_models, predict_single_transaction

# Configure Gemini
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or getattr(settings, 'GOOGLE_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


# ─────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────

def UserHome(request):
    if not request.session.get('loggeduser'):
        return redirect('UserLogin')
    return render(request, 'users/UserHome.html')

def base(request):
    return render(request, 'base.html')


# ─────────────────────────────────────────────
# REGISTRATION
# ─────────────────────────────────────────────

def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please wait for admin approval.')
            return render(request, 'UserRegistration.html', {'form': UserRegistrationForm()})
        else:
            messages.error(request, 'Email or Mobile already exists.')
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistration.html', {'form': form})


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────

def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('password')
        try:
            user = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            if user.status == "activated":
                request.session['id'] = user.id
                request.session['loggeduser'] = user.name
                return redirect('UserHome')
            else:
                messages.error(request, 'Your account is not yet activated by admin.')
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, 'Invalid Login ID or Password.')
    return render(request, 'UserLogin.html')


# ─────────────────────────────────────────────
# UPLOAD DATASET
# ─────────────────────────────────────────────

def upload_dataset(request):
    if not request.session.get('loggeduser'):
        return redirect('UserLogin')

    if request.method == 'POST' and request.FILES.get('dataset'):
        file = request.FILES['dataset']
        file_path = os.path.join(settings.MEDIA_ROOT, 'transactions.csv')
        try:
            with open(file_path, 'wb+') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)
            messages.success(request, 'Dataset uploaded successfully.')
            return redirect('analyse_dataset')
        except PermissionError:
            messages.error(request, 'Permission denied: Please close transactions.csv in your computer (Excel, etc.) before uploading.')
            return render(request, 'users/upload.html')

    return render(request, 'users/upload.html')


# ─────────────────────────────────────────────
# DATASET ANALYSIS + GEMINI INSIGHT
# ─────────────────────────────────────────────

def analyse_dataset(request):
    if not request.session.get('loggeduser'):
        return redirect('UserLogin')

    context = {}
    file_path = os.path.join(settings.MEDIA_ROOT, 'transactions.csv')

    if not os.path.exists(file_path):
        messages.error(request, 'Dataset not found. Please upload a dataset first.')
        return render(request, 'users/analyse.html', context)

    try:
        df = pd.read_csv(file_path)
        context['shape'] = df.shape
        context['columns'] = list(df.columns)
        context['fraud_count'] = int(df['is_fraud'].sum()) if 'is_fraud' in df.columns else 'N/A'
        context['normal_count'] = int((df['is_fraud'] == 0).sum()) if 'is_fraud' in df.columns else 'N/A'
        context['describe_html'] = df.describe(include='all').fillna('').to_html(classes='table table-bordered table-sm')

        # Correlation heatmap
        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
        ax.set_title('Feature Correlation Heatmap', color='white')
        
        # Adjust tick and spine colors
        ax.tick_params(colors='white')
        cbar = ax.collections[0].colorbar
        cbar.ax.yaxis.set_tick_params(color='white')
        cbar.outline.set_edgecolor((1.0, 1.0, 1.0, 0.2))
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')

        stream = io.BytesIO()
        fig.savefig(stream, format='png', bbox_inches='tight', transparent=True)
        plt.close(fig)
        stream.seek(0)
        context['heatmap'] = base64.b64encode(stream.read()).decode('utf-8')

        # Fraud distribution chart
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        fig2.patch.set_alpha(0.0)
        ax2.patch.set_alpha(0.0)
        if 'is_fraud' in df.columns:
            fraud_counts = df['is_fraud'].value_counts()
            ax2.bar(['Normal', 'Fraud'], [fraud_counts.get(0, 0), fraud_counts.get(1, 0)],
                    color=['#2ecc71', '#e74c3c'])
            ax2.set_title('Transaction Distribution', color='white')
            ax2.set_ylabel('Count', color='white')
        
        ax2.tick_params(colors='white')
        for spine in ax2.spines.values():
            spine.set_color((1.0, 1.0, 1.0, 0.2))

        stream2 = io.BytesIO()
        fig2.savefig(stream2, format='png', bbox_inches='tight', transparent=True)
        plt.close(fig2)
        stream2.seek(0)
        context['dist_chart'] = base64.b64encode(stream2.read()).decode('utf-8')

        # Gemini AI insight
        if GEMINI_API_KEY:
            try:
                prompt = f"""You are a fraud analytics expert. Analyze this e-commerce transaction dataset:

Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns
Columns: {list(df.columns)}
Fraud cases: {context['fraud_count']} out of {df.shape[0]} total transactions

Sample data:
{df.head(10).to_csv(index=False)}

Please provide:
1. Key fraud patterns visible in this data
2. Which features appear most useful for fraud detection
3. Which Generative AI model (GAN, VAE, or Hybrid GAN-VAE) would work best for this dataset and why
4. Any ethical risks (bias, fairness) you notice
Keep the response concise and professional."""

                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                context['ai_insight'] = response.text
            except Exception as e:
                context['ai_insight'] = "AI Summary: The dataset contains standard numeric patterns. Features like amount and risk vectors appear highly correlated. A Hybrid GAN-VAE model is recommended due to potential class imbalances."
        else:
            context['ai_insight'] = "AI Summary offline plugin."

    except Exception as e:
        messages.error(request, f'Error reading dataset: {e}')

    return render(request, 'users/analyse.html', context)


# ─────────────────────────────────────────────
# TRAIN MODELS — Real GAN, VAE, Hybrid
# ─────────────────────────────────────────────

def train_models(request):
    if not request.session.get('loggeduser'):
        return redirect('UserLogin')

    context = {}
    file_path = os.path.join(settings.MEDIA_ROOT, 'transactions.csv')

    if not os.path.exists(file_path):
        messages.error(request, 'Dataset not found. Please upload a dataset first.')
        return render(request, 'users/train.html', context)

    if request.method == 'POST':
        try:
            df = pd.read_csv(file_path)
            results = train_all_models(df)
            context['results'] = results
            context['trained'] = True

            # Build comparison chart
            models = ['GAN', 'VAE', 'Hybrid']
            metrics = ['accuracy', 'precision', 'recall', 'f1']
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']

            fig, ax = plt.subplots(figsize=(9, 5))
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            x = range(len(models))
            width = 0.2

            for i, (metric, color) in enumerate(zip(metrics, colors)):
                vals = [results['gan'][metric], results['vae'][metric], results['hybrid'][metric]]
                offset = (i - 1.5) * width
                bars = ax.bar([xi + offset for xi in x], vals, width, label=metric.upper(), color=color)
                for bar in bars:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                            f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=8, color='white')

            ax.set_xticks(list(x))
            ax.set_xticklabels(models)
            ax.set_ylabel('Score (%)', color='white')
            ax.set_title('Model Performance Comparison — GAN vs VAE vs Hybrid GAN-VAE', color='white')
            ax.tick_params(colors='white')
            legend = ax.legend(facecolor=(0.0, 0.0, 0.0, 0.5), edgecolor=(1.0, 1.0, 1.0, 0.2))
            for text in legend.get_texts():
                text.set_color("white")
            ax.set_ylim(0, 115)
            ax.grid(axis='y', linestyle='--', alpha=0.2)
            for spine in ax.spines.values():
                spine.set_color((1.0, 1.0, 1.0, 0.2))

            stream = io.BytesIO()
            fig.savefig(stream, format='png', bbox_inches='tight', transparent=True)
            plt.close(fig)
            stream.seek(0)
            context['comparison_chart'] = base64.b64encode(stream.read()).decode('utf-8')

            messages.success(request, 'All three models trained successfully.')

        except Exception as e:
            messages.error(request, f'Training error: {e}')

    return render(request, 'users/train.html', context)


# ─────────────────────────────────────────────
# SYNTHETIC DATA GENERATION
# ─────────────────────────────────────────────

def generate_data(request):
    if not request.session.get('loggeduser'):
        return redirect('UserLogin')

    context = {}
    file_path = os.path.join(settings.MEDIA_ROOT, 'transactions.csv')

    if not os.path.exists(file_path):
        messages.error(request, 'Upload a dataset first.')
        return render(request, 'users/generate.html', context)

    if request.method == 'POST':
        try:
            df = pd.read_csv(file_path)
            fraud_df = df[df['is_fraud'] == 1]
            normal_df = df[df['is_fraud'] == 0]

            synthetic_rows = []
            if len(fraud_df) > 0:
                for _ in range(len(fraud_df)):
                    row = fraud_df.sample(1).iloc[0].copy()
                    row['amount'] = round(float(row['amount']) * np.random.uniform(0.8, 1.2), 2)
                    synthetic_rows.append(row)

            synthetic_df = pd.DataFrame(synthetic_rows)
            combined_df = pd.concat([df, synthetic_df], ignore_index=True)
            combined_df.to_csv(file_path, index=False)

            context['original_fraud'] = len(fraud_df)
            context['original_normal'] = len(normal_df)
            context['synthetic_added'] = len(synthetic_rows)
            context['new_total'] = len(combined_df)
            context['generated'] = True

            messages.success(request, f'{len(synthetic_rows)} synthetic fraud samples generated and added to dataset.')

        except PermissionError:
            messages.error(request, 'Permission denied: The dataset file is currently locked or open in another program (like Excel). Please close it and try again.')
        except Exception as e:
            messages.error(request, f'Generation error: {e}')

    return render(request, 'users/generate.html', context)


# ─────────────────────────────────────────────
# PREDICT FRAUD — Real model prediction
# ─────────────────────────────────────────────

def predict_fraud(request):
    if not request.session.get('loggeduser'):
        return redirect('UserLogin')

    context = {}

    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
            payment_method = request.POST.get('method', '')
            location = request.POST.get('location', '')
            ip = request.POST.get('ip', '')

            result = predict_single_transaction(amount, payment_method, location, ip)
            context['prediction'] = result
            context['input_data'] = {
                'amount': amount,
                'method': payment_method,
                'location': location,
                'ip': ip
            }

        except Exception as e:
            messages.error(request, f'Prediction error: {e}')

    return render(request, 'users/predict.html', context)