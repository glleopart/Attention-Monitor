"""
Attention tracking with temporal smoothing.
"""

from collections import deque
import time


class AttentionTracker:
    """Tracks attention state over time."""
    
    def __init__(self, alert_threshold=5.0, yaw_threshold=25.0, 
                 pitch_threshold=20.0, smoothing_window=5, 
                 min_consecutive_frames=3):
        """Initialize tracker."""
        self.alert_threshold = alert_threshold
        self.yaw_threshold = yaw_threshold
        self.pitch_threshold = pitch_threshold
        self.smoothing_window = smoothing_window
        self.min_consecutive_frames = min_consecutive_frames
        
        # State
        self.current_state = "looking"
        self.previous_state = "looking"
        self.state_buffer = deque(maxlen=smoothing_window)
        self.consecutive_count = 0
        
        # Time tracking
        self.time_not_looking = 0.0
        self.last_update_time = time.time()
        self.alert_active = False
        
        # Statistics
        self.total_frames = 0
        self.frames_looking = 0
        self.frames_not_looking = 0
    
    def classify_attention(self, yaw, pitch):
        """
        Classify if person is looking at screen.
        
        Returns:
            str: "looking" or "not_looking"
        """
        if yaw is None or pitch is None:
            return "not_looking"
        
        is_looking = (abs(yaw) < self.yaw_threshold and 
                     abs(pitch) < self.pitch_threshold)
        
        return "looking" if is_looking else "not_looking"
    
    def update(self, yaw, pitch):
        """
        Update attention state with new frame data.
        
        Returns:
            dict: State information
        """
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Classify current frame
        raw_state = self.classify_attention(yaw, pitch)
        self.state_buffer.append(raw_state)
        
        # Smooth over buffer (majority vote)
        if len(self.state_buffer) >= self.smoothing_window:
            looking_count = self.state_buffer.count("looking")
            confidence = looking_count / len(self.state_buffer)
            smoothed_state = "looking" if confidence > 0.5 else "not_looking"
        else:
            smoothed_state = raw_state
            confidence = 1.0 if smoothed_state == "looking" else 0.0
        
        # Check for state transition
        if smoothed_state != self.current_state:
            if smoothed_state == self.previous_state:
                self.consecutive_count += 1
            else:
                self.consecutive_count = 1
                self.previous_state = smoothed_state
            
            # Confirm state change
            if self.consecutive_count >= self.min_consecutive_frames:
                self.current_state = smoothed_state
                self.consecutive_count = 0
                
                if self.current_state == "looking":
                    self.time_not_looking = 0.0
                    self.alert_active = False
        else:
            self.consecutive_count = 0
            self.previous_state = smoothed_state
        
        # Accumulate time
        if self.current_state == "not_looking":
            self.time_not_looking += delta_time
            if self.time_not_looking >= self.alert_threshold:
                self.alert_active = True
        
        # Update statistics
        self.total_frames += 1
        if self.current_state == "looking":
            self.frames_looking += 1
        else:
            self.frames_not_looking += 1
        
        return {
            'state': self.current_state,
            'time_not_looking': self.time_not_looking,
            'alert_active': self.alert_active,
            'confidence': confidence,
            'raw_state': raw_state
        }
    
    def reset(self):
        """Reset all tracking state."""
        self.current_state = "looking"
        self.previous_state = "looking"
        self.state_buffer.clear()
        self.consecutive_count = 0
        self.time_not_looking = 0.0
        self.last_update_time = time.time()
        self.alert_active = False
    
    def get_statistics(self):
        """Get tracking statistics."""
        if self.total_frames == 0:
            attention_ratio = 1.0
        else:
            attention_ratio = self.frames_looking / self.total_frames
        
        return {
            'total_frames': self.total_frames,
            'frames_looking': self.frames_looking,
            'frames_not_looking': self.frames_not_looking,
            'attention_ratio': attention_ratio,
            'current_state': self.current_state,
            'time_not_looking': self.time_not_looking,
            'alert_active': self.alert_active
        }
