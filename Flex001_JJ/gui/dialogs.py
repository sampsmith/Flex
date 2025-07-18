

from PySide6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                             QHBoxLayout, QVBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QComboBox, QGroupBox,
                             QFileDialog, QMessageBox, QWidget)
from PySide6.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """Settings dialog for configuring application parameters."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.parent = parent
        
        layout = QFormLayout(self)
        
        self.nail_model_path = QLineEdit(parent.settings.nail_model_path or "")
        self.nail_model_path.setFixedWidth(300)
        self.nail_model_path.setPlaceholderText("Select nail detection model...")
        nail_browse_btn = QPushButton("Browse")
        nail_browse_btn.clicked.connect(lambda: self.browse_model_path(self.nail_model_path))
        nail_path_layout = QHBoxLayout()
        nail_path_layout.addWidget(self.nail_model_path)
        nail_path_layout.addWidget(nail_browse_btn)
        layout.addRow("Nail Model Path:", nail_path_layout)
        
        self.board_model_path = QLineEdit(parent.settings.board_model_path or "")
        self.board_model_path.setFixedWidth(300)
        self.board_model_path.setPlaceholderText("Select board alignment model...")
        board_browse_btn = QPushButton("Browse")
        board_browse_btn.clicked.connect(lambda: self.browse_model_path(self.board_model_path))
        board_path_layout = QHBoxLayout()
        board_path_layout.addWidget(self.board_model_path)
        board_path_layout.addWidget(board_browse_btn)
        layout.addRow("Board Model Path:", board_path_layout)
        
        self.ratio_input = QLineEdit(str(parent.settings.pixels_to_mm))
        self.ratio_input.setFixedWidth(100)
        layout.addRow("Pixels to mm ratio:", self.ratio_input)
        
        self.target_measurement_input = QLineEdit(str(parent.settings.target_measurement_mm))
        self.target_measurement_input.setFixedWidth(100)
        layout.addRow("Target measurement (mm):", self.target_measurement_input)
        
        self.measurement_threshold_input = QLineEdit(str(parent.settings.measurement_threshold_mm))
        self.measurement_threshold_input.setFixedWidth(100)
        layout.addRow("Measurement tolerance (±mm):", self.measurement_threshold_input)
        
        self.nail_conf_input = QLineEdit(str(parent.settings.nail_confidence))
        self.nail_conf_input.setFixedWidth(100)
        layout.addRow("Nail detection confidence:", self.nail_conf_input)
        
        self.board_conf_input = QLineEdit(str(parent.settings.board_confidence))
        self.board_conf_input.setFixedWidth(100)
        layout.addRow("Board detection confidence:", self.board_conf_input)
        
        self.relay_port_input = QLineEdit(parent.settings.relay_port)
        self.relay_port_input.setFixedWidth(100)
        layout.addRow("Relay COM Port:", self.relay_port_input)
        
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow("", button_layout)
        
        self.setLayout(layout)
    
    def browse_model_path(self, line_edit):
        """Browse for model file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Model File", "", "Model Files (*.pt)"
        )
        if file_path:
            line_edit.setText(file_path)

    def get_settings_data(self):
        """Get settings data from dialog."""
        nail_path = self.nail_model_path.text().strip()
        board_path = self.board_model_path.text().strip()
        
        return {
            'nail_model_path': nail_path if nail_path else None,
            'board_model_path': board_path if board_path else None,
            'pixels_to_mm': float(self.ratio_input.text()),
            'target_measurement_mm': float(self.target_measurement_input.text()),
            'measurement_threshold_mm': float(self.measurement_threshold_input.text()),
            'nail_confidence': float(self.nail_conf_input.text()),
            'board_confidence': float(self.board_conf_input.text()),
            'relay_port': self.relay_port_input.text()
        }


