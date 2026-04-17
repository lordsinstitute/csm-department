# stroke-prediction
Automated Stroke Prediction Using Machine Learning: An Explainable and Exploratory Study With a Web Application for Early Intervention


Overview

This project focuses on predicting the risk of stroke using advanced Machine Learning techniques. It aims to provide early detection and assist healthcare professionals by offering accurate predictions along with explainable insights.

Stroke is one of the leading causes of death and disability worldwide. Early prediction can significantly reduce risks and improve patient outcomes.

-----------------------> Objectives <-------------

Build a reliable machine learning model for stroke prediction
Handle class imbalance using SMOTE
Identify important features using:
Chi-Square Test
ANOVA
Mutual Information
Provide model explainability using:
SHAP
LIME
Compare multiple ML algorithms
Develop an end-to-end system with a user interface

-------------------------> Technologies Used <-------------------
💻 Programming Language
Python 3.7+


----------> Libraries<-------------------------
NumPy
Pandas
Matplotlib
Seaborn
Scikit-learn
XGBoost
SHAP
LIME
Imbalanced-learn (SMOTE)
Tkinter (GUI)


------------------------>🤖 Machine Learning Models Used<---------------------
Logistic Regression
Support Vector Machine (SVM)
K-Nearest Neighbors (KNN)
Random Forest
Naive Bayes
XGBoost


------------------------> Features of the Project <-----------------------------

Data preprocessing and cleaning
Handling missing values
Feature scaling (Normalization)
Class imbalance handling using SMOTE
Feature selection using Chi-Square
Model training and evaluation
Visualization (graphs, heatmaps, distributions)
Explainable AI (SHAP & LIME)
GUI-based prediction system

------------------------> Dataset <---------------------
Healthcare Stroke Dataset
Includes features like:
Age
Gender
Hypertension
Heart Disease
BMI
Smoking Status
Glucose Level

-----------------------> Workflow <-----------------------
Data Collection
Data Preprocessing
Data Visualization
Feature Engineering
Handling Imbalanced Data (SMOTE)
Model Training
Model Evaluation
Explainability (SHAP & LIME)
Prediction via GUI/Web App

--------------------------> Results <------------------------
Achieved accuracy up to ~91%
Compared multiple models to find the best performer
Random Forest and XGBoost performed best

------------------------> System Requirements <---------------------
Hardware
Processor: Intel i3 or above
RAM: 4GB minimum
Storage: 500GB
Software
OS: Windows 10 or above
Python (3.7+)
Jupyter Notebook / IDE


------------------> How to Run the Project <--------------------------
# Clone the repository
git clone https://github.com/your-username/stroke-prediction.git

# Navigate to project folder
cd stroke-prediction

# Install dependencies
pip install -r requirements.txt

# Run the project
python main.py
📊 Sample Output
Accuracy, Precision, Recall, F1 Score
Graphical visualizations
Stroke prediction result


--------------------> Future Improvements <-----------------------
Deploy as a web application
Integrate real-time hospital data
Improve model accuracy with deep learning
Add mobile application support



------------------------> License <----------------------------------

This project is for educational and research purposes.