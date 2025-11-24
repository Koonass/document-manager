#!/usr/bin/env python3
"""
Database Manager - Handle SQLite database operations for tracking processed files
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "document_manager.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Table for CSV data
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS csv_imports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        filename TEXT,
                        record_count INTEGER
                    )
                ''')

                # Table for PDF processing log
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS processed_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sales_order TEXT NOT NULL,
                        pdf_path TEXT NOT NULL,
                        processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        csv_import_id INTEGER,
                        status TEXT DEFAULT 'processed',
                        FOREIGN KEY (csv_import_id) REFERENCES csv_imports (id),
                        UNIQUE(sales_order, pdf_path)
                    )
                ''')

                # Table for correlations (temporary storage before processing)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS correlations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sales_order TEXT NOT NULL,
                        pdf_path TEXT NOT NULL,
                        csv_data TEXT,
                        correlation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_processed BOOLEAN DEFAULT FALSE
                    )
                ''')

                # Index for faster lookups
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_sales_order
                    ON processed_files(sales_order)
                ''')

                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_processed_date
                    ON processed_files(processed_date)
                ''')

                conn.commit()
                logging.info("Database initialized successfully")

        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            raise

    def store_csv_data(self, csv_data: pd.DataFrame, filename: str = "unknown") -> int:
        """Store CSV import information and return import ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO csv_imports (filename, record_count)
                    VALUES (?, ?)
                ''', (filename, len(csv_data)))

                import_id = cursor.lastrowid
                conn.commit()

                logging.info(f"Stored CSV import info: {filename} with {len(csv_data)} records")
                return import_id

        except Exception as e:
            logging.error(f"Failed to store CSV data: {e}")
            raise

    def is_processed(self, sales_order: str, pdf_path: str) -> bool:
        """Check if a sales order/PDF combination has been processed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT COUNT(*) FROM processed_files
                    WHERE sales_order = ? AND pdf_path = ?
                ''', (sales_order, pdf_path))

                count = cursor.fetchone()[0]
                return count > 0

        except Exception as e:
            logging.error(f"Error checking processed status: {e}")
            return False

    def mark_as_processed(self, sales_order: str, pdf_path: str, csv_import_id: Optional[int] = None):
        """Mark a sales order/PDF combination as processed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT OR REPLACE INTO processed_files
                    (sales_order, pdf_path, csv_import_id, status)
                    VALUES (?, ?, ?, 'processed')
                ''', (sales_order, pdf_path, csv_import_id))

                conn.commit()
                logging.info(f"Marked as processed: {sales_order} -> {pdf_path}")

        except Exception as e:
            logging.error(f"Failed to mark as processed: {e}")
            raise

    def get_processed_files(self, days_back: int = 30) -> List[Dict]:
        """Get list of processed files from the last N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT sales_order, pdf_path, processed_date, status
                    FROM processed_files
                    WHERE processed_date >= datetime('now', '-{} days')
                    ORDER BY processed_date DESC
                '''.format(days_back))

                rows = cursor.fetchall()
                return [
                    {
                        'sales_order': row[0],
                        'pdf_path': row[1],
                        'processed_date': row[2],
                        'status': row[3]
                    }
                    for row in rows
                ]

        except Exception as e:
            logging.error(f"Error retrieving processed files: {e}")
            return []

    def get_unprocessed_correlations(self) -> List[Dict]:
        """Get all unprocessed correlations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT sales_order, pdf_path, csv_data, correlation_date
                    FROM correlations
                    WHERE is_processed = FALSE
                    ORDER BY correlation_date DESC
                ''')

                rows = cursor.fetchall()
                return [
                    {
                        'sales_order': row[0],
                        'pdf_path': row[1],
                        'csv_data': row[2],
                        'correlation_date': row[3]
                    }
                    for row in rows
                ]

        except Exception as e:
            logging.error(f"Error retrieving unprocessed correlations: {e}")
            return []

    def store_correlation(self, sales_order: str, pdf_path: str, csv_data: str):
        """Store a correlation temporarily"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT OR REPLACE INTO correlations
                    (sales_order, pdf_path, csv_data, is_processed)
                    VALUES (?, ?, ?, FALSE)
                ''', (sales_order, pdf_path, csv_data))

                conn.commit()

        except Exception as e:
            logging.error(f"Failed to store correlation: {e}")

    def mark_correlation_processed(self, sales_order: str, pdf_path: str):
        """Mark a correlation as processed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE correlations
                    SET is_processed = TRUE
                    WHERE sales_order = ? AND pdf_path = ?
                ''', (sales_order, pdf_path))

                conn.commit()

        except Exception as e:
            logging.error(f"Failed to mark correlation as processed: {e}")

    def get_statistics(self) -> Dict:
        """Get processing statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total processed files
                cursor.execute('SELECT COUNT(*) FROM processed_files')
                total_processed = cursor.fetchone()[0]

                # Files processed today
                cursor.execute('''
                    SELECT COUNT(*) FROM processed_files
                    WHERE DATE(processed_date) = DATE('now')
                ''')
                processed_today = cursor.fetchone()[0]

                # Total CSV imports
                cursor.execute('SELECT COUNT(*) FROM csv_imports')
                total_imports = cursor.fetchone()[0]

                # Pending correlations
                cursor.execute('SELECT COUNT(*) FROM correlations WHERE is_processed = FALSE')
                pending_correlations = cursor.fetchone()[0]

                return {
                    'total_processed': total_processed,
                    'processed_today': processed_today,
                    'total_imports': total_imports,
                    'pending_correlations': pending_correlations
                }

        except Exception as e:
            logging.error(f"Error getting statistics: {e}")
            return {
                'total_processed': 0,
                'processed_today': 0,
                'total_imports': 0,
                'pending_correlations': 0
            }

    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old processed files data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    DELETE FROM processed_files
                    WHERE processed_date < datetime('now', '-{} days')
                '''.format(days_to_keep))

                deleted_count = cursor.rowcount
                conn.commit()

                logging.info(f"Cleaned up {deleted_count} old records")
                return deleted_count

        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
            return 0