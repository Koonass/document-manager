#!/usr/bin/env python3
"""
CSV Processor - Extract order numbers from CSV files and match to orders
Similar to PDF processor but for BisTrack material import CSVs
"""

import re
import csv
import logging
from pathlib import Path
from typing import Optional, List, Dict
import codecs

class CSVProcessor:
    def __init__(self):
        # CSV files from iStruct have order number in "Job Description" field (line 3)
        # Format:
        #   Line 1: Contract Lumber,,,,
        #   Line 2: Date Issued:,DD/MM/YYYY,,,
        #   Line 3: Job Description:,ORDER_NUMBER,,,
        #   Line 4: Job Path:,PROJECT_NAME,,,
        #   Line 5+: Material data

        # Order numbers are ALWAYS 7 digits (same as PDFs)
        self.order_patterns = [
            r'\b(\d{7})\b',  # Exactly 7 digits with word boundaries
            r'(?:SO|Sales Order|Order|Job)[:\s#]*(\d{7})',  # With prefix
            r'(\d{4,8})',  # Fallback: 4-8 digits
        ]

    def extract_sales_order(self, csv_path: Path) -> Optional[str]:
        """
        Extract sales order number from CSV file

        Args:
            csv_path: Path to CSV file

        Returns:
            Order number as string, or None if not found
        """
        try:
            logging.info(f"Extracting sales order from CSV: {csv_path.name}")

            # First try to extract from filename
            filename_order = self.extract_from_filename(csv_path.name)
            if filename_order:
                logging.info(f"Found sales order in filename: {filename_order} (from {csv_path.name})")
                return filename_order

            # Then try to extract from CSV content (Job Description line)
            logging.info(f"Filename extraction failed, trying CSV content...")
            content_order = self.extract_from_content(csv_path)
            if content_order:
                logging.info(f"Found sales order in CSV content: {content_order}")
                return content_order

            logging.warning(f"No sales order found in {csv_path.name} (tried both filename and content)")
            return None

        except Exception as e:
            logging.error(f"Error processing CSV {csv_path}: {e}")
            return None

    def extract_from_filename(self, filename: str) -> Optional[str]:
        """Extract sales order from filename"""
        # Remove file extension
        name_without_ext = Path(filename).stem
        logging.debug(f"Filename stem: '{name_without_ext}'")

        # First, look for exactly 7-digit sequences
        seven_digit_matches = re.findall(r'\b\d{7}\b', name_without_ext)
        if seven_digit_matches:
            order_num = seven_digit_matches[0]
            logging.debug(f"Found 7-digit sequence in filename: {order_num}")
            if self.validate_order_number(order_num):
                logging.info(f"Valid 7-digit order number from filename: {order_num}")
                return order_num

        # Fallback: Try patterns
        for pattern in self.order_patterns:
            match = re.search(pattern, name_without_ext, re.IGNORECASE)
            if match:
                extracted = match.group(1) if match.lastindex >= 1 else match.group(0)
                cleaned = self.clean_order_number(extracted)
                logging.debug(f"Pattern '{pattern}' matched: '{extracted}' -> cleaned: '{cleaned}'")

                if self.validate_order_number(cleaned):
                    logging.info(f"Valid order number from filename: {cleaned}")
                    return cleaned

        return None

    def extract_from_content(self, csv_path: Path) -> Optional[str]:
        """
        Extract sales order from CSV content
        Looks for "Job Description:" field which contains order number
        """
        try:
            # Try different encodings (CSVs might be UTF-8 or ANSI)
            encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1']

            for encoding in encodings:
                try:
                    with open(csv_path, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    break  # Successfully read file
                except UnicodeDecodeError:
                    continue
            else:
                # None of the encodings worked
                logging.error(f"Could not decode CSV file {csv_path.name} with any encoding")
                return None

            # Look for Job Description line (typically line 3)
            # Format: "Job Description:,4116780,,,"
            for i, line in enumerate(lines[:10]):  # Check first 10 lines
                if 'Job Description' in line or 'job description' in line.lower():
                    logging.debug(f"Found Job Description line at line {i+1}: {line.strip()}")

                    # Parse CSV line to get the value after "Job Description:"
                    parts = [p.strip() for p in line.split(',')]

                    # The order number should be in the second column
                    if len(parts) >= 2:
                        potential_order = parts[1]
                        logging.debug(f"Potential order number: '{potential_order}'")

                        # Try to extract order number from this value
                        for pattern in self.order_patterns:
                            match = re.search(pattern, potential_order)
                            if match:
                                extracted = match.group(1) if match.lastindex >= 1 else match.group(0)
                                cleaned = self.clean_order_number(extracted)

                                if self.validate_order_number(cleaned):
                                    logging.info(f"Valid order number from Job Description: {cleaned}")
                                    return cleaned

            logging.debug(f"No Job Description field found in {csv_path.name}")
            return None

        except Exception as e:
            logging.error(f"Error reading CSV content from {csv_path.name}: {e}")
            return None

    def clean_order_number(self, order_num: str) -> str:
        """Clean and normalize order number"""
        # Remove whitespace
        cleaned = order_num.strip()

        # Remove common prefixes/suffixes
        cleaned = re.sub(r'^(SO|ORDER|JOB)[\s#:]*', '', cleaned, flags=re.IGNORECASE)

        # Remove non-digits
        cleaned = re.sub(r'[^\d]', '', cleaned)

        return cleaned

    def validate_order_number(self, order_num: str) -> bool:
        """
        Validate order number
        Order numbers should be 7 digits
        """
        if not order_num:
            return False

        # Should be numeric
        if not order_num.isdigit():
            return False

        # Prefer 7-digit numbers
        if len(order_num) == 7:
            return True

        # Accept 4-8 digits as fallback
        if 4 <= len(order_num) <= 8:
            return True

        return False

    def parse_csv_structure(self, csv_path: Path) -> Dict:
        """
        Parse CSV structure and extract metadata

        Returns dict with:
        - order_number
        - date_issued
        - job_path
        - material_count
        - has_errors
        """
        try:
            result = {
                'order_number': None,
                'date_issued': None,
                'job_path': None,
                'material_count': 0,
                'has_errors': False,
                'error_messages': []
            }

            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1']
            lines = None

            for encoding in encodings:
                try:
                    with open(csv_path, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    break
                except UnicodeDecodeError:
                    continue

            if not lines:
                result['has_errors'] = True
                result['error_messages'].append('Could not read file with any encoding')
                return result

            # Parse header lines (first 4 lines before material data)
            if len(lines) >= 3:
                # Line 2: Date Issued
                if len(lines) > 1 and 'Date Issued' in lines[1]:
                    parts = lines[1].split(',')
                    if len(parts) >= 2:
                        result['date_issued'] = parts[1].strip()

                # Line 3: Job Description (order number)
                if len(lines) > 2 and 'Job Description' in lines[2]:
                    parts = lines[2].split(',')
                    if len(parts) >= 2:
                        order_num = parts[1].strip()
                        if self.validate_order_number(order_num):
                            result['order_number'] = order_num

                # Line 4: Job Path
                if len(lines) > 3 and 'Job Path' in lines[3]:
                    parts = lines[3].split(',')
                    if len(parts) >= 2:
                        result['job_path'] = parts[1].strip()

            # Count material lines (after header, before <EOF>)
            # Material data starts at line 6 (index 5)
            material_lines = 0
            for line in lines[5:]:
                line = line.strip()
                if line and '<EOF>' not in line and line != ',,,':
                    material_lines += 1

            result['material_count'] = material_lines

            logging.info(f"Parsed CSV structure: Order={result['order_number']}, Materials={material_lines}")

            return result

        except Exception as e:
            logging.error(f"Error parsing CSV structure from {csv_path.name}: {e}")
            return {
                'order_number': None,
                'date_issued': None,
                'job_path': None,
                'material_count': 0,
                'has_errors': True,
                'error_messages': [str(e)]
            }

    def get_material_lines(self, csv_path: Path) -> List[Dict]:
        """
        Extract material lines from CSV

        Returns list of dicts with:
        - label
        - length
        - sku
        - material
        - qty
        """
        materials = []

        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1']
            lines = None

            for encoding in encodings:
                try:
                    with open(csv_path, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    break
                except UnicodeDecodeError:
                    continue

            if not lines:
                logging.error(f"Could not read CSV {csv_path.name}")
                return materials

            # Material data starts at line 6 (index 5)
            # Format: LABEL,LENGTH,SKU,MATERIAL,QTY REQ'D
            in_materials = False
            for i, line in enumerate(lines):
                line = line.strip()

                # Check if we've reached the material header
                if 'LABEL' in line and 'SKU' in line and 'MATERIAL' in line:
                    in_materials = True
                    continue

                # Skip until we reach materials
                if not in_materials:
                    continue

                # Stop at end marker
                if '<EOF>' in line or not line or line == ',,,':
                    break

                # Parse material line
                parts = [p.strip().strip('"') for p in line.split(',')]

                if len(parts) >= 5:
                    material = {
                        'line_number': i + 1,
                        'label': parts[0],
                        'length': parts[1],
                        'sku': parts[2],
                        'material': parts[3],
                        'qty': parts[4]
                    }
                    materials.append(material)

            logging.info(f"Extracted {len(materials)} material lines from {csv_path.name}")
            return materials

        except Exception as e:
            logging.error(f"Error extracting materials from {csv_path.name}: {e}")
            return materials


def scan_csv_folder(folder_path: Path) -> List[Dict]:
    """
    Scan folder for CSV files and extract order information

    Returns list of dicts with CSV info:
    - path
    - filename
    - order_number
    - material_count
    - valid
    """
    processor = CSVProcessor()
    csv_files = []

    try:
        if not folder_path.exists():
            logging.error(f"CSV folder does not exist: {folder_path}")
            return csv_files

        # Find all CSV files
        for csv_file in folder_path.glob('**/*.csv'):
            if csv_file.is_file():
                logging.info(f"Processing CSV: {csv_file.name}")

                # Extract order number
                order_number = processor.extract_sales_order(csv_file)

                # Parse structure
                structure = processor.parse_csv_structure(csv_file)

                csv_info = {
                    'path': str(csv_file),
                    'filename': csv_file.name,
                    'order_number': order_number,
                    'material_count': structure.get('material_count', 0),
                    'job_path': structure.get('job_path'),
                    'valid': order_number is not None and not structure.get('has_errors', False)
                }

                csv_files.append(csv_info)

        logging.info(f"Found {len(csv_files)} CSV files in {folder_path}")
        return csv_files

    except Exception as e:
        logging.error(f"Error scanning CSV folder {folder_path}: {e}")
        return csv_files
