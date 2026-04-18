# Methodology — Building Safety through ML-Based Smoke Detection

## 1. Problem Statement

Buildings require early detection of smoke and fire risk to protect occupants and assets. This project aims to **predict fire-alarm conditions from IoT sensor readings** using machine learning, so that building safety systems can act on data-driven predictions in addition to physical sensors.

**Objective:** Classify whether current sensor readings indicate a **Fire Alarm** (smoke/fire risk) or **No Fire Alarm**, using a dataset of real IoT sensor measurements.

---

## 2. Dataset

- **Source:** Smoke Detection IoT dataset (e.g. Kaggle / public datasets).
- **Size:** ~62,000+ rows.
- **Target:** Binary label **Fire Alarm** (0 = No, 1 = Yes).

**Features (13 inputs):**

| Feature          | Description / Unit   |
|------------------|----------------------|
| Temperature[C]   | Ambient temperature (°C) |
| Humidity[%]       | Relative humidity (%) |
| TVOC[ppb]        | Total volatile organic compounds (ppb) |
| eCO2[ppm]        | CO₂ equivalent (ppm) |
| Raw H2            | Raw H₂ sensor (resistance) |
| Raw Ethanol       | Raw ethanol sensor (resistance) |
| Pressure[hPa]    | Atmospheric pressure (hPa) |
| PM1.0, PM2.5     | Particulate matter (µg/m³) |
| NC0.5, NC1.0, NC2.5 | Number concentration (#/cm³) |
| CNT              | Counter / sample index |

Preprocessing: **S.No** and **UTC** are dropped; the remaining numeric columns are used as features. The target is **Fire Alarm**.

---

## 3. Methodology

### 3.1 Train–Test Split

- **Split:** 80% train, 20% test.
- **Random state:** 42 (reproducibility).

### 3.2 Feature Scaling

- **StandardScaler:** Fit on training data only; transform both train and test (and later, user inputs for prediction).
- Prevents features with larger scales from dominating the model.

### 3.3 Classifiers Used (Tabular ML)

Seven classifiers are trained and compared on the **IoT sensor (tabular) data**:

| Model              | Type / Notes        |
|--------------------|---------------------|
| Random Forest      | Ensemble, robust    |
| Gradient Boosting  | Ensemble, sequential |
| AdaBoost           | Ensemble, adaptive   |
| Logistic Regression| Linear, interpretable |
| SVM                | Kernel (RBF), probability=True for scores |
| Decision Tree      | Single tree          |
| KNN                | k-Nearest Neighbors  |

### 3.4 CNN Model (Image-based DL)

In addition to the 7 tabular ML classifiers, the system includes a **Convolutional Neural Network (CNN)** based on **MobileNetV2** for **image-based smoke/fire detection**:

- **Input:** Fire/smoke vs. normal building images uploaded from the CNN DETECT page.  
- **Model:** MobileNetV2 backbone with fine-tuning for binary fire/smoke classification.  
- **Output:** Class label (e.g. *Fire/Smoke* vs. *Normal*) and confidence score.

Although CNNs belong to **Deep Learning (DL)**, DL is a **subset of Machine Learning**, so adding a CNN still fits the ML scope of the project. We include the CNN because:

- It automatically learns spatial patterns (edges, textures, smoke plumes, flames) that are hard to engineer by hand.  
- It **increases accuracy and reliability** for visual detection scenarios, complementing the sensor-based ML models.  
- It adds technical depth by showing both classical ML (tabular) and DL (image) approaches in a single safety system.

### 3.5 Evaluation Metrics

- **Precision** — Of predicted “Fire Alarm”, how many are correct.
- **Recall** — Of actual “Fire Alarm”, how many are detected.
- **AUC-ROC** — Ranking quality (probability scores).
- **IoU (Intersection over Union)** — Overlap between predicted and actual positive class (binary).

The **best tabular ML model** is chosen by **highest AUC-ROC** on the test set. All models are saved (e.g. as `.pkl`) for use in the prediction interface.  
The CNN is trained and evaluated separately on an image dataset using standard DL metrics (accuracy, confusion matrix), and its predictions are served through the CNN DETECT page.

---

## 4. Application Workflow

1. **Training:** User triggers training from the web app. The app loads the CSV, splits data, scales features, trains all seven models, computes metrics, and saves the scaler and models.
2. **Prediction:** User enters 13 sensor values in the form. The app loads the scaler and selected model, scales the input, runs prediction and (where available) probability, and displays **Fire Alarm / No Fire Alarm** and confidence.
3. **Input validation:** All 13 inputs are required; values must be numeric and within defined ranges to avoid invalid or out-of-range sensor data.

---

## 5. Technology Stack

- **Backend:** Django (Python).
- **ML:** scikit-learn (classification, StandardScaler, metrics), pandas, joblib (model persistence).
- **Security:** Passwords hashed (e.g. PBKDF2); admin credentials configurable via environment variables.
- **Frontend:** HTML/CSS/JS, Chart.js (training metrics), DataTables (dataset table), server-side pagination for large dataset.

---

## 6. Limitations and Future Work

- **Data:** Model performance depends on the quality and representativeness of the dataset; different buildings or sensor types may need retraining.
- **Real-time:** Current design is request-based; true real-time streaming would require a different architecture.
- **Explainability:** Adding feature importance or SHAP could help interpret why the model predicted “Fire Alarm”.
- **Deployment:** For production, use strong secrets, HTTPS, and proper deployment (e.g. gunicorn, reverse proxy).

---

## 7. Conclusion

The project delivers an end-to-end system for **building safety through ML-based smoke detection**: from dataset browsing and model training to validated, in-app predictions with multiple classifiers and clear metrics. It meets the goal of a college major project by combining web development, machine learning, and basic security practices.
