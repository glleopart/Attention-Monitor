"""
Examples of using attention-monitor as a library.

This script shows how to integrate the attention monitoring system
into your own applications.
"""

import cv2
import time
from src.face_detector import FaceDetector
from src.attention_tracker import AttentionTracker
from src.ui_overlay import UIOverlay


def example_1_basic_detection():
    """
    Example 1: Basic detection without UI.
    
    Use case: Log attention data without showing anything to user.
    """
    print("\n=== Example 1: Basic Detection ===\n")
    
    # Initialize components
    detector = FaceDetector()
    tracker = AttentionTracker(alert_threshold=5.0)
    cap = cv2.VideoCapture(0)
    
    start_time = time.time()
    frame_count = 0
    
    try:
        while time.time() - start_time < 10:  # Run for 10 seconds
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect and estimate pose
            detected, landmarks, _ = detector.detect_face(frame)
            
            if detected:
                yaw, pitch, roll = detector.estimate_head_pose(landmarks, frame.shape)
                state_info = tracker.update(yaw, pitch, roll)
            else:
                state_info = tracker.update(None, None)
            
            # Log state changes
            if frame_count % 30 == 0:  # Log every second
                print(f"State: {state_info['state']:12s} | "
                      f"Time not looking: {state_info['time_not_looking']:.2f}s | "
                      f"Alert: {state_info['alert_active']}")
            
            frame_count += 1
        
        # Print statistics
        stats = tracker.get_statistics()
        print(f"\nFinal attention ratio: {stats['attention_ratio']:.2%}")
        
    finally:
        cap.release()


def example_2_custom_callback():
    """
    Example 2: Trigger custom actions on state changes.
    
    Use case: Pause music/video when user looks away.
    """
    print("\n=== Example 2: Custom Callbacks ===\n")
    
    def on_attention_lost():
        """Called when user stops looking."""
        print("⚠️  ATTENTION LOST - Pausing media...")
        # Add your code here: pause_music(), pause_video(), etc.
    
    def on_attention_gained():
        """Called when user starts looking again."""
        print("✓ ATTENTION REGAINED - Resuming media...")
        # Add your code here: resume_music(), resume_video(), etc.
    
    detector = FaceDetector()
    tracker = AttentionTracker(alert_threshold=3.0)
    cap = cv2.VideoCapture(0)
    
    previous_state = "looking"
    
    try:
        for _ in range(300):  # ~10 seconds at 30 FPS
            ret, frame = cap.read()
            if not ret:
                break
            
            detected, landmarks, _ = detector.detect_face(frame)
            
            if detected:
                yaw, pitch, roll = detector.estimate_head_pose(landmarks, frame.shape)
                state_info = tracker.update(yaw, pitch, roll)
            else:
                state_info = tracker.update(None, None)
            
            current_state = state_info['state']
            
            # Detect state transitions
            if current_state != previous_state:
                if current_state == "not_looking":
                    on_attention_lost()
                else:
                    on_attention_gained()
                
                previous_state = current_state
            
            time.sleep(0.033)  # ~30 FPS
    
    finally:
        cap.release()


