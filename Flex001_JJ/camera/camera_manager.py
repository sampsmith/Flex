

from pypylon import pylon
import logging

logger = logging.getLogger(__name__)

class CameraManager:
    """Manages camera initialization and configuration."""
    
    def __init__(self):
        """Initialize camera manager."""
        self.available_cameras = []
        self.logger = logging.getLogger(__name__)
        self.logger.info("Camera manager initialized")

    def initialize_cameras(self):
        """
        Initialize and configure all available cameras.
        
        Returns:
            list: List of configured camera objects
        """
        try:
            
            tl_factory = pylon.TlFactory.GetInstance()
            
            
            devices = tl_factory.EnumerateDevices()
            self.logger.info(f"Found {len(devices)} devices")
            
           
            self.available_cameras = []
            for device in devices:
                try:
                    camera = pylon.InstantCamera(tl_factory.CreateDevice(device))
                    camera.Open()
                    
                    camera.PixelFormat.SetValue("BayerRG8")
                    self.logger.info(f"Found and configured camera: {camera.GetDeviceInfo().GetModelName()}")
                    self.available_cameras.append(camera)
                except Exception as e:
                    self.logger.error(f"Error configuring camera: {str(e)}")
            
            self.logger.info(f"Successfully initialized {len(self.available_cameras)} cameras")
            return self.available_cameras
            
        except Exception as e:
            self.logger.error(f"Error initializing cameras: {str(e)}")
            return []

    def get_available_cameras(self):
        """Get list of available cameras."""
        return self.available_cameras

    def get_camera_info(self, camera):
        """
        Get camera information.
        
        Args:
            camera: Camera object
            
        Returns:
            dict: Camera information
        """
        try:
            device_info = camera.GetDeviceInfo()
            return {
                'model_name': device_info.GetModelName(),
                'serial_number': device_info.GetSerialNumber(),
                'vendor_name': device_info.GetVendorName(),
                'device_id': device_info.GetDeviceId()
            }
        except Exception as e:
            self.logger.error(f"Error getting camera info: {str(e)}")
            return {}

    def configure_camera_for_nail_detection(self, camera, resolution=(960, 960)):
        """
        Configure camera for nail detection.
        
        Args:
            camera: Camera object to configure
            resolution (tuple): Target resolution (width, height)
        """
        try:
            
            camera.PixelFormat.SetValue("BayerRG8")
            
           
            try:
                camera.Width.SetValue(resolution[0])
                camera.Height.SetValue(resolution[1])
                self.logger.info(f"Camera resolution set to {resolution[0]}x{resolution[1]}")
            except Exception as e:
                self.logger.warning(f"Could not set camera resolution to {resolution[0]}x{resolution[1]}: {str(e)}")
            
            self.logger.info("Camera configured for nail detection")
        except Exception as e:
            self.logger.error(f"Error configuring camera for nail detection: {str(e)}")

    def configure_camera_for_board_detection(self, camera):
        """
        Configure camera for board detection.
        
        Args:
            camera: Camera object to configure
        """
        try:
           
            camera.PixelFormat.SetValue("BayerRG8")
            self.logger.info("Camera configured for board detection")
        except Exception as e:
            self.logger.error(f"Error configuring camera for board detection: {str(e)}")

    def cleanup_cameras(self):
        """Clean up all camera resources."""
        try:
            for camera in self.available_cameras:
                if camera.IsOpen():
                    camera.Close()
            self.available_cameras.clear()
            self.logger.info("Camera cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during camera cleanup: {str(e)}")

    def get_camera_count(self):
        """Get the number of available cameras."""
        return len(self.available_cameras) 