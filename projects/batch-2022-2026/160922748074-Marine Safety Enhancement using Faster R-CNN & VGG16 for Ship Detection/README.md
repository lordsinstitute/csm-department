# 🚢 Marine Safety Enhancement Using Faster R-CNN with VGG16

> **Ship Detection from Airborne Radar Signals** > An advanced, object-oriented deep learning approach to maritime surveillance using Range-Compressed (RC) radar data, replacing traditional CFAR algorithms with state-of-the-art Convolutional Neural Networks.

---

## 📌 Project Overview

High ship density and illegitimate shipping activities—such as piracy, smuggling, and illegal fishing—pose continuous threats to coastal authorities and marine safety. To effectively enhance maritime situational awareness, rapid and accurate near real-time ship detection is an absolute necessity.

While onboard transponder systems like the Automatic Identification System (AIS) and marine radars are widely utilized, they have critical vulnerabilities. Smaller vessels are often not obligated to carry AIS transponders, making the system reliant on the cooperation of the ships being monitored. Furthermore, standard marine radars suffer from highly restricted acquisition ranges. 

To overcome these blind spots, this project leverages **Airborne Compressed Radar Data**. Airborne radars offer exceptional potential by covering wide geographic areas with high-resolution data, independent of weather or daylight conditions, while achieving shorter revisit times and longer observation periods than spaceborne alternatives.

---

## 🚧 Problem Statement

Conventional airborne ship detection methods rely heavily on the **Constant False Alarm Rate (CFAR)** algorithm. 

**Drawbacks of CFAR:**
* Evaluates radar signals by analyzing pixels individually, which frequently leads to misclassifying clutter as a ship.
* Struggles heavily in high-resolution scenarios where sea clutter, waves, or small islands trigger high rates of false alarms.
* Lacks the contextual understanding required for robust, reliable object detection.

---

## 💡 Proposed Solution & Methodology

This project completely replaces the traditional CFAR approach with an object-oriented deep learning architecture: the **Faster Region-based Convolutional Neural Network (Faster R-CNN)**. 

By operating directly on the radar signals, the system avoids the computationally heavy requirement of generating fully focused Synthetic Aperture Radar (SAR) images. 

### Dual-Domain Processing
The airborne radar dataset contains two distinct types of signal data:
1. **Time Domain Signals:** Utilized by the Faster R-CNN to accurately locate and detect the presence of the object.
2. **Doppler Domain Signals:** Utilized to classify the detected object correctly, confirming whether it is indeed a ship.

### Algorithmic Progression
The project features a comparative study between two backbone network architectures:
* **Proposed Baseline (ResNet-50):** The initial implementation utilizes ResNet-50 as the foundational feature extractor for the Faster R-CNN.
* **Extension Model (VGG16):** Because ResNet-50 is an older architecture in this context, the system's accuracy was significantly enhanced by substituting it with a **VGG16** base model. This extended model consistently outperforms the baseline.

---

## 📊 Dataset Specifications

The deep learning models are trained and evaluated using authentic airborne flight radar signals.

* **Source:** Acquired by DLR’s cutting-edge airborne systems (F-SAR and DBFSAR).
* **Format:** The data is compiled into a `JSON` format.
* **Volume:** Contains **4,000 ship signals**.
* **Data Split:** The system automatically preprocesses the JSON file, shuffling the data and dividing it into an **80% Training Set** and a **20% Testing Set**.

---

## 🖥️ System GUI & Execution Flow

The project features a fully interactive Desktop GUI (built with Tkinter) that guides the user through the entire machine learning pipeline. 

### 1. Data Preparation
* **Upload Airborne Dataset:** Users load the `airborne.json` file containing the radar signals.
* **Preprocess Dataset:** Normalizes the signals and performs the 80/20 train-test split.

### 2. Model Training
* **Propose FRCNN (Resnet50):** Trains the baseline model. The console outputs training progress across epochs, evaluating loss and accuracy.
* **Extension FRCNN (VGG16):** Trains the enhanced model. It achieves noticeably higher accuracy metrics (often hitting 99% to 100%) and lower training loss.

### 3. Performance Analytics
* **Accuracy Graph:** Plots a line graph where the x-axis represents the training epoch and the y-axis represents accuracy. A green line tracks the ResNet50 model, while a blue line tracks the superior VGG16 extension.
* **Loss Graph:** Visualizes the reduction of error during training, demonstrating the VGG16 model's reduced loss compared to the baseline.
* **Comparison Graph:** Renders a multi-colored bar chart comparing both algorithms across key metrics: *Precision, Recall, F-Score, and Accuracy*.

### 4. Real-World Inference
* **Ship Detection:** Accepts a high-resolution airborne input image.
* **Bounding Box Generation:** The model scans the image, classifies the target as a ship, and draws a bold white bounding box around the vessel.
* *Note on Optimization:* Because analyzing massive airborne images for dozens of ships can take hours of computational time, the detection script is optimized to identify a single ship and then successfully break the loop to demonstrate the proof-of-concept efficiently.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Programming Language** | Python 3.7+ |
| **Deep Learning Frameworks** | TensorFlow, Keras |
| **Machine Learning** | Scikit-learn |
| **Computer Vision** | OpenCV, PIL (Pillow) |
| **Data Manipulation** | NumPy, Pandas |
| **Data Visualization** | Matplotlib |
| **Desktop GUI** | Tkinter |

---

| Name | Roll number |
|----------|---------|
| Atif Riyan Ahmed | 160922748074 |
| Ayman Khan | 160922748076 |
| Fawaz Naseeruddin | 160922748078 |

**Project Guide:** Mr Khaja Pasha, Assistant Professor <br />
**Branch and Section:** CSM - 4B <br />
**Institution:** Lords Institute of Engineering and Technology

---

## 🚀 Installation & Usage Guide

### Prerequisites
* Windows 10/11 (or equivalent Linux/macOS environment)
* Minimum 4GB RAM (8GB+ recommended for model training)
* Python 3.7.x installed globally

