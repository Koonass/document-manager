#!/usr/bin/env python3
"""
Document Manager V2.1 - Application Launcher
Enhanced version with 2-week calendar view and PDF actions
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main_v2_1 import main

    if __name__ == "__main__":
        print("=" * 60)
        print("Document Manager V2.1 - Enhanced Calendar View")
        print("=" * 60)
        print()
        print("🗓️  2-Week Calendar View")
        print("   • Orders positioned by 'Date Required' field")
        print("   • 10 weekday boxes (Mon-Fri, 2 weeks)")
        print("   • Navigate between periods with arrow buttons")
        print()
        print("📋 Interactive Order Cards")
        print("   • Click any card to open PDF action menu")
        print("   • Visual indicators: ✅ (has PDF) | ❌ (no PDF)")
        print("   • Shows OrderNumber, Customer, Designer")
        print()
        print("📄 PDF Action Menu")
        print("   • View PDF in default viewer")
        print("   • Print PDF directly")
        print("   • Email PDF (opens mail client)")
        print("   • Attach/Replace PDF manually")
        print("   • Save PDF to different location")
        print()
        print("🔗 Smart Relationship Tracking")
        print("   • OrderNumber matching (unchanged workflow)")
        print("   • Internal unique IDs for PDF relationships")
        print("   • Dynamic status updates (❌ → ✅)")
        print()
        print("⚙️  Enhanced Features")
        print("   • Settings menu for file locations")
        print("   • Search historical data")
        print("   • PDF archival system")
        print("   • Database statistics and logging")
        print()
        print("Starting application...")
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