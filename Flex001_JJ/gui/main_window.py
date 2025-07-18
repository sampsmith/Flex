

import sys
import os
import numpy as np
import cv2
import torch
import threading
import time
import gc
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QHBoxLayout, QSplitter, QGridLayout,
                             QComboBox, QStatusBar, QMessageBox, QDialog)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

from config.settings import Settings
from utils.logger import setup_logger
from hardware.relay_controller import RelayController
from database.fault_database import FaultDatabase
from models.model_manager import ModelManager
from camera.camera_manager import CameraManager
from camera.camera_workers import HardwareTriggeredCameraWorker, TimedCameraWorker
from detection.detection_worker import BatchDetectionWorker
from utils.image_utils import convert_bayer_to_rgb, resize_frame, display_image, draw_detections
from gui.dialogs import SettingsDialog, FaultHistoryDialog

import logging

logger = logging.getLogger(__name__)

class ParallelDetectorGUI(QMainWindow):
    """Main GUI window for the Flex001 application."""
    
    def __init__(self):
        super().__init__()
        logger.info("Initializing ParallelDetectorGUI")
        self.setWindowTitle("Flex001")
        self.setGeometry(100, 100, 1600, 900)
        
        self.settings = Settings()
        
        self.logger = setup_logger(self.settings.log_dir, self.settings.log_level)
        
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("")
        
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.periodic_cleanup)
        self.cleanup_timer.start(self.settings.cleanup_interval)
        
        self.fault_db = FaultDatabase(self.settings.database_path)
        self.relay = RelayController(port=self.settings.relay_port, baudrate=self.settings.relay_baudrate)
        self.relay.connect()
        
        self.camera_manager = CameraManager()
        self.available_cameras = self.camera_manager.initialize_cameras()
        
        self.model_manager = ModelManager(self.settings)
        
        self.nail_cameras = []  
        self.board_cameras = []  
        self.nail_camera_workers = {}  
        self.board_camera_workers = {}  
        self.board_worker_threads = {} 
        self.board_images = [None, None]
        self.board_results = [None, None]
        self.nail_images = [None, None]
        self.nail_results = [None, None]
        
        self.completed_detections = 0
        self.total_inference_time = 0.0
        self.total_start_time = 0.0
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        buttons_layout = QHBoxLayout()
        
        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.show_settings)
        settings_button.setFixedWidth(100)
        buttons_layout.addWidget(settings_button)
        
        history_button = QPushButton("Fault History")
        history_button.clicked.connect(self.show_fault_history)
        history_button.setFixedWidth(100)
        buttons_layout.addWidget(history_button)
        
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        
        nail_widget = QWidget()
        nail_layout = QVBoxLayout(nail_widget)
        
        nail_grid = QGridLayout()
        self.nail_image_labels = [QLabel(), QLabel()]
        self.nail_camera_combos = [QComboBox(), QComboBox()]
        self.nail_start_btns = [QPushButton(f"Start Camera {i+1}") for i in range(2)]
        self.nail_stop_btns = [QPushButton(f"Stop Camera {i+1}") for i in range(2)]
        
        for i in range(2):
            self.nail_image_labels[i].setAlignment(Qt.AlignCenter)
            self.nail_image_labels[i].setMinimumSize(400, 300)
            self.nail_image_labels[i].setStyleSheet("border: 2px solid #ccc;")
            self.nail_stop_btns[i].setEnabled(False)
            nail_grid.addWidget(self.nail_camera_combos[i], 0, i)
            nail_grid.addWidget(self.nail_start_btns[i], 1, i)
            nail_grid.addWidget(self.nail_stop_btns[i], 2, i)
            nail_grid.addWidget(self.nail_image_labels[i], 3, i)
        
        nail_layout.addLayout(nail_grid)
        
        board_widget = QWidget()
        board_layout = QVBoxLayout(board_widget)
        
        board_grid = QGridLayout()
        self.board_image_labels = [QLabel(), QLabel()]
        self.board_camera_combos = [QComboBox(), QComboBox()]
        self.board_start_btns = [QPushButton(f"Start Camera {i+1}") for i in range(2)]
        self.board_stop_btns = [QPushButton(f"Stop Camera {i+1}") for i in range(2)]
        
        for i in range(2):
            self.board_image_labels[i].setAlignment(Qt.AlignCenter)
            self.board_image_labels[i].setMinimumSize(400, 300)
            self.board_image_labels[i].setStyleSheet("border: 2px solid #ccc;")
            self.board_stop_btns[i].setEnabled(False)
            board_grid.addWidget(self.board_camera_combos[i], 0, i)
            board_grid.addWidget(self.board_start_btns[i], 1, i)
            board_grid.addWidget(self.board_stop_btns[i], 2, i)
            board_grid.addWidget(self.board_image_labels[i], 3, i)
        
        board_layout.addLayout(board_grid)
        
        splitter.addWidget(nail_widget)
        splitter.addWidget(board_widget)
        
        main_layout.addWidget(splitter)
        
        self.global_run_btn = QPushButton("Start All Cameras")
        self.global_run_btn.setEnabled(False)
        main_layout.addWidget(self.global_run_btn)
        
        for i in range(2):
            self.nail_start_btns[i].clicked.connect(lambda checked, idx=i: self._start_nail_camera(idx))
            self.nail_stop_btns[i].clicked.connect(lambda checked, idx=i: self._stop_nail_camera(idx))
            self.board_start_btns[i].clicked.connect(lambda checked, idx=i: self._start_camera(idx))
            self.board_stop_btns[i].clicked.connect(lambda checked, idx=i: self._stop_camera(idx))
        
        self.global_run_btn.clicked.connect(self.run_all_detections)
        
        self.workers = []
        
        self._update_camera_lists()

    def _update_camera_lists(self):
        """Update camera lists in UI."""
        logger.debug("Updating camera lists")
        try:
            for combo in self.board_camera_combos + self.nail_camera_combos:
                current_text = combo.currentText()
                combo.clear()
                
                for i, camera in enumerate(self.available_cameras):
                    try:
                        model_name = camera.GetDeviceInfo().GetModelName()
                        combo.addItem(f"Camera {i}: {model_name}", camera)
                        logger.debug(f"Added camera to combo box: {model_name}")
                    except Exception as e:
                        logger.error(f"Error adding camera to combo box: {str(e)}")
                
                index = combo.findText(current_text)
                if index >= 0:
                    combo.setCurrentIndex(index)
            
            self.global_run_btn.setEnabled(len(self.available_cameras) > 0)
            logger.debug("Camera lists updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating camera lists: {str(e)}")

    def _start_nail_camera(self, cam_index):
        """Start a nail camera."""
        logger.info(f"Attempting to start nail camera {cam_index}")
        if cam_index in self.nail_camera_workers:
            logger.warning(f"Nail camera {cam_index} already running")
            return
            
        selected_index = self.nail_camera_combos[cam_index].currentIndex()
        logger.info(f"Selected camera index: {selected_index}, Available cameras: {len(self.available_cameras)}")
        
        if selected_index < len(self.available_cameras):
            camera = self.available_cameras[selected_index]
            logger.info(f"Selected camera: {camera.GetDeviceInfo().GetModelName()}")
            
            if camera in self.nail_cameras:
                error_msg = "Camera is already in use by another nail camera"
                logger.error(f"Camera {cam_index}: {error_msg}")
                self._handle_camera_error(cam_index, error_msg)
                return
            
            if camera not in self.nail_cameras:
                logger.info(f"Adding camera {cam_index} to nail cameras")
                self.nail_cameras.append(camera)
                
                try:
                    self.camera_manager.configure_camera_for_nail_detection(
                        camera, self.settings.nail_camera_resolution
                    )
                    
                    logger.info(f"Creating timed worker for nail camera {cam_index}")
                    worker = TimedCameraWorker(camera, cam_index, self.settings)
                    worker.frame_ready.connect(self._handle_nail_frame)
                    worker.error_occurred.connect(self._handle_camera_error)
                    self.nail_camera_workers[cam_index] = worker
                    
                    logger.info(f"Starting worker for nail camera {cam_index}")
                    worker.start()
                    
                    self.nail_start_btns[cam_index].setEnabled(False)
                    self.nail_stop_btns[cam_index].setEnabled(True)
                    self.nail_camera_combos[cam_index].setEnabled(False)
                    logger.info(f"Nail camera {cam_index} setup completed successfully")
                except Exception as e:
                    logger.error(f"Failed to start nail camera {cam_index}: {str(e)}")
                    self._handle_camera_error(cam_index, f"Failed to start: {str(e)}")
            else:
                logger.warning(f"Camera {cam_index} already in nail cameras list")
        else:
            logger.error(f"Invalid camera selection for nail camera {cam_index}")

    def _stop_nail_camera(self, cam_index):
        """Stop a nail camera."""
        logger.info(f"Attempting to stop nail camera {cam_index}")
        if cam_index in self.nail_camera_workers:
            try:
                logger.info(f"Stopping nail camera {cam_index}")
                self.nail_camera_workers[cam_index].stop()
                del self.nail_camera_workers[cam_index]
                
                camera = self.nail_camera_combos[cam_index].currentData()
                if camera in self.nail_cameras:
                    self.nail_cameras.remove(camera)
                
                self.nail_images[cam_index] = None
                
                self.nail_start_btns[cam_index].setEnabled(True)
                self.nail_stop_btns[cam_index].setEnabled(False)
                self.nail_camera_combos[cam_index].setEnabled(True)
                logger.info(f"Nail camera {cam_index} stopped and cleaned up successfully")
            except Exception as e:
                logger.error(f"Error stopping nail camera {cam_index}: {str(e)}")
        else:
            logger.warning(f"Nail camera {cam_index} not found in workers")

    def _handle_nail_frame(self, cam_index, frame):
        """Handle frame from nail camera."""
        try:
            frame = convert_bayer_to_rgb(frame)
            
            frame = resize_frame(frame, self.settings.nail_camera_resolution)
            
            self.nail_images[cam_index] = frame.copy()
            
            display_image(frame, self.nail_image_labels[cam_index])
            
            nail_model = self.model_manager.get_nail_model()
            if nail_model:
                try:
                    logger.info(f"Starting nail detection for camera {cam_index}")
                    worker = BatchDetectionWorker(nail_model, [frame], 'nail',
                                               [cam_index], self.model_manager.get_device(), 
                                               conf=self.settings.nail_confidence)
                    worker.detection_complete.connect(self.handle_batch_detection_results)
                    self.workers.append(worker)
                    worker.start()
                except Exception as e:
                    logger.error(f"Error starting nail detection: {str(e)}")
        except Exception as e:
            logger.error(f"Error handling nail frame: {str(e)}")

    def _start_camera(self, cam_index):
        """Start a board camera."""
        logger.info(f"Attempting to start board camera {cam_index}")
        if cam_index in self.board_camera_workers:
            logger.warning(f"Board camera {cam_index} already running")
            return
            
        selected_index = self.board_camera_combos[cam_index].currentIndex()
        logger.info(f"Selected camera index: {selected_index}, Available cameras: {len(self.available_cameras)}")
        
        if selected_index < len(self.available_cameras):
            camera = self.available_cameras[selected_index]
            logger.info(f"Selected camera: {camera.GetDeviceInfo().GetModelName()}")
            
            if camera in self.board_cameras:
                error_msg = "Camera is already in use by another board camera"
                logger.error(f"Camera {cam_index}: {error_msg}")
                self._handle_camera_error(cam_index, error_msg)
                return
            
            if camera not in self.board_cameras:
                logger.info(f"Adding camera {cam_index} to board cameras")
                self.board_cameras.append(camera)
                
                try:
                    self.camera_manager.configure_camera_for_board_detection(camera)
                    
                    logger.info(f"Creating hardware triggered worker for board camera {cam_index}")
                    worker = HardwareTriggeredCameraWorker(camera, cam_index, self.settings)
                    worker.frame_ready.connect(self._handle_board_frame)
                    worker.error_occurred.connect(self._handle_camera_error)
                    self.board_camera_workers[cam_index] = worker
                    
                    logger.info(f"Starting worker and thread for board camera {cam_index}")
                    worker.start()
                    thread = threading.Thread(target=worker.run)
                    thread.daemon = True
                    self.board_worker_threads[cam_index] = thread
                    thread.start()
                    
                    self.board_start_btns[cam_index].setEnabled(False)
                    self.board_stop_btns[cam_index].setEnabled(True)
                    self.board_camera_combos[cam_index].setEnabled(False)
                    logger.info(f"Board camera {cam_index} setup completed successfully")
                except Exception as e:
                    logger.error(f"Failed to start board camera {cam_index}: {str(e)}")
                    self._handle_camera_error(cam_index, f"Failed to start: {str(e)}")
                    if camera in self.board_cameras:
                        self.board_cameras.remove(camera)
                    if cam_index in self.board_camera_workers:
                        del self.board_camera_workers[cam_index]
            else:
                logger.warning(f"Camera {cam_index} already in board cameras list")
        else:
            logger.error(f"Invalid camera selection for board camera {cam_index}")

    def _stop_camera(self, cam_index):
        """Stop a board camera."""
        logger.info(f"Attempting to stop board camera {cam_index}")
        if cam_index in self.board_camera_workers:
            try:
                logger.info(f"Stopping board camera {cam_index}")
                self.board_camera_workers[cam_index].stop()
                if cam_index in self.board_worker_threads:
                    logger.info(f"Joining thread for board camera {cam_index}")
                    self.board_worker_threads[cam_index].join()
                    del self.board_worker_threads[cam_index]
                del self.board_camera_workers[cam_index]
                
                camera = self.board_camera_combos[cam_index].currentData()
                if camera in self.board_cameras:
                    self.board_cameras.remove(camera)
                
                self.board_images[cam_index] = None
                
                self.board_start_btns[cam_index].setEnabled(True)
                self.board_stop_btns[cam_index].setEnabled(False)
                self.board_camera_combos[cam_index].setEnabled(True)
                logger.info(f"Board camera {cam_index} stopped and cleaned up successfully")
            except Exception as e:
                logger.error(f"Error stopping board camera {cam_index}: {str(e)}")
        else:
            logger.warning(f"Board camera {cam_index} not found in workers")

    def _handle_board_frame(self, cam_index, frame):
        """Handle frame from board camera."""
        try:
            frame = convert_bayer_to_rgb(frame)
            
            self.board_images[cam_index] = frame.copy()
            
            display_image(frame, self.board_image_labels[cam_index])
            
            board_model = self.model_manager.get_board_model()
            if board_model:
                try:
                    logger.info(f"Starting board detection for camera {cam_index}")
                    worker = BatchDetectionWorker(board_model, [frame], 'board',
                                               [cam_index], self.model_manager.get_device(), 
                                               conf=self.settings.board_confidence)
                    worker.detection_complete.connect(self.handle_batch_detection_results)
                    self.workers.append(worker)
                    worker.start()
                except Exception as e:
                    logger.error(f"Error starting board detection: {str(e)}")
        except Exception as e:
            logger.error(f"Error handling board frame: {str(e)}")

    def run_all_detections(self):
        """Start all cameras."""
        self.workers.clear()
        self.total_start_time = time.time()
        self.completed_detections = 0
        self.total_inference_time = 0.0
        
        logger.info("Starting all detections...")
        
        if self.model_manager.get_device() == 'cuda':
            gpu_memory = torch.cuda.memory_allocated() / 1024**2
            logger.info(f"Initial GPU memory: {gpu_memory:.2f} MB")
        
        for i in range(2):
            if self.board_camera_combos[i].currentIndex() >= 0:
                logger.info(f"Starting board camera {i}")
                self._start_camera(i)
            
            if self.nail_camera_combos[i].currentIndex() >= 0:
                logger.info(f"Starting nail camera {i}")
                self._start_nail_camera(i)
        
        self.global_run_btn.setText("Stop All Cameras")
        self.global_run_btn.clicked.disconnect()
        self.global_run_btn.clicked.connect(self.stop_all_detections)

    def stop_all_detections(self):
        """Stop all cameras."""
        for i in range(2):
            if i in self.board_camera_workers:
                self._stop_camera(i)
            
            if i in self.nail_camera_workers:
                self._stop_nail_camera(i)
        
        self.global_run_btn.setText("Start All Cameras")
        self.global_run_btn.clicked.disconnect()
        self.global_run_btn.clicked.connect(self.run_all_detections)

    def handle_batch_detection_results(self, results_list, detector_type, image_indices, inference_time):
        """Handle detection results from workers."""
        if not results_list or all(r is None for r in results_list):
            logger.error(f"Batch detection failed for {detector_type} detector")
            QMessageBox.critical(self, "Error", f"Batch detection failed for {detector_type} detector")
            return
            
        logger.info(f"Received {detector_type} detection results for images {image_indices}")
        logger.info(f"Inference time: {inference_time:.2f} seconds")
            
        for result, image_index in zip(results_list, image_indices):
            if result is None:
                logger.warning(f"No results for {detector_type} detection on image {image_index}")
                continue
                
            if detector_type == 'nail':
                self.nail_results[image_index] = result
                has_nails = len(result.boxes) > 0
                if has_nails:
                    logger.warning(f"DEFECT: Nail detected in image {image_index + 1}")
                    self.fault_db.log_fault("Nail", image_index + 1, 
                                          f"Detected {len(result.boxes)} nails")
                    self.relay.trigger(self.settings.relay_trigger_duration)
                draw_detections(self.nail_images[image_index], result, 
                              self.nail_image_labels[image_index], 
                              self.settings, is_defect=has_nails)
            else:
                self.board_results[image_index] = result
                draw_detections(self.board_images[image_index], result, 
                              self.board_image_labels[image_index], 
                              self.settings)
        
        self.completed_detections += len(image_indices)
        self.total_inference_time += inference_time
        
        if self.completed_detections == sum(len(w.image_indices) for w in self.workers):
            total_time = time.time() - self.total_start_time
            logger.info("\n=== Detection Timing Report ===")
            logger.info(f"Total wall clock time: {total_time:.2f} seconds")
            logger.info(f"Total inference time: {self.total_inference_time:.2f} seconds")
            logger.info(f"Average inference time per detection: {self.total_inference_time/self.completed_detections:.2f} seconds")
            logger.info(f"Number of detections: {self.completed_detections}")
            logger.info("=== End of Detection Report ===\n")
            
            if self.model_manager.get_device() == 'cuda':
                gpu_memory = torch.cuda.memory_allocated() / 1024**2
                logger.info(f"Final GPU memory usage: {gpu_memory:.2f} MB")

    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            try:
                settings_data = dialog.get_settings_data()
                
                self.settings.update_from_dialog(settings_data)
                
                errors = self.settings.validate()
                if errors:
                    error_msg = "\n".join(errors)
                    QMessageBox.warning(self, "Invalid Settings", error_msg)
                    return
                
                if (settings_data['nail_model_path'] != self.settings.nail_model_path or 
                    settings_data['board_model_path'] != self.settings.board_model_path):
                    self.model_manager.reload_models()
                    logger.info("Models reloaded with new paths")
                
                if settings_data['relay_port'] != self.settings.relay_port:
                    self.relay.disconnect()
                    self.relay = RelayController(port=self.settings.relay_port, 
                                               baudrate=self.settings.relay_baudrate)
                    self.relay.connect()
                    logger.info(f"Relay updated to port {self.settings.relay_port}")
                
                for i, result in enumerate(self.board_results):
                    if result is not None:
                        draw_detections(self.board_images[i], result, 
                                      self.board_image_labels[i], self.settings)
                
                logger.info("Settings updated successfully")
                
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Settings", str(e))
                return

    def show_fault_history(self):
        """Show fault history dialog."""
        dialog = FaultHistoryDialog(self)
        dialog.exec()

    def closeEvent(self, event):
        """Clean up when the application is closed."""
        try:
            logger.info("Starting application cleanup")
            
            self.cleanup_timer.stop()
            
            for cam_index in list(self.nail_camera_workers.keys()):
                self._stop_nail_camera(cam_index)
            for cam_index in list(self.board_camera_workers.keys()):
                self._stop_camera(cam_index)
            
            self.camera_manager.cleanup_cameras()
            
            self.board_images = [None, None]
            self.nail_images = [None, None]
            
            self.board_results = [None, None]
            self.nail_results = [None, None]
            
            self.workers.clear()
            
            self.model_manager.cleanup()
            
            self.relay.disconnect()
            
            gc.collect()
            
            if self.model_manager.get_device() == 'cuda':
                torch.cuda.empty_cache()
            
            logger.info("Application cleanup completed")
            event.accept()
        except Exception as e:
            logger.error(f"Error during application cleanup: {str(e)}")
            event.accept()

    def _handle_camera_error(self, cam_index, error_msg):
        """Handle camera errors."""
        logger.error(f"Camera {cam_index} error: {error_msg}")
        
        if "explicit triggering" in error_msg.lower():
            self.set_status_message(f"Camera {cam_index}: {error_msg}", timeout=10000)
            return
        
        if cam_index < len(self.nail_image_labels):
            self.nail_image_labels[cam_index].setText(f"Error: {error_msg}")
        if cam_index < len(self.board_image_labels):
            self.board_image_labels[cam_index].setText(f"Error: {error_msg}")
        
        if "Failed to start" in error_msg or "Camera not responding" in error_msg:
            if cam_index in self.nail_camera_workers:
                logger.info(f"Stopping camera {cam_index} due to critical error")
                if cam_index in self.nail_cameras:
                    self._stop_nail_camera(cam_index)
                elif cam_index in self.board_cameras:
                    self._stop_camera(cam_index)

    def periodic_cleanup(self):
        """Periodic cleanup of resources."""
        try:
            logger.info("Running periodic cleanup")
            
            self.workers = [w for w in self.workers if w.isRunning()]
            
            for i in range(2):
                if self.board_images[i] is not None and not self.board_camera_workers.get(i, None):
                    self.board_images[i] = None
                if self.nail_images[i] is not None and not self.nail_camera_workers.get(i, None):
                    self.nail_images[i] = None
            
            gc.collect()
            
            if self.model_manager.get_device() == 'cuda':
                gpu_memory = torch.cuda.memory_allocated() / 1024**2
                logger.info(f"GPU memory after cleanup: {gpu_memory:.2f} MB")
            
            logger.info("Periodic cleanup completed")
        except Exception as e:
            logger.error(f"Error during periodic cleanup: {str(e)}")

    def set_status_message(self, message, timeout=5000):
        """Show a message in the status bar for a given timeout (ms)."""
        self.status_bar.showMessage(message, timeout) 