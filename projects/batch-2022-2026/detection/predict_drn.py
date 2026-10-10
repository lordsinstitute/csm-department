"""
DRN Prediction Module for Microaneurysm Detection

Integrates the Dilated Residual Network with the existing detection pipeline.
Automatically uses DRN if available, otherwise falls back to OpenCV detector.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None

from detection.model_drn import load_drn_model
from detection.model import detect_with_opencv

# Model path
DRN_MODEL_PATH = Path(__file__).parent / 'models' / 'drn_microaneurysm_detector.h5'


def preprocess_image_for_drn(image_path: str, target_size: Tuple[int, int] = (512, 512)) -> np.ndarray:
    """
    Preprocess retina image for DRN model.
    
    Args:
        image_path: Path to retina image
        target_size: Target image size (512, 512)
        
    Returns:
        Preprocessed image array
    """
    if cv2 is None:
        raise ImportError("OpenCV required for image preprocessing")
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Resize to target size
    image = cv2.resize(image, target_size)
    
    # Normalize to [0, 1]
    image = image.astype(np.float32) / 255.0
    
    # Add batch dimension
    image = np.expand_dims(image, axis=0)
    
    return image


def detect_microaneurysms_drn(image_path: str, confidence_threshold: float = 0.5) -> Dict:
    """
    Detect microaneurysms using DRN model.
    
    Args:
        image_path: Path to retina image
        confidence_threshold: Minimum confidence for detection
        
    Returns:
        Dictionary with detection results matching OpenCV detector interface
    """
    if not DRN_MODEL_PATH.exists():
        raise FileNotFoundError(f"DRN model not found: {DRN_MODEL_PATH}")
    
    # Load model
    try:
        model = load_drn_model(str(DRN_MODEL_PATH))
    except Exception as e:
        raise RuntimeError(f"Failed to load DRN model: {str(e)}")
    
    # Preprocess image
    image_array = preprocess_image_for_drn(image_path)
    
    # Run inference
    predictions = model.predict(image_array, verbose=0)
    
    # Extract predictions
    ma_probabilities = predictions['ma_probability'][0]
    bboxes = predictions['bbox'][0]
    confidences = predictions['confidence'][0]
    
    # Filter detections by confidence threshold
    detections = []
    
    if float(confidences[0]) > confidence_threshold:
        x, y, w, h = bboxes
        
        # Convert from normalized to pixel coordinates
        image = cv2.imread(image_path)
        h_img, w_img = image.shape[:2]
        
        x_px = int(x * w_img)
        y_px = int(y * h_img)
        w_px = int(w * w_img)
        h_px = int(h * h_img)
        
        # Diameter approximation
        diameter = max(w_px, h_px)
        
        detections.append({
            'x': x_px + w_px // 2,
            'y': y_px + h_px // 2,
            'diameter': diameter,
            'confidence': float(confidences[0])
        })
    
    # Calculate metrics
    ma_count = len(detections)
    total_lesion_area = sum(
        np.pi * (d['diameter'] / 2.0) ** 2 for d in detections
    )
    overall_confidence = float(ma_probabilities[0])
    
    # Create processed image with detections overlayed
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=os.path.splitext(image_path)[1])
    os.close(tmp_fd)
    
    _draw_detections_on_image(image_path, detections, tmp_path)
    
    return {
        'processed_image_path': tmp_path,
        'processed_image_relative_path': None,
        'ma_count': ma_count,
        'lesion_area': round(total_lesion_area, 2),
        'confidence': round(overall_confidence, 3),
        'processing_time': 0.5,  # Placeholder
        'microaneurysms': detections,
        'model_type': 'DRN'  # Identifier for DRN model
    }


def _draw_detections_on_image(src_path: str, detections: List[Dict], out_path: str):
    """
    Draw detected microaneurysms on image.
    
    Args:
        src_path: Source image path
        detections: List of detection dictionaries
        out_path: Output image path
    """
    if Image is None:
        raise ImportError("Pillow required for image drawing")
    
    img = Image.open(src_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Draw circles for each detection
    for d in detections:
        x = d.get('x', 0)
        y = d.get('y', 0)
        r = d.get('diameter', 10) / 2.0
        
        # Draw circle
        bbox = [x - r, y - r, x + r, y + r]
        draw.ellipse(bbox, outline=(255, 0, 0), width=3)
        
        # Draw confidence text
        confidence = d.get('confidence', 0)
        draw.text((x - r, y - r - 15), f"{confidence:.2f}", fill=(255, 0, 0))
    
    img.save(out_path)


def predict_with_drn_fallback(image_path: str, use_drn: bool = True) -> Dict:
    """
    Predict microaneurysms with DRN, falling back to OpenCV if needed.
    
    Args:
        image_path: Path to retina image
        use_drn: Whether to try DRN model first
        
    Returns:
        Detection results dictionary
    """
    # Try DRN if available
    if use_drn and DRN_MODEL_PATH.exists():
        try:
            print("Using DRN model for detection...")
            return detect_microaneurysms_drn(image_path)
        except Exception as e:
            print(f"⚠️  DRN detection failed, falling back to OpenCV: {str(e)}")
    
    # Fallback to OpenCV
    print("Using OpenCV detector...")
    return detect_with_opencv(image_path)


def batch_predict_drn(image_paths: List[str], use_drn: bool = True) -> List[Dict]:
    """
    Run predictions on multiple images.
    
    Args:
        image_paths: List of image paths
        use_drn: Whether to use DRN model
        
    Returns:
        List of detection results
    """
    results = []
    
    for i, image_path in enumerate(image_paths):
        print(f"Processing image {i+1}/{len(image_paths)}: {image_path}")
        
        try:
            result = predict_with_drn_fallback(image_path, use_drn=use_drn)
            results.append(result)
        except Exception as e:
            print(f"❌ Error processing {image_path}: {str(e)}")
            results.append(None)
    
    return results


def get_model_info() -> Dict:
    """Get information about available models."""
    info = {
        'drn_available': DRN_MODEL_PATH.exists(),
        'drn_path': str(DRN_MODEL_PATH) if DRN_MODEL_PATH.exists() else None,
        'opencv_available': cv2 is not None
    }
    
    return info


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Predict microaneurysms using DRN')
    parser.add_argument('image_path', type=str, help='Path to retina image')
    parser.add_argument('--use-opencv', action='store_true', help='Force OpenCV detector')
    
    args = parser.parse_args()
    
    print("🔍 Microaneurysm Detection (DRN)")
    print("=" * 50)
    
    result = predict_with_drn_fallback(args.image_path, use_drn=not args.use_opencv)
    
    print(f"\n📊 Detection Results:")
    print(f"   Microaneurysms: {result['ma_count']}")
    print(f"   Lesion Area: {result['lesion_area']} px²")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Model Type: {result.get('model_type', 'OpenCV')}")
    print(f"\n✅ Detections saved to: {result['processed_image_path']}")