class FaultHistoryDialog(QDialog):
    """Dialog for viewing fault history and statistics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fault History Dashboard")
        self.setModal(True)
        self.setMinimumSize(1200, 800)
        self.parent = parent
        
        layout = QVBoxLayout(self)
        
        filter_layout = QHBoxLayout()
        
        date_group = QGroupBox("Date Range")
        date_layout = QHBoxLayout()
        self.start_date = QLineEdit()
        self.end_date = QLineEdit()
        self.start_date.setPlaceholderText("Start Date (YYYY-MM-DD)")
        self.end_date.setPlaceholderText("End Date (YYYY-MM-DD)")
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(self.end_date)
        date_group.setLayout(date_layout)
        filter_layout.addWidget(date_group)
        
        type_group = QGroupBox("Fault Type")
        type_layout = QHBoxLayout()
        self.fault_type_combo = QComboBox()
        self.fault_type_combo.addItems(["All", "Nail", "Board Alignment"])
        type_layout.addWidget(self.fault_type_combo)
        type_group.setLayout(type_layout)
        filter_layout.addWidget(type_group)
        
        layout.addLayout(filter_layout)
        
        stats_layout = QHBoxLayout()
        
        total_group = QGroupBox("Total Faults")
        total_layout = QVBoxLayout()
        self.total_faults_label = QLabel("0")
        self.total_faults_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        total_layout.addWidget(self.total_faults_label)
        total_group.setLayout(total_layout)
        stats_layout.addWidget(total_group)
        
        type_stats_group = QGroupBox("Faults by Type")
        type_stats_layout = QVBoxLayout()
        self.nail_faults_label = QLabel("Nail Faults: 0")
        self.board_faults_label = QLabel("Board Alignment Faults: 0")
        type_stats_layout.addWidget(self.nail_faults_label)
        type_stats_layout.addWidget(self.board_faults_label)
        type_stats_group.setLayout(type_stats_layout)
        stats_layout.addWidget(type_stats_group)
        
        layout.addLayout(stats_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Type", "Image", "Details", "Measurement", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_faults)
        button_layout.addWidget(refresh_button)
        
        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_to_csv)
        button_layout.addWidget(export_button)
        
        clear_button = QPushButton("Clear History")
        clear_button.clicked.connect(self.clear_history)
        button_layout.addWidget(clear_button)
        
        layout.addLayout(button_layout)
        
        self.load_faults()
    
    def load_faults(self):
        """Load faults from database and update display."""
        try:
            faults = self.parent.fault_db.get_faults(
                start_date=self.start_date.text() if self.start_date.text() else None,
                end_date=self.end_date.text() if self.end_date.text() else None,
                fault_type=self.fault_type_combo.currentText()
            )
            
            stats = self.parent.fault_db.get_statistics(faults)
            self.update_statistics(stats)
            
            self.table.setRowCount(len(faults))
            for i, fault in enumerate(faults):
                self.table.setItem(i, 0, QTableWidgetItem(fault[0]))
                
                type_item = QTableWidgetItem(fault[1])
                if fault[1] == "Nail":
                    type_item.setBackground(Qt.red)
                else:
                    type_item.setBackground(Qt.yellow)
                self.table.setItem(i, 1, type_item)
                
                self.table.setItem(i, 2, QTableWidgetItem(str(fault[2])))
                
                self.table.setItem(i, 3, QTableWidgetItem(fault[3]))
                
                measurement = str(fault[4]) if fault[4] is not None else ""
                self.table.setItem(i, 4, QTableWidgetItem(measurement))
                
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(0, 0, 0, 0)
                
                view_button = QPushButton("View")
                view_button.clicked.connect(lambda checked, row=i: self.view_fault(row))
                action_layout.addWidget(view_button)
                
                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda checked, row=i: self.delete_fault(row))
                action_layout.addWidget(delete_button)
                
                self.table.setCellWidget(i, 5, action_widget)
                
        except Exception as e:
            logger.error(f"Error loading faults: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load faults: {str(e)}")
    
    def update_statistics(self, stats):
        """Update statistics display."""
        self.total_faults_label.setText(str(stats['total_faults']))
        self.nail_faults_label.setText(f"Nail Faults: {stats['nail_faults']}")
        self.board_faults_label.setText(f"Board Alignment Faults: {stats['board_faults']}")
    
    def view_fault(self, row):
        """View fault details."""
        try:
            timestamp = self.table.item(row, 0).text()
            fault_type = self.table.item(row, 1).text()
            image_index = int(self.table.item(row, 2).text())
            details = self.table.item(row, 3).text()
            measurement = self.table.item(row, 4).text()
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Fault Details")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            
            info_text = f"Timestamp: {timestamp}\n"
            info_text += f"Type: {fault_type}\n"
            info_text += f"Image Index: {image_index}\n"
            info_text += f"Details: {details}\n"
            if measurement:
                info_text += f"Measurement: {measurement}mm"
            
            info_label = QLabel(info_text)
            layout.addWidget(info_label)
            
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)
            
            dialog.exec()
        except Exception as e:
            logger.error(f"Error viewing fault: {str(e)}")
    
    def delete_fault(self, row):
        """Delete a fault from the database."""
        try:
            timestamp = self.table.item(row, 0).text()
            fault_type = self.table.item(row, 1).text()
            image_index = int(self.table.item(row, 2).text())
            
            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete this {fault_type} fault from {timestamp}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.parent.fault_db.delete_fault(timestamp, fault_type, image_index)
                self.load_faults()
        except Exception as e:
            logger.error(f"Error deleting fault: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to delete fault: {str(e)}")
    
    def export_to_csv(self):
        """Export faults to CSV file."""
        try:
            from PySide6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export to CSV", "", "CSV Files (*.csv)"
            )
            
            if file_path:
                faults = []
                for row in range(self.table.rowCount()):
                    fault_data = []
                    for col in range(5):
                        item = self.table.item(row, col)
                        fault_data.append(item.text() if item else "")
                    faults.append(fault_data)
                
                self.parent.fault_db.export_to_csv(file_path, faults)
                QMessageBox.information(self, "Success", "Data exported successfully!")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
    
    def clear_history(self):
        """Clear all fault history."""
        try:
            reply = QMessageBox.question(
                self, "Confirm Clear",
                "Are you sure you want to clear all fault history? This cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.parent.fault_db.clear_all_faults()
                self.load_faults()
        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to clear history: {str(e)}") 