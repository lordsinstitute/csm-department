import streamlit as st
from image_xai import explain_image
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import shap

st.subheader("Image Explainability (Grad-CAM)")

@st.cache_resource
def load_image_model():
    return tf.keras.models.load_model("../../models/image_models/image_deepfake_model.keras")

image_model = load_image_model()


fig, cam_img = explain_image(
    img_path="../../training/image/Rimage.png",
    model=image_model,
    last_conv_layer_name="block14_sepconv2_act"  # example for Xception
)


st.pyplot(fig)
st.caption(
    "Grad-CAM highlights facial regions that influenced the deepfake prediction, such as eyes, mouth, and boundary artifacts."
)