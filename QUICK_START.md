# Document Manager V2.3 - Quick Start Guide

## For End Users

### Installation (5 minutes)

1. **Install Python** (if not already installed)
   - Download from: https://www.python.org/downloads/
   - Use version 3.8 or higher
   - During installation, you do NOT need to check "Add Python to PATH"

2. **Run INSTALL.bat**
   - Double-click `INSTALL.bat`
   - Wait for package installation to complete
   - If it fails, right-click `INSTALL.bat` and select "Run as Administrator"

3. **Launch the Application**
   - Double-click `START_APP.bat` (created by INSTALL.bat)
   - OR manually run: `python run_v2_3.py`

### First-Time Setup

1. **Configure File Paths**
   - Click "Settings" in the application
   - Set **HTML/CSV Path**: Where your order HTML files are located
   - Set **PDF Path**: Where your PDF plot files are stored
   - Click "Save Settings"

2. **Load Orders**
   - Click "Reload Data" to scan for orders
   - The calendar will populate with order statistics

### Using the Application

#### Calendar View
- **10-day view** showing order statistics
- **Green numbers**: Orders ready to print (with PDFs)
- **Red numbers**: Orders missing PDFs
- **Gray numbers**: Previously processed orders
- **Navigation buttons**: ◀ Previous | Today | Next ▶

#### Working with Orders
1. **Click any day** to view detailed orders
2. **Browse PDFs**: Attach or replace PDF files
3. **Print orders**: Select orders and click "Print All"
4. **Mark as processed**: Orders automatically move to gray after printing

## For IT/Deployment

### Creating a Distribution Package

Run the provided script:
```batch
CREATE_DISTRIBUTION_PACKAGE.bat
```

This creates a clean folder with only necessary files.

### Deploying to Multiple Users

#### Option 1: Local Installation
1. Copy distribution folder to each machine
2. Run INSTALL.bat on each machine
3. Configure file paths in application

#### Option 2: Network/OneDrive Installation
1. Place application in shared location
2. Run INSTALL.bat on each machine (installs packages locally)
3. Edit `settings_v2_3.json` to point to shared paths:
   ```json
   {
     "html_path": "\\\\server\\share\\Orders",
     "pdf_path": "\\\\server\\share\\PDFs",
     "db_path": "\\\\server\\share\\database.db"
   }
   ```

### Folder Label Printing Setup

1. **Verify Template**
   ```batch
   python diagnose_label_printing.py
   ```

2. **Check Bookmarks** (in Word template)
   - Open `LABEL TEMPLATE\Contract_Lumber_Label_Template.docx`
   - Verify bookmarks exist:
     - `builder` (Customer name)
     - `Lot / subdivision` (Job reference)
     - `floors` (Delivery area)
     - `designer` (Designer name)

3. **Configure Printer** (in application)
   - Open application
   - Go to Print Settings
   - Enable "Folder Printer"
   - Select printer from dropdown
   - Settings save automatically

4. **Test Print**
   - Select a single order
   - Enable only folder printer
   - Click "Print All"
   - Verify label prints correctly

### Troubleshooting

#### Installation Issues
```batch
REM Run as Administrator
INSTALL.bat

REM If pywin32 fails, try:
python -m pip install pywin32==305
python -m pywin32_postinstall -install
```

#### Label Printing Issues
```batch
REM Run diagnostics
python diagnose_label_printing.py

REM Fix bookmark mismatch
python FIX_BOOKMARK_MISMATCH.py
```

#### Application Won't Start
```batch
REM Check log file
type document_manager_v2.3.log

REM Verify packages
python -c "import pandas; import PyPDF2; import win32com.client; print('OK')"
```

### Python Not in PATH

If Python is not in PATH, use full path:

```batch
REM Find Python
where /R C:\ python.exe

REM Run with full path
"C:\Users\USERNAME\AppData\Local\Programs\Python\Python312\python.exe" run_v2_3.py
```

### Files Overview

**Required for Operation:**
- `run_v2_3.py` - Application launcher
- `src/*.py` - Source code (12 files)
- `LABEL TEMPLATE/*.docx` - Word template
- `requirements.txt` - Package dependencies

**Setup/Support:**
- `INSTALL.bat` - Installation script
- `START_APP.bat` - Launch script (created by INSTALL.bat)
- `diagnose_label_printing.py` - Diagnostic tool
- `FIX_BOOKMARK_MISMATCH.py` - Template fix tool

**Documentation:**
- `INSTALLATION_INSTRUCTIONS.md` - Detailed install guide
- `FOLDER_PRINTING_GUIDE.md` - Label printing setup
- `CLEAN_INSTALLATION_PACKAGE.md` - Deployment guide

**Generated at Runtime:**
- `settings_v2_3.json` - User settings
- `document_manager_v2.3.log` - Application log
- `*.db` - Database file
- `archive/` - Processed orders

## Common Tasks

### Update Python Packages
```batch
python -m pip install --upgrade pandas PyPDF2 pywin32 lxml
```

### Reset Settings
```batch
del settings_v2_3.json
REM Restart application to recreate with defaults
```

### View All Printers
```batch
python -c "import win32print; [print(p) for p in win32print.EnumPrinters(2)]"
```

### Export Data
- Archive processed orders automatically
- Check `archive/` folder for archived data
- Database file: `document_manager_v2.1.db` (SQLite format)

## Support Resources

1. **Log File**: `document_manager_v2.3.log`
   - Contains detailed error messages
   - Updated in real-time

2. **Diagnostic Tools**:
   - `diagnose_label_printing.py` - Check label printing setup
   - `verify_template.py` - Verify Word template bookmarks

3. **Documentation**:
   - `FOLDER_PRINTING_GUIDE.md` - Complete label printing guide
   - `INSTALLATION_INSTRUCTIONS.md` - Installation details
   - `LABEL_PRINTING_TROUBLESHOOTING.md` - Common issues

## Feature Overview

### V2.3 Features
- ✅ Statistics calendar with 10-day view
- ✅ Enhanced expanded view with categorized orders
- ✅ Real-time PDF management
- ✅ Batch printing with folder labels
- ✅ Automatic order processing
- ✅ Archive management
- ✅ Relationship tracking (additions/reorders)
- ✅ Search and filter capabilities

### Printing Capabilities
- **11x17 Printer**: Plot printing
- **24x36 Printer**: Large format plotting
- **Folder Printer**: Automatic label printing with Word templates

### Order Categories
- **🟢 Green**: Ready to print (PDFs attached)
- **🔴 Red**: Missing PDFs
- **⚫ Gray**: Previously processed

## Getting Help

If you encounter issues:

1. Check the log file
2. Run diagnostic scripts
3. Review documentation
4. Verify Python and package versions

For bookmark/template issues:
```batch
python FIX_BOOKMARK_MISMATCH.py
```

For general diagnostics:
```batch
python diagnose_label_printing.py
```

---

**Version:** 2.3.0
**Updated:** November 2024
