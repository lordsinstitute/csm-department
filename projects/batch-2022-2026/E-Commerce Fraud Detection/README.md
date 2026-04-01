# Hybrid Generative AI Framework for Real-Time E-Commerce Fraud Detection 🛡️💳

An advanced, real-time E-Commerce Fraud Detection platform built with a dynamic **Hybrid GAN-VAE Framework** and integrated with AI Insights for explainability and ethical bias analysis. This project is developed to accurately identify, explain, and mitigate fraudulent transactions in digital payments.

## 🌟 Key Features

- **Hybrid GAN-VAE Machine Learning Model**: Combines Generative Adversarial Networks (GAN) and Variational Autoencoders (VAE) to handle highly imbalanced datasets and detect complex fraudulent patterns effectively.
- **Explainable AI (XAI)**: Utilizes the Google Gemini Large Language Model (LLM) to generate natural language explanations out of complex numerical ML predictions, helping users understand *why* a transaction was flagged.
- **Secure Admin Dashboard**: Features an exclusive authorization panel to oversee user activity, view transaction analytics, and examine fraud trends.
- **User-Facing Portal**: An interactive, glassmorphic UI where users can upload transaction datasets, monitor real-time predictions, and generate synthetic data for testing.
- **Ethical AI Bias Analysis**: Inbuilt algorithms and prompts ensure fairness across demographic and transactional metadata.

## 🛠️ Technology Stack

- **Backend Framework**: Python, Django
- **Frontend Design**: HTML5, Vanilla CSS (Glassmorphism aesthetics), JavaScript
- **Machine Learning**: Scikit-Learn, Pandas, NumPy, Keras/TensorFlow (GAN-VAE)
- **Generative AI**: Google Gemini API (`google.generativeai`)
- **Database**: SQLite3

## 📂 Project Structure

```text
E-Commerce Fraud Detection/
├── .gitignore               # Ignored files (virtual environments, keys)
├── Ecommers_Fraud_detection/# Main Django project configuration settings
├── manage.py                # Django execution entry point
├── requirements.txt         # Required Python dependency libraries
├── admins/                  # Admin portal application and logic
├── users/                   # End-user dashboard, ML predictions & UI
│   ├── ml_models.py         # The Hybrid GAN-VAE and prediction architecture
│   ├── saved_models/        # Pre-trained models (.pkl files)
└── templates/               # Client-side HTML interfaces
```

## 🚀 How to Run Locally

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Environment Setup
Clone the repository and navigate into the project directory:
```bash
git clone <your-repository-url>
cd "E-Commerce Fraud Detection"
```

Create and activate a virtual environment:
**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup API Keys
Create a `.env` file in the root directory (alongside `manage.py`) and supply your Google Gemini API key:
```env
GOOGLE_API_KEY=your_secure_api_key_here
```
*(Note: Never commit the `.env` file. It is safely added to `.gitignore`)*

### 5. Apply Migrations and Run 
Set up the local database and launch the development server:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### 6. Access the Application
Open your web browser and navigate to:
`http://127.0.0.1:8000/`

## 👥 Contributors

- **LIET CSM Students** - *Batch of 2022-2026*
- **Major Project Review Submission**
