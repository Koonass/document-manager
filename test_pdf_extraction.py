#!/usr/bin/env python3
"""
Test PDF Extraction - Diagnostic tool to see what order numbers can be extracted from a PDF
"""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from pdf_processor import PDFProcessor
import logging

# Set up logging to see all debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s'
)

# Test the sample PDF
pdf_path = Path("samples/sample plots/RH-913-DRAKE-PROD.pdf")

if not pdf_path.exists():
    print(f"ERROR: PDF file not found at {pdf_path}")
    sys.exit(1)

print("=" * 80)
print(f"Testing PDF: {pdf_path}")
print("=" * 80)

processor = PDFProcessor()
order_number = processor.extract_sales_order(pdf_path)

print("\n" + "=" * 80)
if order_number:
    print(f"✅ SUCCESS: Extracted order number: {order_number}")
else:
    print(f"❌ FAILED: Could not extract order number from PDF")
print("=" * 80)
