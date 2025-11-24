#!/usr/bin/env python3
"""
Test the CSV processor with sample file
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from csv_processor import CSVProcessor

# Test with sample CSV
sample_csv = Path(r"/mnt/c/code/Document Manager/sample csv/HH-109-HF-2.csv")

print("="*70)
print("Testing CSV Processor")
print("="*70)
print()

processor = CSVProcessor()

# Test extraction
print(f"Testing file: {sample_csv.name}")
print()

# Extract order number
order_num = processor.extract_sales_order(sample_csv)
print(f"Extracted Order Number: {order_num}")
print()

# Parse structure
structure = processor.parse_csv_structure(sample_csv)
print("CSV Structure:")
print(f"  Order Number: {structure['order_number']}")
print(f"  Date Issued: {structure['date_issued']}")
print(f"  Job Path: {structure['job_path']}")
print(f"  Material Count: {structure['material_count']}")
print(f"  Has Errors: {structure['has_errors']}")
print()

# Get materials
materials = processor.get_material_lines(sample_csv)
print(f"Found {len(materials)} material lines:")
print()

# Show first 5 materials
for i, mat in enumerate(materials[:5], 1):
    print(f"{i}. {mat['label']:<8} {mat['sku']:<25} Qty: {mat['qty']}")

if len(materials) > 5:
    print(f"   ... and {len(materials) - 5} more")

print()
print("="*70)
print("✓ Test Complete")
print("="*70)
