# Create your views here.
from django.contrib import messages
from django.shortcuts import render
import markdown
from django.utils.safestring import mark_safe
from .forms import UserRegistrationForm
from .models import UserRegistrationModel, TokenCountModel
import os
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.shortcuts import render
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LeakyReLU, BatchNormalization
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from django.conf import settings

SECRET_KEY = "ce9941882f6e044f9809bcee90a2992b4d9d9c21235ab7c537ad56517050f26b"
ALGORITHM = "HS256"


# Create your views here.
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            loginId = form.cleaned_data['loginid']
            TokenCountModel.objects.create(loginid=loginId, count=0)
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
                data = {'loginid': loginid}

                print("User id At", check.id, status)
                return render(request, 'users/UserHomePage.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})


def UserHome(request):
    return render(request, 'users/UserHomePage.html', {})


def usr_synthesis_data(request):
    if request.method == 'POST':
        company = request.POST.get('company')
        goal = request.POST.get("goal")
        from .utility import gen_synthasis_emails_data
        phishing_email, malware_description = gen_synthasis_emails_data.start_generations(company, goal)
        data1 = mark_safe(markdown.markdown(phishing_email))
        data2 = mark_safe(markdown.markdown(malware_description))
        return render(request, 'users/synthesis_result.html', {"dat1": data1, "data2": data2})

    else:
        return render(request, 'users/synthesis_data_gen.html', {})


LATENT_DIM = 100
EPOCHS = 50
BATCH_SIZE = 32
OUTPUT_DIM = 5


def generate_real_data(num_samples=1000):
    np.random.seed(42)
    data = {
        'packet_size': np.random.normal(1500, 300, num_samples).astype(int),
        'src_port': np.random.randint(1024, 65535, num_samples),
        'dest_port': np.random.choice([80, 443, 22, 21, 53], num_samples),
        'duration': np.random.uniform(0.1, 10.0, num_samples),
        'protocol_type': np.random.randint(0, 2, num_samples)
    }
    df = pd.DataFrame(data)
    df['packet_size'] = np.maximum(df['packet_size'], 100)
    return df 


def build_generator(latent_dim, output_dim):
    model = Sequential([
        Dense(256, input_dim=latent_dim), LeakyReLU(0.2), BatchNormalization(momentum=0.8),
        Dense(512), LeakyReLU(0.2), BatchNormalization(momentum=0.8),
        Dense(1024), LeakyReLU(0.2), BatchNormalization(momentum=0.8),
        Dense(output_dim, activation='tanh')
    ])
    return model


def build_discriminator(input_dim):
    model = Sequential([
        Dense(1024, input_dim=input_dim), LeakyReLU(0.2),
        Dense(512), LeakyReLU(0.2),
        Dense(256), LeakyReLU(0.2),
        Dense(1, activation='sigmoid')
    ])
    model.compile(loss='binary_crossentropy', optimizer=Adam(0.0002, 0.5), metrics=['accuracy'])
    return model


def build_gan(generator, discriminator):
    discriminator.trainable = False
    model = Sequential([generator, discriminator])
    model.compile(loss='binary_crossentropy', optimizer=Adam(0.0002, 0.5))
    return model


def generate_new_incoming_data(num_samples=200):
    normal_data_df = generate_real_data(int(num_samples * 0.8))
    num_anomalies = num_samples - normal_data_df.shape[0]
    anomalous_data = {
        'packet_size': np.random.normal(10000, 2000, num_anomalies).astype(int),
        'src_port': np.random.randint(1, 1023, num_anomalies),
        'dest_port': np.random.randint(49152, 65535, num_anomalies),
        'duration': np.random.uniform(50.0, 200.0, num_anomalies),
        'protocol_type': np.random.choice([2, 3], num_anomalies)
    }
    anomalous_df = pd.DataFrame(anomalous_data)
    anomalous_df['packet_size'] = np.maximum(anomalous_df['packet_size'], 5000)
    combined_df = pd.concat([normal_data_df, anomalous_df], ignore_index=True).sample(frac=1).reset_index(drop=True)
    combined_df['true_label'] = [0] * normal_data_df.shape[0] + [1] * anomalous_df.shape[0]
    return combined_df


def detect_anomalies(data_df, discriminator_model, scaler, threshold=0.7):
    scaled_data = scaler.transform(data_df.drop(columns=['true_label'], errors='ignore'))
    scores = discriminator_model.predict(scaled_data).flatten()
    anomaly_likelihood = 1 - scores
    predictions = (anomaly_likelihood > threshold).astype(int)

    results = data_df.copy()
    results['discriminator_score'] = scores
    results['anomaly_likelihood'] = anomaly_likelihood
    results['predicted_anomaly'] = predictions
    return results


def save_plot(fig, filename):
    path = os.path.join(settings.BASE_DIR, 'assets', 'static', 'images', filename)
    fig.savefig(path)
    plt.close(fig)


def gan_detection(request):
    real_data_df = generate_real_data(5000)
    scaler = MinMaxScaler(feature_range=(-1, 1))
    scaled_real_data = scaler.fit_transform(real_data_df)

    generator = build_generator(LATENT_DIM, OUTPUT_DIM)
    discriminator = build_discriminator(OUTPUT_DIM)
    gan = build_gan(generator, discriminator)

    d_losses, g_losses = [], []
    for epoch in range(EPOCHS):
        idx = np.random.randint(0, scaled_real_data.shape[0], BATCH_SIZE)
        real = scaled_real_data[idx]
        noise = np.random.normal(0, 1, (BATCH_SIZE, LATENT_DIM))
        fake = generator.predict(noise)

        d_loss_real = discriminator.train_on_batch(real, np.ones((BATCH_SIZE, 1)))
        d_loss_fake = discriminator.train_on_batch(fake, np.zeros((BATCH_SIZE, 1)))
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
        d_losses.append(d_loss[0])

        g_loss = gan.train_on_batch(noise, np.ones((BATCH_SIZE, 1)))
        g_losses.append(g_loss)

    # Plot training loss
    fig1 = plt.figure(figsize=(10, 5))
    plt.plot(d_losses, label='Discriminator Loss')
    plt.plot(g_losses, label='Generator Loss')
    plt.legend();
    plt.title("Training Loss")
    save_plot(fig1, "training_loss.png")

    # Plot histogram comparison
    gen_noise = np.random.normal(0, 1, (500, LATENT_DIM))
    gen_data_scaled = generator.predict(gen_noise)
    gen_df = pd.DataFrame(scaler.inverse_transform(gen_data_scaled), columns=real_data_df.columns)
    fig2 = plt.figure(figsize=(10, 5))
    plt.hist(real_data_df['packet_size'], bins=50, alpha=0.5, label='Real', density=True)
    plt.hist(gen_df['packet_size'], bins=50, alpha=0.5, label='Generated', density=True)
    plt.legend();
    plt.title("Packet Size Distribution")
    save_plot(fig2, "packet_size_distribution.png")

    incoming_data = generate_new_incoming_data(500)
    anomaly_results = detect_anomalies(incoming_data, discriminator, scaler)

    fig3 = plt.figure(figsize=(10, 5))
    plt.hist(anomaly_results[anomaly_results['true_label'] == 0]['anomaly_likelihood'], bins=50, alpha=0.5,
             label='Normal', color='green', density=True)
    plt.hist(anomaly_results[anomaly_results['true_label'] == 1]['anomaly_likelihood'], bins=50, alpha=0.5,
             label='Anomaly', color='red', density=True)
    plt.axvline(x=0.7, color='black', linestyle='--')
    plt.legend();
    plt.title("Anomaly Likelihood Distribution")
    save_plot(fig3, "anomaly_likelihood.png")

    metrics = {
        'accuracy': round(accuracy_score(anomaly_results['true_label'], anomaly_results['predicted_anomaly']), 4),
        'precision': round(precision_score(anomaly_results['true_label'], anomaly_results['predicted_anomaly']), 4),
        'recall': round(recall_score(anomaly_results['true_label'], anomaly_results['predicted_anomaly']), 4),
        'f1': round(f1_score(anomaly_results['true_label'], anomaly_results['predicted_anomaly']), 4),
        'conf_matrix': confusion_matrix(anomaly_results['true_label'], anomaly_results['predicted_anomaly']).tolist()
    }

    return render(request, "users/gan_results.html", {
        'results': anomaly_results.head(10).to_html(classes='table table-bordered', index=False),
        'metrics': metrics,
        'images': [
            'images/training_loss.png',
            'images/packet_size_distribution.png',
            'images/anomaly_likelihood.png'
        ]
    })
