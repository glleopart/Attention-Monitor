"""
Face detection and head pose estimation using MediaPipe.
"""

import cv2
import numpy as np
import mediapipe as mp


class FaceDetector:
    """Detects faces and estimates head pose."""
    
    def __init__(self, min_detection_confidence=0.5):
        """Initialize MediaPipe Face Mesh."""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5
        )
        
        # 3D model points for head pose estimation
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ], dtype=np.float64)
        
        # Corresponding MediaPipe landmark indices
        self.landmark_indices = [1, 152, 33, 263, 61, 291]
        
    def detect_face(self, frame):
        """
        Detect face in frame.
        
        Returns:
            tuple: (success, landmarks, rgb_frame)
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            return True, results.multi_face_landmarks[0], rgb_frame
        return False, None, rgb_frame
    
    def estimate_head_pose(self, landmarks, frame_shape):
        """
        Estimate head pose (yaw, pitch, roll) from landmarks.
        
        Returns:
            tuple: (yaw, pitch, roll) in degrees or (None, None, None)
        """
        h, w, _ = frame_shape
        
        # Extract 2D image points
        image_points = np.array([
            (landmarks.landmark[idx].x * w, landmarks.landmark[idx].y * h)
            for idx in self.landmark_indices
        ], dtype=np.float64)
        
        # Camera matrix
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        
        dist_coeffs = np.zeros((4, 1))
        
        # Solve PnP
        success, rotation_vec, translation_vec = cv2.solvePnP(
            self.model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return None, None, None
        
        # Convert to rotation matrix
        rotation_mat, _ = cv2.Rodrigues(rotation_vec)
        
        # Extract Euler angles
        sy = np.sqrt(rotation_mat[0, 0] ** 2 + rotation_mat[1, 0] ** 2)
        singular = sy < 1e-6
        
        if not singular:
            pitch = np.arctan2(rotation_mat[2, 1], rotation_mat[2, 2])
            yaw = np.arctan2(-rotation_mat[2, 0], sy)
            roll = np.arctan2(rotation_mat[1, 0], rotation_mat[0, 0])
        else:
            pitch = np.arctan2(-rotation_mat[1, 2], rotation_mat[1, 1])
            yaw = np.arctan2(-rotation_mat[2, 0], sy)
            roll = 0
        
        # Convert to degrees
        return np.degrees(yaw), np.degrees(pitch), np.degrees(roll)
    
    def draw_debug_info(self, frame, landmarks, yaw, pitch, roll):
        """Draw debug information on frame."""
        h, w, _ = frame.shape
        
        # Draw landmarks
        for idx in self.landmark_indices:
            x = int(landmarks.landmark[idx].x * w)
            y = int(landmarks.landmark[idx].y * h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        
        # Draw angles
        if yaw is not None:
            cv2.putText(frame, f"Yaw: {yaw:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Pitch: {pitch:.1f}", (10, 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Roll: {roll:.1f}", (10, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def __del__(self):
        """Clean up resources."""
        self.face_mesh.close()
