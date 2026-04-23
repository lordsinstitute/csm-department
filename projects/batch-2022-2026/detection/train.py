"""
Training module for Diabetic Retinopathy Detection Model

This module provides infrastructure for training a microaneurysm detection model
using available retina images and their associated detection results.

Supports:
  - OpenCV-based feature extraction for quick training
  - TensorFlow/Keras integration (optional) for deep learning
  - Data augmentation and preprocessing
  - Model validation and evaluation

Usage:
  from detection.train import train_model
  model_path = train_model(epochs=10, batch_size=32)
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import Tuple, List, Dict, Optional

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

# Model checkpoint and metadata paths
MODEL_DIR = Path(__file__).parent / 'models'
MODEL_PATH = MODEL_DIR / 'detection_model.h5'
METADATA_PATH = MODEL_DIR / 'training_metadata.json'


def ensure_model_dir():
    """Create models directory if it doesn't exist."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)


def extract_features_opencv(image_path: str) -> Optional[np.ndarray]:
    """Extract features from a retina image using OpenCV.
    
    Args:
        image_path: Path to the retina image file
        
    Returns:
        Feature vector (numpy array) or None if extraction fails
    """
    if cv2 is None:
        return None
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Compute histogram features
        hist = cv2.calcHist([enhanced], [0], None, [32], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        
        # Compute Canny edges for structural features
        edges = cv2.Canny(enhanced, 50, 150)
        edge_ratio = np.sum(edges > 0) / edges.size
        
        # Compute Laplacian variance (focus measure)
        laplacian = cv2.Laplacian(enhanced, cv2.CV_64F)
        focus = laplacian.var()
        
        # Combine features
        features = np.concatenate([hist, [edge_ratio, focus]])
        
        return features
    
    except Exception as e:
        print(f"Error extracting features from {image_path}: {e}")
        return None


def create_keras_model(input_shape: int) -> keras.Model:
    """Create a simple Keras model for microaneurysm detection.
    
    Args:
        input_shape: Number of input features
        
    Returns:
        Compiled Keras model
    """
    if not HAS_TENSORFLOW:
        raise ImportError("TensorFlow/Keras not installed. "
                         "Install with: pip install tensorflow")
    
    model = keras.Sequential([
        layers.Dense(128, activation='relu', input_shape=(input_shape,)),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(32, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', keras.metrics.AUC()]
    )
    
    return model


def prepare_training_data(image_queryset) -> Tuple[np.ndarray, np.ndarray]:
    """Prepare features and labels from Django RetinaImage queryset.
    
    Args:
        image_queryset: Django QuerySet of RetinaImage objects
        
    Returns:
        Tuple of (features_array, labels_array)
    """
    features_list = []
    labels_list = []
    
    for retina_image in image_queryset:
        image_path = retina_image.original_image.path
        
        # Extract features
        features = extract_features_opencv(image_path)
        if features is None:
            continue
        
        # Determine label: 1 if microaneurysms detected, 0 otherwise
        has_detection = hasattr(retina_image, 'detection_result')
        label = 1 if (has_detection and retina_image.detection_result.microaneurysms_count > 0) else 0
        
        features_list.append(features)
        labels_list.append(label)
    
    if not features_list:
        raise ValueError("No valid training data could be extracted")
    
    X = np.array(features_list)
    y = np.array(labels_list)
    
    return X, y


def train_model(
    epochs: int = 10,
    batch_size: int = 32,
    validation_split: float = 0.2,
    save: bool = True
) -> Optional[str]:
    """Train the microaneurysm detection model using available retina images.
    
    Args:
        epochs: Number of training epochs
        batch_size: Training batch size
        validation_split: Fraction of data to use for validation
        save: Whether to save the trained model
        
    Returns:
        Path to saved model file, or None if training failed
    """
    ensure_model_dir()
    
    # Import Django models
    try:
        from images.models import RetinaImage
    except ImportError as e:
        print(f"Error importing Django models: {e}")
        return None
    
    # Prepare training data
    try:
        image_queryset = RetinaImage.objects.all()
        X, y = prepare_training_data(image_queryset)
        print(f"Prepared {len(X)} training samples")
        print(f"Class distribution: {np.sum(y)} positive, {len(y) - np.sum(y)} negative")
    except ValueError as e:
        print(f"Error preparing training data: {e}")
        return None
    
    # Create and train model
    if not HAS_TENSORFLOW:
        print("⚠️  TensorFlow not installed. Using fallback OpenCV detector.")
        print("Install TensorFlow for model training: pip install tensorflow")
        return None
    
    try:
        model = create_keras_model(X.shape[1])
        
        history = model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )
        
        # Save model and metadata
        if save:
            model.save(str(MODEL_PATH))
            
            metadata = {
                'num_samples': len(X),
                'num_features': X.shape[1],
                'epochs': epochs,
                'batch_size': batch_size,
                'final_accuracy': float(history.history['accuracy'][-1]),
                'final_val_accuracy': float(history.history['val_accuracy'][-1])
            }
            
            with open(METADATA_PATH, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"\n✅ Model saved to {MODEL_PATH}")
            print(f"📊 Metadata saved to {METADATA_PATH}")
            
            return str(MODEL_PATH)
    
    except Exception as e:
        print(f"Error during training: {e}")
        return None


def evaluate_model(X_test: np.ndarray, y_test: np.ndarray) -> Optional[Dict]:
    """Evaluate the trained model on test data.
    
    Args:
        X_test: Test features array
        y_test: Test labels array
        
    Returns:
        Dict with evaluation metrics, or None if model not found
    """
    if not MODEL_PATH.exists() or not HAS_TENSORFLOW:
        return None
    
    try:
        model = keras.models.load_model(str(MODEL_PATH))
        loss, accuracy, auc = model.evaluate(X_test, y_test, verbose=0)
        
        return {
            'loss': float(loss),
            'accuracy': float(accuracy),
            'auc': float(auc)
        }
    except Exception as e:
        print(f"Error evaluating model: {e}")
        return None


if __name__ == '__main__':
    # CLI entry point for training
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Train diabetic retinopathy detection model'
    )
    parser.add_argument('--epochs', type=int, default=10, 
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Training batch size')
    parser.add_argument('--validation-split', type=float, default=0.2,
                       help='Validation data split ratio')
    
    args = parser.parse_args()
    
    print("🚀 Starting model training...")
    model_path = train_model(
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_split=args.validation_split
    )
    
    if model_path:
        print(f"\n✅ Training completed successfully!")
        print(f"Model: {model_path}")
    else:
        print("\n❌ Training failed or not completed")
