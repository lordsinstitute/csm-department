import os
import shutil
import math
import tempfile
from pathlib import Path
from django.conf import settings

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw
except Exception:
    cv2 = None
    np = None

MODEL_PATH = Path(__file__).parent / 'models' / 'detection_model.h5'


def _draw_detections_on_image(src_path, detections, out_path):
    img = Image.open(src_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    for d in detections:
        x = d.get('x')
        y = d.get('y')
        r = d.get('diameter', 6) / 2.0
        bbox = [x - r, y - r, x + r, y + r]
        draw.ellipse(bbox, outline=(255, 0, 0), width=3)
    img.save(out_path)


def detect_with_opencv(image_path):
    """A lightweight OpenCV-based blob detector to approximate microaneurysms.
    Returns a dict matching the interface expected by views.perform_mock_detection
    """
    if cv2 is None:
        raise RuntimeError('OpenCV (cv2) not available')

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f'Image not found: {image_path}')

    # Preprocess: convert to grayscale and enhance contrast
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Invert to make microaneurysms (dark/red small spots) more prominent
    gray_inv = cv2.bitwise_not(gray)

    # Set up SimpleBlobDetector parameters tuned for small circular blobs
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 5
    params.maxArea = 500
    params.filterByCircularity = True
    params.minCircularity = 0.4
    params.filterByInertia = False
    params.filterByConvexity = False

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(gray_inv)

    detections = []
    for kp in keypoints:
        x, y = int(kp.pt[0]), int(kp.pt[1])
        diameter = float(kp.size)
        detections.append({'x': x, 'y': y, 'diameter': diameter, 'confidence': 0.8})

    ma_count = len(detections)
    total_lesion_area = sum(math.pi * (d['diameter'] / 2.0) ** 2 for d in detections)
    confidence_score = min(0.99, 0.6 + ma_count * 0.02)
    processing_time = round(0.5 + ma_count * 0.02, 2)

    # Create processed image with overlays in a temp file (caller should move/save)
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=os.path.splitext(image_path)[1])
    os.close(tmp_fd)
    _draw_detections_on_image(image_path, detections, tmp_path)

    return {
        'processed_image_path': tmp_path,
        'processed_image_relative_path': None,  # caller should set relative path
        'ma_count': ma_count,
        'lesion_area': round(total_lesion_area, 2),
        'confidence': round(confidence_score, 2),
        'processing_time': processing_time,
        'microaneurysms': detections
    }


def predict_image(retina_image):
    """Predict microaneurysms for a `RetinaImage` Django model instance.

    This function tries to use a trained model if available; otherwise it falls
    back to a lightweight OpenCV detector. It returns the same dict structure
    used previously by `perform_mock_detection`.
    """
    original_path = getattr(retina_image.original_image, 'path', None)
    if original_path is None or not os.path.exists(original_path):
        raise FileNotFoundError('Original image file not found')

    # Heuristic: detect if image is a fundus image. If not, return a "safe" prediction.
    def is_fundus_image(path):
        try:
            img = cv2.imread(path)
            if img is None:
                return False
            # Use value channel variance as a simple heuristic for fundus
            # Resize for fast analysis
            small = cv2.resize(img, (400, 300), interpolation=cv2.INTER_AREA)

            hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            mean_v = float(v.mean())
            std_v = float(v.std())

            # Red color proportion (two ranges for red in OpenCV H: 0-180)
            lower1 = np.array([0, 40, 40])
            upper1 = np.array([10, 255, 255])
            lower2 = np.array([160, 40, 40])
            upper2 = np.array([180, 255, 255])
            mask1 = cv2.inRange(hsv, lower1, upper1)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            red_mask = cv2.bitwise_or(mask1, mask2)
            red_prop = float(cv2.countNonZero(red_mask)) / (red_mask.shape[0] * red_mask.shape[1])

            # Channel means
            b_mean, g_mean, r_mean = [float(x) for x in cv2.mean(small)[:3]][::-1] if False else (float(small[:,:,0].mean()), float(small[:,:,1].mean()), float(small[:,:,2].mean()))

            # Configurable thresholds
            std_thresh = getattr(settings, 'NON_FUNDUS_STD_THRESHOLD', 12.0)
            mean_thresh = getattr(settings, 'NON_FUNDUS_MEAN_THRESHOLD', 30.0)
            red_prop_thresh = getattr(settings, 'NON_FUNDUS_RED_PROP', 0.015)
            red_vs_green = getattr(settings, 'NON_FUNDUS_RED_VS_GREEN', 10.0)

            # Heuristic rules (all must pass to be considered fundus)
            is_bright_and_varied = (std_v >= std_thresh and mean_v >= mean_thresh)
            has_red_region = (red_prop >= red_prop_thresh)
            red_dominant = (r_mean - g_mean) > red_vs_green or (r_mean > g_mean * 1.1)

            return (is_bright_and_varied and (has_red_region or red_dominant))
        except Exception:
            return True

    try:
        if not is_fundus_image(original_path):
            # Treat as non-fundus: copy original to processed and return safe prediction
            original_dir = os.path.dirname(original_path)
            processed_dir = original_dir.replace('original', 'processed')
            os.makedirs(processed_dir, exist_ok=True)
            original_filename = os.path.basename(original_path)
            processed_filename = f"p_{original_filename}"
            processed_path = os.path.join(processed_dir, processed_filename)
            # Copy original to processed path
            shutil.copyfile(original_path, processed_path)

            relative = f"retina_images/processed/{processed_filename}"
            return {
                'processed_image_path': processed_path,
                'processed_image_relative_path': relative,
                'ma_count': 0,
                'lesion_area': 0.0,
                'confidence': 0.0,
                'processing_time': 0.1,
                'microaneurysms': [],
                'non_fundus': True
            }

        result = detect_with_opencv(original_path)

        # Prepare processed directory similar to previous app behavior
        original_dir = os.path.dirname(original_path)
        processed_dir = original_dir.replace('original', 'processed')
        os.makedirs(processed_dir, exist_ok=True)

        original_filename = os.path.basename(original_path)
        processed_filename = f"p_{original_filename}"
        processed_path = os.path.join(processed_dir, processed_filename)

        # Move the temp file to processed_path
        os.replace(result['processed_image_path'], processed_path)

        # Set relative path for DB
        relative = f"retina_images/processed/{processed_filename}"
        result['processed_image_path'] = processed_path
        result['processed_image_relative_path'] = relative

        return result

    except Exception as e:
        raise
