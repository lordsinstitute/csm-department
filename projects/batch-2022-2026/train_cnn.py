"""
CNN Smoke/Fire Detection Training Script
Uses MobileNetV2 Transfer Learning
Run once: python train_cnn.py
Saves model to: media/cnn_model.h5
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Config ──────────────────────────────────────────────
IMG_SIZE    = (224, 224)
BATCH_SIZE  = 32
EPOCHS      = 15
DATASET_DIR = os.path.join('media', 'cnn_dataset')   # fire/ and no_fire/ inside
MODEL_OUT   = os.path.join('media', 'cnn_model.h5')

# ── Check dataset exists ─────────────────────────────────
fire_dir    = os.path.join(DATASET_DIR, 'fire')
no_fire_dir = os.path.join(DATASET_DIR, 'no_fire')

if not os.path.exists(fire_dir) or not os.path.exists(no_fire_dir):
    print("ERROR: Dataset folders not found!")
    print(f"  Expected: {fire_dir}")
    print(f"  Expected: {no_fire_dir}")
    print("\nPlease create the folder structure:")
    print("  media/cnn_dataset/fire/       <-- fire/smoke images here")
    print("  media/cnn_dataset/no_fire/    <-- normal images here")
    exit(1)

fire_count    = len(os.listdir(fire_dir))
no_fire_count = len(os.listdir(no_fire_dir))
print(f"✅ Dataset found: {fire_count} fire images, {no_fire_count} no-fire images")

# ── Data Augmentation ────────────────────────────────────
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
    zoom_range=0.1
)

val_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='binary',
    subset='training',
    shuffle=True
)

val_generator = val_datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='binary',
    subset='validation',
    shuffle=False
)

print(f"\n📊 Class indices: {train_generator.class_indices}")
print(f"   Training samples  : {train_generator.samples}")
print(f"   Validation samples: {val_generator.samples}")

# ── Build Model (MobileNetV2 Transfer Learning) ──────────
print("\n🔧 Building MobileNetV2 model...")
base_model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)

# Freeze base layers
base_model.trainable = False

# Add custom classification head
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.3)(x)
output = Dense(1, activation='sigmoid')(x)

model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print(f"✅ Model built. Total params: {model.count_params():,}")

# ── Callbacks ────────────────────────────────────────────
callbacks = [
    ModelCheckpoint(
        MODEL_OUT,
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    EarlyStopping(
        monitor='val_accuracy',
        patience=4,
        restore_best_weights=True,
        verbose=1
    )
]

# ── Train ────────────────────────────────────────────────
print(f"\n🚀 Starting training for up to {EPOCHS} epochs...")
print(f"   Using GPU: {len(tf.config.list_physical_devices('GPU')) > 0}")
print("-" * 50)

history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=val_generator,
    callbacks=callbacks,
    verbose=1
)

# ── Fine-tune top layers ─────────────────────────────────
print("\n🔧 Fine-tuning top 30 layers...")
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.00001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

history_fine = model.fit(
    train_generator,
    epochs=5,
    validation_data=val_generator,
    callbacks=callbacks,
    verbose=1
)

# ── Results ──────────────────────────────────────────────
val_loss, val_acc = model.evaluate(val_generator, verbose=0)
print("\n" + "="*50)
print(f"✅ TRAINING COMPLETE!")
print(f"   Final Validation Accuracy : {val_acc*100:.2f}%")
print(f"   Final Validation Loss     : {val_loss:.4f}")
print(f"   Model saved to            : {MODEL_OUT}")
print("="*50)

# Save class mapping
import json
class_indices = train_generator.class_indices
# class_indices is like {'fire': 0, 'no_fire': 1} or reversed
# We save it so Django knows which index = fire
with open(os.path.join('media', 'cnn_classes.json'), 'w') as f:
    json.dump(class_indices, f)
print(f"   Class mapping saved to    : media/cnn_classes.json")
print(f"   Class mapping             : {class_indices}")
print("\n✅ You can now run: python manage.py runserver")
