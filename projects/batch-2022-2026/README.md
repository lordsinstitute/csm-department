# 📌 Role of Generative AI in Enhancing Threat Intelligence and Cyber Security Measures

A Django-based web application that examines the role of generative AI, particularly in cybersecurity contexts. This project demonstrates the application of generative adversarial networks (GANs) for data synthesis and anomaly detection.

## 👥 Team Members

| S.No | Name                     | Roll Number   |
|------|--------------------------|---------------|
| 1    | Mohammed Abdul Jamal     | 160922748058  |
| 2    | Mohd Abdul Salam         | 160922748026  |
| 3    | Nameera Bareen           | 160922748008  |
| 4    | Afifa Iram               | 160922748019  |

## 🚀Key Features

- User registration and authentication
- Admin panel for managing users
- Generative AI data synthesis for emails and cybersecurity data
- GAN-based anomaly detection
- Interactive Jupyter notebook for AI experiments
- Web interface for viewing results and generating synthetic data

## 🛠️ Technologies Used

- Django (Python web framework)
- TensorFlow/Keras (for GAN implementation)
- SQLite (database)
- HTML/CSS (frontend)
- Jupyter Notebook (for AI experimentation)

## ⚙️ Installation

1. Clone the repository:
   ```
   git clone https://github.com/abdul-salam26/major-project-.git
   cd major-project-
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser (optional, for admin access):
   ```
   python manage.py createsuperuser
   ```

## ▶️ Usage

1. Start the Django development server:
   ```
   python manage.py runserver
   ```

2. Open your browser and navigate to `http://127.0.0.1:8000/`

3. Register as a user or login as admin

4. Explore the generative AI features:
   - View synthetic data generation results
   - Access the Jupyter notebook in the media folder for AI experiments

## 📂 Project Structure

- `ExamineAIIntelligence/` - Main Django project settings
- `users/` - User management app
- `admins/` - Admin panel app
- `assets/` - Static files and templates
- `media/` - Jupyter notebooks and experimental files
- `db.sqlite3` - SQLite database

## 🤝 Contributing

Feel free to fork this repository and submit pull requests.

## 📜 License

This project is for educational purposes.