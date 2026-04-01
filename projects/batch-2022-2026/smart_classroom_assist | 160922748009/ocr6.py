from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import time
from PIL import Image
import pytesseract
import easyocr
from fpdf import FPDF
import google.generativeai as genai
import re

# === Configuration ===
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
genai.configure(api_key="AIzaSyAkbyZQPcLJzy9AxyaYQw4ak8fOf9OJwBw")
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
CORS(app)

# === Mediapipe Setup ===
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# === OCR & PDF Functions ===
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, h=30)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    return image, thresh

def extract_text_tesseract(processed_img):
    return pytesseract.image_to_string(processed_img)

def extract_text_easyocr(image_path):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(image_path, detail=0)
    return "\n".join(results)

def summarize_text(text):
    prompt = f"""You are an expert teacher explaining the topic: "{text}" to a beginner.
Provide:
1. A clear and concise explanation (easy to understand).
2. 2 or 3 real-life examples or applications.
Avoid markdown, asterisks, or special formatting characters in your output."""
    response = model.generate_content(prompt)
    return response.text.strip()

def sanitize_text_for_pdf(text):
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    text = re.sub(r'[^\x00-\xFF]+', '', text)
    return text

def generate_pdf(summary_text, output_path="summarized_notes.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    summary_text = sanitize_text_for_pdf(summary_text)
    pdf.multi_cell(0, 10, summary_text)
    pdf.output(output_path)
    print(f"[✓] PDF saved as '{output_path}'")

def process_board_image(image_path):
    print("[INFO] Preprocessing image...")
    image, processed = preprocess_image(image_path)

    print("[INFO] Extracting text with Tesseract OCR...")
    extracted_text = extract_text_tesseract(processed)
    print("[DEBUG] Tesseract Output:\n", extracted_text)

    if not extracted_text.strip():
        print("[WARNING] Tesseract found no text. Trying EasyOCR...")
        extracted_text = extract_text_easyocr(image_path)
        print("[DEBUG] EasyOCR Output:\n", extracted_text)

    if not extracted_text.strip():
        print("[ERROR] No text detected by either OCR engine.")
        return

    print("[INFO] Summarizing extracted text using Gemini...")
    summary = summarize_text(extracted_text)

    print("[INFO] Generating PDF...")
    generate_pdf(summary)

# === Gesture Detection ===
def fingersup(lm):
    fingers = []
    fingers.append(0)  # Thumb
    fingers.append(1 if lm[8][1] < lm[6][1] else 0)
    fingers.append(1 if lm[12][1] < lm[10][1] else 0)
    fingers.append(1 if lm[16][1] < lm[14][1] else 0)
    fingers.append(1 if lm[20][1] < lm[18][1] else 0)
    return fingers

# === Video Streaming Logic ===
triggered = False
trigger_time = None
image_captured = False
video_path = 'WhatsApp Video 2025-05-18 at 09.49.33_280ba28a.mp4'

def generate_frames():
    global triggered, trigger_time, image_captured
    cap = cv2.VideoCapture(video_path)

    while True:
        success, img = cap.read()
        if not success:
            break

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            lm_list = []
            h, w, _ = img.shape
            for lm in hand.landmark:
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))

            finger_state = fingersup(lm_list)
            print("Fingers:", finger_state)

            if finger_state == [0, 0, 1, 1, 0] and not triggered:
                print("[INFO] Gesture Detected: Starting wait before capture...")
                triggered = True
                trigger_time = time.time()

        if triggered and not image_captured:
            elapsed = time.time() - trigger_time
            if elapsed >= 6:
                image_path = "ocr_capture.png"
                cv2.imwrite(image_path, img)
                print("[INFO] Frame captured. Starting OCR and PDF generation.")
                process_board_image(image_path)
                image_captured = True

        _, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return jsonify({"message": "OCR Gesture Flask Server Running."})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
