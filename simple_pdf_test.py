#!/usr/bin/env python3
"""
Simple PDF text extraction test - shows what text PyPDF2 can extract
"""

import sys
import re
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    print("ERROR: PyPDF2 not installed")
    print("Install with: pip install PyPDF2")
    sys.exit(1)

# Test the sample PDF
pdf_path = Path("samples/sample plots/RH-913-DRAKE-PROD.pdf")

if not pdf_path.exists():
    print(f"ERROR: PDF file not found at {pdf_path}")
    sys.exit(1)

print("=" * 80)
print(f"Testing PDF: {pdf_path}")
print("=" * 80)
print()

try:
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        print(f"PDF has {len(pdf_reader.pages)} pages")
        print()

        # Extract text from first 3 pages
        all_text = ""
        for page_num in range(min(3, len(pdf_reader.pages))):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            all_text += page_text

            print(f"--- Page {page_num + 1} ---")
            print(f"Text length: {len(page_text)} characters")
            print()
            # Show first 500 chars of this page
            print("First 500 characters:")
            print(page_text[:500])
            print()

        print("=" * 80)
        print("SEARCHING FOR 7-DIGIT NUMBERS")
        print("=" * 80)
        print()

        # Look for 7-digit sequences
        seven_digit_matches = re.findall(r'\b\d{7}\b', all_text)
        if seven_digit_matches:
            print(f"Found {len(seven_digit_matches)} 7-digit sequences:")
            for i, match in enumerate(seven_digit_matches[:10], 1):
                print(f"  {i}. {match}")
        else:
            print("No 7-digit sequences found")

        print()
        print("=" * 80)
        print("SEARCHING FOR ALL DIGIT SEQUENCES (4+ digits)")
        print("=" * 80)
        print()

        # Look for any 4+ digit sequences
        digit_matches = re.findall(r'\b\d{4,}\b', all_text)
        if digit_matches:
            print(f"Found {len(digit_matches)} sequences with 4+ digits:")
            for i, match in enumerate(digit_matches[:20], 1):
                print(f"  {i}. {match} ({len(match)} digits)")
        else:
            print("No digit sequences found")

        print()
        print("=" * 80)
        print("LOOKING FOR ORDER NUMBER 4077102")
        print("=" * 80)
        print()

        if '4077102' in all_text:
            print("✅ SUCCESS: Order number 4077102 FOUND in PDF!")
            # Show context around it
            idx = all_text.find('4077102')
            start = max(0, idx - 100)
            end = min(len(all_text), idx + 107)
            print()
            print("Context (100 chars before and after):")
            print(all_text[start:end])
        else:
            print("❌ Order number 4077102 NOT found in PDF")
            print()
            print("This might mean:")
            print("  1. The number is in an image (not extractable text)")
            print("  2. The number is formatted differently (spaces, dashes, etc.)")
            print("  3. PyPDF2 cannot extract text from this PDF format")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
