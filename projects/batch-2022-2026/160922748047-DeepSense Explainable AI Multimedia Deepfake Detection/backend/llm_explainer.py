from google import genai
import os
import time
import streamlit as st
import threading

# -----------------------------
# RATE LIMIT SETTINGS
# -----------------------------
RATE_LIMIT_SECONDS = 5   # per-user (~12 RPM)
GLOBAL_RATE_LIMIT = 4    # ~15 RPM safe globally

# Global tracker (shared across users)
LAST_GLOBAL_CALL = 0
lock = threading.Lock()


def explain_with_llm(modality, prediction, confidence, image_paths=None):

    global LAST_GLOBAL_CALL

    # -----------------------------
    # PER-USER RATE LIMIT
    # -----------------------------
    if "last_called" not in st.session_state:
        st.session_state.last_called = 0

    current_time = time.time()

    if current_time - st.session_state.last_called < RATE_LIMIT_SECONDS:
        return "⚠️ Too many requests. Please wait a few seconds."

    # -----------------------------
    # GLOBAL RATE LIMIT (MULTI-USER SAFE)
    # -----------------------------
    with lock:
        current_time = time.time()

        if current_time - LAST_GLOBAL_CALL < GLOBAL_RATE_LIMIT:
            return "⚠️ Server busy (rate limit reached). Try again shortly."

        LAST_GLOBAL_CALL = current_time

    # update user timestamp AFTER passing global check
    st.session_state.last_called = time.time()

    # -----------------------------
    # API KEY CHECK
    # -----------------------------
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ API key not set"

    client = genai.Client(api_key=api_key)

    # -----------------------------
    # YOUR EXISTING CODE
    # -----------------------------
    if image_paths is None:
        image_paths = []

    prompt = f"""
You are an AI forensic analyst helping users understand deepfake detection results.

Media Type: {modality}
Prediction: {prediction}
Confidence: {confidence:.2f}

Explain clearly in simple language WHY the media might be {prediction}.
Refer to the visual evidence if available.
"""

    contents = []

    for path in image_paths:
        uploaded_file = client.files.upload(file=path)
        contents.append(uploaded_file)

    contents.append(prompt)

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=contents
    )

    return response.text