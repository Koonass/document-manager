#!/usr/bin/env python3
"""
Document Manager V2.3 - Application Launcher
Enhanced Expanded View with Category Separation and Batch Processing
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main_v2_3 import main

    if __name__ == "__main__":
        print("=" * 75)
        print("Document Manager V2.3 - Enhanced Expanded View")
        print("=" * 75)
        print()
        print("🗓️  IMPROVED NAVIGATION")
        print("   • ◀ Previous and Next ▶ buttons for 2-week periods")
        print("   • 📅 Today button to jump to current date")
        print("   • Smooth navigation with statistics refresh")
        print()
        print("📊 ENHANCED EXPANDED VIEW")
        print("   • Click any day box to see detailed categorized orders")
        print("   • 🟢 Green Category: Orders ready to print (with PDFs)")
        print("   • 🔴 Red Category: Orders missing PDFs")
        print("   • ⚫ Gray Category: Previously processed orders")
        print()
        print("📄 INTERACTIVE PDF MANAGEMENT")
        print("   • 📄 View PDF links in green category")
        print("   • Browse buttons to attach/replace PDFs in all categories")
        print("   • Real-time movement between categories after PDF attachment")
        print("   • Instant statistics refresh after changes")
        print()
        print("🖨️  BATCH PROCESSING WORKFLOW")
        print("   • 🖨️ Print All button in green category")
        print("   • Batch prints all PDFs with confirmation")
        print("   • Automatically marks printed orders as processed")
        print("   • Orders move from green → gray after printing")
        print()
        print("⚡ DYNAMIC FEATURES")
        print("   • Real-time category updates")
        print("   • Statistics refresh after PDF changes")
        print("   • Complete workflow: View → Attach → Print → Process")
        print("   • Professional categorized interface")
        print()
        print("Starting Document Manager V2.3...")
        print("Click any day box to access the enhanced expanded view!")
        print()

        main()

except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure all required packages are installed:")
    print("pip install pandas PyPDF2")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)