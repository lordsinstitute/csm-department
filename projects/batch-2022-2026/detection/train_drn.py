"""
DRN Training Module for Microaneurysm Detection

Supports training on benchmark datasets:
- e-ophtha-MA (e-ophtha Microaneurysm dataset)
- DiaretDB1-MA (DiaretDB1 Microaneurysm subset)
- ROC (Retinopathy Online Challenge)

Features:
- Data augmentation with medical image-specific transforms
- Validation on multiple datasets
- Checkpointing and early stopping
- Learning rate scheduling
- Comprehensive evaluation metrics
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List, Optional
import cv2

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import callbacks
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

from detection.model_drn import create_drn_model, load_drn_model

# Model paths
MODEL_DIR = Path(__file__).parent / 'models'
DRN_MODEL_PATH = MODEL_DIR / 'drn_microaneurysm_detector.h5'
DRN_WEIGHTS_PATH = MODEL_DIR / 'drn_weights.h5'
DRN_METADATA_PATH = MODEL_DIR / 'drn_training_metadata.json'


def ensure_model_dir():
    """Create models directory if it doesn't exist."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)


class MicroaneurysmDataGenerator(keras.utils.Sequence):
    """
    Custom data generator for microaneurysm detection.
    Loads and augments fundus images with MA annotations.
    """
    
    def __init__(
        self,
        image_paths: List[str],
        annotations: List[Dict],
        batch_size: int = 16,
        image_size: Tuple[int, int] = (512, 512),
        augment: bool = True
    ):
        self.image_paths = image_paths
        self.annotations = annotations
        self.batch_size = batch_size
        self.image_size = image_size
        self.augment = augment
        self.indexes = np.arange(len(image_paths))
    
    def __len__(self):
        """Return number of batches per epoch."""
        return int(np.floor(len(self.image_paths) / self.batch_size))
    
    def __getitem__(self, index):
        """Generate one batch of data."""
        # Get indexes of batch
        batch_indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]
        
        # Get file paths and annotations
        batch_paths = [self.image_paths[k] for k in batch_indexes]
        batch_annotations = [self.annotations[k] for k in batch_indexes]
        
        # Load and process images
        X, y = self._load_batch(batch_paths, batch_annotations)
        return X, y
    
    def _load_batch(self, paths: List[str], annotations: List[Dict]):
        """Load and preprocess a batch of images."""
        X = np.zeros((len(paths), *self.image_size, 3), dtype=np.float32)
        y_ma_prob = np.zeros((len(paths), 1), dtype=np.float32)
        y_bbox = np.zeros((len(paths), 4), dtype=np.float32)
        y_conf = np.zeros((len(paths), 1), dtype=np.float32)
        
        for i, (path, annot) in enumerate(zip(paths, annotations)):
            # Load image
            image = cv2.imread(path)
            if image is None:
                continue
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, self.image_size)
            
            # Data augmentation
            if self.augment:
                image = self._augment_image(image)
            
            X[i] = image
            
            # Parse annotations
            y_ma_prob[i] = 1.0 if annot.get('has_ma', False) else 0.0
            y_bbox[i] = annot.get('bbox', [0, 0, 0, 0])
            y_conf[i] = annot.get('confidence', 0.5)
        
        return X, {
            'ma_probability': y_ma_prob,
            'bbox': y_bbox,
            'confidence': y_conf
        }
    
    def _augment_image(self, image: np.ndarray) -> np.ndarray:
        """Apply medical image-specific augmentation."""
        # Random rotation (-15 to 15 degrees)
        if np.random.rand() > 0.5:
            angle = np.random.uniform(-15, 15)
            h, w = image.shape[:2]
            M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
            image = cv2.warpAffine(image, M, (w, h))
        
        # Random flip (horizontal/vertical)
        if np.random.rand() > 0.5:
            image = cv2.flip(image, 1)  # Horizontal flip
        
        # Random brightness/contrast adjustment
        if np.random.rand() > 0.5:
            alpha = np.random.uniform(0.8, 1.2)  # Contrast
            beta = np.random.uniform(-20, 20)    # Brightness
            image = cv2.convertScaleAbs(image * alpha + beta)
        
        # Gaussian blur occasionally
        if np.random.rand() > 0.7:
            image = cv2.GaussianBlur(image, (3, 3), 0)
        
        return image
    
    def on_epoch_end(self):
        """Shuffle indexes after each epoch."""
        np.random.shuffle(self.indexes)


