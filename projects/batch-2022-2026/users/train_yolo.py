from ultralytics import YOLO
import os

DATA_YAML = os.path.abspath(r"media\car\yolov8n.pt")

model = YOLO('yolov8n.pt')

results = model.train(
    data=DATA_YAML,
    epochs=10,
    imgsz=640,
    project='yolo_project',
    name='exp1',
    exist_ok=True
)

metrics_path = os.path.join('yolo_project', 'exp1', 'metrics.txt')
with open(metrics_path, 'w') as f:
    f.write(str(results))
