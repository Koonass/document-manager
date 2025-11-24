# Document Manager V2.3 - Clean Installation Package

## Purpose

This document describes a minimal, clean installation package for deploying Document Manager V2.3 to end users.

## Required Files for Distribution

### Core Application Files

```
Document Manager/
├── run_v2_3.py                          # Main launcher script
├── requirements.txt                     # Python package dependencies
├── INSTALL.bat                          # Automated installation script
├── START_APP.bat                        # Quick start script (created by INSTALL.bat)
├── INSTALLATION_INSTRUCTIONS.md         # Manual installation guide
├── diagnose_label_printing.py           # Diagnostic tool for troubleshooting
├── FIX_BOOKMARK_MISMATCH.py            # Fix tool for template issues
│
├── src/                                 # Source code folder
│   ├── __init__.py
│   ├── main_v2_3.py                    # Main application logic
│   ├── pdf_processor.py                # PDF handling
│   ├── enhanced_database_v2.py         # Database management
│   ├── relationship_manager.py         # Order relationships
│   ├── statistics_calendar_widget.py   # Calendar UI
│   ├── enhanced_expanded_view.py       # Detailed order view
│   ├── enhanced_search_view.py         # Search interface
│   ├── archive_manager.py              # Archive functionality
│   ├── word_template_processor.py      # Folder label printing
│   ├── error_logger.py                 # Error logging
│   └── verify_template.py              # Template verification tool
│
└── LABEL TEMPLATE/                      # Template folder
    └── Contract_Lumber_Label_Template.docx  # Word template for labels
```

### Optional Files for Advanced Users

```
├── FOLDER_PRINTING_GUIDE.md            # Label printing documentation
├── NETWORK_DEPLOYMENT_GUIDE.md         # Network installation guide
├── LABEL_PRINTING_TROUBLESHOOTING.md   # Troubleshooting guide
```

## Files That Can Be EXCLUDED from Distribution

### Development/Testing Files
- `run_v2_1.py`, `run_v2_2.py`, `run_redesigned_app.py` (old versions)
- `test_*.py` (test scripts)
- `check_order.py`, `simple_pdf_test.py` (diagnostic tests)
- `update_attachment_reasons.py` (database migration)

### Documentation/Guides (optional)
- `*.md` files except the ones listed in "Required Files"
- `DESIGN FILES/` folder (unless needed for reference)

### Build/Archive Files
- `archive/` folder (will be created automatically)
- `*.db` (database files - will be created on first run)
- `*.log` (log files)
- `venv/` (virtual environment)
- `python/` (portable Python installation)
- `__pycache__/` folders

### Configuration Files (machine-specific)
- `settings_v2_3.json` (will be created on first run)
- `print_presets.json` (will be created when user configures printing)

### Old/Backup Files
- `*.backup_*` (backup files)
- `src/*.py.backup_*` (code backups)

### Teams Deployment Folder
- `TEAMS_DEPLOYMENT/` (separate deployment package)

## Minimal Installation Package Structure

For the absolute minimum installation:

```
Document_Manager_v2.3/
│
├── run_v2_3.py
├── requirements.txt
├── INSTALL.bat
├── INSTALLATION_INSTRUCTIONS.md
│
├── src/
│   ├── __init__.py
│   ├── main_v2_3.py
│   ├── pdf_processor.py
│   ├── enhanced_database_v2.py
│   ├── relationship_manager.py
│   ├── statistics_calendar_widget.py
│   ├── enhanced_expanded_view.py
│   ├── enhanced_search_view.py
│   ├── archive_manager.py
│   ├── word_template_processor.py
│   └── error_logger.py
│
└── LABEL TEMPLATE/
    └── Contract_Lumber_Label_Template.docx
```

**Total:** 1 launcher + 10 Python modules + 1 template + 2 support files = **14 files**

## Creating a Clean Distribution Package

### Step 1: Create a new folder

```batch
mkdir "Document_Manager_v2.3_Distribution"
cd "Document_Manager_v2.3_Distribution"
```

### Step 2: Copy required files

