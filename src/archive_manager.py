#!/usr/bin/env python3
"""
Archive Manager - Handle PDF archival and historical data
"""

import shutil
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional

class ArchiveManager:
    def __init__(self, archive_base_path: str = "archive"):
        self.archive_base_path = Path(archive_base_path)
        self.setup_archive_structure()

    def setup_archive_structure(self):
        """Create archive folder structure"""
        try:
            # Create main archive directory
            self.archive_base_path.mkdir(exist_ok=True)

            # Create yearly subdirectories
            current_year = datetime.now().year
            for year in range(current_year - 2, current_year + 2):  # Previous 2 years to next 2 years
                year_path = self.archive_base_path / str(year)
                year_path.mkdir(exist_ok=True)

            logging.info(f"Archive structure created at {self.archive_base_path}")

        except Exception as e:
            logging.error(f"Failed to create archive structure: {e}")
            raise

    def archive_pdf(self, pdf_path: str, order_number: str, order_data: Dict) -> str:
        """
        Archive a PDF file with metadata
        Returns the new archive path
        """
        try:
            source_path = Path(pdf_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source PDF not found: {pdf_path}")

            # Create archive filename with metadata
            current_date = datetime.now()
            year_folder = self.archive_base_path / str(current_date.year)
            year_folder.mkdir(exist_ok=True)

            # Generate archived filename: OrderNumber_Customer_Date.pdf
            customer = self.sanitize_filename(order_data.get('Customer', 'Unknown'))
            date_str = current_date.strftime('%Y%m%d')
            archived_filename = f"{order_number}_{customer}_{date_str}.pdf"

            archive_path = year_folder / archived_filename

            # Handle duplicate names
            counter = 1
            while archive_path.exists():
                name_parts = archived_filename.rsplit('.', 1)
                archived_filename = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                archive_path = year_folder / archived_filename
                counter += 1

            # Copy file to archive
            shutil.copy2(source_path, archive_path)

            # Create metadata file
            self.create_metadata_file(archive_path, order_number, order_data, str(source_path))

            logging.info(f"Archived PDF: {pdf_path} -> {archive_path}")
            return str(archive_path)

        except Exception as e:
            logging.error(f"Failed to archive PDF {pdf_path}: {e}")
            raise

    def create_metadata_file(self, archive_path: Path, order_number: str, order_data: Dict, original_path: str):
        """Create a metadata file alongside the archived PDF"""
        try:
            metadata_path = archive_path.with_suffix('.metadata.txt')

            metadata_content = [
                f"Archive Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Original Path: {original_path}",
                f"Order Number: {order_number}",
                "",
                "Order Data:",
            ]

            for key, value in order_data.items():
                metadata_content.append(f"  {key}: {value}")

            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(metadata_content))

        except Exception as e:
            logging.warning(f"Could not create metadata file for {archive_path}: {e}")

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a string for use in filename"""
        # Remove or replace problematic characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Limit length
        return filename[:50] if len(filename) > 50 else filename

    def remove_processed_pdf(self, pdf_path: str):
        """Remove the original PDF file after archiving"""
        try:
            source_path = Path(pdf_path)
            if source_path.exists():
                source_path.unlink()
                logging.info(f"Removed processed PDF: {pdf_path}")
            else:
                logging.warning(f"PDF not found for removal: {pdf_path}")

        except Exception as e:
            logging.error(f"Failed to remove PDF {pdf_path}: {e}")

    def search_archived_files(self, search_term: str) -> List[Dict]:
        """Search archived files by order number, customer, or metadata"""
        results = []

        try:
            # Search through all archived files
            for year_folder in self.archive_base_path.iterdir():
                if not year_folder.is_dir():
                    continue

                for file_path in year_folder.glob("*.pdf"):
                    metadata_path = file_path.with_suffix('.metadata.txt')

                    # Check filename for search term
                    if search_term.lower() in file_path.name.lower():
                        result = self.create_search_result(file_path, metadata_path)
                        results.append(result)
                        continue

                    # Check metadata file for search term
                    if metadata_path.exists():
                        try:
                            with open(metadata_path, 'r', encoding='utf-8') as f:
                                metadata_content = f.read()
                                if search_term.lower() in metadata_content.lower():
                                    result = self.create_search_result(file_path, metadata_path)
                                    results.append(result)
                        except Exception as e:
                            logging.warning(f"Could not read metadata file {metadata_path}: {e}")

        except Exception as e:
            logging.error(f"Error during archive search: {e}")

        return results

    def create_search_result(self, pdf_path: Path, metadata_path: Path) -> Dict:
        """Create a search result dictionary from archived file info"""
        result = {
            'pdf_path': str(pdf_path),
            'filename': pdf_path.name,
            'archive_date': datetime.fromtimestamp(pdf_path.stat().st_mtime),
            'metadata': {}
        }

        # Read metadata if available
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    result['metadata_content'] = content

                    # Parse key information
                    lines = content.split('\n')
                    for line in lines:
                        if ':' in line and not line.startswith('  '):
                            key, value = line.split(':', 1)
                            result['metadata'][key.strip()] = value.strip()

            except Exception as e:
                logging.warning(f"Could not parse metadata for {pdf_path}: {e}")

        return result

    def get_archive_statistics(self) -> Dict:
        """Get statistics about archived files"""
        stats = {
            'total_files': 0,
            'files_by_year': {},
            'total_size_mb': 0
        }

        try:
            for year_folder in self.archive_base_path.iterdir():
                if not year_folder.is_dir():
                    continue

                year = year_folder.name
                year_files = list(year_folder.glob("*.pdf"))
                year_count = len(year_files)

                stats['files_by_year'][year] = year_count
                stats['total_files'] += year_count

                # Calculate size
                for pdf_file in year_files:
                    try:
                        stats['total_size_mb'] += pdf_file.stat().st_size / (1024 * 1024)
                    except:
                        pass  # Skip if file is inaccessible

        except Exception as e:
            logging.error(f"Error calculating archive statistics: {e}")

        return stats

    def cleanup_empty_folders(self):
        """Remove empty year folders from archive"""
        try:
            for year_folder in self.archive_base_path.iterdir():
                if year_folder.is_dir() and not any(year_folder.iterdir()):
                    year_folder.rmdir()
                    logging.info(f"Removed empty archive folder: {year_folder}")

        except Exception as e:
            logging.error(f"Error during archive cleanup: {e}")

    def export_archive_index(self, export_path: str):
        """Export an index of all archived files to CSV"""
        try:
            import csv

            with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['filename', 'archive_path', 'archive_date', 'order_number', 'customer', 'original_path']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for year_folder in self.archive_base_path.iterdir():
                    if not year_folder.is_dir():
                        continue

                    for pdf_file in year_folder.glob("*.pdf"):
                        metadata_path = pdf_file.with_suffix('.metadata.txt')

                        row = {
                            'filename': pdf_file.name,
                            'archive_path': str(pdf_file),
                            'archive_date': datetime.fromtimestamp(pdf_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                            'order_number': '',
                            'customer': '',
                            'original_path': ''
                        }

                        # Parse metadata if available
                        if metadata_path.exists():
                            try:
                                with open(metadata_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    for line in content.split('\n'):
                                        if line.startswith('Order Number:'):
                                            row['order_number'] = line.split(':', 1)[1].strip()
                                        elif line.startswith('Original Path:'):
                                            row['original_path'] = line.split(':', 1)[1].strip()
                                        elif '  Customer:' in line:
                                            row['customer'] = line.split(':', 1)[1].strip()
                            except:
                                pass  # Skip if metadata can't be read

                        writer.writerow(row)

            logging.info(f"Archive index exported to: {export_path}")

        except Exception as e:
            logging.error(f"Failed to export archive index: {e}")
            raise