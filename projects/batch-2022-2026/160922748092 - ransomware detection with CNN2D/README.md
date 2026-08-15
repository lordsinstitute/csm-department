# 🔐 Ransomware Detection using CNN2D with Explainable AI and Robustness Evaluation

Major Project - Bachelor of Engineering in Computer Science and Engineering (AIML)  
Lords Institute of Engineering and Technology (UGC Autonomous), Hyderabad  
Academic Year 2025-2026

---

## 👥 Team Members

| Name | Roll Number |
| --- | --- |
| Md Shoaib Uddin Chanda | 160922748092 |
| Mohammed Asim | 160922748108 |
| Maimona Jaweed | 160922748083 |

---

## 📌 Project Overview

This project introduces a behavior-driven ransomware detection pipeline that analyzes runtime system activity rather than file signatures.

The system combines:

1. Classical machine learning baselines
2. Deep learning architectures
3. Explainable AI with SHAP
4. Robustness checks under adversarial perturbations

The final selected model is CNN2D, which achieved strong and consistent performance on system behavior data.

---

## 📚 Table of Contents

- Team Members
- Objectives
- Methodology
- Models Evaluated
- Dataset
- Results
- Visual Results
- Explainability
- Robustness Evaluation
- GUI Application
- Outputs Generated
- Tech Stack
- Repository Structure
- Quick Start
- Execution
- How to Add or Update Figures in README
- How to Push to GitHub
- License

---

## 🎯 Objectives

- Detect ransomware using runtime behavior (CPU and Disk I/O) instead of static signatures
- Benchmark traditional ML and deep learning models on the same dataset
- Improve model interpretability using SHAP
- Test model reliability under adversarial noise
- Validate generalization using stratified 10-fold cross-validation

---

## ⚙️ Methodology

### Data Pipeline

1. Collect system-level activity signals (CPU and Disk I/O)
2. Clean and normalize the dataset
3. Build feature representation for model input
4. Train and evaluate with stratified splits

### Modeling Strategy

- Compare multiple ML and DL models
- Select best model based on performance and stability
- Finalize CNN2D for deployment and reporting

### Evaluation Framework

- Accuracy and confusion matrix analysis
- 10-fold stratified cross-validation
- Adversarial perturbation robustness testing
- SHAP-based explainability analysis

---

## 🧠 Models Evaluated

### Machine Learning Models

- Support Vector Machine (SVM)
- K-Nearest Neighbors (KNN)
- Decision Tree
- Random Forest
- XGBoost

### Deep Learning Models

- Deep Neural Network (DNN)
- Long Short-Term Memory (LSTM)
- Convolutional Neural Network (CNN2D) - Final Model

---

## 📊 Dataset

- Source: HPC system activity behavioral dataset
- Training file: Dataset/hpc_io_data.csv
- External validation file: Dataset/testData.csv
- Focus: behavioral ransomware signatures from runtime activity patterns

---

## 📈 Results

| Metric | Value |
| --- | --- |
| Accuracy (10-Fold CV) | 99.08% +- 0.39% |
| Evaluation Strategy | Stratified Cross Validation |
| Total Models Compared | 8 |

### Key Insight

CNN2D outperformed both classical ML and sequential DL models, suggesting that spatial feature learning is highly effective for ransomware behavior detection.

---

## 📸 Visual Results

### 1. All Algorithms Performance Comparison

![All Algorithms Performance Comparison](figures/all_algorithms_performance_graph.png)

This figure compares Accuracy, F1 Score, Precision, and Recall across all evaluated algorithms.
It provides a single-view summary of overall model quality.

### 2. Model Accuracy Comparison (CNN2D highlighted)

![Model Accuracy Comparison (CNN2D highlighted)](figures/model_comparison.png)

This chart ranks models by accuracy and highlights CNN2D, making it easy to justify model selection.

### 3. 10-Fold Stratified CV Accuracy

![10-Fold Stratified CV Accuracy](figures/kfold_cv_accuracy.png)

This graph shows fold-wise accuracy stability, including mean and standard deviation bands.
It demonstrates consistent generalization performance.

---

## 🔍 Explainability (SHAP)

- Highlights the most influential features per prediction
- Improves transparency and trust for security analysts
- Provides behavioral interpretation of ransomware indicators

---

## 🛡️ Robustness Evaluation

- Injects adversarial perturbations into inputs
- Evaluates prediction stability in noisy environments
- Assesses real-world resilience of the detection pipeline

---

## 🖥️ GUI Application

The Tkinter interface supports:

- Dataset loading and preprocessing
- Model training and comparison
- External test data prediction
- Visual metrics generation and export
- Automated report output

---

## 📊 Outputs Generated

- Confusion matrices
- Comparative model charts
- SHAP feature-importance outputs
- Robustness analysis artifacts
- Real-time simulation outputs

Output directories:

- figures/
- model/

---

## 🛠️ Tech Stack

| Layer | Technology |
| --- | --- |
| Language | Python |
| ML | scikit-learn, XGBoost |
| DL | TensorFlow, Keras |
| Explainability | SHAP |
| Data | NumPy, Pandas |
| Visualization | Matplotlib, Seaborn |
| GUI | Tkinter |

---

## 📂 Repository Structure

```text
.
├── Main.py
├── Ransomware_Paper_Enhancements.ipynb
├── Dataset/
│   ├── hpc_io_data.csv
│   └── testData.csv
├── model/
├── figures/
├── run.bat
├── Requirements.txt
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites

- Anaconda or Miniconda installed
- Python 3.7 environment (recommended for current dependency versions)

### Setup

```bash
conda create -n ransomware-detect python=3.7 -y
conda activate ransomware-detect
uv pip install -r Requirements.txt
```

---

## ▶️ Execution

### Full Pipeline (Windows)

```bat
run.bat
```

### Main Application

```bash
python Main.py
```

### Execute Notebook End-to-End

```bash
python -m nbconvert --to notebook --execute Ransomware_Paper_Enhancements.ipynb --inplace --ExecutePreprocessor.timeout=-1
```

---

## 🖼️ How to Add or Update Figures in README

1. Save your graph images in the figures folder.
2. Use clear file names like model_comparison.png or kfold_cv_accuracy.png.
3. Reference images using relative paths from README.md.
4. Add one short explanation under each image so readers understand what it proves.

Example markdown pattern:

```markdown
### Figure Title
![Figure alt text](figures/your_figure_name.png)

One or two lines explaining why this figure matters.
```

---

## 🚀 How to Push to GitHub

Run these commands from the ransomware-detection-cnn2D folder:

```bash
git status
git add README.md figures/*.png
git commit -m "Update README with visual project explanation and image sections"
git push origin add-ransomware-project
```

After push, open your repository on GitHub and refresh the README page.

---

## 📜 License

This project is licensed under the terms provided in the LICENSE file.
