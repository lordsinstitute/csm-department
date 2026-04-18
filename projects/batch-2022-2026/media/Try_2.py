import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Reshape, LeakyReLU, BatchNormalization
from tensorflow.keras.optimizers import Adam

# --- Configuration ---
LATENT_DIM = 100 # Dimension of the latent space for the generator
EPOCHS = 5000    # Number of training epochs
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

# --- Main Training Loop ---
if __name__ == "__main__":
    # Generate and preprocess real data
    real_data_df = generate_real_data(num_samples=5000)
    scaler = MinMaxScaler(feature_range=(-1, 1)) # Scale real data to match tanh output
    scaled_real_data = scaler.fit_transform(real_data_df)

    generator = build_generator(LATENT_DIM, OUTPUT_DIM)
    discriminator = build_discriminator(OUTPUT_DIM)
    gan = build_gan(generator, discriminator)

    # Store losses for plotting
    d_losses = []
    g_losses = []

    print("Starting GAN training...")
    for epoch in range(EPOCHS):
        # --- Train Discriminator ---
        # Select a random batch of real data
        idx = np.random.randint(0, scaled_real_data.shape[0], BATCH_SIZE)
        real_samples = scaled_real_data[idx]

        # Generate a batch of fake data
        noise = np.random.normal(0, 1, (BATCH_SIZE, LATENT_DIM))
        fake_samples = generator.predict(noise)

        # Train discriminator
        d_loss_real = discriminator.train_on_batch(real_samples, np.ones((BATCH_SIZE, 1))) # Real labels = 1
        d_loss_fake = discriminator.train_on_batch(fake_samples, np.zeros((BATCH_SIZE, 1))) # Fake labels = 0
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
        d_losses.append(d_loss[0])

        # --- Train Generator ---
        # Generate new noise for generator training
        noise = np.random.normal(0, 1, (BATCH_SIZE, LATENT_DIM))
        # Generator aims to fool the discriminator (labels = 1, "real")
        g_loss = gan.train_on_batch(noise, np.ones((BATCH_SIZE, 1)))
        g_losses.append(g_loss)

        # Print progress
        if epoch % 100 == 0:
            print(f"Epoch {epoch}/{EPOCHS} | D Loss: {d_loss[0]:.4f}, D Acc: {100*d_loss[1]:.2f}% | G Loss: {g_loss:.4f}")

    print("\nGAN training complete.")

    # --- Generate new synthetic data using the trained generator ---
    num_synthetic_samples = 500
    noise = np.random.normal(0, 1, (num_synthetic_samples, LATENT_DIM))
    generated_data_scaled = generator.predict(noise)
    # Inverse transform to get data in original scale
    generated_data_df = pd.DataFrame(scaler.inverse_transform(generated_data_scaled), columns=real_data_df.columns)
    
    # Post-process generated data (e.g., make ports and protocols integers)
    generated_data_df['packet_size'] = generated_data_df['packet_size'].astype(int)
    generated_data_df['src_port'] = generated_data_df['src_port'].astype(int)
    generated_data_df['dest_port'] = generated_data_df['dest_port'].astype(int)
    generated_data_df['protocol_type'] = np.round(generated_data_df['protocol_type']).astype(int)
    generated_data_df['protocol_type'] = np.clip(generated_data_df['protocol_type'], 0, 1) # Ensure 0 or 1


    print("\nSample of generated synthetic data:")
    print(generated_data_df.head())

    # --- Visualize training losses ---
    plt.figure(figsize=(10, 5))
    plt.plot(d_losses, label='Discriminator Loss')
    plt.plot(g_losses, label='Generator Loss')
    plt.title('GAN Training Loss Over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

    # --- Visualize distributions of real vs. generated data (example for 'packet_size') ---
    plt.figure(figsize=(12, 6))
    plt.hist(real_data_df['packet_size'], bins=50, alpha=0.5, label='Real Packet Size', color='blue', density=True)
    plt.hist(generated_data_df['packet_size'], bins=50, alpha=0.5, label='Generated Packet Size', color='red', density=True)
    plt.title('Distribution of Packet Sizes: Real vs. Generated')
    plt.xlabel('Packet Size')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    plt.show()

    print("Synthetic data generation POC complete.")
