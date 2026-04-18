import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Reshape, LeakyReLU, BatchNormalization
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# --- Configuration ---
LATENT_DIM = 100 # Dimension of the latent space for the generator
EPOCHS = 500    # Number of training epochs
BATCH_SIZE = 32  # Batch size for training
OUTPUT_DIM = 5   # Number of features for our synthetic network traffic (e.g., [packet_size, src_port, dest_port, duration, protocol_type])

# --- 1. Generate a "real" (simulated benign) dataset ---
def generate_real_data(num_samples=1000):
    """
    Generates a simple, simulated dataset representing benign network traffic.
    Features: packet_size, src_port, dest_port, duration, protocol_type (0 for TCP, 1 for UDP)
    """
    np.random.seed(42) # for reproducibility
    data = {
        'packet_size': np.random.normal(1500, 300, num_samples).astype(int), # Avg packet size around 1500 bytes
        'src_port': np.random.randint(1024, 65535, num_samples),
        'dest_port': np.random.choice([80, 443, 22, 21, 53], num_samples), # Common ports
        'duration': np.random.uniform(0.1, 10.0, num_samples),
        'protocol_type': np.random.randint(0, 2, num_samples) # 0 for TCP, 1 for UDP
    }
    df = pd.DataFrame(data)
    # Ensure packet_size is positive
    df['packet_size'] = np.maximum(df['packet_size'], 100)
    return df

# --- 2. Define the Generator Model (G) ---
def build_generator(latent_dim, output_dim):
    model = Sequential()
    model.add(Dense(256, input_dim=latent_dim))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization(momentum=0.8))
    model.add(Dense(512))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization(momentum=0.8))
    model.add(Dense(1024))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization(momentum=0.8))
    model.add(Dense(output_dim, activation='tanh')) # Tanh to output values between -1 and 1
    return model

# --- 3. Define the Discriminator Model (D) ---
def build_discriminator(input_dim):
    model = Sequential()
    model.add(Dense(1024, input_dim=input_dim))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(512))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(256))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(1, activation='sigmoid')) # Sigmoid for binary classification (real/fake)
    model.compile(loss='binary_crossentropy', optimizer=Adam(0.0002, 0.5), metrics=['accuracy'])
    return model

# --- 4. Build the GAN (Generator + Discriminator) ---
def build_gan(generator, discriminator):
    discriminator.trainable = False # Discriminator is only trained by itself
    model = Sequential()
    model.add(generator)
    model.add(discriminator)
    model.compile(loss='binary_crossentropy', optimizer=Adam(0.0002, 0.5))
    return model

# --- Simulate new incoming data (some normal, some anomalous) ---
def generate_new_incoming_data(num_samples=200):
    normal_data_df = generate_real_data(num_samples=int(num_samples * 0.8)) # 80% normal
    
    # Introduce some anomalies: e.g., very large packet sizes, unusual ports
    num_anomalies = num_samples - normal_data_df.shape[0]
    anomalous_data = {
        'packet_size': np.random.normal(10000, 2000, num_anomalies).astype(int), # Very large packets
        'src_port': np.random.randint(1, 1023, num_anomalies), # Privileged ports as source
        'dest_port': np.random.randint(49152, 65535, num_anomalies), # High ports as destination
        'duration': np.random.uniform(50.0, 200.0, num_anomalies), # Long durations
        'protocol_type': np.random.choice([2,3], num_anomalies) # Unknown protocol types (beyond 0, 1)
    }
    anomalous_df = pd.DataFrame(anomalous_data)
    anomalous_df['packet_size'] = np.maximum(anomalous_df['packet_size'], 5000)

    # Combine normal and anomalous data
    incoming_data_df = pd.concat([normal_data_df, anomalous_df], ignore_index=True).sample(frac=1).reset_index(drop=True)
    
    # Add a true_label column for evaluation
    incoming_data_df['true_label'] = [0] * normal_data_df.shape[0] + [1] * anomalous_df.shape[0]
    
    return incoming_data_df

# --- Anomaly Detection Function ---
def detect_anomalies(data_df, discriminator_model, scaler, threshold=0.5):
    """
    Detects anomalies using the trained discriminator.
    Higher discriminator score (closer to 1) means more likely to be real/normal.
    Lower score (closer to 0) means more likely to be fake/anomalous.
    """
    scaled_data = scaler.transform(data_df.drop(columns=['true_label'], errors='ignore'))
    discriminator_scores = discriminator_model.predict(scaled_data).flatten()
    
    # Anomalies are where the discriminator score is low (close to 0, indicating "fake")
    # We invert the score to represent "anomaly likelihood"
    anomaly_likelihood = 1 - discriminator_scores 
    
    # Classify based on threshold
    predictions = (anomaly_likelihood > threshold).astype(int)
    
    results_df = data_df.copy()
    results_df['discriminator_score'] = discriminator_scores
    results_df['anomaly_likelihood'] = anomaly_likelihood
    results_df['predicted_anomaly'] = predictions
    
    return results_df

