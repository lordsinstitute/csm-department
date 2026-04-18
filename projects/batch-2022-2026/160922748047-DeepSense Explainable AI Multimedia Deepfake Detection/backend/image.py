import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# -----------------------------
# CONFIG
# -----------------------------
IMAGE_SIZE = (299, 299)
MODEL_PATH = "models/image_models/image_deepfake_model.keras"
THRESHOLD = 0.55


# -----------------------------
# LOAD MODEL (ONCE)
# -----------------------------
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

image_model = load_model(MODEL_PATH, compile=False)


# -----------------------------
# IMAGE PREPROCESSING
# -----------------------------
def preprocess_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found at {image_path}")

    img = load_img(image_path, target_size=IMAGE_SIZE)
    img = img_to_array(img) / 255.0
    img = np.expand_dims(img, axis=0).astype("float32")

    return img


# -----------------------------
# IMAGE PREDICTION (MAIN API)
# -----------------------------
def predict_image(image_path):
    """
    Returns:
        prediction_label (str)
        probabilities (dict)
    """

    img = preprocess_image(image_path)

    # Sigmoid output → fake probability
    prob = float(image_model.predict(img)[0][0])
    

    prediction_label = "FAKE" if prob > THRESHOLD else "REAL"

    return prediction_label, prob