class BenchmarkDatasetLoader:
    """
    Loads benchmark datasets for microaneurysm detection:
    - e-ophtha-MA
    - DiaretDB1-MA
    - ROC (Retinopathy Online Challenge)
    """
    
    @staticmethod
    def load_eophtha_ma(dataset_path: str) -> Tuple[List[str], List[Dict]]:
        """
        Load e-ophtha Microaneurysm dataset.
        Expected structure:
        - dataset_path/
          - images/
          - annotations/
        """
        image_paths = []
        annotations = []
        
        images_dir = Path(dataset_path) / 'images'
        annot_dir = Path(dataset_path) / 'annotations'
        
        for img_file in images_dir.glob('*.jpg'):
            annot_file = annot_dir / f"{img_file.stem}.json"
            
            if annot_file.exists():
                with open(annot_file) as f:
                    annot = json.load(f)
                
                image_paths.append(str(img_file))
                annotations.append(annot)
        
        return image_paths, annotations
    
    @staticmethod
    def load_diaretdb1_ma(dataset_path: str) -> Tuple[List[str], List[Dict]]:
        """
        Load DiaretDB1 Microaneurysm dataset.
        Expected structure:
        - dataset_path/
          - images/
          - masks/
        """
        image_paths = []
        annotations = []
        
        images_dir = Path(dataset_path) / 'images'
        masks_dir = Path(dataset_path) / 'masks'
        
        for img_file in images_dir.glob('*.jpg'):
            mask_file = masks_dir / f"{img_file.stem}_MA.png"
            
            if mask_file.exists():
                # Load and analyze mask to extract MA locations
                mask = cv2.imread(str(mask_file), cv2.IMREAD_GRAYSCALE)
                contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                
                has_ma = len(contours) > 0
                
                if contours:
                    x, y, w, h = cv2.boundingRect(np.vstack(contours))
                    bbox = [x, y, w, h]
                    confidence = 0.9
                else:
                    bbox = [0, 0, 0, 0]
                    confidence = 0.1
                
                image_paths.append(str(img_file))
                annotations.append({
                    'has_ma': has_ma,
                    'bbox': bbox,
                    'confidence': confidence
                })
        
        return image_paths, annotations
    
    @staticmethod
    def load_roc_dataset(dataset_path: str) -> Tuple[List[str], List[Dict]]:
        """
        Load ROC (Retinopathy Online Challenge) dataset.
        Expected structure:
        - dataset_path/
          - images/
          - lesions/
        """
        image_paths = []
        annotations = []
        
        images_dir = Path(dataset_path) / 'images'
        lesions_dir = Path(dataset_path) / 'lesions'
        
        for img_file in images_dir.glob('*.tif'):
            lesion_file = lesions_dir / f"{img_file.stem}_MA.txt"
            
            # Load image
            image_paths.append(str(img_file))
            
            # Load lesion annotations if exists
            if lesion_file.exists():
                with open(lesion_file) as f:
                    lines = f.readlines()
                
                has_ma = len(lines) > 0
                
                if lines:
                    # Parse first microaneurysm (format: x,y,diameter,type)
                    parts = lines[0].strip().split(',')
                    x, y, d = float(parts[0]), float(parts[1]), float(parts[2])
                    bbox = [x - d/2, y - d/2, d, d]
                    confidence = 0.9
                else:
                    bbox = [0, 0, 0, 0]
                    confidence = 0.1
                
                annotations.append({
                    'has_ma': has_ma,
                    'bbox': bbox,
                    'confidence': confidence
                })
            else:
                annotations.append({
                    'has_ma': False,
                    'bbox': [0, 0, 0, 0],
                    'confidence': 0.1
                })
        
        return image_paths, annotations


