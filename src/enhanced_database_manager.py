#!/usr/bin/env python3
"""
Enhanced Database Manager - Updated schema for new workflow and archival system
"""

import sqlite3
import pandas as pd
import logging
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

class EnhancedDatabaseManager:
    def __init__(self, db_path: str = "document_manager_v2.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables with enhanced schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Orders table - stores CSV order data
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_number TEXT UNIQUE NOT NULL,
                        customer TEXT,
                        job_reference TEXT,
                        designer TEXT,
                        order_date DATE,
                        csv_data TEXT,  -- JSON dump of all CSV columns
                        import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                ''')

                # PDF files table - tracks all PDF files (active and archived)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pdf_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_number TEXT NOT NULL,
                        original_path TEXT NOT NULL,
                        current_path TEXT,  -- NULL if archived/removed
                        archive_path TEXT,  -- Path in archive folder
                        file_size INTEGER,
                        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        archived_date TIMESTAMP,
                        status TEXT DEFAULT 'active',  -- active, archived, removed
                        assignment_type TEXT DEFAULT 'auto',  -- auto, manual
                        FOREIGN KEY (order_number) REFERENCES orders (order_number)
                    )
                ''')

                # CSV files table - tracks BisTrack material import CSVs
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS csv_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_number TEXT NOT NULL,
                        original_path TEXT NOT NULL,
                        current_path TEXT,  -- NULL if archived/removed
                        archive_path TEXT,  -- Path in archive folder
                        file_size INTEGER,
                        material_count INTEGER DEFAULT 0,  -- Number of material lines
                        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        validated_date TIMESTAMP,
                        uploaded_date TIMESTAMP,
                        archived_date TIMESTAMP,
                        status TEXT DEFAULT 'pending',  -- pending, validated, uploaded, archived
                        validation_status TEXT DEFAULT 'not_validated',  -- not_validated, valid, has_errors, has_warnings
                        validation_errors TEXT,  -- JSON array of validation errors
                        assignment_type TEXT DEFAULT 'auto',  -- auto, manual
                        FOREIGN KEY (order_number) REFERENCES orders (order_number)
                    )
                ''')

                # Processing log - tracks sync operations and processing history
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS processing_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        operation_type TEXT NOT NULL,  -- sync, archive, manual_assign
                        order_number TEXT,
                        pdf_path TEXT,
                        details TEXT,  -- JSON details about the operation
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        success BOOLEAN DEFAULT TRUE
                    )
                ''')

                # Search history - tracks user searches
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS search_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        search_term TEXT NOT NULL,
                        search_type TEXT DEFAULT 'general',  -- general, order, customer
                        results_count INTEGER DEFAULT 0,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Settings table - application configuration
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS app_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Create indexes for better performance
                indexes = [
                    'CREATE INDEX IF NOT EXISTS idx_order_number ON orders(order_number)',
                    'CREATE INDEX IF NOT EXISTS idx_customer ON orders(customer)',
                    'CREATE INDEX IF NOT EXISTS idx_pdf_order_number ON pdf_files(order_number)',
                    'CREATE INDEX IF NOT EXISTS idx_pdf_status ON pdf_files(status)',
                    'CREATE INDEX IF NOT EXISTS idx_csv_order_number ON csv_files(order_number)',
                    'CREATE INDEX IF NOT EXISTS idx_csv_status ON csv_files(status)',
                    'CREATE INDEX IF NOT EXISTS idx_csv_validation_status ON csv_files(validation_status)',
                    'CREATE INDEX IF NOT EXISTS idx_processing_timestamp ON processing_log(timestamp)',
                    'CREATE INDEX IF NOT EXISTS idx_search_timestamp ON search_history(timestamp)'
                ]

                for index_sql in indexes:
                    cursor.execute(index_sql)

                conn.commit()
                logging.info("Enhanced database initialized successfully")

        except Exception as e:
            logging.error(f"Enhanced database initialization failed: {e}")
            raise

    def store_orders_from_csv(self, csv_data: pd.DataFrame) -> int:
        """Store order data from CSV file"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                orders_added = 0
                orders_updated = 0

                for _, row in csv_data.iterrows():
                    row_dict = row.to_dict()

                    # Extract key fields (adjust column names as needed)
                    order_number = str(row_dict.get('OrderNumber', ''))
                    customer = row_dict.get('Customer', '')
                    job_reference = row_dict.get('JobReference', '')
                    designer = row_dict.get('Designer', '')

                    # Try to parse order date
                    order_date = None
                    for date_col in ['OrderDate', 'Date', 'order_date']:
                        if date_col in row_dict and pd.notna(row_dict[date_col]):
                            try:
                                order_date = pd.to_datetime(row_dict[date_col]).strftime('%Y-%m-%d')
                                break
                            except:
                                pass

                    # Store full CSV data as JSON
                    csv_data_json = json.dumps(row_dict, default=str)

                    # Insert or update order
                    cursor.execute('''
                        INSERT OR REPLACE INTO orders
                        (order_number, customer, job_reference, designer, order_date, csv_data, import_date)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (order_number, customer, job_reference, designer, order_date, csv_data_json))

                    if cursor.rowcount > 0:
                        orders_added += 1

                # Log the import
                cursor.execute('''
                    INSERT INTO processing_log (operation_type, details)
                    VALUES ('csv_import', ?)
                ''', (json.dumps({
                    'orders_processed': len(csv_data),
                    'orders_added': orders_added
                }),))

                conn.commit()
                logging.info(f"Stored {orders_added} orders from CSV")
                return orders_added

        except Exception as e:
            logging.error(f"Failed to store CSV orders: {e}")
            raise

    def assign_pdf_to_order(self, order_number: str, pdf_path: str, assignment_type: str = 'auto') -> bool:
        """Assign a PDF file to an order"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if order exists
                cursor.execute('SELECT id FROM orders WHERE order_number = ?', (order_number,))
                if not cursor.fetchone():
                    logging.warning(f"Order {order_number} not found in database")
                    return False

                # Get file size
                file_size = 0
                try:
                    file_size = Path(pdf_path).stat().st_size
                except:
                    pass

                # Insert PDF record
                cursor.execute('''
                    INSERT OR REPLACE INTO pdf_files
                    (order_number, original_path, current_path, file_size, assignment_type, status)
                    VALUES (?, ?, ?, ?, ?, 'active')
                ''', (order_number, pdf_path, pdf_path, file_size, assignment_type))

                # Log the assignment
                cursor.execute('''
                    INSERT INTO processing_log (operation_type, order_number, details)
                    VALUES ('pdf_assign', ?, ?)
                ''', (order_number, json.dumps({
                    'pdf_path': pdf_path,
                    'assignment_type': assignment_type,
                    'file_size': file_size
                })))

                conn.commit()
                return True

        except Exception as e:
            logging.error(f"Failed to assign PDF {pdf_path} to order {order_number}: {e}")
            return False

    def get_orders_with_pdf_status(self) -> List[Dict]:
        """Get all active orders with their PDF status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT
                        o.order_number,
                        o.customer,
                        o.job_reference,
                        o.designer,
                        o.order_date,
                        o.csv_data,
                        p.current_path as pdf_path,
                        p.status as pdf_status,
                        CASE WHEN p.id IS NOT NULL THEN 1 ELSE 0 END as has_pdf
                    FROM orders o
                    LEFT JOIN pdf_files p ON o.order_number = p.order_number
                        AND p.status = 'active'
                    WHERE o.is_active = 1
                    ORDER BY o.order_number
                ''')

                results = []
                for row in cursor.fetchall():
                    # Parse CSV data JSON
                    csv_data = {}
                    try:
                        csv_data = json.loads(row[5]) if row[5] else {}
                    except:
                        pass

                    result = {
                        'order_number': row[0],
                        'customer': row[1],
                        'job_reference': row[2],
                        'designer': row[3],
                        'order_date': row[4],
                        'csv_data': csv_data,
                        'pdf_path': row[6],
                        'pdf_status': row[7],
                        'has_pdf': bool(row[8])
                    }
                    results.append(result)

                return results

        except Exception as e:
            logging.error(f"Failed to get orders with PDF status: {e}")
            return []

    def archive_pdf(self, order_number: str, original_path: str, archive_path: str) -> bool:
        """Mark a PDF as archived and update its path"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE pdf_files
                    SET archive_path = ?,
                        current_path = NULL,
                        status = 'archived',
                        archived_date = CURRENT_TIMESTAMP
                    WHERE order_number = ? AND original_path = ?
                ''', (archive_path, order_number, original_path))

                if cursor.rowcount > 0:
                    # Log the archival
                    cursor.execute('''
                        INSERT INTO processing_log (operation_type, order_number, details)
                        VALUES ('archive', ?, ?)
                    ''', (order_number, json.dumps({
                        'original_path': original_path,
                        'archive_path': archive_path,
                        'archived_date': datetime.now().isoformat()
                    })))

                    conn.commit()
                    return True

                return False

        except Exception as e:
            logging.error(f"Failed to archive PDF {original_path}: {e}")
            return False

    def search_orders(self, search_term: str, search_type: str = 'general') -> List[Dict]:
        """Search orders by various criteria"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Log the search
                cursor.execute('''
                    INSERT INTO search_history (search_term, search_type)
                    VALUES (?, ?)
                ''', (search_term, search_type))

                # Perform the search
                search_pattern = f'%{search_term}%'

                if search_type == 'order':
                    search_sql = '''
                        SELECT * FROM orders
                        WHERE order_number LIKE ?
                        ORDER BY order_number
                    '''
                    cursor.execute(search_sql, (search_pattern,))

                elif search_type == 'customer':
                    search_sql = '''
                        SELECT * FROM orders
                        WHERE customer LIKE ?
                        ORDER BY customer, order_number
                    '''
                    cursor.execute(search_sql, (search_pattern,))

                else:  # general search
                    search_sql = '''
                        SELECT * FROM orders
                        WHERE order_number LIKE ?
                           OR customer LIKE ?
                           OR job_reference LIKE ?
                           OR designer LIKE ?
                           OR csv_data LIKE ?
                        ORDER BY order_number
                    '''
                    cursor.execute(search_sql, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))

                results = []
                for row in cursor.fetchall():
                    csv_data = {}
                    try:
                        csv_data = json.loads(row[6]) if row[6] else {}
                    except:
                        pass

                    result = {
                        'id': row[0],
                        'order_number': row[1],
                        'customer': row[2],
                        'job_reference': row[3],
                        'designer': row[4],
                        'order_date': row[5],
                        'csv_data': csv_data,
                        'import_date': row[7],
                        'is_active': bool(row[8])
                    }
                    results.append(result)

                # Update search history with results count
                cursor.execute('''
                    UPDATE search_history
                    SET results_count = ?
                    WHERE id = last_insert_rowid()
                ''', (len(results),))

                conn.commit()
                return results

        except Exception as e:
            logging.error(f"Search failed for term '{search_term}': {e}")
            return []

    def get_processing_statistics(self) -> Dict:
        """Get comprehensive processing statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                stats = {}

                # Order statistics
                cursor.execute('SELECT COUNT(*) FROM orders WHERE is_active = 1')
                stats['active_orders'] = cursor.fetchone()[0]

                # PDF statistics
                cursor.execute('SELECT status, COUNT(*) FROM pdf_files GROUP BY status')
                pdf_stats = dict(cursor.fetchall())
                stats['pdfs_active'] = pdf_stats.get('active', 0)
                stats['pdfs_archived'] = pdf_stats.get('archived', 0)

                # Matching statistics
                cursor.execute('''
                    SELECT
                        COUNT(DISTINCT o.order_number) as total_orders,
                        COUNT(DISTINCT p.order_number) as orders_with_pdf
                    FROM orders o
                    LEFT JOIN pdf_files p ON o.order_number = p.order_number AND p.status = 'active'
                    WHERE o.is_active = 1
                ''')
                matching_stats = cursor.fetchone()
                stats['total_orders'] = matching_stats[0]
                stats['orders_with_pdf'] = matching_stats[1]
                stats['orders_without_pdf'] = matching_stats[0] - matching_stats[1]

                # Recent activity
                cursor.execute('''
                    SELECT COUNT(*) FROM processing_log
                    WHERE timestamp >= datetime('now', '-24 hours')
                ''')
                stats['operations_today'] = cursor.fetchone()[0]

                # Search activity
                cursor.execute('''
                    SELECT COUNT(*) FROM search_history
                    WHERE timestamp >= datetime('now', '-7 days')
                ''')
                stats['searches_this_week'] = cursor.fetchone()[0]

                return stats

        except Exception as e:
            logging.error(f"Failed to get statistics: {e}")
            return {}

    def cleanup_old_data(self, days_to_keep: int = 90) -> Dict:
        """Clean up old data and return cleanup statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cleanup_stats = {}

                # Clean old processing logs
                cursor.execute('''
                    DELETE FROM processing_log
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days_to_keep))
                cleanup_stats['processing_logs_removed'] = cursor.rowcount

                # Clean old search history
                cursor.execute('''
                    DELETE FROM search_history
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days_to_keep))
                cleanup_stats['searches_removed'] = cursor.rowcount

                # Mark old orders as inactive (don't delete for historical purposes)
                cursor.execute('''
                    UPDATE orders
                    SET is_active = 0
                    WHERE import_date < datetime('now', '-{} days')
                    AND is_active = 1
                '''.format(days_to_keep * 2))  # Keep orders longer than logs
                cleanup_stats['orders_deactivated'] = cursor.rowcount

                conn.commit()

                logging.info(f"Cleanup completed: {cleanup_stats}")
                return cleanup_stats

        except Exception as e:
            logging.error(f"Cleanup failed: {e}")
            return {}

    def export_data(self, export_path: str, include_archived: bool = True) -> bool:
        """Export all data to CSV for backup purposes"""
        try:
            import csv

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Export orders
                orders_file = Path(export_path) / 'orders_export.csv'
                cursor.execute('SELECT * FROM orders')
                orders_data = cursor.fetchall()

                with open(orders_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Write header
                    writer.writerow(['id', 'order_number', 'customer', 'job_reference',
                                   'designer', 'order_date', 'csv_data', 'import_date', 'is_active'])
                    writer.writerows(orders_data)

                # Export PDF files
                pdf_file = Path(export_path) / 'pdf_files_export.csv'
                if include_archived:
                    cursor.execute('SELECT * FROM pdf_files')
                else:
                    cursor.execute('SELECT * FROM pdf_files WHERE status = "active"')

                pdf_data = cursor.fetchall()
                with open(pdf_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['id', 'order_number', 'original_path', 'current_path',
                                   'archive_path', 'file_size', 'added_date', 'archived_date',
                                   'status', 'assignment_type'])
                    writer.writerows(pdf_data)

                logging.info(f"Data exported to {export_path}")
                return True

        except Exception as e:
            logging.error(f"Data export failed: {e}")
            return False

    # ========== CSV File Management Methods ==========

    def assign_csv_to_order(self, order_number: str, csv_path: str, material_count: int = 0,
                           assignment_type: str = 'auto') -> bool:
        """Assign a CSV file to an order"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if order exists, create if not
                cursor.execute('SELECT id FROM orders WHERE order_number = ?', (order_number,))
                if not cursor.fetchone():
                    # Create order record
                    cursor.execute('''
                        INSERT INTO orders (order_number, import_date)
                        VALUES (?, CURRENT_TIMESTAMP)
                    ''', (order_number,))

                # Get file size
                file_size = 0
                try:
                    file_size = Path(csv_path).stat().st_size
                except:
                    pass

                # Insert or update CSV record
                cursor.execute('''
                    INSERT OR REPLACE INTO csv_files
                    (order_number, original_path, current_path, file_size, material_count,
                     assignment_type, status, validation_status)
                    VALUES (?, ?, ?, ?, ?, ?, 'pending', 'not_validated')
                ''', (order_number, csv_path, csv_path, file_size, material_count, assignment_type))

                # Log the assignment
                cursor.execute('''
                    INSERT INTO processing_log (operation_type, order_number, details)
                    VALUES ('csv_assign', ?, ?)
                ''', (order_number, json.dumps({
                    'csv_path': csv_path,
                    'assignment_type': assignment_type,
                    'file_size': file_size,
                    'material_count': material_count
                })))

                conn.commit()
                logging.info(f"Assigned CSV {Path(csv_path).name} to order {order_number}")
                return True

        except Exception as e:
            logging.error(f"Failed to assign CSV {csv_path} to order {order_number}: {e}")
            return False

    def update_csv_validation(self, csv_path: str, validation_status: str,
                             validation_errors: List = None) -> bool:
        """Update CSV validation status and errors"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                errors_json = json.dumps(validation_errors) if validation_errors else None

                cursor.execute('''
                    UPDATE csv_files
                    SET validation_status = ?,
                        validation_errors = ?,
                        validated_date = CURRENT_TIMESTAMP
                    WHERE current_path = ?
                ''', (validation_status, errors_json, csv_path))

                conn.commit()
                logging.info(f"Updated validation status for {Path(csv_path).name}: {validation_status}")
                return True

        except Exception as e:
            logging.error(f"Failed to update CSV validation: {e}")
            return False

    def mark_csv_uploaded(self, csv_path: str) -> bool:
        """Mark CSV as uploaded to BisTrack"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE csv_files
                    SET status = 'uploaded',
                        uploaded_date = CURRENT_TIMESTAMP
                    WHERE current_path = ?
                ''', (csv_path,))

                # Log the upload
                cursor.execute('SELECT order_number FROM csv_files WHERE current_path = ?', (csv_path,))
                result = cursor.fetchone()
                if result:
                    order_number = result[0]
                    cursor.execute('''
                        INSERT INTO processing_log (operation_type, order_number, details)
                        VALUES ('csv_upload', ?, ?)
                    ''', (order_number, json.dumps({
                        'csv_path': csv_path,
                        'status': 'uploaded'
                    })))

                conn.commit()
                logging.info(f"Marked CSV {Path(csv_path).name} as uploaded")
                return True

        except Exception as e:
            logging.error(f"Failed to mark CSV as uploaded: {e}")
            return False

    def archive_csv(self, order_number: str, original_path: str, archive_path: str) -> bool:
        """Archive a CSV file"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE csv_files
                    SET current_path = NULL,
                        archive_path = ?,
                        status = 'archived',
                        archived_date = CURRENT_TIMESTAMP
                    WHERE order_number = ? AND original_path = ?
                ''', (archive_path, order_number, original_path))

                # Log the archive operation
                cursor.execute('''
                    INSERT INTO processing_log (operation_type, order_number, details)
                    VALUES ('csv_archive', ?, ?)
                ''', (order_number, json.dumps({
                    'original_path': original_path,
                    'archive_path': archive_path
                })))

                conn.commit()
                logging.info(f"Archived CSV for order {order_number}")
                return True

        except Exception as e:
            logging.error(f"Failed to archive CSV: {e}")
            return False

    def get_csv_files_by_order(self, order_number: str) -> List[Dict]:
        """Get all CSV files for a specific order"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT id, original_path, current_path, archive_path, file_size,
                           material_count, status, validation_status, validation_errors,
                           added_date, validated_date, uploaded_date, archived_date
                    FROM csv_files
                    WHERE order_number = ?
                    ORDER BY added_date DESC
                ''', (order_number,))

                rows = cursor.fetchall()
                csv_files = []
                for row in rows:
                    csv_files.append({
                        'id': row[0],
                        'original_path': row[1],
                        'current_path': row[2],
                        'archive_path': row[3],
                        'file_size': row[4],
                        'material_count': row[5],
                        'status': row[6],
                        'validation_status': row[7],
                        'validation_errors': json.loads(row[8]) if row[8] else None,
                        'added_date': row[9],
                        'validated_date': row[10],
                        'uploaded_date': row[11],
                        'archived_date': row[12]
                    })

                return csv_files

        except Exception as e:
            logging.error(f"Failed to get CSV files for order {order_number}: {e}")
            return []

    def get_pending_csv_files(self) -> List[Dict]:
        """Get all CSV files pending validation or upload"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT c.id, c.order_number, c.current_path, c.material_count,
                           c.status, c.validation_status, c.validation_errors, c.added_date
                    FROM csv_files c
                    WHERE c.status IN ('pending', 'validated')
                    AND c.current_path IS NOT NULL
                    ORDER BY c.added_date DESC
                ''')

                rows = cursor.fetchall()
                csv_files = []
                for row in rows:
                    csv_files.append({
                        'id': row[0],
                        'order_number': row[1],
                        'current_path': row[2],
                        'material_count': row[3],
                        'status': row[4],
                        'validation_status': row[5],
                        'validation_errors': json.loads(row[6]) if row[6] else None,
                        'added_date': row[7]
                    })

                return csv_files

        except Exception as e:
            logging.error(f"Failed to get pending CSV files: {e}")
            return []