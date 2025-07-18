

import numpy as np
import cv2
import time
import threading
import gc
from PySide6.QtCore import QObject, Signal, QTimer
from pypylon import pylon
import logging

logger = logging.getLogger(__name__)

class HardwareTriggeredCameraWorker(QObject):
    """Worker for hardware-triggered cameras (board detection)."""
    
    frame_ready = Signal(int, np.ndarray)
    error_occurred = Signal(int, str)
    
    def __init__(self, camera, cam_index, settings):
        """
        Initialize hardware triggered camera worker.
        
        Args:
            camera: Camera object
            cam_index (int): Camera index
            settings: Settings object
        """
        super().__init__()
        self.camera = camera
        self.cam_index = cam_index
        self.settings = settings
        self.running = False
        self.retry_count = 0
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        self.last_frame = None
        logger.info(f"Initialized HardwareTriggeredCameraWorker for camera {cam_index}")
    
    def start(self):
        """Start the camera worker."""
        try:
            logger.info(f"Starting hardware triggered camera {self.cam_index}")
            self.running = True
            self.camera.Open()
            logger.info(f"Camera {self.cam_index} opened successfully")
            
            # Configure for hardware trigger
            self.camera.TriggerMode.SetValue("On")
            self.camera.TriggerSource.SetValue("Line1")
            self.camera.TriggerSelector.SetValue("FrameStart")
            self.camera.TriggerActivation.SetValue("RisingEdge")
            self.camera.AcquisitionMode.SetValue("Continuous")
            logger.info(f"Camera {self.cam_index} configured for hardware trigger")
            
            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            logger.info(f"Camera {self.cam_index} started grabbing")
            self.retry_count = 0
        except Exception as e:
            error_msg = f"Failed to start camera: {str(e)}"
            logger.error(f"Camera {self.cam_index} - {error_msg}")
            self.error_occurred.emit(self.cam_index, error_msg)
            self.running = False
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if self.camera.IsGrabbing():
                self.camera.StopGrabbing()
            if self.camera.IsOpen():
                self.camera.Close()
            self.last_frame = None
            # Garbage collection
            gc.collect()
        except Exception as e:
            logger.error(f"Error during camera cleanup: {str(e)}")
    
    def stop(self):
        """Stop the camera worker."""
        logger.info(f"Stopping hardware triggered camera {self.cam_index}")
        self.running = False
        self.cleanup()
    
    def run(self):
        """Main camera loop."""
        while self.running:
            try:
                if self.camera.IsGrabbing():
                    grab_result = self.camera.RetrieveResult(
                        self.settings.board_camera_timeout, 
                        pylon.TimeoutHandling_ThrowException
                    )
                    if grab_result and grab_result.GrabSucceeded():
                        try:
                            img = grab_result.Array
                            logger.debug(f"Camera {self.cam_index} captured frame: {img.shape}")
                            self.frame_ready.emit(self.cam_index, img)
                            self.retry_count = 0
                        finally:
                            grab_result.Release()
                    else:
                        error_msg = f"Grab failed: {grab_result.GetErrorDescription() if grab_result else 'No grab result'}"
                        logger.error(f"Camera {self.cam_index} - {error_msg}")
                        self.error_occurred.emit(self.cam_index, error_msg)
                        self._handle_error()
            except pylon.TimeoutException:
                logger.debug(f"Camera {self.cam_index} - Grab timed out - waiting for trigger")
                time.sleep(0.1)  # Short sleep to prevent CPU spinning
            except Exception as e:
                error_msg = f"Error in camera loop: {str(e)}"
                logger.error(f"Camera {self.cam_index} - {error_msg}")
                self.error_occurred.emit(self.cam_index, error_msg)
                self._handle_error()
                time.sleep(0.1)  

    def _handle_error(self):
        """Handle camera errors with retry logic."""
        self.retry_count += 1
        if self.retry_count >= self.max_retries:
            self.error_occurred.emit(self.cam_index, f"Max retries ({self.max_retries}) exceeded - attempting camera restart")
            self._restart_camera()
            self.retry_count = 0
        else:
            time.sleep(self.retry_delay)
    
    def _restart_camera(self):
        """Restart the camera after an error."""
        try:
            if self.camera.IsGrabbing():
                self.camera.StopGrabbing()
            if self.camera.IsOpen():
                self.camera.Close()
            time.sleep(1.0)  # Sometimes issues here with the camera not fully closing
            self.camera.Open()
            # Reconfigure camera settings
            self.camera.TriggerMode.SetValue("On")
            self.camera.TriggerSource.SetValue("Line1")
            self.camera.TriggerSelector.SetValue("FrameStart")
            self.camera.TriggerActivation.SetValue("RisingEdge")
            self.camera.AcquisitionMode.SetValue("Continuous")
            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            logger.info(f"Camera {self.cam_index} restarted successfully")
        except Exception as e:
            error_msg = f"Failed to restart camera: {str(e)}"
            logger.error(f"Camera {self.cam_index} - {error_msg}")
            self.error_occurred.emit(self.cam_index, error_msg)
            self.running = False


