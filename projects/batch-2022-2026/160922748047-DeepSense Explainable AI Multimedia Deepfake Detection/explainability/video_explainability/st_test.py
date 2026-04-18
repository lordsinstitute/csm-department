import streamlit as st
from video_xai import explain_video, build_model

st.subheader("Video Explainability (Key Frames)")

model_path = "../../models/video_models/video_deepfake_model.keras"

model = build_model()
model.load_weights(model_path)

cam_frames = explain_video(
    video_path="../../fake.mp4",
    model=model,
    last_conv_layer_name="block14_sepconv2_act"
)

cols = st.columns(3)

for i, frame in enumerate(cam_frames):
    with cols[i % 3]:
        st.image(frame, width=260)
        st.caption(f"{i+1}-frame Grad-CAM")