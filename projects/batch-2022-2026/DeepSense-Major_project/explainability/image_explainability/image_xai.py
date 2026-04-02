import tensorflow as tf
import numpy as np
import cv2
import matplotlib.pyplot as plt
from ..grad_cam import generate_gradcam, overlay_gradcam


def load_image_model():
    return tf.keras.models.load_model("models/image_models/image_deepfake_model.keras")

model = load_image_model()

# -------------------------------
# Load & preprocess image
# -------------------------------
def preprocess_image(img_path, target_size=(299, 299)):
    img = tf.keras.preprocessing.image.load_img(img_path, target_size=target_size)
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    return img_array, img


# -------------------------------
# Main Explainability Function
# -------------------------------

def explain_image(img_path, last_conv_layer_name):

    img_array, original_img = preprocess_image(img_path)

    heatmap = generate_gradcam(model, img_array, last_conv_layer_name)
    cam_image = overlay_gradcam(original_img, heatmap)

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))

    ax[0].imshow(original_img)
    ax[0].set_title("Original Image")
    ax[0].axis("off")

    ax[1].imshow(cam_image)
    ax[1].set_title("Grad-CAM Explanation")
    ax[1].axis("off")

    plt.tight_layout()

    return fig, cam_image