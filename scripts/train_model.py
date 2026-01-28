"""
Optional ML training script for supervised attention classification.

This script trains a Random Forest classifier on labeled data.

Usage:
    1. Collect data: python src/main.py --collect-data --output data/training
    2. Train model: python scripts/train_model.py --data data/training --output models/attention_clf.pkl
    3. Use model: python src/main.py --use-model models/attention_clf.pkl

Features used:
- Head pose (yaw, pitch, roll)
- Eye aspect ratio (both eyes)
- Temporal derivatives (velocities)
"""

import os
import sys
import argparse
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_data(data_dir):
    """
    Load training data from directory.
    
    Expected format:
        data/training/
            features.npy  - Feature vectors (N x F)
            labels.npy    - Binary labels (N,) - 1=looking, 0=not_looking
    
    Args:
        data_dir: Path to data directory
        
    Returns:
        tuple: (X, y) feature matrix and labels
    """
    features_path = os.path.join(data_dir, 'features.npy')
    labels_path = os.path.join(data_dir, 'labels.npy')
    
    if not os.path.exists(features_path) or not os.path.exists(labels_path):
        raise FileNotFoundError(f"Data files not found in {data_dir}")
    
    X = np.load(features_path)
    y = np.load(labels_path)
    
    print(f"Loaded {len(X)} samples with {X.shape[1]} features")
    print(f"Class distribution: {np.bincount(y)}")
    
    return X, y


def train_model(X, y, n_estimators=100, max_depth=10):
    """
    Train Random Forest classifier.
    
    Args:
        X: Feature matrix (N x F)
        y: Labels (N,)
        n_estimators: Number of trees
        max_depth: Maximum tree depth
        
    Returns:
        tuple: (model, X_train, X_test, y_train, y_test)
    """
    print("\nDividiendo datos en train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Train: {len(X_train)} samples")
    print(f"Test: {len(X_test)} samples")
    
    print(f"\nEntrenando Random Forest ({n_estimators} árboles)...")
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Cross-validation
    print("\nValidación cruzada (5-fold)...")
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, n_jobs=-1)
    print(f"CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    return model, X_train, X_test, y_train, y_test


def evaluate_model(model, X_test, y_test):
    """
    Evaluate model on test set.
    
    Args:
        model: Trained classifier
        X_test: Test features
        y_test: Test labels
    """
    print("\n" + "="*50)
    print("EVALUACIÓN EN TEST SET")
    print("="*50)
    
    y_pred = model.predict(X_test)
    
    print("\nClassification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=['Not Looking', 'Looking']
    ))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print("              Predicted")
    print("              Not Looking  Looking")
    print(f"Actual Not    {cm[0,0]:6d}       {cm[0,1]:6d}")
    print(f"       Look   {cm[1,0]:6d}       {cm[1,1]:6d}")
    
    # Feature importance
    if hasattr(model, 'feature_importances_'):
        print("\nFeature Importances:")
        feature_names = ['yaw', 'pitch', 'roll', 'ear_left', 'ear_right',
                        'd_yaw', 'd_pitch', 'd_roll', 'd_ear_left', 'd_ear_right']
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        for i in range(min(10, len(feature_names))):
            idx = indices[i]
            if idx < len(feature_names):
                print(f"  {feature_names[idx]:15s}: {importances[idx]:.4f}")


def save_model(model, output_path):
    """
    Save trained model to disk.
    
    Args:
        model: Trained classifier
        output_path: Path to save model (.pkl)
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\n✓ Modelo guardado en: {output_path}")
    print(f"  Tamaño: {os.path.getsize(output_path) / 1024:.1f} KB")


def main():
    """Main training pipeline."""
    parser = argparse.ArgumentParser(
        description='Entrenar modelo ML para clasificación de atención'
    )
    
    parser.add_argument(
        '--data',
        type=str,
        default='data/training',
        help='Directorio con datos de entrenamiento'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='models/attention_clf.pkl',
        help='Ruta donde guardar modelo entrenado'
    )
    
    parser.add_argument(
        '--n-estimators',
        type=int,
        default=100,
        help='Número de árboles en Random Forest'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=10,
        help='Profundidad máxima de árboles'
    )
    
    args = parser.parse_args()
    
    try:
        # Load data
        print("Cargando datos...")
        X, y = load_data(args.data)
        
        # Train model
        model, X_train, X_test, y_train, y_test = train_model(
            X, y,
            n_estimators=args.n_estimators,
            max_depth=args.max_depth
        )
        
        # Evaluate
        evaluate_model(model, X_test, y_test)
        
        # Save
        save_model(model, args.output)
        
        print("\n✓ Entrenamiento completado exitosamente")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
