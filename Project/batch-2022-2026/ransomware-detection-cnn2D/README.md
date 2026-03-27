# 🔐 Ransomware Detection using CNN2D with Explainable AI and Robustness Evaluation

## 📌 Overview

Ransomware continues to evolve, rendering traditional signature-based detection ineffective.
This project presents a **behavior-driven ransomware detection system** leveraging system-level activity (CPU and disk I/O), combined with deep learning and explainable AI techniques.

Unlike static analysis approaches, this system focuses on **runtime behavioral patterns**, enabling detection of previously unseen and obfuscated ransomware variants.

---

## 🎯 Objectives

* Detect ransomware using system behavior rather than signatures
* Compare classical ML and deep learning approaches
* Improve interpretability using SHAP (Explainable AI)
* Evaluate robustness under adversarial perturbations
* Validate generalization using stratified cross-validation

---

## ⚙️ Methodology

### 🔹 Data Pipeline

1. System activity data acquisition (CPU + Disk I/O)
2. Data preprocessing and normalization
3. Feature representation for model input
4. Train-test split with stratification

### 🔹 Modeling Strategy

* Benchmark multiple ML and DL models
* Identify best-performing architecture
* Use CNN2D as the final model due to superior pattern extraction capability

### 🔹 Evaluation Framework

* Standard metrics (accuracy, confusion matrix)
* 10-Fold Stratified Cross Validation
* Robustness testing under adversarial noise
* Explainability using SHAP

---

## 🧠 Models Evaluated

### Machine Learning

* Support Vector Machine (SVM)
* K-Nearest Neighbors (KNN)
* Decision Tree
* Random Forest
* XGBoost

### Deep Learning

* Deep Neural Network (DNN)
* Long Short-Term Memory (LSTM)
* **Convolutional Neural Network (CNN2D)** *(Final Model)*

---

## 🏗️ System Design

* **Input:** System-level activity (CPU usage, Disk I/O)
* **Processing:** Feature extraction and transformation
* **Model:** CNN2D classifier
* **Output:** Binary classification (Ransomware / Benign)

---

## 📊 Dataset

* HPC system activity dataset 
* Captures runtime behavior patterns rather than static signatures
* Includes training dataset and external validation dataset

---

## 📈 Results

| Metric                | Value                       |
| --------------------- | --------------------------- |
| Accuracy (10-Fold CV) | **99.08% ± 0.39%**          |
| Evaluation Strategy   | Stratified Cross Validation |
| Models Compared       | 8                           |

### Key Insight

CNN2D outperformed both classical ML and sequential models, indicating that **spatial feature representation of behavioral data is highly effective for ransomware detection**.

---

## 🔍 Explainability (SHAP)

* Identifies most influential features contributing to predictions
* Enhances trust and interpretability of the model
* Provides insight into ransomware behavior patterns

---

## 🛡️ Robustness Evaluation

* Introduces adversarial perturbations to test model stability
* Ensures reliability in noisy, real-world environments

---

## 🔁 Cross-Validation Strategy

* 10-Fold Stratified Cross Validation
* Ensures model generalization across data splits
* Reduces overfitting risk

---

## ⚡ Real-Time Simulation

* Simulates streaming system activity
* Evaluates model performance in dynamic conditions

---

## 🖥️ GUI Application

A Tkinter-based interface provides:

* Dataset upload and preprocessing
* Model training and evaluation
* Comparative performance visualization
* Prediction on external test data
* Automated report generation

---

## 📊 Outputs Generated

* Confusion matrices for all models
* Model comparison graphs
* SHAP plots and feature importance
* Adversarial robustness analysis
* Real-time simulation outputs
* Combined PDF report

All outputs are stored in:

```id="figdir123"
figures/
```

---

## 📂 Repository Structure

```id="struct123"
.
├── Main.py
├── Ransomware_Paper_Enhancements.ipynb
├── Dataset/
├── model/
├── figures/
├── run.bat
├── Requirements.txt
```

---

## ⚙️ Installation

```id="install123"
conda create -n ransomware-detect python=3.7 -y
conda activate ransomware-detect
uv pip install -r Requirements.txt
```

---

## ▶️ Execution

### Full Pipeline

```id="run123"
run.bat
```

### GUI Mode

```id="gui123"
python Main.py
```

### Notebook Execution

```id="nb123"
python -m nbconvert --to notebook --execute Ransomware_Paper_Enhancements.ipynb --inplace --ExecutePreprocessor.timeout=-1
```

---

## 📌 Key Contributions

* Behavior-based ransomware detection system
* Comprehensive ML vs DL benchmarking
* CNN2D-based classification framework
* Integration of SHAP for explainability
* Adversarial robustness evaluation
* Real-time simulation pipeline
* Automated reporting system

---

## 👨‍💻 Team Members

* **md shoaib uddin chanda** — 160922748092
* **Mohammed Asim** — 160922748108
* **Maimona Jaweed** — 160922748083

---

## 📜 License

Refer to the LICENSE file for details.
