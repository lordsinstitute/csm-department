# users/predict.py
# This file is kept for compatibility.
# All prediction logic has been moved to ml_models.py

from .ml_models import predict_single_transaction, train_all_models

__all__ = ['predict_single_transaction', 'train_all_models']