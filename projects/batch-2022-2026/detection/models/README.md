# Trained DRN Models Storage

This directory stores trained Dilated Residual Network (DRN) models for microaneurysm detection.

## Contents

After training, the following files will be created here:

- `drn_microaneurysm_detector.h5` - Trained DRN model (TensorFlow/Keras format)
- `drn_training_metadata.json` - Training parameters and statistics
- `drn_microaneurysm_detector.tflite` - (Optional) Mobile-optimized TFLite format

## Training

To train a new model:

```bash
python manage.py train_drn train \
    --dataset eophtha \
    --path /path/to/eophtha-ma/dataset \
    --epochs 50
```

Model will be automatically saved to `drn_microaneurysm_detector.h5` in this directory.

## Usage

The prediction module automatically loads the model from here:

```python
from detection.predict_drn import predict_with_drn_fallback

result = predict_with_drn_fallback('/path/to/image.jpg')
```

## Model Format

- **Size**: ~15-20MB (TensorFlow format)
- **Framework**: TensorFlow 2.10+
- **Input**: 512x512 RGB fundus images
- **Outputs**: 3 heads (classification, bbox, confidence)

## Backup

Keep backup copies of successful models:

```bash
cp drn_microaneurysm_detector.h5 drn_microaneurysm_detector_backup.h5
cp drn_training_metadata.json drn_training_metadata_backup.json
```

---

**For training details**, see `../DRN_TRAINING_GUIDE.md`
**For integration details**, see `../DRN_INTEGRATION_GUIDE.md`
