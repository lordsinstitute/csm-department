"""
Django Management Command for DRN Model Training

Usage:
    python manage.py train_drn --dataset eophtha --path /data/eophtha-ma --epochs 50
    python manage.py train_drn --dataset diaretdb1 --path /data/diaretdb1-ma
    python manage.py train_drn --dataset roc --path /data/roc-ma
    python manage.py evaluate_drn --model-path detection/models/drn_microaneurysm_detector.h5 --dataset eophtha --path /data/eophtha-ma
"""

from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Train and evaluate DRN microaneurysm detection models'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Action to perform')

        # Training subcommand
        train_parser = subparsers.add_parser('train', help='Train DRN model')
        train_parser.add_argument('--dataset', type=str, required=True,
                                choices=['eophtha', 'diaretdb1', 'roc'],
                                help='Dataset to train on')
        train_parser.add_argument('--path', type=str, required=True,
                                help='Path to dataset directory')
        train_parser.add_argument('--epochs', type=int, default=50,
                                help='Number of training epochs (default: 50)')
        train_parser.add_argument('--batch-size', type=int, default=16,
                                help='Batch size (default: 16)')
        train_parser.add_argument('--validation-split', type=float, default=0.2,
                                help='Validation split ratio (default: 0.2)')
        train_parser.add_argument('--learning-rate', type=float, default=1e-4,
                                help='Initial learning rate (default: 1e-4)')
        train_parser.add_argument('--early-stopping-patience', type=int, default=10,
                                help='Early stopping patience (default: 10)')
        train_parser.add_argument('--output-model', type=str, default=None,
                                help='Output model path (default: detection/models/drn_microaneurysm_detector.h5)')
        train_parser.add_argument('--save-metadata', action='store_true', default=True,
                                help='Save training metadata')

        # Evaluation subcommand
        eval_parser = subparsers.add_parser('evaluate', help='Evaluate DRN model')
        eval_parser.add_argument('--model-path', type=str, required=True,
                                help='Path to trained model')
        eval_parser.add_argument('--dataset', type=str, required=True,
                                choices=['eophtha', 'diaretdb1', 'roc'],
                                help='Dataset to evaluate on')
        eval_parser.add_argument('--path', type=str, required=True,
                                help='Path to dataset directory')
        eval_parser.add_argument('--batch-size', type=int, default=16,
                                help='Batch size (default: 16)')

        # Predict subcommand
        predict_parser = subparsers.add_parser('predict', help='Predict on single image')
        predict_parser.add_argument('--image', type=str, required=True,
                                   help='Path to image file')
        predict_parser.add_argument('--use-opencv', action='store_true',
                                   help='Force OpenCV detector (no DRN)')
        predict_parser.add_argument('--confidence-threshold', type=float, default=0.5,
                                   help='Confidence threshold (default: 0.5)')

        # Model info subcommand
        info_parser = subparsers.add_parser('info', help='Show model information')

    def handle(self, *args, **options):
        action = options.get('action')

        if not action:
            self.print_help('manage.py', 'train_drn')
            return

        try:
            if action == 'train':
                self.handle_train(**options)
            elif action == 'evaluate':
                self.handle_evaluate(**options)
            elif action == 'predict':
                self.handle_predict(**options)
            elif action == 'info':
                self.handle_info()
        except Exception as e:
            raise CommandError(f'Error: {str(e)}')

    def handle_train(self, **options):
        """Train DRN model"""
        from detection.train_drn import train_drn_model

        self.stdout.write(self.style.SUCCESS('🚀 Starting DRN Model Training'))
        self.stdout.write('-' * 60)

        dataset_type = options['dataset']
        dataset_path = options['path']
        epochs = options['epochs']
        batch_size = options['batch_size']
        validation_split = options['validation_split']
        learning_rate = options.get('learning_rate', 1e-4)
        early_stopping_patience = options.get('early_stopping_patience', 10)
        output_model = options.get('output_model')

        self.stdout.write(f"📊 Dataset: {dataset_type}")
        self.stdout.write(f"📁 Path: {dataset_path}")
        self.stdout.write(f"🔄 Epochs: {epochs}")
        self.stdout.write(f"📦 Batch Size: {batch_size}")
        self.stdout.write(f"✂️  Validation Split: {validation_split}")
        self.stdout.write(f"🎓 Learning Rate: {learning_rate}")
        self.stdout.write(f"⏹️  Early Stopping Patience: {early_stopping_patience}")
        self.stdout.write('-' * 60)

        start_time = datetime.now()

        try:
            model_path = train_drn_model(
                dataset_type=dataset_type,
                dataset_path=dataset_path,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                early_stopping_patience=early_stopping_patience,
                output_model=output_model
            )

            elapsed = (datetime.now() - start_time).total_seconds()

            self.stdout.write(self.style.SUCCESS(f'\n✅ Training Completed!'))
            self.stdout.write(f"⏱️  Time Elapsed: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
            self.stdout.write(f"💾 Model Saved: {model_path}")

            # Save training metadata
            if options.get('save_metadata'):
                metadata = {
                    'dataset': dataset_type,
                    'dataset_path': dataset_path,
                    'epochs': epochs,
                    'batch_size': batch_size,
                    'validation_split': validation_split,
                    'learning_rate': learning_rate,
                    'early_stopping_patience': early_stopping_patience,
                    'training_time_seconds': elapsed,
                    'timestamp': datetime.now().isoformat(),
                    'model_path': model_path
                }

                metadata_path = Path(model_path).parent / 'drn_training_metadata.json'
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)

                self.stdout.write(f"📝 Metadata: {metadata_path}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Training Failed: {str(e)}'))
            raise CommandError(str(e))

    def handle_evaluate(self, **options):
        """Evaluate trained model"""
        from detection.train_drn import evaluate_drn_model

        self.stdout.write(self.style.SUCCESS('📈 Evaluating DRN Model'))
        self.stdout.write('-' * 60)

        model_path = options['model_path']
        dataset_type = options['dataset']
        dataset_path = options['path']
        batch_size = options['batch_size']

        self.stdout.write(f"🧠 Model: {model_path}")
        self.stdout.write(f"📊 Dataset: {dataset_type}")
        self.stdout.write(f"📁 Path: {dataset_path}")
        self.stdout.write(f"📦 Batch Size: {batch_size}")
        self.stdout.write('-' * 60)

        try:
            metrics = evaluate_drn_model(
                model_path=model_path,
                dataset_type=dataset_type,
                dataset_path=dataset_path,
                batch_size=batch_size
            )

            self.stdout.write(self.style.SUCCESS('\n✅ Evaluation Complete!'))
            self.stdout.write('\n📊 Results:')

            if isinstance(metrics, dict):
                for key, value in metrics.items():
                    if isinstance(value, float):
                        self.stdout.write(f"   {key}: {value:.4f}")
                    else:
                        self.stdout.write(f"   {key}: {value}")
            else:
                self.stdout.write(f"   {metrics}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Evaluation Failed: {str(e)}'))
            raise CommandError(str(e))

    def handle_predict(self, **options):
        """Run prediction on single image"""
        from detection.predict_drn import predict_with_drn_fallback, get_model_info

        image_path = options['image']
        use_opencv = options['use_opencv']
        confidence_threshold = options.get('confidence_threshold', 0.5)

        self.stdout.write(self.style.SUCCESS('🔍 Microaneurysm Detection'))
        self.stdout.write('-' * 60)

        # Check model availability
        model_info = get_model_info()
        self.stdout.write(f"🧠 DRN Model Available: {model_info['drn_available']}")
        self.stdout.write(f"🖥️  OpenCV Available: {model_info['opencv_available']}")
        self.stdout.write('-' * 60)

        try:
            result = predict_with_drn_fallback(
                image_path,
                use_drn=not use_opencv
            )

            self.stdout.write(self.style.SUCCESS('\n✅ Detection Complete!'))
            self.stdout.write('\n📊 Results:')
            self.stdout.write(f"   Microaneurysms: {result['ma_count']}")
            self.stdout.write(f"   Lesion Area: {result['lesion_area']} px²")
            self.stdout.write(f"   Confidence: {result['confidence']:.3f}")
            self.stdout.write(f"   Model: {result.get('model_type', 'Unknown')}")
            self.stdout.write(f"   Processing Time: {result['processing_time']:.3f}s")

            self.stdout.write(f"\n💾 Processed Image: {result['processed_image_path']}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Prediction Failed: {str(e)}'))
            raise CommandError(str(e))

    def handle_info(self):
        """Display model information"""
        from detection.predict_drn import get_model_info, DRN_MODEL_PATH

        self.stdout.write(self.style.SUCCESS('ℹ️  DRN Model Information'))
        self.stdout.write('-' * 60)

        info = get_model_info()

        self.stdout.write(f"🧠 DRN Model Available: {info['drn_available']}")
        self.stdout.write(f"📁 DRN Path: {info['drn_path'] or 'Not found'}")
        self.stdout.write(f"🖥️  OpenCV Available: {info['opencv_available']}")

        if info['drn_available']:
            self.stdout.write(self.style.SUCCESS('\n✅ DRN model is ready for inference!'))
            self.stdout.write("   Use: python manage.py train_drn predict --image /path/to/image.jpg")
        else:
            self.stdout.write(self.style.WARNING('\n⚠️  DRN model not found'))
            self.stdout.write(f"   Path: {DRN_MODEL_PATH}")
            self.stdout.write("   Train with: python manage.py train_drn train --dataset eophtha --path /data/eophtha-ma")

        self.stdout.write('-' * 60)
        self.stdout.write('\n📚 Quick Start:')
        self.stdout.write('   1. Train: python manage.py train_drn train --dataset eophtha --path /data/eophtha-ma')
        self.stdout.write('   2. Evaluate: python manage.py train_drn evaluate --model-path detection/models/drn_microaneurysm_detector.h5 --dataset eophtha --path /data/eophtha-ma')
        self.stdout.write('   3. Predict: python manage.py train_drn predict --image /path/to/image.jpg')
