"""
UI overlay for alerts and statistics.
"""

import cv2


class UIOverlay:
    """Manages on-screen visual elements."""
    
    def __init__(self, alert_message="⚠️ ¡ATENCIÓN! No estás mirando la pantalla",
                 alert_color=(0, 0, 255), alert_font_scale=1.5, alert_thickness=3):
        """Initialize UI overlay."""
        self.alert_message = alert_message
        self.alert_color = alert_color
        self.alert_font_scale = alert_font_scale
        self.alert_thickness = alert_thickness
        self.alert_alpha = 0.0
        self.alert_pulse_direction = 1
    
    def draw_alert(self, frame, alert_active, time_not_looking):
        """Draw alert message with animation."""
        if not alert_active:
            self.alert_alpha = 0.0
            return frame
        
        h, w, _ = frame.shape
        
        # Semi-transparent background
        overlay = frame.copy()
        rect_height = 120
        rect_top = h // 2 - rect_height // 2
        cv2.rectangle(overlay, (0, rect_top), (w, rect_top + rect_height),
                     (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        # Pulsing animation
        self.alert_alpha += 0.05 * self.alert_pulse_direction
        if self.alert_alpha >= 1.0:
            self.alert_alpha = 1.0
            self.alert_pulse_direction = -1
        elif self.alert_alpha <= 0.5:
            self.alert_alpha = 0.5
            self.alert_pulse_direction = 1
        
        # Alert text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(self.alert_message, font, 
                                   self.alert_font_scale, self.alert_thickness)[0]
        text_x = (w - text_size[0]) // 2
        text_y = h // 2
        
        color_pulsed = tuple(int(c * self.alert_alpha) for c in self.alert_color)
        cv2.putText(frame, self.alert_message, (text_x, text_y),
                   font, self.alert_font_scale, color_pulsed, self.alert_thickness)
        
        # Time counter
        time_text = f"Tiempo sin mirar: {time_not_looking:.1f}s"
        time_size = cv2.getTextSize(time_text, font, 0.8, 2)[0]
        time_x = (w - time_size[0]) // 2
        time_y = text_y + 50
        cv2.putText(frame, time_text, (time_x, time_y),
                   font, 0.8, (255, 255, 255), 2)
        
        return frame
    
    def draw_status_bar(self, frame, state, time_not_looking, confidence):
        """Draw status bar at top."""
        h, w, _ = frame.shape
        
        # Background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 35), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
        
        # State
        state_color = (0, 255, 0) if state == "looking" else (0, 165, 255)
        cv2.putText(frame, f"Estado: {state.upper()}", (10, 23),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, state_color, 2)
        
        # Time
        cv2.putText(frame, f"Tiempo: {time_not_looking:.1f}s", (250, 23),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Confidence
        cv2.putText(frame, f"Conf: {confidence:.2f}", (450, 23),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def draw_statistics(self, frame, stats, fps=None):
        """Draw statistics overlay."""
        h, w, _ = frame.shape
        x_start = w - 300
        y_start = h - 150
        
        # Background
        overlay = frame.copy()
        cv2.rectangle(overlay, (x_start - 10, y_start - 10),
                     (w - 10, h - 10), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
        
        # Statistics
        font = cv2.FONT_HERSHEY_SIMPLEX
        y = y_start
        
        if fps:
            cv2.putText(frame, f"FPS: {fps:.1f}", (x_start, y),
                       font, 0.5, (255, 255, 255), 1)
            y += 25
        
        cv2.putText(frame, f"Total frames: {stats['total_frames']}", 
                   (x_start, y), font, 0.5, (255, 255, 255), 1)
        y += 25
        
        cv2.putText(frame, f"Attention: {stats['attention_ratio']:.1%}",
                   (x_start, y), font, 0.5, (255, 255, 255), 1)
        y += 25
        
        cv2.putText(frame, f"Looking: {stats['frames_looking']}",
                   (x_start, y), font, 0.5, (0, 255, 0), 1)
        y += 25
        
        cv2.putText(frame, f"Not looking: {stats['frames_not_looking']}",
                   (x_start, y), font, 0.5, (0, 165, 255), 1)
        
        return frame
    
    def draw_progress_bar(self, frame, time_not_looking, threshold):
        """Draw progress bar."""
        h, w, _ = frame.shape
        bar_width = 400
        bar_height = 20
        bar_x = (w - bar_width) // 2
        bar_y = h - 50
        
        # Background
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                     (100, 100, 100), -1)
        
        # Progress
        progress = min(time_not_looking / threshold, 1.0)
        fill_width = int(bar_width * progress)
        
        # Color
        if progress < 0.5:
            color = (0, 255, 0)
        elif progress < 0.8:
            color = (0, 255, 255)
        else:
            color = (0, 0, 255)
        
        if fill_width > 0:
            cv2.rectangle(frame, (bar_x, bar_y), 
                         (bar_x + fill_width, bar_y + bar_height), color, -1)
        
        # Border
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                     (255, 255, 255), 2)
        
        # Text
        text = f"{time_not_looking:.1f}s / {threshold:.1f}s"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        text_x = bar_x + (bar_width - text_size[0]) // 2
        text_y = bar_y - 10
        cv2.putText(frame, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def draw_instructions(self, frame):
        """Draw keyboard instructions."""
        h = frame.shape[0]
        instructions = [
            "Q/ESC - Salir",
            "R - Reset",
            "S - Stats"
        ]
        
        y = h - 80
        for text in instructions:
            cv2.putText(frame, text, (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            y += 20
        
        return frame
