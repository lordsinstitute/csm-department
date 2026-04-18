import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications.xception import preprocess_input
from mtcnn import MTCNN
from ..grad_cam import generate_gradcam, overlay_gradcam

# -----------------------------
# CONFIG
# -----------------------------
TIME_STEPS = 30
HEIGHT = 299
WIDTH = 299
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

model_path = "models/video_models/video_deepfake_model.keras"

model = build_model()
model.load_weights(model_path)


# -----------------------------
# EXTRACT FRAMES FOR XAI
# -----------------------------
def extract_faces_for_xai(video_path, max_frames=6):
    cap = cv2.VideoCapture(video_path)
    faces = []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = np.linspace(0, total_frames - 1, max_frames).astype(int)
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
                faces.append(face)

        current += 1

    cap.release()

    if len(faces) == 0:
        raise ValueError("No faces extracted for explainability")

    return faces


# -----------------------------
# VIDEO EXPLAINABILITY
# -----------------------------
def explain_video(video_path, last_conv_layer_name, max_frames=6):
    faces = extract_faces_for_xai(video_path, max_frames)
    cam_frames = []

    # Access Xception inside TimeDistributed
    xception_model = model.layers[1].layer

    for face in faces:
        img = preprocess_input(face.astype("float32"))
        img_array = np.expand_dims(img, axis=0)

        heatmap = generate_gradcam(
            xception_model,
            img_array,
            last_conv_layer_name
        )

        cam = overlay_gradcam(face, heatmap)
        cam_frames.append(cam)

    return cam_frames