# Document Manager

A desktop application for correlating Bistrack CSV schedule exports with PDF plot files, displaying unprocessed items in a weekday calendar view.

## Project Overview

This application helps manage document processing workflows by:
- Importing Bistrack schedule data from CSV files
- Scanning PDF folders for plot files
- Matching sales order numbers between CSV and PDFs
- Tracking processed items to show only unprocessed work
- Displaying results in a weekday-only calendar interface

## Features

- **CSV Import**: Import Bistrack schedule exports with sales order data
- **PDF Correlation**: Automatically extract sales order numbers from PDF files
- **Processing Log**: Track which PDFs have been processed to avoid duplicates
- **Weekday Calendar**: Visual calendar showing only Monday-Friday with unprocessed items
- **Database Storage**: SQLite database for persistent tracking of processed files

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- pandas
- PyPDF2
- sqlite3 (included with Python)

## Installation

1. Navigate to the project directory:
   ```bash
   cd "/mnt/c/code/Document Manager"
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python run_app.py
   ```

2. **Import Bistrack Schedule**: Click the "Import Bistrack Schedule (.csv)" button to load your CSV export

3. **Sync PDF Folder**: Click the "Sync with Plot Folder (.pdf)" button to scan and correlate PDF files

4. **View Results**: The weekday calendar will display unprocessed items. Click on dates to see details.

## File Structure

- `src/main.py` - Main application and GUI
- `src/pdf_processor.py` - PDF text extraction and sales order detection
- `src/database_manager.py` - SQLite database operations for tracking
- `src/calendar_widget.py` - Custom weekday calendar widget
- `run_app.py` - Application launcher
- `requirements.txt` - Python dependencies

## Configuration

The application automatically creates:
- `document_manager.db` - SQLite database for tracking processed files
- `document_manager.log` - Application log file

## Contributing

This is a custom business application. Modify as needed for your specific Bistrack export format and PDF naming conventions.

## License

Private business application.