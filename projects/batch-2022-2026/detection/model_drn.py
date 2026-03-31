"""
Dilated Residual Network (DRN) for Microaneurysm Detection

Implements a state-of-the-art deep learning model with:
- Dilated convolutions for expanded receptive field
- ROI (Region of Interest) layer for 28x28 high-resolution detection
- Batch normalization and dropout for regularization
- Optimized for small, low-contrast microaneurysm features

Architecture:
    Input (512x512) → DRN Backbone → ROI Layer (28x28) → Dense Classifier → Output
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import numpy as np


class DilatedResidualBlock(layers.Layer):
    """
    Dilated Residual Block with exponentially increasing dilation rates.
    Allows model to see larger receptive fields without losing resolution.
    """
    
    def __init__(self, filters, dilation_rate=1, kernel_size=3, **kwargs):
        super(DilatedResidualBlock, self).__init__(**kwargs)
        self.filters = filters
        self.dilation_rate = dilation_rate
        self.kernel_size = kernel_size
        
        # Dilated convolution
        self.conv1 = layers.Conv2D(
            filters, 
            kernel_size, 
            padding='same',
            dilation_rate=dilation_rate,
            activation=None,
            use_bias=False
        )
        self.bn1 = layers.BatchNormalization()
        self.activation = layers.ReLU()
        
        # Second dilated convolution
        self.conv2 = layers.Conv2D(
            filters,
            kernel_size,
            padding='same',
            dilation_rate=dilation_rate,
            activation=None,
            use_bias=False
        )
        self.bn2 = layers.BatchNormalization()
        
        # Skip connection (1x1 conv if needed)
        self.conv_skip = layers.Conv2D(filters, 1, padding='same', use_bias=False)
        self.bn_skip = layers.BatchNormalization()
    
    def call(self, x):
        # Main path
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.activation(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        # Skip connection
        skip = self.conv_skip(x)
        skip = self.bn_skip(skip)
        
        # Add and activate
        out = layers.Add()([out, skip])
        out = self.activation(out)
        
        return out


class ROILayer(layers.Layer):
    """
    Region of Interest (ROI) Layer that processes 28x28 patches.
    Operates on high-resolution features to detect small, low-contrast microaneurysms.
    
    Process:
    1. Extract 28x28 patches from feature maps
    2. Process each patch independently
    3. Aggregate patch-level predictions
    """
    
    def __init__(self, roi_size=28, num_rois=16, **kwargs):
        super(ROILayer, self).__init__(**kwargs)
        self.roi_size = roi_size
        self.num_rois = num_rois
        
        # Conv layers for ROI processing
        self.roi_conv1 = layers.Conv2D(64, 3, padding='same', activation='relu')
        self.roi_pool = layers.MaxPooling2D(2)
        self.roi_conv2 = layers.Conv2D(32, 3, padding='same', activation='relu')
        self.roi_flat = layers.Flatten()
        self.roi_dense = layers.Dense(64, activation='relu')
        self.roi_dropout = layers.Dropout(0.3)
    
    def call(self, x):
        """
        Process feature maps through ROI layer.
        x: (batch_size, height, width, channels)
        """
        batch_size = tf.shape(x)[0]
        h = tf.shape(x)[1]
        w = tf.shape(x)[2]
        
        # Extract overlapping ROI patches (28x28)
        # For simplicity, extract center patches and corners
        roi_features = []
        
        # Center ROI
        roi_center = tf.image.central_crop(x, 0.5)  # 28x28 from 56x56
        roi_features.append(self._process_roi(roi_center))
        
        # Top-left, top-right, bottom-left, bottom-right corners
        for i in range(1, min(self.num_rois, 5)):
            # Random augmentation of ROI position
            roi = tf.image.random_crop(x, [batch_size, self.roi_size, self.roi_size, tf.shape(x)[-1]])
            roi_features.append(self._process_roi(roi))
        
        # Aggregate ROI features
        if roi_features:
            aggregated = tf.reduce_mean(tf.stack(roi_features, axis=1), axis=1)
            return aggregated
        
        return x
    
    def _process_roi(self, roi_patch):
        """Process a single ROI patch through the network."""
        x = self.roi_conv1(roi_patch)
        x = self.roi_pool(x)
        x = self.roi_conv2(x)
        x = self.roi_pool(x)
        x = self.roi_flat(x)
        x = self.roi_dense(x)
        x = self.roi_dropout(x)
        return x


class DRNMicroaneurysmDetector(models.Model):
    """
    Dilated Residual Network for Microaneurysm Detection.
    
    Architecture:
    - Input: 512x512 RGB fundus image
    - Backbone: DRN with dilated convolutions (dilation rates: 1, 2, 4)
    - ROI Layer: 28x28 high-resolution feature processing
    - Classifier: Dense layers for binary classification (MA or not)
    - Output: Microaneurysm probability and bounding box coordinates
    """
    
    def __init__(self, num_rois=8, **kwargs):
        super(DRNMicroaneurysmDetector, self).__init__(**kwargs)
        self.num_rois = num_rois
        
        # Input layer
        self.input_layer = layers.Input(shape=(512, 512, 3))
        
        # Preprocessing: Normalization
        self.normalize = layers.Lambda(lambda x: x / 255.0)
        
        # Initial convolution block
        self.init_conv = layers.Conv2D(32, 7, padding='same', activation='relu')
        self.init_bn = layers.BatchNormalization()
        self.init_pool = layers.MaxPooling2D(2)  # 256x256
        
        # DRN blocks with increasing dilation rates
        self.drn_block1 = DilatedResidualBlock(64, dilation_rate=1)
        self.drn_block2 = DilatedResidualBlock(128, dilation_rate=2)
        self.drn_block3 = DilatedResidualBlock(256, dilation_rate=4)
        
        # Downsampling
        self.downsample1 = layers.MaxPooling2D(2)  # 128x128
        self.downsample2 = layers.MaxPooling2D(2)  # 64x64
        
        # ROI Layer
        self.roi_layer = ROILayer(roi_size=28, num_rois=num_rois)
        
        # Classifier head
        self.classifier_dense1 = layers.Dense(256, activation='relu')
        self.classifier_dropout1 = layers.Dropout(0.4)
        self.classifier_dense2 = layers.Dense(128, activation='relu')
        self.classifier_dropout2 = layers.Dropout(0.3)
        
        # Output heads
        self.ma_probability = layers.Dense(1, activation='sigmoid', name='ma_probability')
        self.bbox_regression = layers.Dense(4, activation=None, name='bbox')  # [x, y, w, h]
        self.confidence = layers.Dense(1, activation='sigmoid', name='confidence')
    
    def call(self, x, training=False):
        """Forward pass through DRN with ROI processing."""
        
        # Normalization
        x = self.normalize(x)
        
        # Initial conv block
        x = self.init_conv(x)
        x = self.init_bn(x)
        x = self.init_pool(x)  # 256x256
        
        # DRN blocks
        x = self.drn_block1(x)
        x = self.downsample1(x)  # 128x128
        
        x = self.drn_block2(x)
        x = self.downsample2(x)  # 64x64
        
        x = self.drn_block3(x)  # 64x64
        
        # ROI Layer processes 28x28 patches
        x = self.roi_layer(x)
        
        # Classifier
        x = self.classifier_dense1(x)
        x = self.classifier_dropout1(x, training=training)
        x = self.classifier_dense2(x)
        x = self.classifier_dropout2(x, training=training)
        
        # Outputs
        ma_prob = self.ma_probability(x)
        bbox = self.bbox_regression(x)
        conf = self.confidence(x)
        
        return {
            'ma_probability': ma_prob,
            'bbox': bbox,
            'confidence': conf
        }


def create_drn_model(num_rois=8, learning_rate=1e-4):
    """
    Create and compile a DRN model for microaneurysm detection.
    
    Args:
        num_rois: Number of ROI patches to process
        learning_rate: Adam optimizer learning rate
        
    Returns:
        Compiled Keras model
    """
    model = DRNMicroaneurysmDetector(num_rois=num_rois)
    
    # Build model
    model.build(input_shape=(None, 512, 512, 3))
    
    # Compile
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    
    model.compile(
        optimizer=optimizer,
        loss={
            'ma_probability': keras.losses.BinaryCrossentropy(),
            'bbox': keras.losses.MeanSquaredError(),
            'confidence': keras.losses.BinaryCrossentropy()
        },
        loss_weights={
            'ma_probability': 1.0,
            'bbox': 0.5,
            'confidence': 0.5
        },
        metrics={
            'ma_probability': ['accuracy', keras.metrics.AUC()],
            'confidence': ['accuracy']
        }
    )
    
    return model


def load_drn_model(model_path):
    """Load a pre-trained DRN model."""
    return keras.models.load_model(
        model_path,
        custom_objects={
            'DilatedResidualBlock': DilatedResidualBlock,
            'ROILayer': ROILayer,
            'DRNMicroaneurysmDetector': DRNMicroaneurysmDetector
        }
    )


if __name__ == '__main__':
    # Test model creation
    print("Creating DRN Model...")
    model = create_drn_model(num_rois=8)
    model.summary()
    
    print("\nModel created successfully!")
    print("Input shape: (None, 512, 512, 3)")
    print("Output: {ma_probability, bbox, confidence}")
