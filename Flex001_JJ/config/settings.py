

import os
from pathlib import Path

class Settings:
    """Application settings and configuration."""
    
    def __init__(self):
        self.nail_model_path = None
        self.board_model_path = None
        
        self.pixels_to_mm = 0.1
        self.target_measurement_mm = 0.0
        self.measurement_threshold_mm = 5.0
        
        self.nail_confidence = 0.25
        self.board_confidence = 0.5
        
        self.relay_port = 'COM4'
        self.relay_baudrate = 9600
        
        self.nail_camera_interval = 800
        self.board_camera_timeout = 5000
        self.nail_camera_resolution = (960, 960)
        
        self.log_level = "ERROR"
        self.log_dir = "logs"
        
        self.database_path = "faults.db"
        
        self.cleanup_interval = 300000
        
        self.relay_on_command = bytes([0xA0, 0x01, 0x01, 0xA2])
        self.relay_off_command = bytes([0xA0, 0x01, 0x00, 0xA1])
        self.relay_trigger_duration = 0.5
    
    def update_from_dialog(self, dialog_data):
        """Update settings from dialog data."""
        self.nail_model_path = dialog_data.get('nail_model_path', self.nail_model_path)
        self.board_model_path = dialog_data.get('board_model_path', self.board_model_path)
        self.pixels_to_mm = dialog_data.get('pixels_to_mm', self.pixels_to_mm)
        self.target_measurement_mm = dialog_data.get('target_measurement_mm', self.target_measurement_mm)
        self.measurement_threshold_mm = dialog_data.get('measurement_threshold_mm', self.measurement_threshold_mm)
        self.nail_confidence = dialog_data.get('nail_confidence', self.nail_confidence)
        self.board_confidence = dialog_data.get('board_confidence', self.board_confidence)
        self.relay_port = dialog_data.get('relay_port', self.relay_port)
    
    def validate(self):
        """Validate settings and return any errors."""
        errors = []
        
        if not self.nail_model_path:
            errors.append("Nail model path not set")
        elif not os.path.exists(self.nail_model_path):
            errors.append(f"Nail model not found at: {self.nail_model_path}")
        
        if not self.board_model_path:
            errors.append("Board model path not set")
        elif not os.path.exists(self.board_model_path):
            errors.append(f"Board model not found at: {self.board_model_path}")
        
        if self.pixels_to_mm <= 0:
            errors.append("Pixels to mm ratio must be positive")
        
        if self.measurement_threshold_mm <= 0:
            errors.append("Measurement threshold must be positive")
        
        if not 0 <= self.nail_confidence <= 1:
            errors.append("Nail confidence must be between 0 and 1")
        
        if not 0 <= self.board_confidence <= 1:
            errors.append("Board confidence must be between 0 and 1")
        
        return errors 