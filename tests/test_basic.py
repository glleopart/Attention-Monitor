"""
Basic tests to verify system functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.face_detector import FaceDetector
from src.attention_tracker import AttentionTracker
from src.ui_overlay import UIOverlay
import numpy as np


def test_face_detector():
    """Test FaceDetector initialization."""
    print("Test 1: FaceDetector initialization...", end=" ")
    detector = FaceDetector()
    assert detector is not None
    print("✓")


def test_attention_tracker():
    """Test AttentionTracker initialization."""
    print("Test 2: AttentionTracker initialization...", end=" ")
    tracker = AttentionTracker()
    assert tracker.current_state == "looking"
    assert tracker.alert_active == False
    print("✓")


def test_classification():
    """Test classification logic."""
    print("Test 3: Classification logic...", end=" ")
    tracker = AttentionTracker(yaw_threshold=25.0, pitch_threshold=20.0)
    
    # Looking straight
    state = tracker.classify_attention(0.0, 0.0)
    assert state == "looking"
    
    # Looking away
    state = tracker.classify_attention(30.0, 0.0)
    assert state == "not_looking"
    
    print("✓")


def test_state_transitions():
    """Test state transitions."""
    print("Test 4: State transitions...", end=" ")
    tracker = AttentionTracker(smoothing_window=3)
    
    # Look away
    for _ in range(5):
        tracker.update(30.0, 0.0)
    
    assert tracker.current_state == "not_looking"
    
    # Reset
    tracker.reset()
    assert tracker.time_not_looking == 0.0
    print("✓")


def test_ui_overlay():
    """Test UIOverlay."""
    print("Test 5: UIOverlay...", end=" ")
    ui = UIOverlay()
    assert ui is not None
    
    # Test drawing
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame = ui.draw_alert(frame, True, 3.5)
    assert frame is not None
    print("✓")


def test_smoothing():
    """Test temporal smoothing."""
    print("Test 6: Temporal smoothing...", end=" ")
    tracker = AttentionTracker(smoothing_window=5)
    
    states = []
    for i in range(10):
        yaw = 30.0 if i % 2 == 0 else 0.0
        result = tracker.update(yaw, 0.0)
        states.append(result['state'])
    
    # Should stabilize, not flicker
    changes = sum(1 for i in range(1, len(states)) if states[i] != states[i-1])
    assert changes < 5
    print("✓")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*50)
    print("EJECUTANDO TESTS")
    print("="*50 + "\n")
    
    try:
        test_face_detector()
        test_attention_tracker()
        test_classification()
        test_state_transitions()
        test_ui_overlay()
        test_smoothing()
        
        print("\n" + "="*50)
        print("✓ TODOS LOS TESTS PASARON")
        print("="*50 + "\n")
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
