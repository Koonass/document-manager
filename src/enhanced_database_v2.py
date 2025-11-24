#!/usr/bin/env python3
"""
Enhanced Database Manager V2 - Updated with relationship tracking
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import uuid

class EnhancedDatabaseV2:
    def __init__(self, db_path: str = "document_manager_v2.1.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables with relationship tracking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Enable WAL mode for better concurrent access on network shares
                conn.execute("PRAGMA journal_mode=WAL")
                cursor = conn.cursor()

                # Relationships table - core table linking CSV orders to PDFs with unique IDs
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS relationships (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        relationship_id TEXT UNIQUE NOT NULL,
                        order_number TEXT NOT NULL,
                        csv_data TEXT NOT NULL,  -- JSON dump of CSV row data
                        pdf_path TEXT,  -- Current PDF path (NULL if no PDF attached)
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        processed BOOLEAN DEFAULT FALSE,
                        processed_date TIMESTAMP
                    )
                ''')

                # PDF change history - tracks all PDF attachments/replacements
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pdf_change_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        relationship_id TEXT NOT NULL,
                        action TEXT NOT NULL,  -- 'attach', 'replace', 'remove'
                        old_pdf_path TEXT,
                        new_pdf_path TEXT,
                        reason TEXT,  -- 'automatic_matching', 'manual_attachment', etc.
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (relationship_id) REFERENCES relationships (relationship_id)
                    )
                ''')

                # Processing log - tracks sync operations and other activities
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS processing_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        operation_type TEXT NOT NULL,  -- 'sync', 'csv_import', 'pdf_match', etc.
                        relationship_id TEXT,
                        order_number TEXT,
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
                        search_type TEXT DEFAULT 'general',
                        results_count INTEGER DEFAULT 0,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Archive tracking - tracks PDFs moved to archive
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS archive_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        relationship_id TEXT NOT NULL,
                        original_path TEXT NOT NULL,
                        archive_path TEXT NOT NULL,
                        archive_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata_path TEXT,  -- Path to metadata file
                        FOREIGN KEY (relationship_id) REFERENCES relationships (relationship_id)
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

                # Create indexes for performance
                indexes = [
                    'CREATE INDEX IF NOT EXISTS idx_rel_id ON relationships(relationship_id)',
                    'CREATE INDEX IF NOT EXISTS idx_order_number ON relationships(order_number)',
                    'CREATE INDEX IF NOT EXISTS idx_rel_active ON relationships(is_active)',
                    'CREATE INDEX IF NOT EXISTS idx_pdf_history_rel ON pdf_change_history(relationship_id)',
                    'CREATE INDEX IF NOT EXISTS idx_processing_timestamp ON processing_log(timestamp)',
                    'CREATE INDEX IF NOT EXISTS idx_search_timestamp ON search_history(timestamp)',
                    'CREATE INDEX IF NOT EXISTS idx_archive_rel ON archive_log(relationship_id)'
                ]

                for index_sql in indexes:
                    cursor.execute(index_sql)

                # Create triggers to auto-update timestamps
                cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS update_relationship_timestamp
                    AFTER UPDATE ON relationships
                    FOR EACH ROW
                    BEGIN
                        UPDATE relationships
                        SET updated_date = CURRENT_TIMESTAMP
                        WHERE relationship_id = NEW.relationship_id;
                    END
                ''')

                conn.commit()

                # Migrate existing databases - add processed columns if they don't exist
                try:
                    cursor.execute("PRAGMA table_info(relationships)")
                    columns = [col[1] for col in cursor.fetchall()]

                    if 'processed' not in columns:
                        cursor.execute('ALTER TABLE relationships ADD COLUMN processed BOOLEAN DEFAULT FALSE')
                        logging.info("Added 'processed' column to relationships table")

                    if 'processed_date' not in columns:
                        cursor.execute('ALTER TABLE relationships ADD COLUMN processed_date TIMESTAMP')
                        logging.info("Added 'processed_date' column to relationships table")

                    conn.commit()
                except Exception as migrate_error:
                    logging.warning(f"Migration warning (may be normal if columns exist): {migrate_error}")

                logging.info("Enhanced database V2 initialized successfully")

        except Exception as e:
            logging.error(f"Enhanced database V2 initialization failed: {e}")
            raise

    def store_relationship(self, relationship_data: Dict) -> bool:
        """Store a new relationship record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT OR REPLACE INTO relationships
                    (relationship_id, order_number, csv_data, pdf_path)
                    VALUES (?, ?, ?, ?)
                ''', (
                    relationship_data['relationship_id'],
                    relationship_data['order_number'],
                    json.dumps(relationship_data['csv_data'], default=str),
                    relationship_data.get('pdf_path')
                ))

                # Log the operation
                cursor.execute('''
                    INSERT INTO processing_log (operation_type, relationship_id, order_number, details)
                    VALUES ('relationship_created', ?, ?, ?)
                ''', (
                    relationship_data['relationship_id'],
                    relationship_data['order_number'],
                    json.dumps({'action': 'new_relationship'})
                ))

                conn.commit()
                return True

        except Exception as e:
            logging.error(f"Failed to store relationship: {e}")
            return False

    def get_relationship(self, relationship_id: str) -> Optional[Dict]:
        """Get relationship by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT relationship_id, order_number, csv_data, pdf_path,
                           created_date, updated_date, is_active, processed, processed_date
                    FROM relationships
                    WHERE relationship_id = ? AND is_active = TRUE
                ''', (relationship_id,))

                row = cursor.fetchone()
                if not row:
                    return None

                # Get PDF change history
                cursor.execute('''
                    SELECT action, old_pdf_path, new_pdf_path, reason, timestamp
                    FROM pdf_change_history
                    WHERE relationship_id = ?
                    ORDER BY timestamp DESC
                ''', (relationship_id,))

                pdf_changes = []
                for change_row in cursor.fetchall():
                    pdf_changes.append({
                        'action': change_row[0],
                        'old_pdf_path': change_row[1],
                        'new_pdf_path': change_row[2],
                        'reason': change_row[3],
                        'timestamp': change_row[4]
                    })

                return {
                    'relationship_id': row[0],
                    'order_number': row[1],
                    'csv_data': json.loads(row[2]) if row[2] else {},
                    'pdf_path': row[3],
                    'created_date': row[4],
                    'updated_date': row[5],
                    'is_active': bool(row[6]),
                    'processed': bool(row[7]) if row[7] is not None else False,
                    'processed_date': row[8],
                    'pdf_changes': pdf_changes
                }

        except Exception as e:
            logging.error(f"Failed to get relationship {relationship_id}: {e}")
            return None

    def get_relationship_by_order(self, order_number: str) -> Optional[Dict]:
        """Get relationship by order number"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT relationship_id
                    FROM relationships
                    WHERE order_number = ? AND is_active = TRUE
                    ORDER BY created_date DESC
                    LIMIT 1
                ''', (order_number,))

                row = cursor.fetchone()
                if row:
                    return self.get_relationship(row[0])
                return None

        except Exception as e:
            logging.error(f"Failed to get relationship for order {order_number}: {e}")
            return None

    def update_relationship(self, relationship_id: str, update_data: Dict) -> bool:
        """Update relationship data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Build update query dynamically
                update_fields = []
                update_values = []

                if 'csv_data' in update_data:
                    update_fields.append('csv_data = ?')
                    update_values.append(json.dumps(update_data['csv_data'], default=str))

                if 'pdf_path' in update_data:
                    # Get current PDF path for history tracking
                    cursor.execute('SELECT pdf_path FROM relationships WHERE relationship_id = ?', (relationship_id,))
                    current_row = cursor.fetchone()
                    old_pdf_path = current_row[0] if current_row else None

                    # Update PDF path
                    update_fields.append('pdf_path = ?')
                    update_values.append(update_data['pdf_path'])

                    # Record the change
                    action = 'attach' if not old_pdf_path else 'replace'
                    if update_data['pdf_path'] is None:
                        action = 'remove'

                    cursor.execute('''
                        INSERT INTO pdf_change_history
                        (relationship_id, action, old_pdf_path, new_pdf_path, reason)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        relationship_id,
                        action,
                        old_pdf_path,
                        update_data['pdf_path'],
                        update_data.get('reason', 'unknown')
                    ))

                if 'processed' in update_data:
                    update_fields.append('processed = ?')
                    update_values.append(update_data['processed'])
                    if update_data['processed']:
                        update_fields.append('processed_date = CURRENT_TIMESTAMP')

                if 'processed_date' in update_data:
                    update_fields.append('processed_date = ?')
                    update_values.append(update_data['processed_date'])

                if update_fields:
                    update_values.append(relationship_id)
                    update_sql = f"UPDATE relationships SET {', '.join(update_fields)} WHERE relationship_id = ?"
                    cursor.execute(update_sql, update_values)

                    # Log the update
                    cursor.execute('''
                        INSERT INTO processing_log (operation_type, relationship_id, details)
                        VALUES ('relationship_updated', ?, ?)
                    ''', (relationship_id, json.dumps(update_data, default=str)))

                conn.commit()
                return True

        except Exception as e:
            logging.error(f"Failed to update relationship {relationship_id}: {e}")
            return False

    def get_all_relationships(self, include_inactive: bool = False) -> List[Dict]:
        """Get all relationships"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                where_clause = "" if include_inactive else "WHERE is_active = TRUE"
                cursor.execute(f'''
                    SELECT relationship_id, order_number, csv_data, pdf_path,
                           created_date, updated_date, is_active, processed, processed_date
                    FROM relationships
                    {where_clause}
                    ORDER BY order_number
                ''')

                relationships = []
                for row in cursor.fetchall():
                    relationships.append({
                        'relationship_id': row[0],
                        'order_number': row[1],
                        'csv_data': json.loads(row[2]) if row[2] else {},
                        'pdf_path': row[3],
                        'created_date': row[4],
                        'updated_date': row[5],
                        'is_active': bool(row[6]),
                        'processed': bool(row[7]) if row[7] is not None else False,
                        'processed_date': row[8]
                    })

                return relationships

        except Exception as e:
            logging.error(f"Failed to get all relationships: {e}")
            return []

    def search_relationships(self, search_term: str, search_type: str = 'general') -> List[Dict]:
        """Search relationships by various criteria"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Log the search
                cursor.execute('''
                    INSERT INTO search_history (search_term, search_type)
                    VALUES (?, ?)
                ''', (search_term, search_type))

                search_pattern = f'%{search_term}%'

                if search_type == 'order':
                    cursor.execute('''
                        SELECT relationship_id FROM relationships
                        WHERE order_number LIKE ? AND is_active = TRUE
                        ORDER BY order_number
                    ''', (search_pattern,))
                else:  # general search
                    cursor.execute('''
                        SELECT relationship_id FROM relationships
                        WHERE (order_number LIKE ? OR csv_data LIKE ?) AND is_active = TRUE
                        ORDER BY order_number
                    ''', (search_pattern, search_pattern))

                relationship_ids = [row[0] for row in cursor.fetchall()]

                # Get full relationship data
                results = []
                for rel_id in relationship_ids:
                    rel_data = self.get_relationship(rel_id)
                    if rel_data:
                        results.append(rel_data)

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

    def archive_relationship_pdf(self, relationship_id: str, original_path: str, archive_path: str, metadata_path: str = None) -> bool:
        """Mark a relationship's PDF as archived"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Record the archive operation
                cursor.execute('''
                    INSERT INTO archive_log (relationship_id, original_path, archive_path, metadata_path)
                    VALUES (?, ?, ?, ?)
                ''', (relationship_id, original_path, archive_path, metadata_path))

                # Update the relationship to remove current PDF path
                cursor.execute('''
                    UPDATE relationships
                    SET pdf_path = NULL
                    WHERE relationship_id = ?
                ''', (relationship_id,))

                # Log the archival in PDF change history
                cursor.execute('''
                    INSERT INTO pdf_change_history
                    (relationship_id, action, old_pdf_path, new_pdf_path, reason)
                    VALUES (?, 'archive', ?, ?, 'automated_archival')
                ''', (relationship_id, original_path, archive_path))

                conn.commit()
                return True

        except Exception as e:
            logging.error(f"Failed to archive PDF for relationship {relationship_id}: {e}")
            return False

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                stats = {}

                # Relationship statistics
                cursor.execute('SELECT COUNT(*) FROM relationships WHERE is_active = TRUE')
                stats['total_relationships'] = cursor.fetchone()[0]

                cursor.execute('SELECT COUNT(*) FROM relationships WHERE pdf_path IS NOT NULL AND is_active = TRUE')
                stats['relationships_with_pdf'] = cursor.fetchone()[0]

                stats['relationships_without_pdf'] = stats['total_relationships'] - stats['relationships_with_pdf']

                # PDF change statistics
                cursor.execute('SELECT COUNT(*) FROM pdf_change_history WHERE timestamp >= datetime("now", "-24 hours")')
                stats['pdf_changes_today'] = cursor.fetchone()[0]

                cursor.execute('SELECT COUNT(*) FROM pdf_change_history WHERE action = "attach"')
                stats['total_pdf_attachments'] = cursor.fetchone()[0]

                cursor.execute('SELECT COUNT(*) FROM pdf_change_history WHERE action = "replace"')
                stats['total_pdf_replacements'] = cursor.fetchone()[0]

                # Archive statistics
                cursor.execute('SELECT COUNT(*) FROM archive_log')
                stats['total_archived_pdfs'] = cursor.fetchone()[0]

                # Recent activity
                cursor.execute('SELECT COUNT(*) FROM processing_log WHERE timestamp >= datetime("now", "-24 hours")')
                stats['operations_today'] = cursor.fetchone()[0]

                # Search activity
                cursor.execute('SELECT COUNT(*) FROM search_history WHERE timestamp >= datetime("now", "-7 days")')
                stats['searches_this_week'] = cursor.fetchone()[0]

                return stats

        except Exception as e:
            logging.error(f"Failed to get statistics: {e}")
            return {}

    def cleanup_old_data(self, days_to_keep: int = 90) -> Dict:
        """Clean up old data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cleanup_stats = {}

                # Clean old processing logs
                cursor.execute(f'''
                    DELETE FROM processing_log
                    WHERE timestamp < datetime('now', '-{days_to_keep} days')
                ''')
                cleanup_stats['processing_logs_removed'] = cursor.rowcount

                # Clean old search history
                cursor.execute(f'''
                    DELETE FROM search_history
                    WHERE timestamp < datetime('now', '-{days_to_keep} days')
                ''')
                cleanup_stats['searches_removed'] = cursor.rowcount

                # Clean old PDF change history (keep longer than logs)
                cursor.execute(f'''
                    DELETE FROM pdf_change_history
                    WHERE timestamp < datetime('now', '-{days_to_keep * 2} days')
                ''')
                cleanup_stats['pdf_changes_removed'] = cursor.rowcount

                conn.commit()
                logging.info(f"Cleanup completed: {cleanup_stats}")
                return cleanup_stats

        except Exception as e:
            logging.error(f"Cleanup failed: {e}")
            return {}

    def mark_relationship_processed(self, relationship_id: str) -> bool:
        """Mark a relationship as processed"""
        try:
            return self.update_relationship(relationship_id, {'processed': True})
        except Exception as e:
            logging.error(f"Failed to mark relationship {relationship_id} as processed: {e}")
            return False

    def unmark_relationship_processed(self, relationship_id: str) -> bool:
        """Unmark a relationship as processed (for re-sync purposes)"""
        try:
            return self.update_relationship(relationship_id, {
                'processed': False,
                'processed_date': None
            })
        except Exception as e:
            logging.error(f"Failed to unmark relationship {relationship_id} as processed: {e}")
            return False

    def export_data(self, export_path: str) -> bool:
        """Export all data for backup"""
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'database_version': '2.1.0',
                'relationships': self.get_all_relationships(include_inactive=True),
                'statistics': self.get_statistics()
            }

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)

            logging.info(f"Data exported to {export_path}")
            return True

        except Exception as e:
            logging.error(f"Data export failed: {e}")
            return False