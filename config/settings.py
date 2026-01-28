"""
Configuration settings for attention monitoring system.
"""

# Detection thresholds
ALERT_THRESHOLD = 5.0      # Seconds before alert
YAW_THRESHOLD = 25.0       # Degrees (left-right rotation)
PITCH_THRESHOLD = 20.0     # Degrees (up-down rotation)

# Temporal smoothing
SMOOTHING_WINDOW = 5       # Number of frames for smoothing
MIN_CONSECUTIVE_FRAMES = 3 # Frames to confirm state change

# Camera settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
TARGET_FPS = 30

# Detection confidence
MIN_DETECTION_CONFIDENCE = 0.5

# UI settings
ALERT_MESSAGE = "⚠️ ¡ATENCIÓN! No estás mirando la pantalla"
ALERT_COLOR = (0, 0, 255)  # BGR: Red
ALERT_FONT_SCALE = 1.5
ALERT_THICKNESS = 3
SHOW_DEBUG_INFO = True
SHOW_FPS = True

# Optional features
USE_EAR = False  # Eye Aspect Ratio (not needed for basic version)
