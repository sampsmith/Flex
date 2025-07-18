
#Image processing for the application, starting programming 03/09/2024
import cv2
import numpy as np
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

def convert_bayer_to_rgb(frame):
    """
    Convert Bayer format image to RGB.
    
    Args:
        frame (np.ndarray): Input frame in Bayer format
        
    Returns:
        np.ndarray: RGB frame
    """
    try:
        return cv2.cvtColor(frame, cv2.COLOR_BayerRG2RGB)
    except Exception as e:
        logger.error(f"Error converting Bayer to RGB: {str(e)}")
        return frame

def resize_frame(frame, target_size):
    """
    Resize frame to target size.
    
    Args:
        frame (np.ndarray): Input frame
        target_size (tuple): Target size (width, height)
        
    Returns:
        np.ndarray: Resized frame
    """
    try:
        if frame.shape[0] != target_size[1] or frame.shape[1] != target_size[0]:
            frame = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
            logger.debug(f"Resized frame to {target_size}")
        return frame
    except Exception as e:
        logger.error(f"Error resizing frame: {str(e)}")
        return frame

def numpy_to_qimage(arr):
    """
    Convert numpy array to QImage.
    
    Args:
        arr (np.ndarray): Input array
        
    Returns:
        QImage: Converted QImage
    """
    try:
        height, width, channel = arr.shape
        bytes_per_line = 3 * width
        return QImage(arr.data, width, height, bytes_per_line, QImage.Format_RGB888)
    except Exception as e:
        logger.error(f"Error converting numpy to QImage: {str(e)}")
        return None

def display_image(image, label):
    """
    Display image in a QLabel.
    
    Args:
        image (np.ndarray): Image to display
        label (QLabel): Label to display image in
    """
    try:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        qimage = numpy_to_qimage(rgb_image)
        scaled_pixmap = QPixmap.fromImage(qimage).scaled(
            label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)
        del rgb_image
        del qimage
        del scaled_pixmap
    except Exception as e:
        logger.error(f"Error displaying image: {str(e)}")

def draw_detections(image, results, label, settings, is_defect=False):
    """
    Draw detection results on image.
    
    Args:
        image (np.ndarray): Input image
        results: YOLO detection results
        label (QLabel): Label to display result in
        settings: Application settings
        is_defect (bool): Whether this is a defect detection
    """
    if not results:
        logger.warning("No detection results to draw")
        return
    
    logger.info(f"\n=== {label.objectName()} Detection Results ===")
    display_image = image.copy()
    
    if is_defect:
        cv2.rectangle(display_image, (0, 0), 
                     (display_image.shape[1], display_image.shape[0]), 
                     (0, 0, 255), 5)
        cv2.putText(display_image, "DEFECT", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    boxes = []
    for i, box in enumerate(results.boxes):
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        conf = box.conf[0].item()
        cls = int(box.cls[0].item())
        label_text = f"{results.names[cls]} {conf:.2f}"
        boxes.append((x1, y1, x2, y2, label_text))
        
        logger.info(f"\nDetection {i+1}:")
        logger.info(f"Class: {results.names[cls]}")
        logger.info(f"Confidence: {conf:.2f}")
        logger.info(f"Coordinates: ({x1}, {y1}, {x2}, {y2})")
        
        cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(display_image, label_text, (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    if hasattr(label, 'parent') and hasattr(label.parent(), 'board_image_labels'):
        if label in label.parent().board_image_labels and len(boxes) >= 2:
            boxes.sort(key=lambda x: x[0])
            box1 = boxes[0]
            box2 = boxes[-1]
            y_level = min(box1[3], box2[3])
            
            right_dist_px = box2[2] - box1[2]
            left_dist_px = box2[0] - box1[0]
            right_dist_mm = right_dist_px * settings.pixels_to_mm
            left_dist_mm = left_dist_px * settings.pixels_to_mm
            
            avg_measurement = (right_dist_mm + left_dist_mm) / 2
            
            measurement_diff = abs(avg_measurement - settings.target_measurement_mm)
            is_measurement_defect = measurement_diff > settings.measurement_threshold_mm
            
            if is_measurement_defect:
                logger.warning(f"DEFECT: Measurement {avg_measurement:.1f}mm outside tolerance of {settings.target_measurement_mm}mm ±{settings.measurement_threshold_mm}mm")
                if not is_defect:
                    cv2.rectangle(display_image, (0, 0), 
                                (display_image.shape[1], display_image.shape[0]), 
                                (0, 0, 255), 5)
                    cv2.putText(display_image, "DEFECT", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            cv2.line(display_image, (box1[2], y_level), (box2[2], y_level), (255, 0, 0), 2)
            cv2.putText(display_image, f"{right_dist_mm:.1f}mm", 
                       ((box1[2] + box2[2])//2, y_level - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            cv2.line(display_image, (box1[0], y_level), (box2[0], y_level), (0, 0, 255), 2)
            cv2.putText(display_image, f"{left_dist_mm:.1f}mm", 
                       ((box1[0] + box2[0])//2, y_level - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            cv2.putText(display_image, f"Target: {settings.target_measurement_mm}mm ±{settings.measurement_threshold_mm}mm", 
                       (10, display_image.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            logger.info(f"\nMeasurements:")
            logger.info(f"Right-to-right distance: {right_dist_mm:.1f}mm")
            logger.info(f"Left-to-left distance: {left_dist_mm:.1f}mm")
            logger.info(f"Average measurement: {avg_measurement:.1f}mm")
            logger.info(f"Target measurement: {settings.target_measurement_mm}mm ±{settings.measurement_threshold_mm}mm")
    
    logger.info("\n=== Finished Drawing Detections ===")
    display_image(display_image, label) 