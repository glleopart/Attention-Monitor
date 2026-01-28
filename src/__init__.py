"""
Attention monitoring system package.

Main modules:
- face_detector: Face detection and head pose estimation
- attention_tracker: Attention state tracking and temporal logic
- ui_overlay: Visual overlays and alerts
"""

__version__ = "1.0.0"
__author__ = "Attention Monitor Project"

from .face_detector import FaceDetector
from .attention_tracker import AttentionTracker
from .ui_overlay import UIOverlay

__all__ = ['FaceDetector', 'AttentionTracker', 'UIOverlay']
