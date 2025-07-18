

import sqlite3
import csv
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FaultDatabase:
    """Handles fault logging and database operations."""
    
    def __init__(self, database_path="faults.db"):
        """
        Initialize fault database.
        
        Args:
            database_path (str): Path to the SQLite database file
        """
        self.database_path = database_path
        self.init_database()
        logger.info(f"Fault database initialized: {database_path}")

    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faults (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                fault_type TEXT,
                image_index INTEGER,
                details TEXT,
                measurement REAL
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database tables initialized")

    def log_fault(self, fault_type, image_index, details, measurement=None):
        """
        Log a fault to the database.
        
        Args:
            fault_type (str): Type of fault (e.g., "Nail", "Board Alignment")
            image_index (int): Index of the image where fault was detected
            details (str): Detailed description of the fault
            measurement (float, optional): Measurement value if applicable
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO faults (timestamp, fault_type, image_index, details, measurement)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
              fault_type, image_index, details, measurement))
        conn.commit()
        conn.close()
        logger.info(f"Fault logged: {fault_type} - {details}")

    def get_faults(self, start_date=None, end_date=None, fault_type=None):
        """
        Retrieve faults from database with optional filtering.
        
        Args:
            start_date (str, optional): Start date filter (YYYY-MM-DD)
            end_date (str, optional): End date filter (YYYY-MM-DD)
            fault_type (str, optional): Fault type filter
            
        Returns:
            list: List of fault records
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        
        query = "SELECT timestamp, fault_type, image_index, details, measurement FROM faults WHERE 1=1"
        params = []
        
        # Apply date filters
        if start_date:
            query += " AND timestamp >= ?"
            params.append(f"{start_date} 00:00:00")
        if end_date:
            query += " AND timestamp <= ?"
            params.append(f"{end_date} 23:59:59")
            
        
        if fault_type and fault_type != "All":
            query += " AND fault_type = ?"
            params.append(fault_type)
            
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        faults = cursor.fetchall()
        conn.close()
        
        logger.info(f"Retrieved {len(faults)} faults from database")
        return faults

    def get_statistics(self, faults):
        """
        Calculate statistics from fault data.
        
        Args:
            faults (list): List of fault records
            
        Returns:
            dict: Statistics including total faults and counts by type
        """
        total_faults = len(faults)
        nail_faults = sum(1 for f in faults if f[1] == "Nail")
        board_faults = sum(1 for f in faults if f[1] == "Board Alignment")
        
        return {
            'total_faults': total_faults,
            'nail_faults': nail_faults,
            'board_faults': board_faults
        }

    def delete_fault(self, timestamp, fault_type, image_index):
        """
        Delete a specific fault from the database.
        
        Args:
            timestamp (str): Timestamp of the fault
            fault_type (str): Type of the fault
            image_index (int): Image index of the fault
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM faults WHERE timestamp = ? AND fault_type = ? AND image_index = ?",
            (timestamp, fault_type, image_index)
        )
        conn.commit()
        conn.close()
        logger.info(f"Deleted fault: {fault_type} at {timestamp}")

    def clear_all_faults(self):
        """Clear all faults from the database."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM faults")
        conn.commit()
        conn.close()
        logger.info("All faults cleared from database")

    def export_to_csv(self, file_path, faults):
        """
        Export faults to CSV file.
        
        Args:
            file_path (str): Path to save the CSV file
            faults (list): List of fault records to export
        """
        try:
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
               
                writer.writerow(["Timestamp", "Type", "Image", "Details", "Measurement"])
                
                
                for fault in faults:
                    writer.writerow([
                        fault[0],  # timestamp
                        fault[1],  # type
                        fault[2],  # image
                        fault[3],  # details
                        fault[4] if fault[4] is not None else ""  
                    ])
            
            logger.info(f"Faults exported to CSV: {file_path}")
        except Exception as e:
            logger.error(f"Failed to export faults to CSV: {str(e)}")
            raise 