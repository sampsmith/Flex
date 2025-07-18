

import serial
import time
import logging

logger = logging.getLogger(__name__)

class RelayController:
    """Controls relay hardware via serial communication."""
    
    def __init__(self, port='COM4', baudrate=9600):
        """
        Initialize relay controller.
        
        Args:
            port (str): Serial port (e.g., 'COM4')
            baudrate (int): Baud rate for serial communication
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        logger.info(f"Relay controller initialized for port {port}")

    def connect(self):
        """
        Connect to the relay.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            logger.info(f"Connected to relay on {self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to relay: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from the relay."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            logger.info("Disconnected from relay")

    def turn_on(self):
        """
        Turn the relay ON.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.serial or not self.serial.is_open:
            logger.warning("Not connected to relay")
            return False
        
        # Command to turn ON: $A0 $01 $01 $A2
        command = bytes([0xA0, 0x01, 0x01, 0xA2])
        try:
            self.serial.write(command)
            logger.info("Relay turned ON")
            return True
        except Exception as e:
            logger.error(f"Failed to turn ON: {str(e)}")
            return False

    def turn_off(self):
        """
        Turn the relay OFF.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.serial or not self.serial.is_open:
            logger.warning("Not connected to relay")
            return False
        
        # Command to turn OFF: $A0 $01 $00 $A1
        command = bytes([0xA0, 0x01, 0x00, 0xA1])
        try:
            self.serial.write(command)
            logger.info("Relay turned OFF")
            return True
        except Exception as e:
            logger.error(f"Failed to turn OFF: {str(e)}")
            return False

    def trigger(self, duration=0.5):
        """
        Trigger the relay for a specified duration.
        
        Args:
            duration (float): Duration in seconds to keep relay on
        """
        if self.turn_on():
            time.sleep(duration)
            self.turn_off()
            logger.info(f"Relay triggered for {duration} seconds")
        else:
            logger.error("Failed to trigger relay") 