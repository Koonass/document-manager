#!/usr/bin/env python3
"""
Document Manager - Redesigned Application Launcher
Run this file to start the enhanced Document Manager application
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main_redesign import main

    if __name__ == "__main__":
        print("Starting Document Manager - Enhanced Version")
        print("Features:")
        print("- Settings-based file location management")
        print("- Single Sync button workflow")
        print("- Card-based order display with 2-week view")
        print("- PDF archival system")
        print("- Historical data search")
        print()
        main()

except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure all required packages are installed.")
    print("Run: pip install pandas PyPDF2")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)