# --- Main Execution ---
if __name__ == "__main__":
    # --- GAN Training Phase ---
    print("--- Starting GAN Training ---")
    real_data_df = generate_real_data(num_samples=5000)
    scaler = MinMaxScaler(feature_range=(-1, 1)) # Scale real data to match tanh output
    scaled_real_data = scaler.fit_transform(real_data_df)

    generator = build_generator(LATENT_DIM, OUTPUT_DIM)
    discriminator = build_discriminator(OUTPUT_DIM)
    gan = build_gan(generator, discriminator)

    # Store losses for plotting
    d_losses = []
    g_losses = []

    for epoch in range(EPOCHS):
        # Train Discriminator
        idx = np.random.randint(0, scaled_real_data.shape[0], BATCH_SIZE)
        real_samples = scaled_real_data[idx]
        noise = np.random.normal(0, 1, (BATCH_SIZE, LATENT_DIM))
        fake_samples = generator.predict(noise)

        d_loss_real = discriminator.train_on_batch(real_samples, np.ones((BATCH_SIZE, 1)))
        d_loss_fake = discriminator.train_on_batch(fake_samples, np.zeros((BATCH_SIZE, 1)))
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
        d_losses.append(d_loss[0])

        # Train Generator
        noise = np.random.normal(0, 1, (BATCH_SIZE, LATENT_DIM))
        g_loss = gan.train_on_batch(noise, np.ones((BATCH_SIZE, 1)))
        g_losses.append(g_loss)

        if epoch % 1000 == 0: # Print less frequently for merged output
            print(f"Epoch {epoch}/{EPOCHS} | D Loss: {d_loss[0]:.4f}, D Acc: {100*d_loss[1]:.2f}% | G Loss: {g_loss:.4f}")

    print("\nGAN training complete.")

    # Generate sample synthetic data for demonstration
    num_synthetic_samples = 500
    noise = np.random.normal(0, 1, (num_synthetic_samples, LATENT_DIM))
    generated_data_scaled = generator.predict(noise)
    generated_data_df = pd.DataFrame(scaler.inverse_transform(generated_data_scaled), columns=real_data_df.columns)
    
    # Post-process generated data (e.g., make ports and protocols integers)
    generated_data_df['packet_size'] = generated_data_df['packet_size'].astype(int)
    generated_data_df['src_port'] = generated_data_df['src_port'].astype(int)
    generated_data_df['dest_port'] = generated_data_df['dest_port'].astype(int)
    generated_data_df['protocol_type'] = np.round(generated_data_df['protocol_type']).astype(int)
    generated_data_df['protocol_type'] = np.clip(generated_data_df['protocol_type'], 0, 1) # Ensure 0 or 1

    print("\n--- Sample of Generated Synthetic Data ---")
    print(generated_data_df.head())

    # Visualize training losses
    plt.figure(figsize=(10, 5))
    plt.plot(d_losses, label='Discriminator Loss')
    plt.plot(g_losses, label='Generator Loss')
    plt.title('GAN Training Loss Over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Visualize distributions of real vs. generated data (example for 'packet_size')
    plt.figure(figsize=(12, 6))
    plt.hist(real_data_df['packet_size'], bins=50, alpha=0.5, label='Real Packet Size', color='blue', density=True)
    plt.hist(generated_data_df['packet_size'], bins=50, alpha=0.5, label='Generated Packet Size', color='red', density=True)
    plt.title('Distribution of Packet Sizes: Real vs. Generated')
    plt.xlabel('Packet Size')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    plt.show()

    print("\n--- Starting Anomaly Detection Phase ---")
    # Generate new data with anomalies
    new_incoming_data = generate_new_incoming_data(num_samples=500)
    print("\nSample of incoming data (true labels: 0=normal, 1=anomaly):")
    print(new_incoming_data.head())

    # Detect anomalies
    # Anomaly detection threshold: Adjust based on desired sensitivity. Higher threshold = fewer FPs but potentially more FNs.
    anomaly_results = detect_anomalies(new_incoming_data, discriminator, scaler, threshold=0.7) 

    print("\nAnomaly Detection Results (first 10 entries):")
    print(anomaly_results[['packet_size', 'src_port', 'true_label', 'discriminator_score', 'predicted_anomaly']].head(10))

    # Evaluate performance (simple metrics)
    true_labels = anomaly_results['true_label']
    predicted_labels = anomaly_results['predicted_anomaly']

    print(f"\nAccuracy: {accuracy_score(true_labels, predicted_labels):.4f}")
    print(f"Precision: {precision_score(true_labels, predicted_labels):.4f}")
    print(f"Recall: {recall_score(true_labels, predicted_labels):.4f}")
    print(f"F1-Score: {f1_score(true_labels, predicted_labels):.4f}")
    print("\nConfusion Matrix:\n", confusion_matrix(true_labels, predicted_labels))

    # Visualize anomaly likelihood distribution
    plt.figure(figsize=(10, 6))
    plt.hist(anomaly_results[anomaly_results['true_label'] == 0]['anomaly_likelihood'], bins=50, alpha=0.5, label='Normal Traffic', color='green', density=True)
    plt.hist(anomaly_results[anomaly_results['true_label'] == 1]['anomaly_likelihood'], bins=50, alpha=0.5, label='Anomalous Traffic', color='purple', density=True)
    plt.axvline(x=0.7, color='red', linestyle='--', label=f'Threshold ({0.7})') # Using the threshold from detect_anomalies call
    plt.title('Anomaly Likelihood Distribution')
    plt.xlabel('Anomaly Likelihood (1 - Discriminator Score)')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    plt.show()

    print("\n--- All operations complete ---")
