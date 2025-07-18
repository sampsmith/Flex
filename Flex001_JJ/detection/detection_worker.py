
import time
import torch
from PySide6.QtCore import QThread, Signal
import logging

logger = logging.getLogger(__name__)

class BatchDetectionWorker(QThread):
    """Worker for running batch YOLO detections."""
    
    detection_complete = Signal(list, str, list, float)
    
    def __init__(self, model, images, detector_type, image_indices, device='cpu', conf=0.25):
        """
        Initialize batch detection worker.
        
        Args:
            model: YOLO model to use for inference
            images (list): List of images to process
            detector_type (str): Type of detector ('nail' or 'board')
            image_indices (list): List of image indices
            device (str): Device to run inference on ('cpu' or 'cuda')
            conf (float): Confidence threshold
        """
        super().__init__()
        self.model = model
        self.images = images
        self.detector_type = detector_type
        self.image_indices = image_indices
        self.device = device
        self.conf = conf
        logger.info(f"Initialized {detector_type} detection worker for images {image_indices}")
        
    def run(self):
        """Run the detection."""
        try:
            start_time = time.time()
            logger.info(f"Starting {self.detector_type} detection for images {self.image_indices}")
            
            if self.device == 'cuda':
                gpu_memory = torch.cuda.memory_allocated() / 1024**2
                logger.info(f"GPU memory before {self.detector_type} detection: {gpu_memory:.2f} MB")
                self.model.model.cuda()
            
            logger.info(f"Running inference for {self.detector_type} on {len(self.images)} images")
            results = self.model(self.images, device=self.device, conf=self.conf, verbose=False)
            
            inference_time = time.time() - start_time
            logger.info(f"{self.detector_type} detection completed in {inference_time:.2f} seconds")
            
            if self.device == 'cuda':
                gpu_memory = torch.cuda.memory_allocated() / 1024**2
                logger.info(f"GPU memory after {self.detector_type} detection: {gpu_memory:.2f} MB")
            
            self.detection_complete.emit(results, self.detector_type, self.image_indices, inference_time)
        except Exception as e:
            logger.error(f"Error in {self.detector_type} batch detection: {str(e)}")
            self.detection_complete.emit([None] * len(self.images), self.detector_type, self.image_indices, 0.0) 