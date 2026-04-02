import numpy as np
import librosa
from tensorflow.keras.models import load_model

# -----------------------------
# CONFIG
# -----------------------------
SAMPLE_RATE = 16000
N_MFCC = 40
MAX_LENGTH = 500
MODEL_PATH = "models/audio_models/audio_deepfake_model.h5"


# -----------------------------
# LOAD MODEL (ONCE)
# -----------------------------
audio_model = load_model(MODEL_PATH)


# -----------------------------
# AUDIO PREPROCESSING
# -----------------------------
def preprocess_audio_for_model(audio_path):
    audio, _ = librosa.load(audio_path, sr=SAMPLE_RATE)

    mfccs = librosa.feature.mfcc(
        y=audio,
        sr=SAMPLE_RATE,
        n_mfcc=N_MFCC
    )

    if mfccs.shape[1] < MAX_LENGTH:
        mfccs = np.pad(
            mfccs,
            ((0, 0), (0, MAX_LENGTH - mfccs.shape[1])),
            mode="constant"
        )
    else:
        mfccs = mfccs[:, :MAX_LENGTH]

    mfccs = mfccs[..., np.newaxis]        # (40, 500, 1)
    mfccs = np.expand_dims(mfccs, axis=0) # (1, 40, 500, 1)

    return mfccs


# -----------------------------
# AUDIO PREDICTION (MAIN API)
# -----------------------------
def predict_audio(audio_path):
    """
    Returns:
        prediction_label (str)
        probabilities (dict)
    """

    input_features = preprocess_audio_for_model(audio_path)

    # Sigmoid output → fake probability
    prob_fake = float(audio_model.predict(input_features)[0][0])
    prob_real = 1.0 - prob_fake

    prediction_label = "FAKE" if prob_fake > 0.5 else "REAL"

    return prediction_label, {
        "real": prob_real,
        "fake": prob_fake
    }
