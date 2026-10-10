from django.shortcuts import render


def home(request):
    features = [
        {"icon": "🔍", "title": "UPA-YOLO Detection", "desc": "Improved YOLOv7-Tiny with underwater perception attention for precise sea treasure identification.", "color": "rgba(13,110,253,0.15)"},
        {"icon": "⚡", "title": "Real-Time Edge AI", "desc": "Deploy on NVIDIA Jetson Nano with TensorRT acceleration for real-time underwater monitoring.", "color": "rgba(0,212,170,0.15)"},
        {"icon": "📊", "title": "Performance Analytics", "desc": "Detailed mAP scores, inference times, confidence distributions, and species count statistics.", "color": "rgba(255,165,0,0.15)"},
        {"icon": "🎯", "title": "High Accuracy", "desc": "97.8% mAP@0.5 on sea cucumber, sea urchin, and shell detection with minimal false positives.", "color": "rgba(239,68,68,0.12)"},
        {"icon": "🗂️", "title": "Dataset Management", "desc": "Organize and manage underwater datasets for training, validation, and testing workflows.", "color": "rgba(139,92,246,0.15)"},
        {"icon": "📥", "title": "Export Results", "desc": "Download annotated images, bounding box data, and detection reports in multiple formats.", "color": "rgba(6,182,212,0.15)"},
    ]
    return render(request, "core/home.html", {"features": features})


def about(request):
    return render(request, "core/about.html")
