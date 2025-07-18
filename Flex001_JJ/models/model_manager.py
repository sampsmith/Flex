

import os
import torch
from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages YOLO models for nail and board detection."""
    
    def __init__(self, settings):
        """
        Initialize model manager.
        
        Args:
            settings: Application settings object
        """
        self.settings = settings
        self.nail_model = None
        self.board_model = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        logger.info(f"Model manager initialized - Device: {self.device}")
        if self.device == 'cuda':
            logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")

    def load_models(self):
        """Load nail and board detection models."""
        try:
            if not self.settings.nail_model_path:
                logger.warning("Nail model path not set - skipping nail model loading")
                return
            
            if not self.settings.board_model_path:
                logger.warning("Board model path not set - skipping board model loading")
                return
            
            if not os.path.exists(self.settings.nail_model_path):
                raise FileNotFoundError(f"Nail model not found at: {self.settings.nail_model_path}")
            
            self.nail_model = YOLO(self.settings.nail_model_path)
            if self.device == 'cuda':
                self.nail_model.to(self.device)
                self.nail_model.model.cuda()
            logger.info("Nail model loaded successfully")
            
            if not os.path.exists(self.settings.board_model_path):
                raise FileNotFoundError(f"Board model not found at: {self.settings.board_model_path}")
            
            self.board_model = YOLO(self.settings.board_model_path)
            if self.device == 'cuda':
                self.board_model.to(self.device)
                self.board_model.model.cuda()
            logger.info("Board model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load models: {str(e)}")
            raise

    def reload_models(self):
        """Reload models with current settings."""
        logger.info("Reloading models...")
        self.load_models()

    def get_nail_model(self):
        """Get the nail detection model."""
        return self.nail_model

    def get_board_model(self):
        """Get the board alignment model."""
        return self.board_model

    def get_device(self):
        """Get the current device (cuda/cpu)."""
        return self.device

    def validate_models(self):
        """
        Validate that all models are loaded correctly.
        
        Returns:
            list: List of validation errors, empty if all valid
        """
        errors = []
        
        if not self.settings.nail_model_path:
            errors.append("Nail model path not set")
        elif self.nail_model is None:
            errors.append("Nail model not loaded")
        
        if not self.settings.board_model_path:
            errors.append("Board model path not set")
        elif self.board_model is None:
            errors.append("Board model not loaded")
        
        if self.settings.nail_model_path and not os.path.exists(self.settings.nail_model_path):
            errors.append(f"Nail model file not found: {self.settings.nail_model_path}")
        
        if self.settings.board_model_path and not os.path.exists(self.settings.board_model_path):
            errors.append(f"Board model file not found: {self.settings.board_model_path}")
        
        return errors

    def cleanup(self):
        """Clean up model resources."""
        try:
            if self.device == 'cuda':
                torch.cuda.empty_cache()
            
            self.nail_model = None
            self.board_model = None
            
            logger.info("Model manager cleanup completed")
        except Exception as e:
            logger.error(f"Error during model cleanup: {str(e)}") 