def example_3_data_collection():
    """
    Example 3: Collect labeled data for ML training.
    
    Use case: Build custom dataset for your specific use case.
    """
    print("\n=== Example 3: Data Collection ===\n")
    print("Press '1' when looking at screen")
    print("Press '0' when looking away")
    print("Press 'q' to quit")
    
    detector = FaceDetector()
    cap = cv2.VideoCapture(0)
    
    features = []
    labels = []
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            detected, landmarks, _ = detector.detect_face(frame)
            
            if detected:
                yaw, pitch, roll = detector.estimate_head_pose(landmarks, frame.shape)
                ear_left = detector.calculate_ear(landmarks, frame.shape, 'left')
                ear_right = detector.calculate_ear(landmarks, frame.shape, 'right')
                
                # Show current pose
                cv2.putText(frame, f"Yaw: {yaw:.1f}  Pitch: {pitch:.1f}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Samples collected: {len(features)}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Data Collection', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('1') and detected:
                # Label as "looking"
                features.append([yaw, pitch, roll, ear_left, ear_right])
                labels.append(1)
                print(f"✓ Labeled as LOOKING (total: {len(features)})")
                
            elif key == ord('0') and detected:
                # Label as "not looking"
                features.append([yaw, pitch, roll, ear_left, ear_right])
                labels.append(0)
                print(f"✗ Labeled as NOT LOOKING (total: {len(features)})")
                
            elif key == ord('q'):
                break
        
        # Save collected data
        if features:
            import numpy as np
            np.save('data/features.npy', np.array(features))
            np.save('data/labels.npy', np.array(labels))
            print(f"\n✓ Saved {len(features)} labeled samples")
            print(f"  Looking: {sum(labels)}")
            print(f"  Not looking: {len(labels) - sum(labels)}")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()


def example_4_custom_ui():
    """
    Example 4: Build custom UI overlay.
    
    Use case: Integrate into existing application with custom styling.
    """
    print("\n=== Example 4: Custom UI ===\n")
    
    detector = FaceDetector()
    tracker = AttentionTracker(alert_threshold=5.0)
    ui = UIOverlay(
        alert_message="⚠️ Please focus!",
        alert_color=(0, 100, 255),  # Orange
        alert_font_scale=2.0
    )
    cap = cv2.VideoCapture(0)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            detected, landmarks, _ = detector.detect_face(frame)
            
            if detected:
                yaw, pitch, roll = detector.estimate_head_pose(landmarks, frame.shape)
                state_info = tracker.update(yaw, pitch, roll)
            else:
                state_info = tracker.update(None, None)
            
            # Custom minimal UI
            h, w = frame.shape[:2]
            
            # Simple indicator circle
            color = (0, 255, 0) if state_info['state'] == 'looking' else (0, 0, 255)
            cv2.circle(frame, (w - 30, 30), 15, color, -1)
            
            # Only show alert if threshold exceeded
            if state_info['alert_active']:
                frame = ui.draw_alert(frame, True, state_info['time_not_looking'])
            
            cv2.imshow('Custom UI', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()


def example_5_batch_processing():
    """
    Example 5: Process pre-recorded video file.
    
    Use case: Analyze attention in recorded sessions.
    """
    print("\n=== Example 5: Batch Processing ===\n")
    
    video_path = "path/to/your/video.mp4"  # Change this
    
    detector = FaceDetector()
    tracker = AttentionTracker(alert_threshold=5.0)
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Processing video: {video_path}")
    print(f"FPS: {fps}, Total frames: {total_frames}")
    
    frame_count = 0
    attention_per_second = []
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            detected, landmarks, _ = detector.detect_face(frame)
            
            if detected:
                yaw, pitch, roll = detector.estimate_head_pose(landmarks, frame.shape)
                state_info = tracker.update(yaw, pitch, roll)
            else:
                state_info = tracker.update(None, None)
            
            # Record attention per second
            if frame_count % int(fps) == 0:
                attention_per_second.append(1 if state_info['state'] == 'looking' else 0)
            
            frame_count += 1
            
            if frame_count % 100 == 0:
                print(f"Progress: {frame_count}/{total_frames} frames")
        
        # Final report
        stats = tracker.get_statistics()
        print("\n" + "="*50)
        print("BATCH PROCESSING RESULTS")
        print("="*50)
        print(f"Total frames: {stats['total_frames']}")
        print(f"Attention ratio: {stats['attention_ratio']:.2%}")
        print(f"Time looking: {stats['frames_looking'] / fps:.1f}s")
        print(f"Time not looking: {stats['frames_not_looking'] / fps:.1f}s")
        print("="*50)
        
    finally:
        cap.release()


if __name__ == "__main__":
    print("Attention Monitor - Usage Examples")
    print("="*50)
    
    examples = {
        '1': ('Basic Detection (logging only)', example_1_basic_detection),
        '2': ('Custom Callbacks', example_2_custom_callback),
        '3': ('Data Collection for ML', example_3_data_collection),
        '4': ('Custom UI Overlay', example_4_custom_ui),
        '5': ('Batch Video Processing', example_5_batch_processing),
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelect example (1-5) or 'q' to quit: ").strip()
    
    if choice in examples:
        _, example_func = examples[choice]
        example_func()
    elif choice.lower() == 'q':
        print("Goodbye!")
    else:
        print("Invalid choice")
