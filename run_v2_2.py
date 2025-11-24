#!/usr/bin/env python3
"""
Document Manager V2.2 - Application Launcher
Simplified Statistics Calendar with 10-Box Layout
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main_v2_2 import main

    if __name__ == "__main__":
        print("=" * 70)
        print("Document Manager V2.2 - Statistics Calendar")
        print("=" * 70)
        print()
        print("🗓️  SIMPLIFIED 10-BOX CALENDAR")
        print("   • Clean minimalist design inspired by modern dashboards")
        print("   • 2 weeks × 5 weekdays = 10 boxes total")
        print("   • Large day numbers for easy identification")
        print("   • Hover effects and smooth interactions")
        print()
        print("📊 DAILY STATISTICS AT A GLANCE")
        print("   • ✅ Successful matches (orders with PDFs)")
        print("   • ❌ No matches (orders without PDFs)")
        print("   • 📋 Previously processed orders")
        print("   • Color-coded statistics for quick scanning")
        print()
        print("🖱️  INTERACTIVE DAY BOXES")
        print("   • Click any day to see detailed order list")
        print("   • Detailed view shows all orders for that date")
        print("   • Access PDF actions from detailed view")
        print("   • Clean, organized data presentation")
        print()
        print("🎨 MODERN DESIGN")
        print("   • Minimalist styling with subtle shadows")
        print("   • Consistent spacing and typography")
        print("   • Professional color scheme")
        print("   • Responsive layout design")
        print()
        print("⚙️  ENHANCED FEATURES")
        print("   • Same powerful backend (OrderNumber matching)")
        print("   • Relationship tracking with unique IDs")
        print("   • Settings-based configuration")
        print("   • Search and statistics functionality")
        print()
        print("Starting Document Manager V2.2...")
        print("Navigate with ◀ Previous and Next ▶ buttons")
        print("Click any day box to view detailed orders")
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