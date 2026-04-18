import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import os

class YOLOPredictor:
    def __init__(self, model_path):
        """Initialize the YOLO model."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        self.model = YOLO(model_path)

    def predict_image(self, image_path, show=True, save_output=False, output_path=None):
        """Predict and optionally display/save annotated image."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")

        results = self.model(image_path)
        annotated = results[0].plot()
        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

        if save_output and output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            Image.fromarray(annotated_rgb).save(output_path)

        if show:
            try:
                Image.fromarray(annotated_rgb).show()
            except Exception as e:
                print(f"Error displaying image: {e}")

        return annotated

    def predict_video(self, video_path, display=True, save_output=False, output_path='media/outputs/output_video.avi'):
        """Predict objects in a video and optionally display/save it."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found at {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError("Error opening video stream")

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        out = None
        if save_output:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("End of video or frame read error.")
                break

            results = self.model.predict(source=frame, conf=0.3)
            annotated_frame = results[0].plot()

            if display:
                try:
                    cv2.imshow('YOLOv8 Detection', annotated_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Stopped by user.")
                        break
                except cv2.error as e:
                    print("Display not supported in this environment:", e)
                    break

            if save_output and out:
                out.write(annotated_frame)

        cap.release()
        if out:
            out.release()
        if display:
            cv2.destroyAllWindows()

    def predict_frame(self, frame):
        """Predict objects in a single frame (e.g., from webcam)."""
        results = self.model.predict(source=frame, conf=0.3)[0]
        return results.plot()
