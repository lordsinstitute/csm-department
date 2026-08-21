import pandas as pd
import numpy as np
import os

# Create media directory if it doesn't exist
media_dir = r"c:\Users\samaa\OneDrive\Documents\My Personal Docs\LIET\8 Sem\Major Project\208.E-Commerce Fraud Detection\E-Commerce Fraud Detection\E-Commerce Fraud Detection\media"
os.makedirs(media_dir, exist_ok=True)

# Generate synthetic dataset
np.random.seed(42)
n_samples = 500

methods = ['Credit Card', 'Debit Card', 'Net Banking', 'Wallet', 'UPI']
locations = ['MUM', 'DEL', 'BLR', 'HYD', 'CHE', 'PUN', 'KOL', 'AHD']

data = {
    'amount': [],
    'payment_method': [],
    'location': [],
    'ip': [],
    'is_fraud': []
}

for i in range(n_samples):
    # 5% fraud rate
    is_fraud = 1 if np.random.rand() < 0.05 else 0
    
    if is_fraud:
        amount = round(np.random.uniform(10000, 100000), 2)
        method = np.random.choice(['Credit Card', 'Net Banking'])
        location = np.random.choice(locations)
        # Random IP format
        ip = f"{np.random.randint(1, 200)}.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}"
    else:
        amount = round(np.random.uniform(10, 5000), 2)
        method = np.random.choice(methods)
        location = np.random.choice(locations)
        # Random local IP format
        ip = f"192.168.{np.random.randint(0, 5)}.{np.random.randint(1, 255)}"
        
    data['amount'].append(amount)
    data['payment_method'].append(method)
    data['location'].append(location)
    data['ip'].append(ip)
    data['is_fraud'].append(is_fraud)

df = pd.DataFrame(data)
df.to_csv(os.path.join(media_dir, 'transactions.csv'), index=False)
print("Dataset generated successfully at media/transactions.csv")