class TimedCameraWorker(QObject):
    """Worker for timed cameras (nail detection)."""
    
    frame_ready = Signal(int, np.ndarray)
    error_occurred = Signal(int, str)
    
    def __init__(self, camera, cam_index, settings, interval=None):
        """
        Initialize timed camera worker.
        
        Args:
            camera: Camera object
            cam_index (int): Camera index
            settings: Settings object
            interval (int): Frame capture interval in milliseconds
        """
        super().__init__()
        self.camera = camera
        self.cam_index = cam_index
        self.settings = settings
        self.interval = interval or settings.nail_camera_interval
        self.running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.grab_frame)
        self.last_frame = None
        logger.info(f"Initialized TimedCameraWorker for camera {cam_index}")
    
    def start(self):
        """Start the camera worker."""
        try:
            logger.info(f"Starting timed camera {self.cam_index}")
            self.running = True
            self.camera.Open()
            logger.info(f"Camera {self.cam_index} opened successfully")
            
            # Configure for continuous acquisition
            self.camera.TriggerMode.SetValue("Off")
            self.camera.AcquisitionMode.SetValue("Continuous")
            logger.info(f"Camera {self.cam_index} configured for continuous acquisition")
            
            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            logger.info(f"Camera {self.cam_index} started grabbing")
            
            self.timer.start(self.interval)
            logger.info(f"Camera {self.cam_index} timer started at {self.interval}ms interval")
        except Exception as e:
            error_msg = f"Failed to start camera: {str(e)}"
            logger.error(f"Camera {self.cam_index} - {error_msg}")
            self.error_occurred.emit(self.cam_index, error_msg)
            self.running = False
    
    def cleanup(self):
        """Clean up resources."""
        try:
            self.timer.stop()
            if self.camera.IsGrabbing():
                self.camera.StopGrabbing()
            if self.camera.IsOpen():
                self.camera.Close()
            self.last_frame = None
            
            gc.collect()
        except Exception as e:
            logger.error(f"Error during camera cleanup: {str(e)}")
    
    def stop(self):
        """Stop the camera worker."""
        logger.info(f"Stopping timed camera {self.cam_index}")
        self.running = False
        self.cleanup()
        
    def grab_frame(self):
        """Grab a frame from the camera."""
        if self.running and self.camera.IsOpen():
            try:
                grab_result = self.camera.RetrieveResult(
                    self.settings.board_camera_timeout, 
                    pylon.TimeoutHandling_ThrowException
                )
                if grab_result.GrabSucceeded():
                    img = grab_result.Array
                    logger.debug(f"Camera {self.cam_index} captured frame: {img.shape}")
                    self.frame_ready.emit(self.cam_index, img)
                else:
                    error_msg = f"Grab failed: {grab_result.GetErrorDescription()}"
                    logger.error(f"Camera {self.cam_index} - {error_msg}")
                    self.error_occurred.emit(self.cam_index, error_msg)
                grab_result.Release()
            except Exception as e:
                error_msg = f"Error grabbing frame: {str(e)}"
                logger.error(f"Camera {self.cam_index} - {error_msg}")
                self.error_occurred.emit(self.cam_index, error_msg) 