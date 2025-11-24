#!/usr/bin/env python3
"""
PDF Processor - Extract sales order numbers from PDF files
"""

import re
import logging
from pathlib import Path
from typing import Optional, List
import PyPDF2

class PDFProcessor:
    def __init__(self):
        # Common patterns for sales order numbers
        # IMPORTANT: Order numbers are ALWAYS 7 digits
        self.order_patterns = [
            r'(?:SO|Sales Order|Order)[:\s#]*(\d{7})',  # SO + 7 digits
            r'(?:Job|Project)[:\s#]*(\d{7})',  # Job/Project + 7 digits
            r'(?:Order Number)[:\s#]*(\d{7})',  # Order Number + 7 digits
            r'\b(\d{7})\b',  # Exactly 7 digits with word boundaries
            r'(?:SO|Sales Order|Order)[:\s#]*([A-Z0-9\-]+)',  # Fallback with prefix
            r'(\d{4,8})',  # Generic number pattern (fallback)
        ]

    def extract_sales_order(self, pdf_path: Path) -> Optional[str]:
        """Extract sales order number from PDF file"""
        try:
            logging.info(f"Extracting sales order from PDF: {pdf_path.name}")

            # First try to extract from filename
            filename_order = self.extract_from_filename(pdf_path.name)
            if filename_order:
                logging.info(f"Found sales order in filename: {filename_order} (from {pdf_path.name})")
                return filename_order

            # Then try to extract from PDF content
            logging.info(f"Filename extraction failed, trying PDF content...")
            content_order = self.extract_from_content(pdf_path)
            if content_order:
                logging.info(f"Found sales order in content: {content_order}")
                return content_order

            logging.warning(f"No sales order found in {pdf_path.name} (tried both filename and content)")
            return None

        except Exception as e:
            logging.error(f"Error processing PDF {pdf_path}: {e}")
            return None

    def extract_from_filename(self, filename: str) -> Optional[str]:
        """Extract sales order from filename"""
        # Remove file extension
        name_without_ext = Path(filename).stem
        logging.debug(f"Filename stem: '{name_without_ext}'")

        # Try each pattern
        for pattern in self.order_patterns:
            match = re.search(pattern, name_without_ext, re.IGNORECASE)
            if match:
                extracted = match.group(1) if match.lastindex >= 1 else match.group(0)
                cleaned = self.clean_order_number(extracted)
                logging.debug(f"Pattern '{pattern}' matched: '{extracted}' -> cleaned: '{cleaned}'")

                # Validate the extracted order number
                if self.validate_order_number(cleaned):
                    logging.info(f"Valid order number from filename: {cleaned}")
                    return cleaned
                else:
                    logging.debug(f"Order number '{cleaned}' failed validation")

        # If no pattern matches, look for digit sequences
        # IMPORTANT: Order numbers are ALWAYS 7 digits - prioritize those

        # First, look for exactly 7-digit sequences
        seven_digit_matches = re.findall(r'\b\d{7}\b', name_without_ext)
        if seven_digit_matches:
            order_num = seven_digit_matches[0]
            logging.debug(f"Found 7-digit sequence: {order_num}")
            if self.validate_order_number(order_num):
                logging.info(f"Valid 7-digit order number: {order_num}")
                return order_num

        # Fallback: Look for 4+ consecutive digits (for edge cases)
        digit_matches = re.findall(r'\d{4,}', name_without_ext)
        if digit_matches:
            # Prefer 7-digit matches
            for match in digit_matches:
                if len(match) == 7:
                    order_num = match
                    logging.debug(f"Found 7-digit in fallback: {order_num}")
                    if self.validate_order_number(order_num):
                        logging.info(f"Valid 7-digit order number from fallback: {order_num}")
                        return order_num

            # Last resort: take first match of any length
            order_num = digit_matches[0]
            logging.debug(f"Found digit sequence: {order_num}")
            if self.validate_order_number(order_num):
                logging.info(f"Valid order number from digit sequence: {order_num}")
                return order_num

        logging.debug(f"No valid order number found in filename: {filename}")
        return None

    def extract_from_content(self, pdf_path: Path) -> Optional[str]:
        """Extract sales order from PDF content"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                logging.debug(f"PDF has {len(pdf_reader.pages)} pages")

                # Extract text from first few pages (orders usually on first page)
                text = ""
                for page_num in range(min(3, len(pdf_reader.pages))):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    text += page_text
                    logging.debug(f"Page {page_num + 1} text length: {len(page_text)} chars")

                logging.debug(f"Total extracted text: {len(text)} chars")
                logging.debug(f"First 200 chars: {text[:200]}")

                # Try each pattern on the extracted text
                for pattern in self.order_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        extracted = match.group(1) if match.lastindex >= 1 else match.group(0)
                        order_number = self.clean_order_number(extracted)
                        logging.debug(f"Content pattern '{pattern}' matched: '{extracted}' -> '{order_number}'")

                        if self.validate_order_number(order_number):
                            logging.info(f"Valid order number from PDF content: {order_number}")
                            return order_number
                        else:
                            logging.debug(f"Order '{order_number}' failed validation")

                # Also try finding digit sequences in content as fallback
                # IMPORTANT: Order numbers are ALWAYS 7 digits - prioritize those

                # First, try to find exactly 7-digit sequences
                seven_digit_matches = re.findall(r'\b\d{7}\b', text)
                if seven_digit_matches:
                    logging.debug(f"Found 7-digit sequences in content: {seven_digit_matches[:5]}")  # Show first 5
                    for match in seven_digit_matches[:5]:  # Try first 5 7-digit matches
                        if self.validate_order_number(match):
                            logging.info(f"Valid 7-digit order number from content: {match}")
                            return match

                # Fallback: try finding 4+ digit sequences
                digit_matches = re.findall(r'\b\d{4,}\b', text)
                if digit_matches:
                    logging.debug(f"Found digit sequences in content: {digit_matches[:5]}")  # Show first 5
                    # First pass: look for 7-digit matches
                    for match in digit_matches:
                        if len(match) == 7 and self.validate_order_number(match):
                            logging.info(f"Valid 7-digit order number from content fallback: {match}")
                            return match
                    # Second pass: try any valid match
                    for match in digit_matches[:10]:  # Try first 10 matches
                        if self.validate_order_number(match):
                            logging.info(f"Valid order number from content digit sequence: {match}")
                            return match

                logging.debug("No valid order number found in PDF content")
                return None

        except Exception as e:
            logging.error(f"Error reading PDF content from {pdf_path}: {e}")
            return None

    def clean_order_number(self, raw_order: str) -> str:
        """Clean and normalize order number"""
        # Remove common prefixes/suffixes and whitespace
        cleaned = raw_order.strip()
        cleaned = re.sub(r'^(SO|Order|Job)[:\s\-]*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'[:\s]*$', '', cleaned)
        return cleaned.upper()

    def validate_order_number(self, order_number: str) -> bool:
        """Validate if the extracted string looks like a valid order number"""
        if not order_number:
            return False

        # Must be between 3 and 20 characters
        if len(order_number) < 3 or len(order_number) > 20:
            return False

        # Must contain at least one digit
        if not re.search(r'\d', order_number):
            return False

        # Should not be all the same character
        if len(set(order_number)) < 2:
            return False

        return True

    def scan_folder(self, folder_path: Path) -> List[tuple]:
        """Scan folder for PDFs and extract all sales orders"""
        results = []

        if not folder_path.exists():
            logging.error(f"Folder does not exist: {folder_path}")
            return results

        pdf_files = list(folder_path.glob("*.pdf"))
        logging.info(f"Found {len(pdf_files)} PDF files in {folder_path}")

        for pdf_file in pdf_files:
            sales_order = self.extract_sales_order(pdf_file)
            results.append((str(pdf_file), sales_order))

        return results