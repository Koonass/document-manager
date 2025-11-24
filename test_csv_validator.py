#!/usr/bin/env python3
"""
Test the CSV validator
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from csv_validator import CSVValidator, ValidationError

# Test with sample CSV and products file
sample_csv = Path(r"/mnt/c/code/Document Manager/sample csv/HH-109-HF-2.csv")
products_file = Path(r"/mnt/c/code/Document Manager/sample csv/products_master.csv")

print("="*70)
print("Testing CSV Validator")
print("="*70)
print()

# Create validator with products file
validator = CSVValidator(products_file)

print(f"Loaded {len(validator.valid_skus)} SKUs from products file")
print()

# Validate the CSV
print(f"Validating: {sample_csv.name}")
print()

errors = validator.validate_csv(sample_csv, strict_mode=False)

# Get summary
summary = validator.get_validation_summary(errors)

print("="*70)
print("VALIDATION RESULTS")
print("="*70)
print(f"Total Issues: {summary['total']}")
print(f"  Errors:   {summary['errors']} (must fix)")
print(f"  Warnings: {summary['warnings']} (recommended to fix)")
print(f"  Info:     {summary['info']} (informational)")
print()
print(f"Can Upload: {'✓ YES' if summary['can_upload'] else '✗ NO'}")
print()

if errors:
    print("="*70)
    print("ISSUES FOUND")
    print("="*70)
    print()

    # Group by severity
    errors_list = [e for e in errors if e.severity == ValidationError.ERROR]
    warnings_list = [e for e in errors if e.severity == ValidationError.WARNING]
    info_list = [e for e in errors if e.severity == ValidationError.INFO]

    if errors_list:
        print("ERRORS (Must Fix):")
        print("-" * 70)
        for error in errors_list[:10]:  # Show first 10
            print(f"Line {error.line_number}: {error.field}")
            print(f"  ✗ {error.message}")
            if error.suggested_fix:
                print(f"  → Suggested fix: {error.suggested_fix}")
            print()
        if len(errors_list) > 10:
            print(f"  ... and {len(errors_list) - 10} more errors")
            print()

    if warnings_list:
        print("WARNINGS (Recommended to Fix):")
        print("-" * 70)
        for warning in warnings_list[:10]:  # Show first 10
            print(f"Line {warning.line_number}: {warning.field}")
            print(f"  ⚠ {warning.message}")
            if warning.suggested_fix:
                print(f"  → Suggested fix: {warning.suggested_fix}")
            print()
        if len(warnings_list) > 10:
            print(f"  ... and {len(warnings_list) - 10} more warnings")
            print()

    if info_list:
        print("INFO (Informational):")
        print("-" * 70)
        for info in info_list[:5]:  # Show first 5
            print(f"Line {info.line_number}: {info.field}")
            print(f"  ℹ {info.message}")
            print()
        if len(info_list) > 5:
            print(f"  ... and {len(info_list) - 5} more info messages")
            print()

else:
    print("✓ No issues found - CSV is valid!")
    print()

print("="*70)
print("Test Complete")
print("="*70)
