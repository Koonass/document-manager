#!/usr/bin/env python3
"""
Relationship Manager - Handles unique identifiers and PDF-CSV relationships
"""

import uuid
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class RelationshipManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_relationship(self, order_number: str, csv_data: Dict, pdf_path: Optional[str] = None) -> str:
        """
        Create a new relationship between CSV order and PDF
        Returns the unique relationship ID
        """
        try:
            # Generate unique relationship ID
            relationship_id = str(uuid.uuid4())

            # Store relationship in database
            relationship_data = {
                'relationship_id': relationship_id,
                'order_number': order_number,
                'csv_data': csv_data,
                'pdf_path': pdf_path,
                'created_date': None,  # Will be set by database
                'updated_date': None,
                'pdf_changes': []  # Track PDF attachment/replacement history
            }

            success = self.db_manager.store_relationship(relationship_data)

            if success:
                logging.info(f"Created relationship {relationship_id} for order {order_number}")
                return relationship_id
            else:
                raise Exception("Database storage failed")

        except Exception as e:
            logging.error(f"Failed to create relationship for order {order_number}: {e}")
            raise

    def update_relationship_pdf(self, relationship_id: str, pdf_path: str, update_reason: str = "manual_attachment") -> bool:
        """
        Update the PDF path for an existing relationship
        Tracks the change history
        """
        try:
            # Get existing relationship
            relationship = self.db_manager.get_relationship(relationship_id)
            if not relationship:
                logging.error(f"Relationship {relationship_id} not found")
                return False

            # Track the change
            change_record = {
                'timestamp': None,  # Will be set by database
                'action': update_reason,
                'old_pdf_path': relationship.get('pdf_path'),
                'new_pdf_path': pdf_path
            }

            # Update the relationship
            update_data = {
                'pdf_path': pdf_path,
                'pdf_changes': relationship.get('pdf_changes', []) + [change_record]
            }

            success = self.db_manager.update_relationship(relationship_id, update_data)

            if success:
                logging.info(f"Updated relationship {relationship_id} with new PDF: {pdf_path}")
                return True
            else:
                return False

        except Exception as e:
            logging.error(f"Failed to update relationship {relationship_id}: {e}")
            return False

    def get_relationship_by_order(self, order_number: str) -> Optional[Dict]:
        """Get relationship data by order number"""
        try:
            return self.db_manager.get_relationship_by_order(order_number)
        except Exception as e:
            logging.error(f"Failed to get relationship for order {order_number}: {e}")
            return None

    def get_relationship_by_id(self, relationship_id: str) -> Optional[Dict]:
        """Get relationship data by relationship ID"""
        try:
            return self.db_manager.get_relationship(relationship_id)
        except Exception as e:
            logging.error(f"Failed to get relationship {relationship_id}: {e}")
            return None

    def remove_pdf_from_relationship(self, relationship_id: str, removal_reason: str = "manual_removal") -> bool:
        """
        Remove PDF from relationship (but keep the relationship record)
        """
        try:
            relationship = self.db_manager.get_relationship(relationship_id)
            if not relationship:
                return False

            # Track the removal
            change_record = {
                'timestamp': None,  # Will be set by database
                'action': removal_reason,
                'old_pdf_path': relationship.get('pdf_path'),
                'new_pdf_path': None
            }

            update_data = {
                'pdf_path': None,
                'pdf_changes': relationship.get('pdf_changes', []) + [change_record]
            }

            return self.db_manager.update_relationship(relationship_id, update_data)

        except Exception as e:
            logging.error(f"Failed to remove PDF from relationship {relationship_id}: {e}")
            return False

    def get_orders_with_relationships(self) -> List[Dict]:
        """
        Get all orders with their relationship status
        Combines CSV data with PDF status
        """
        try:
            relationships = self.db_manager.get_all_relationships()

            orders_with_status = []
            for rel in relationships:
                csv_data = rel.get('csv_data', {})

                # Determine attachment method from PDF change history
                attachment_method = None
                if rel.get('pdf_path') and rel.get('pdf_changes'):
                    # Get the most recent attach action
                    for change in reversed(rel.get('pdf_changes', [])):
                        if change.get('action') in ['attach', 'replace']:
                            reason = change.get('reason', '')
                            if reason == 'automatic_matching':
                                attachment_method = 'automatic'
                            elif reason in ['manual_attachment', 'unknown']:
                                attachment_method = 'manual'
                            break

                order_info = {
                    'relationship_id': rel.get('relationship_id'),
                    'order_number': rel.get('order_number'),
                    'csv_data': csv_data,
                    'has_pdf': bool(rel.get('pdf_path')),
                    'pdf_path': rel.get('pdf_path'),
                    'created_date': rel.get('created_date'),
                    'updated_date': rel.get('updated_date'),
                    'pdf_change_count': len(rel.get('pdf_changes', [])),
                    'processed': rel.get('processed', False),
                    'processed_date': rel.get('processed_date'),
                    'attachment_method': attachment_method  # 'automatic', 'manual', or None
                }

                # Extract commonly used fields for easy access
                order_info.update({
                    'OrderNumber': csv_data.get('OrderNumber', ''),
                    'Customer': csv_data.get('Customer', ''),
                    'JobReference': csv_data.get('JobReference', ''),
                    'Designer': csv_data.get('Designer', ''),
                    'DateRequired': csv_data.get('DateRequired', '')
                })

                orders_with_status.append(order_info)

            return orders_with_status

        except Exception as e:
            logging.error(f"Failed to get orders with relationships: {e}")
            return []

    def sync_csv_data(self, csv_records: List[Dict]) -> Tuple[int, int, int]:
        """
        Sync CSV data with existing relationships
        Returns: (new_relationships, updated_relationships, unchanged_relationships)
        """
        try:
            new_count = 0
            updated_count = 0
            unchanged_count = 0

            for csv_record in csv_records:
                order_number = str(csv_record.get('OrderNumber', ''))
                if not order_number:
                    continue

                # Check if relationship already exists
                existing_rel = self.get_relationship_by_order(order_number)

                if existing_rel:
                    # Update existing relationship with new CSV data
                    # IMPORTANT: Preserve processed status during sync
                    current_csv_data = existing_rel.get('csv_data', {})

                    # Check if CSV data has changed
                    if current_csv_data != csv_record:
                        update_data = {'csv_data': csv_record}
                        # Note: update_relationship only updates specified fields
                        # The processed flag and other fields are preserved automatically
                        if self.db_manager.update_relationship(existing_rel['relationship_id'], update_data):
                            updated_count += 1
                        else:
                            unchanged_count += 1
                    else:
                        unchanged_count += 1
                else:
                    # Create new relationship
                    try:
                        self.create_relationship(order_number, csv_record)
                        new_count += 1
                    except Exception as e:
                        logging.warning(f"Failed to create relationship for order {order_number}: {e}")

            logging.info(f"CSV sync complete: {new_count} new, {updated_count} updated, {unchanged_count} unchanged")
            return new_count, updated_count, unchanged_count

        except Exception as e:
            logging.error(f"Failed to sync CSV data: {e}")
            return 0, 0, 0

    def match_pdfs_to_relationships(self, pdf_files: List[str], pdf_processor) -> Tuple[int, int]:
        """
        Automatically match PDF files to existing relationships based on OrderNumber
        Skips matching for orders with dates in the past for efficiency
        Returns: (matched_count, unmatched_count)
        """
        from datetime import datetime

        try:
            matched_count = 0
            unmatched_count = 0
            skipped_past_dates = 0
            today = datetime.now().date()

            for pdf_path in pdf_files:
                try:
                    # Extract order number from PDF
                    order_number = pdf_processor.extract_sales_order(Path(pdf_path))

                    if order_number:
                        # Find relationship for this order
                        relationship = self.get_relationship_by_order(order_number)

                        if relationship:
                            # Check if order date is in the past
                            csv_data = relationship.get('csv_data', {})
                            date_required = csv_data.get('DateRequired', '')

                            # Skip matching for past dates (efficiency optimization)
                            if date_required:
                                try:
                                    # Parse the date (assuming format like "YYYY-MM-DD" or similar)
                                    # Try multiple date formats
                                    order_date = None
                                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                                        try:
                                            order_date = datetime.strptime(str(date_required), fmt).date()
                                            break
                                        except:
                                            continue

                                    if order_date and order_date < today:
                                        # Skip matching for past orders
                                        skipped_past_dates += 1
                                        logging.debug(f"Skipping past date order {order_number} (date: {date_required})")
                                        continue
                                except Exception as e:
                                    # If date parsing fails, continue with matching
                                    logging.debug(f"Could not parse date {date_required} for order {order_number}: {e}")

                            # Check if PDF is already attached
                            if not relationship.get('pdf_path'):
                                # Attach PDF to relationship
                                if self.update_relationship_pdf(
                                    relationship['relationship_id'],
                                    pdf_path,
                                    "automatic_matching"
                                ):
                                    matched_count += 1
                                    logging.info(f"Auto-matched PDF {pdf_path} to order {order_number}")
                                else:
                                    unmatched_count += 1
                            # If PDF already attached, don't count as unmatched
                        else:
                            unmatched_count += 1
                            logging.warning(f"No relationship found for order {order_number} in PDF {pdf_path}")
                    else:
                        unmatched_count += 1
                        logging.warning(f"Could not extract order number from PDF {pdf_path}")

                except Exception as e:
                    unmatched_count += 1
                    logging.warning(f"Error processing PDF {pdf_path}: {e}")

            logging.info(f"PDF matching complete: {matched_count} matched, {unmatched_count} unmatched, {skipped_past_dates} past dates skipped")
            return matched_count, unmatched_count

        except Exception as e:
            logging.error(f"Failed to match PDFs to relationships: {e}")
            return 0, 0

    def get_relationship_history(self, relationship_id: str) -> List[Dict]:
        """Get the change history for a relationship"""
        try:
            relationship = self.get_relationship_by_id(relationship_id)
            if relationship:
                return relationship.get('pdf_changes', [])
            return []
        except Exception as e:
            logging.error(f"Failed to get history for relationship {relationship_id}: {e}")
            return []

    def cleanup_orphaned_relationships(self) -> int:
        """
        Remove relationships that no longer have corresponding CSV data
        Returns count of cleaned up relationships
        """
        try:
            # This would be implemented based on your business rules
            # For now, we'll just return 0 as a placeholder
            logging.info("Relationship cleanup not implemented yet")
            return 0
        except Exception as e:
            logging.error(f"Failed to cleanup relationships: {e}")
            return 0

    def export_relationships(self, export_path: str) -> bool:
        """Export all relationships to a JSON file for backup"""
        try:
            relationships = self.db_manager.get_all_relationships()

            export_data = {
                'export_date': None,  # Will be set by database
                'export_version': '2.1.0',
                'total_relationships': len(relationships),
                'relationships': relationships
            }

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)

            logging.info(f"Exported {len(relationships)} relationships to {export_path}")
            return True

        except Exception as e:
            logging.error(f"Failed to export relationships: {e}")
            return False

    def mark_order_processed(self, order_number: str) -> bool:
        """Mark an order as processed"""
        try:
            relationship = self.get_relationship_by_order(order_number)
            if relationship:
                return self.db_manager.mark_relationship_processed(relationship['relationship_id'])
            return False
        except Exception as e:
            logging.error(f"Failed to mark order {order_number} as processed: {e}")
            return False

    def import_relationships(self, import_path: str) -> bool:
        """Import relationships from a JSON backup file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            relationships = import_data.get('relationships', [])
            imported_count = 0

            for rel_data in relationships:
                try:
                    # Store the relationship
                    if self.db_manager.store_relationship(rel_data):
                        imported_count += 1
                except Exception as e:
                    logging.warning(f"Failed to import relationship {rel_data.get('relationship_id', 'unknown')}: {e}")

            logging.info(f"Imported {imported_count} of {len(relationships)} relationships")
            return imported_count > 0

        except Exception as e:
            logging.error(f"Failed to import relationships: {e}")
            return False