def train_drn_model(
    dataset_type: str = 'eophtha',
    dataset_path: Optional[str] = None,
    epochs: int = 50,
    batch_size: int = 16,
    validation_split: float = 0.2,
    save: bool = True
) -> Optional[str]:
    """
    Train DRN model on benchmark datasets.
    
    Args:
        dataset_type: 'eophtha', 'diaretdb1', or 'roc'
        dataset_path: Path to dataset directory
        epochs: Number of training epochs
        batch_size: Training batch size
        validation_split: Fraction for validation
        save: Whether to save trained model
        
    Returns:
        Path to saved model, or None if training failed
    """
    if not HAS_TENSORFLOW:
        print("❌ TensorFlow not installed. Install with: pip install tensorflow")
        return None
    
    ensure_model_dir()
    
    # Load dataset
    print(f"📚 Loading {dataset_type} dataset...")
    loader = BenchmarkDatasetLoader()
    
    if dataset_type.lower() == 'eophtha':
        image_paths, annotations = loader.load_eophtha_ma(dataset_path)
    elif dataset_type.lower() == 'diaretdb1':
        image_paths, annotations = loader.load_diaretdb1_ma(dataset_path)
    elif dataset_type.lower() == 'roc':
        image_paths, annotations = loader.load_roc_dataset(dataset_path)
    else:
        raise ValueError(f"Unknown dataset type: {dataset_type}")
    
    if not image_paths:
        print(f"❌ No images found in {dataset_path}")
        return None
    
    print(f"✅ Loaded {len(image_paths)} images")
    
    # Split into train and validation
    num_samples = len(image_paths)
    num_train = int(num_samples * (1 - validation_split))
    
    train_paths = image_paths[:num_train]
    train_annot = annotations[:num_train]
    val_paths = image_paths[num_train:]
    val_annot = annotations[num_train:]
    
    # Create data generators
    train_gen = MicroaneurysmDataGenerator(
        train_paths, train_annot,
        batch_size=batch_size,
        augment=True
    )
    
    val_gen = MicroaneurysmDataGenerator(
        val_paths, val_annot,
        batch_size=batch_size,
        augment=False
    )
    
    # Create and compile model
    print("🏗️  Creating DRN model...")
    model = create_drn_model(num_rois=8, learning_rate=1e-4)
    
    # Callbacks
    callback_list = [
        callbacks.ModelCheckpoint(
            str(DRN_WEIGHTS_PATH),
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        ),
        callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Train
    print(f"🚀 Training DRN model for {epochs} epochs...")
    history = model.fit(
        train_gen,
        epochs=epochs,
        validation_data=val_gen,
        callbacks=callback_list,
        verbose=1
    )
    
    # Save model and metadata
    if save:
        model.save(str(DRN_MODEL_PATH))
        
        metadata = {
            'dataset_type': dataset_type,
            'num_training_samples': len(train_paths),
            'num_validation_samples': len(val_paths),
            'epochs': epochs,
            'batch_size': batch_size,
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1]),
            'training_history': {
                'loss': [float(x) for x in history.history['loss']],
                'val_loss': [float(x) for x in history.history['val_loss']]
            }
        }
        
        with open(DRN_METADATA_PATH, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Model saved to {DRN_MODEL_PATH}")
        print(f"📊 Metadata saved to {DRN_METADATA_PATH}")
        
        return str(DRN_MODEL_PATH)
    
    return None


def evaluate_drn_model(
    model_path: str,
    dataset_type: str = 'eophtha',
    dataset_path: Optional[str] = None
) -> Dict:
    """
    Evaluate a trained DRN model on a dataset.
    
    Returns:
        Dictionary with evaluation metrics
    """
    if not HAS_TENSORFLOW:
        return {}
    
    # Load model
    model = load_drn_model(model_path)
    
    # Load dataset
    loader = BenchmarkDatasetLoader()
    
    if dataset_type.lower() == 'eophtha':
        image_paths, annotations = loader.load_eophtha_ma(dataset_path)
    elif dataset_type.lower() == 'diaretdb1':
        image_paths, annotations = loader.load_diaretdb1_ma(dataset_path)
    elif dataset_type.lower() == 'roc':
        image_paths, annotations = loader.load_roc_dataset(dataset_path)
    else:
        return {}
    
    # Create evaluation generator
    eval_gen = MicroaneurysmDataGenerator(
        image_paths, annotations,
        batch_size=16,
        augment=False
    )
    
    # Evaluate
    results = model.evaluate(eval_gen)
    
    return {
        'dataset_type': dataset_type,
        'num_samples': len(image_paths),
        'loss': float(results[0]) if isinstance(results, list) else float(results),
        'ma_accuracy': float(results[1]) if len(results) > 1 else None
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train DRN model for microaneurysm detection')
    parser.add_argument('--dataset', type=str, choices=['eophtha', 'diaretdb1', 'roc'],
                       default='eophtha', help='Dataset type')
    parser.add_argument('--path', type=str, help='Path to dataset directory')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size')
    parser.add_argument('--validation-split', type=float, default=0.2, help='Validation split ratio')
    
    args = parser.parse_args()
    
    print("🎯 DRN Training for Microaneurysm Detection")
    print("=" * 50)
    
    model_path = train_drn_model(
        dataset_type=args.dataset,
        dataset_path=args.path,
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_split=args.validation_split
    )
    
    if model_path:
        print(f"\n✅ Training completed successfully!")
        print(f"📦 Model saved: {model_path}")
    else:
        print("\n❌ Training failed")
