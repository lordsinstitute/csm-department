import cv2
import numpy as np
from mtcnn import MTCNN
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications.xception import preprocess_input

# -----------------------------
# CONFIG
# -----------------------------
TIME_STEPS = 30
HEIGHT = 299
WIDTH = 299
MODEL_PATH = "models/video_models/video_deepfake_model.keras"

detector = MTCNN()


# -----------------------------
# FACE EXTRACTION
# -----------------------------
def extract_face(frame):
    if frame is None:
        return None

    h, w, _ = frame.shape
    if h < 50 or w < 50:
        return None

    try:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = detector.detect_faces(frame_rgb)
    except Exception:
        return None

    if len(faces) == 0:
        return None

    faces = sorted(
        faces,
        key=lambda x: x["box"][2] * x["box"][3],
        reverse=True
    )

    x, y, w, h = faces[0]["box"]
    x, y = max(0, x), max(0, y)

    face = frame_rgb[y:y + h, x:x + w]

    if face.size == 0 or face.shape[0] < 50 or face.shape[1] < 50:
        return None

    return face


# -----------------------------
# VIDEO PREPROCESSING
# -----------------------------
def build_video_array(video_path):
    cap = cv2.VideoCapture(video_path)
    faces = []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = np.linspace(0, total_frames - 1, TIME_STEPS).astype(int)
    idx_set = set(indices)

    current = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if current in idx_set:
            face = extract_face(frame)
            if face is not None:
                face = cv2.resize(face, (WIDTH, HEIGHT))
                face = preprocess_input(face.astype("float32"))
                faces.append(face)

        current += 1

    cap.release()

    if len(faces) == 0:
        raise ValueError("No faces detected in video")

    if len(faces) < TIME_STEPS:
        while len(faces) < TIME_STEPS:
            faces.append(faces[-1])
    else:
        faces = faces[:TIME_STEPS]

    video_array = np.expand_dims(np.array(faces), axis=0)
    return video_array


# -----------------------------
# MODEL
# -----------------------------
def build_model(lstm_hidden_size=256, num_classes=2, dropout_rate=0.5):
    inputs = layers.Input(shape=(TIME_STEPS, HEIGHT, WIDTH, 3))

    base_model = keras.applications.Xception(
        weights="imagenet",
        include_top=False,
        pooling="avg"
    )

    x = layers.TimeDistributed(base_model)(inputs)
    x = layers.LSTM(lstm_hidden_size)(x)
    x = layers.Dropout(dropout_rate)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs, outputs)
    return model


# -----------------------------
# LOAD MODEL (ONCE)
# -----------------------------
video_model = build_model()
video_model.load_weights(MODEL_PATH)


# -----------------------------
# VIDEO PREDICTION (MAIN API)
# -----------------------------
def predict_video(video_path):
    """
    Returns:
        prediction_label (str)
        fake_probability (float)
    """

    video_array = build_video_array(video_path)
    predictions = video_model.predict(video_array)

    prob_fake = float(predictions[0][1])
    prob_real = float(predictions[0][0])

    prediction_label = "FAKE" if prob_fake > prob_real else "REAL"

    return prediction_label, prob_fake
