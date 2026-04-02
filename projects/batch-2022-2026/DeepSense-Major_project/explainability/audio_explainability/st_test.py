import streamlit as st
from audio_xai import explain_audio

st.title("Audio Deepfake Explainability")

uploaded_file = st.file_uploader("Upload Audio", type=["wav", "mp3"])

if uploaded_file:
    with open("temp.wav", "wb") as f:
        f.write(uploaded_file.read())

    st.subheader("Audio Explainability Graphs:")

    xai = explain_audio("temp.wav")

    st.plotly_chart(xai["waveform_fig"], use_container_width=True)
    st.caption("Amplitude waveform showing temporal signal variations. Synthetic audio may exhibit abrupt changes or uniform regions.")
    
    st.plotly_chart(xai["mfcc_fig"], use_container_width=True)
    st.plotly_chart(xai["spectral_centroid_fig"], use_container_width=True)
    st.plotly_chart(xai["zcr_fig"], use_container_width=True)
