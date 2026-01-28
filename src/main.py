"""
Main application for attention monitoring.
"""

import cv2
import time
import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.face_detector import FaceDetector
from src.attention_tracker import AttentionTracker
from src.ui_overlay import UIOverlay
from config import settings


class AttentionMonitor:
    """Main application class."""
    
    def __init__(self, camera_index=0, show_debug=True, show_stats=True):
        """Initialize system."""
        print("Inicializando sistema...")
        
        # Initialize camera
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"No se puede acceder a la cámara {camera_index}")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, settings.TARGET_FPS)
        
        # Initialize modules
        self.face_detector = FaceDetector(settings.MIN_DETECTION_CONFIDENCE)
        self.attention_tracker = AttentionTracker(
            alert_threshold=settings.ALERT_THRESHOLD,
            yaw_threshold=settings.YAW_THRESHOLD,
            pitch_threshold=settings.PITCH_THRESHOLD,
            smoothing_window=settings.SMOOTHING_WINDOW,
            min_consecutive_frames=settings.MIN_CONSECUTIVE_FRAMES
        )
        self.ui_overlay = UIOverlay(
            alert_message=settings.ALERT_MESSAGE,
            alert_color=settings.ALERT_COLOR,
            alert_font_scale=settings.ALERT_FONT_SCALE,
            alert_thickness=settings.ALERT_THICKNESS
        )
        
        # State
        self.show_debug = show_debug
        self.show_stats = show_stats
        self.running = True
        
        # FPS
        self.fps = 0.0
        self.frame_count = 0
        self.fps_start_time = time.time()
        
        print("✓ Sistema inicializado")
        print(f"✓ Cámara: {settings.CAMERA_WIDTH}x{settings.CAMERA_HEIGHT}")
        print(f"✓ Umbral: {settings.ALERT_THRESHOLD}s")
        print("\nPresiona Q o ESC para salir")
    
    def calculate_fps(self):
        """Calculate FPS."""
        self.frame_count += 1
        if self.frame_count >= 30:
            end_time = time.time()
            self.fps = self.frame_count / (end_time - self.fps_start_time)
            self.fps_start_time = end_time
            self.frame_count = 0
    
    def process_frame(self, frame):
        """Process single frame."""
        # Detect face
        face_detected, landmarks, rgb_frame = self.face_detector.detect_face(frame)
        
        if not face_detected:
            state_info = self.attention_tracker.update(None, None)
        else:
            # Estimate pose
            yaw, pitch, roll = self.face_detector.estimate_head_pose(
                landmarks, frame.shape
            )
            
            # Update tracker
            state_info = self.attention_tracker.update(yaw, pitch)
            
            # Draw debug
            if self.show_debug and settings.SHOW_DEBUG_INFO:
                frame = self.face_detector.draw_debug_info(
                    frame, landmarks, yaw, pitch, roll
                )
        
        return frame, state_info
    
    def run(self):
        """Main loop."""
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: no se puede leer frame")
                    break
                
                # Mirror frame
                frame = cv2.flip(frame, 1)
                
                # Process
                frame, state_info = self.process_frame(frame)
                
                # Draw UI
                frame = self.ui_overlay.draw_status_bar(
                    frame,
                    state_info['state'],
                    state_info['time_not_looking'],
                    state_info['confidence']
                )
                
                # Progress bar
                if state_info['state'] == 'not_looking':
                    frame = self.ui_overlay.draw_progress_bar(
                        frame,
                        state_info['time_not_looking'],
                        settings.ALERT_THRESHOLD
                    )
                
                # Alert
                if state_info['alert_active']:
                    frame = self.ui_overlay.draw_alert(
                        frame,
                        state_info['alert_active'],
                        state_info['time_not_looking']
                    )
                
                # Statistics
                if self.show_stats:
                    stats = self.attention_tracker.get_statistics()
                    frame = self.ui_overlay.draw_statistics(frame, stats, self.fps)
                
                # Instructions
                frame = self.ui_overlay.draw_instructions(frame)
                
                # FPS
                self.calculate_fps()
                
                # Display
                cv2.imshow('Attention Monitor', frame)
                
                # Keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    print("\nSaliendo...")
                    self.running = False
                elif key == ord('r'):
                    print("\nReseteando...")
                    self.attention_tracker.reset()
                elif key == ord('s'):
                    self.show_stats = not self.show_stats
                    print(f"\nEstadísticas: {'ON' if self.show_stats else 'OFF'}")
                
        except KeyboardInterrupt:
            print("\n\nInterrumpido")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up."""
        print("\nLiberando recursos...")
        stats = self.attention_tracker.get_statistics()
        print(f"\nTotal frames: {stats['total_frames']}")
        print(f"Atención: {stats['attention_ratio']:.1%}")
        print(f"FPS promedio: {self.fps:.1f}")
        self.cap.release()
        cv2.destroyAllWindows()
        print("✓ Terminado")


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(description='Monitoreo de atención en tiempo real')
    parser.add_argument('--camera', type=int, default=0, help='Índice de cámara')
    parser.add_argument('--no-debug', action='store_true', help='Sin debug')
    parser.add_argument('--no-stats', action='store_true', help='Sin stats')
    parser.add_argument('--alert-threshold', type=float, help='Umbral de alerta (segundos)')
    
    args = parser.parse_args()
    
    if args.alert_threshold:
        settings.ALERT_THRESHOLD = args.alert_threshold
    
    try:
        monitor = AttentionMonitor(
            camera_index=args.camera,
            show_debug=not args.no_debug,
            show_stats=not args.no_stats
        )
        monitor.run()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
