# app.py

from flask import Flask, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import cv2
from ultralytics import YOLO
import os
from supabase import create_client, Client

# Supabase config
SUPABASE_URL = "https://xrddldmmgpfqfeazbisl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyZGRsZG1tZ3BmcWZlYXpiaXNsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc0MzU2NDgsImV4cCI6MjA2MzAxMTY0OH0.CjrFofR7s9ilfLxyxhXVCv_bw0LLXsh9Xm8n7-kgozs"  # Replace with your Supabase anon public key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Flask setup
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
db = SQLAlchemy(app)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    status = db.Column(db.String(10))
    time = db.Column(db.Float)

with app.app_context():
    db.create_all()

model = YOLO("classroom.pt")
video_path = "Input/video_20250516_193634.mp4"
cap = cv2.VideoCapture(video_path)

students = ["Shafaq", "Srinivas", "Renuka", "Imran"]
attendance = {name: {"start_frame": None, "total_frames": 0, "last_seen_frame": None, "away": False} for name in students}
fps = cap.get(cv2.CAP_PROP_FPS)
WASHROOM_TIMEOUT_FRAMES = int(fps * 10)
ATTENDANCE_THRESHOLD_FRAMES = int(fps * 30)
frame_number = 0

def boxes_overlap(box1, box2):
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    return x1_min < x2_max and x1_max > x2_min and y1_min < y2_max and y1_max > y2_min

def generate_stream():
    global frame_number
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_number += 1
        frame = cv2.resize(frame, (1920, 1080))
        results = model(frame)[0]

        current_students = {}
        phone_boxes = []
        phone_usage_high = False

        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            bbox = [x1, y1, x2, y2]

            if label == "Phone":
                phone_boxes.append(bbox)
            elif label in students:
                current_students[label] = bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        for pbox in phone_boxes:
            for sbox in current_students.values():
                if boxes_overlap(pbox, sbox):
                    phone_usage_high = True
                    break

        if phone_usage_high:
            cv2.putText(frame, "Mobile Phone usage = HIGH", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        y_pos = 80
        for name in students:
            data = attendance[name]
            if name in current_students:
                if data["start_frame"] is None or data["away"]:
                    data["start_frame"] = frame_number
                    data["away"] = False
                data["last_seen_frame"] = frame_number
            else:
                if not data["away"] and data["last_seen_frame"] is not None:
                    if frame_number - data["last_seen_frame"] > WASHROOM_TIMEOUT_FRAMES:
                        data["total_frames"] += data["last_seen_frame"] - data["start_frame"]
                        data["away"] = True

            temp_total = data["total_frames"]
            if not data["away"] and data["start_frame"] is not None:
                temp_total += (frame_number - data["start_frame"])
            seconds = round(temp_total / fps, 1)
            cv2.putText(frame, f"{name} Attendance Time: {seconds} sec", (20, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            y_pos += 30

        _, jpeg = cv2.imencode('.jpg', frame)
        frame_data = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

@app.route("/")
def home():
    return "Flask backend for attendance is running."

@app.route("/video_feed")
def video_feed():
    return Response(generate_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/run")
def run_attendance():
    for name in students:
        data = attendance[name]
        if not data["away"] and data["start_frame"] is not None:
            data["total_frames"] += (frame_number - data["start_frame"])
        seconds = round(data["total_frames"] / fps, 2)
        status = "Present" if data["total_frames"] >= ATTENDANCE_THRESHOLD_FRAMES else "Absent"

        record = Attendance(name=name, status=status, time=seconds)
        db.session.add(record)

        supabase.table("attendance").insert({
            "name": name,
            "status": status,
            "time": seconds
        }).execute()

    db.session.commit()
    return jsonify({"message": "✅ Attendance uploaded!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