```batch
REM Copy root files
copy "..\Document Manager\run_v2_3.py" .
copy "..\Document Manager\requirements.txt" .
copy "..\Document Manager\INSTALL.bat" .
copy "..\Document Manager\INSTALLATION_INSTRUCTIONS.md" .
copy "..\Document Manager\diagnose_label_printing.py" .
copy "..\Document Manager\FIX_BOOKMARK_MISMATCH.py" .

REM Create src folder and copy core modules
mkdir src
copy "..\Document Manager\src\__init__.py" src\
copy "..\Document Manager\src\main_v2_3.py" src\
copy "..\Document Manager\src\pdf_processor.py" src\
copy "..\Document Manager\src\enhanced_database_v2.py" src\
copy "..\Document Manager\src\relationship_manager.py" src\
copy "..\Document Manager\src\statistics_calendar_widget.py" src\
copy "..\Document Manager\src\enhanced_expanded_view.py" src\
copy "..\Document Manager\src\enhanced_search_view.py" src\
copy "..\Document Manager\src\archive_manager.py" src\
copy "..\Document Manager\src\word_template_processor.py" src\
copy "..\Document Manager\src\error_logger.py" src\
copy "..\Document Manager\src\verify_template.py" src\

REM Create template folder and copy template
mkdir "LABEL TEMPLATE"
copy "..\Document Manager\LABEL TEMPLATE\Contract_Lumber_Label_Template.docx" "LABEL TEMPLATE\"
```

### Step 3: Create a README

Create `README_FIRST.txt`:

```
Document Manager V2.3 - Installation Package
=============================================

QUICK START:
1. Double-click INSTALL.bat to install required packages
2. Double-click START_APP.bat to run the application

For detailed instructions, see INSTALLATION_INSTRUCTIONS.md

System Requirements:
- Windows 7 or later
- Python 3.8+ installed
- Microsoft Word (for folder label printing)

Questions? Check the log file: document_manager_v2.3.log
```

### Step 4: Compress for distribution

Create a ZIP file of the entire folder:
- Right-click folder → Send to → Compressed (zipped) folder
- Name it: `Document_Manager_v2.3_Clean_Install.zip`

## Deployment Options

### Option 1: Direct Installation
1. Copy the clean package folder to target machine
2. Run INSTALL.bat
3. Run START_APP.bat

### Option 2: Network/OneDrive Deployment
1. Place the clean package in a shared location
2. Each user runs INSTALL.bat locally (to install Python packages)
3. Update settings_v2_3.json to point to shared data paths

### Option 3: Portable Python Bundle
1. Include a portable Python installation in the package
2. Modify INSTALL.bat to use the portable Python
3. No Python installation required on target machines

See `PORTABLE_PYTHON_SETUP.md` for details on Option 3.

## User Configuration Required

After installation, users need to configure:

1. **File Paths** (in application settings):
   - HTML/CSV input path
   - PDF storage path
   - Archive path

2. **Printer Settings** (optional, for label printing):
   - Enable folder printer
   - Select printer from dropdown

3. **Template Verification** (optional):
   - Run `diagnose_label_printing.py`
   - Verify template bookmarks

## Troubleshooting

If users encounter issues:

1. **Installation fails:**
   - Run INSTALL.bat as Administrator
   - Check Python version: `python --version` (must be 3.8+)

2. **Application won't start:**
   - Check log file: `document_manager_v2.3.log`
   - Verify all packages installed: Run verification in INSTALL.bat

3. **Label printing doesn't work:**
   - Run `diagnose_label_printing.py`
   - Verify Word template exists in LABEL TEMPLATE folder
   - Check bookmarks in template using `verify_template.py`

## Version Control

When creating updates:

1. Update version number in `run_v2_3.py` and `main_v2_3.py`
2. Create a new distribution package
3. Document changes in a CHANGELOG.md
4. Test installation on a clean machine

## Security Considerations

- Do NOT include sensitive data in the distribution package:
  - No database files with real order data
  - No configuration files with passwords or credentials
  - No log files with user information

- Each installation should start fresh with:
  - Empty database
  - Default settings
  - No cached data

## Support Files to Include

For better user experience, also include:

1. `FOLDER_PRINTING_GUIDE.md` - Label printing setup
2. `LABEL_PRINTING_TROUBLESHOOTING.md` - Common issues
3. `diagnose_label_printing.py` - Diagnostic tool
4. `FIX_BOOKMARK_MISMATCH.py` - Template fix tool

These add minimal size but greatly improve supportability.
