# Document Manager - Installer Requirements & Application Structure

## Executive Summary

**Document Manager** is a Windows desktop application (Python-based, tkinter GUI) designed to correlate Bistrack CSV schedule exports with PDF plot files and manage document processing workflows. The application displays unprocessed items in a calendar view and provides batch printing capabilities with label generation.

**Project Size**: ~24MB (source code: 14,514 lines across 30 Python modules)
**Technology Stack**: Python 3.7+, tkinter, pandas, PyPDF2, pywin32, lxml
**Current Version**: V2.3 (Enhanced expanded view with batch processing)

---

## 1. Main Application Entry Point

### Primary Entry Point
- **File**: `/mnt/c/code/Document Manager/run_app.py` (v1.0)
- **Latest Entry Point**: `/mnt/c/code/Document Manager/run_v2_3.py` (v2.3)

### Entry Point Flow
```
run_app.py (or run_v2_3.py)
    ↓
sys.path.insert(0, src/)
    ↓
from main import main (or from main_v2_3 import main)
    ↓
DocumentManagerApp.__init__()
    ↓
root.mainloop()  [tkinter main loop]
```

### Version History
- **v1.0** (`run_app.py` → `src/main.py`): Basic CSV-PDF correlation with simple calendar
- **v2.1** (`run_v2_1.py` → `src/main_v2_1.py`): Enhanced database with relationships
- **v2.2** (`run_v2_2.py` → `src/main_v2_2.py`): Statistics calendar widget added
- **v2.3** (`run_v2_3.py` → `src/main_v2_3.py`): Enhanced expanded view + batch processing ⭐ LATEST

---

## 2. Key Files & Directories Required for Installation

### Core Application Structure
```
Document Manager/
├── run_v2_3.py                    # MAIN LAUNCHER (entry point)
├── requirements.txt               # Python dependencies
│
├── src/                           # Core application modules (14,514 lines)
│   ├── __init__.py
│   ├── main_v2_3.py              # Main application logic (v2.3)
│   ├── main_v2_2.py              # Main application logic (v2.2)
│   ├── main_v2_1.py              # Main application logic (v2.1)
│   ├── main.py                   # Main application logic (v1.0)
│   │
│   ├── pdf_processor.py           # PDF text extraction & sales order detection
│   ├── enhanced_database_v2.py    # SQLite database with relationships
│   ├── relationship_manager.py    # Order-PDF relationship tracking
│   ├── word_template_processor.py # Word document generation
│   │
│   ├── statistics_calendar_widget.py    # 10-day calendar display
│   ├── two_week_calendar_widget.py      # Alternative calendar view
│   ├── calendar_widget.py               # Basic weekday calendar
│   ├── enhanced_expanded_view.py        # Detailed order view (v2.3)
│   ├── enhanced_search_view.py          # Search functionality
│   │
│   ├── network_printer_manager.py      # Network printer support
│   ├── network_batch_print.py          # Batch printing for network
│   ├── batch_print_with_presets.py     # Preset-based batch printing
│   ├── print_preset_manager.py         # Printer configuration
│   ├── print_preset_ui.py              # Printer UI
│   ├── printer_setup_wizard.py         # Printer setup automation
│   ├── advanced_print_manager.py       # Advanced printing features
│   ├── print_diagnostics.py            # Printer debugging
│   │
│   ├── archive_manager.py         # Archive/backup functionality
│   ├── user_preferences.py        # User settings management
│   ├── error_logger.py            # Error logging
│   ├── log_viewer.py              # Log viewing utility
│   └── verify_template.py         # Template validation
│
├── LABEL TEMPLATE/                # CRITICAL: Word template for labels
│   └── Contract_Lumber_Label_Template.docx  (70KB)
│
├── settings_v2_3.json             # Configuration (v2.3)
├── settings_v2_2.json             # Configuration (v2.2)
├── settings_v2_1.json             # Configuration (v2.1)
├── settings.json                  # Configuration (v1.0)
├── print_presets.json             # Printer presets
│
├── sample csv/                    # Sample data (for testing)
│   └── Export_20251006_090021 (3).htm
│
├── samples/                       # Sample files
│   ├── sample csv/
│   └── sample plots/
│
├── docs/                          # Documentation folder
└── build/ & dist/                 # Build artifacts (optional)
```

### Database Files (Created at Runtime)
- `document_manager_v2.1.db` - SQLite database with relationships, PDF history, processing logs
- `document_manager.log` - Application log file

### Optional Files (Build-related)
- `build/` - PyInstaller build directory
- `dist/` - Compiled executable output
- `installation files/` - Installer staging area

---

## 3. Dependencies & Requirements

### Python Version
- **Required**: Python 3.7+
- **Recommended**: Python 3.9+ for stability

### External Dependencies (from requirements.txt)
```
pandas          # Data import/manipulation (CSV processing)
PyPDF2          # PDF text extraction (sales order extraction)
pywin32         # Windows API (printer management)
lxml            # XML processing (Word template editing)
```

### Built-in Libraries (included with Python)
- `tkinter` - GUI framework (usually pre-installed with Python)
- `sqlite3` - Database engine
- `json` - Configuration file handling
- `logging` - Application logging
- `pathlib` - File path operations
- `re` - Regular expressions
- `datetime` - Date handling
- `typing` - Type hints

### Installation Command
```bash
pip install -r requirements.txt
```

### Additional System Requirements
- **Windows 7+** (pywin32 requires Windows)
- **Microsoft Word** (optional but recommended for label generation)
- **Network Printer Access** (for batch printing features)

---

## 4. Template Files & Resources

### Critical: Word Label Template
- **File**: `/mnt/c/code/Document Manager/LABEL TEMPLATE/Contract_Lumber_Label_Template.docx`
- **Size**: 70KB
- **Purpose**: Used for generating shipping/contract labels via `word_template_processor.py`
- **Status**: MUST be included in installation
- **Usage**: Referenced in `main_v2_3.py`:
  ```python
  self.template_path = os.path.join(root_dir, "LABEL TEMPLATE", 
                                     "Contract_Lumber_Label_Template.docx")
  ```

### Alternative Template
- **File**: `/mnt/c/code/Document Manager/DESIGN FILES/Template.docx`
- **Purpose**: Design reference (optional)

### Sample Data (Optional but Recommended)
- **CSV Samples**: `/mnt/c/code/Document Manager/sample csv/`
- **PDF Samples**: `/mnt/c/code/Document Manager/samples/sample plots/`
- **Purpose**: Testing and demonstration

---

## 5. Configuration Files Used

### Primary Settings File (V2.3)
- **File**: `settings_v2_3.json`
- **Purpose**: Application configuration storage
- **Example Content**:
```json
{
  "html_path": "C:\\code\\Document Manager\\sample csv",
  "pdf_path": "C:/code/Document Manager/samples/sample plots",
  "archive_path": "archive",
  "version": "2.3.0"
}
```

### Configuration Manager (Main_v2_3.py)
- **Class**: `SettingsManagerV23`
- **Handles**: 
  - CSV/PDF folder paths
  - Printer configuration (up to 3 printers)
  - Archive settings
  - User preferences

### Printer Presets
- **File**: `print_presets.json`
- **Purpose**: Predefined printer configurations
- **Example Presets**:
  - "Standard Plot" (both printers enabled)
  - "11x17 Only" (single printer)
  - "24x36 Only" (large format only)

### Settings Inheritance
- V1.0: `settings.json`
- V2.1: `settings_v2.json`
- V2.2: `settings_v2_2.json`
- V2.3: `settings_v2_3.json` ⭐ CURRENT

---

## 6. Comprehensive Application Structure Overview

### Application Layers

#### Presentation Layer
```
tkinter GUI Components
├── main_v2_3.py (Main Application)
├── statistics_calendar_widget.py (10-box calendar)
├── enhanced_expanded_view.py (Detailed order view)
├── enhanced_search_view.py (Search interface)
└── print_preset_ui.py (Printer configuration UI)
```

#### Business Logic Layer
```
Core Processing
├── pdf_processor.py (Extract sales orders from PDFs)
├── word_template_processor.py (Generate labels)
├── relationship_manager.py (Link orders to PDFs)
├── archive_manager.py (Archive processing)
└── user_preferences.py (User settings)
```

#### Data Layer
```
Database & Storage
├── enhanced_database_v2.py (Relationships, history, logs)
├── database_manager.py (Legacy DB operations)
└── storage: document_manager_v2.1.db (SQLite)
```

#### Printing Layer
```
Print Management
├── network_printer_manager.py (Network printer detection)
├── network_batch_print.py (Batch printing)
├── batch_print_with_presets.py (Preset-based printing)
├── printer_setup_wizard.py (Automated setup)
└── print_preset_manager.py (Preset storage)
```

#### Utility & Support
```
Diagnostics & Logging
├── print_diagnostics.py (Printer troubleshooting)
├── error_logger.py (Error tracking)
├── log_viewer.py (View logs)
└── verify_template.py (Template validation)
```

### Data Flow Diagram
```
CSV Import
    ↓
[PDF Processor] ← Scans PDF folder
    ↓
[Sales Order Extraction] (filename or content)
    ↓
[Relationship Manager] ← Links to CSV orders
    ↓
[Enhanced Database V2] ← Stores relationships & history
    ↓
[Calendar Widget] ← Displays unprocessed items
    ↓
[User Selection] ← Click date to view details
    ↓
[Enhanced Expanded View] ← Categorized view (Green/Red/Gray)
    ├→ Green (Ready): View PDF links
    ├→ Red (Missing PDF): Browse for PDF
    └→ Gray (Processed): History
    ↓
[Batch Print] ← Print All or individual
    ↓
[Word Template Processor] → Generate labels
    ↓
[Printer Manager] ← Send to printer
    ↓
[Archive Manager] ← Move processed to archive
    ↓
Database updated: Marked as processed
```

### Key Features by Component

#### PDF Processor (pdf_processor.py)
- Extracts sales order numbers from:
  - PDF filenames (pattern matching)
  - PDF content (text extraction using PyPDF2)
- Patterns supported: SO, Sales Order, Job, Project, Order Number
- Validation: 7-digit numbers preferred, 3-20 char range allowed

#### Relationship Manager (relationship_manager.py)
- Creates bidirectional links between CSV orders and PDF files
- Tracks PDF change history (attach, replace, remove)
- Maintains processing status per relationship
- Generates unique relationship IDs

#### Enhanced Database V2 (enhanced_database_v2.py)
- **relationships**: Core order-PDF links with processing status
- **pdf_change_history**: Audit trail of PDF modifications
- **processing_log**: Sync and processing records
- **search_history**: User search tracking
- **archive_log**: Archive operations
- **app_settings**: Key-value configuration storage
- Features: WAL mode for network compatibility

#### Word Template Processor (word_template_processor.py)
- Uses python-docx to modify Contract_Lumber_Label_Template.docx
- Fills in order details automatically
- Supports multiple data field mappings
- Generates output for network printing

#### Archive Manager (archive_manager.py)
- Moves processed PDFs to archive folder
- Preserves metadata alongside archived files
- Configurable archive location

#### Calendar Widgets
- **statistics_calendar_widget.py**: Main 10-box calendar (v2.2+)
  - Shows Mon-Fri only
  - Daily statistics (total, processed, unprocessed)
  - Color-coded boxes
  - Click to expand details
  
- **enhanced_expanded_view.py**: Detailed order listing (v2.3)
  - Categorized by status (Green/Red/Gray)
  - PDF attachment interface
  - Individual/batch processing
  - Real-time category updates

---

## 7. Installation Package Requirements Checklist

### Required Files for Distribution
```
✓ run_v2_3.py (or chosen entry point)
✓ src/ directory with all 30 .py modules
✓ LABEL TEMPLATE/Contract_Lumber_Label_Template.docx
✓ requirements.txt
✓ settings_v2_3.json (default template)
✓ print_presets.json (printer presets)
✓ README.md (documentation)
```

### Optional but Recommended
```
✓ sample csv/ (example data)
✓ samples/ (test PDFs)
✓ docs/ (documentation)
? settings_v2.json, settings_v2_2.json (legacy support)
? main_v2_1.py, main_v2_2.py (legacy versions)
? DESIGN FILES/ (design references)
```

### Generated at Runtime (Do Not Include)
```
✗ document_manager_v2.1.db (created fresh)
✗ document_manager.log (created fresh)
✗ build/ directory (PyInstaller temp)
✗ dist/ directory (PyInstaller output)
✗ __pycache__/ directories
✗ *.pyc files
```

### Excluded from Distribution
```
✗ .git/ (version control)
✗ .claude/ (IDE configuration)
✗ .gitignore
✗ archive/ (runtime data)
✗ installation files/ (build staging)
```

---

## 8. Installation Workflow Recommendation

### For Windows Executable (.exe)
Use PyInstaller with the following approach:

1. **One-File Distribution**
   ```bash
   pyinstaller --onefile \
     --windowed \
     --add-data "LABEL TEMPLATE:LABEL TEMPLATE" \
     --add-data "settings_v2_3.json:." \
     --add-data "print_presets.json:." \
     --hidden-import=pywin32 \
     --hidden-import=lxml \
     run_v2_3.py
   ```

2. **Folder Distribution** (Alternative, faster startup)
   ```bash
   pyinstaller --onedir \
     --windowed \
     --add-data "LABEL TEMPLATE:LABEL TEMPLATE" \
     --add-data "settings_v2_3.json:." \
     --add-data "print_presets.json:." \
     run_v2_3.py
   ```

### For Portable Installation (Recommended for Network Deployment)
```
DocumentManager/
├── python.exe (or python portable)
├── DLLs/
├── run_v2_3.py
├── src/
├── LABEL TEMPLATE/
├── settings_v2_3.json
├── print_presets.json
└── requirements.txt
```

### For Standard Python Installation
```
pip install -r requirements.txt
python run_v2_3.py
```

---

## 9. Runtime Behavior & Data Persistence

### Database Creation
- Created on first run: `document_manager_v2.1.db`
- Location: Application root directory (portable)
- Contains: CSV orders, PDF relationships, processing history

### Settings Persistence
- Settings file: `settings_v2_3.json`
- Location: Application root directory
- Auto-saved after configuration changes
- Contains: CSV/PDF paths, printer settings

### Log File
- Location: Application root directory
- Filename: `document_manager.log`
- Contains: Detailed operation logs, errors, debugging info
- Useful for troubleshooting PDF extraction issues

### Archive Structure
- Default location: `archive/` subdirectory
- Configurable via settings
- Contains: Processed PDFs with metadata
- Metadata: `.json` files alongside archived PDFs

---

## 10. Key Dependencies Explained

### pandas
- **Purpose**: Load and manipulate CSV files from Bistrack
- **Usage**: `pd.read_csv()`, data filtering and joining
- **Critical**: Yes

### PyPDF2
- **Purpose**: Extract text from PDF files
- **Usage**: Read PDF content to find sales order numbers
- **Critical**: Yes

### pywin32
- **Purpose**: Windows printer access and control
- **Usage**: Enumerate printers, send print jobs
- **Critical**: Yes (Windows-only dependency)

### lxml
- **Purpose**: Parse and modify XML in Word documents
- **Usage**: Edit docx files (Word template processor)
- **Critical**: Yes (for label generation)

---

## 11. Summary: What Goes Into the Installer

### Minimum Viable Package
```
Document Manager Installer/
├── run_v2_3.py
├── requirements.txt
├── src/
│   └── [all 30 Python modules]
├── LABEL TEMPLATE/
│   └── Contract_Lumber_Label_Template.docx
├── settings_v2_3.json
└── print_presets.json
```

### Recommended Full Package
```
Document Manager Installer/
├── run_v2_3.py
├── requirements.txt
├── README.md
├── src/
│   └── [all 30 Python modules]
├── LABEL TEMPLATE/
│   └── Contract_Lumber_Label_Template.docx
├── settings_v2_3.json
├── print_presets.json
├── sample csv/
│   └── [sample data files]
├── samples/
│   └── [sample PDFs for testing]
└── docs/
    └── [user documentation]
```

### PyInstaller Executable Package
```
DocumentManager/
├── DocumentManager.exe (generated)
├── run_v2_3.py
├── src/
├── LABEL TEMPLATE/
├── settings_v2_3.json
├── print_presets.json
└── [supporting DLLs from PyInstaller]
```

---

## Key Insights for Installer Design

1. **Portable Application**: Designed to work from any folder without installation
2. **Relative Paths**: Template and config paths resolve relative to script location
3. **Database Created at Runtime**: No need to include database file
4. **Network-Compatible**: WAL mode database supports network shares
5. **Windows-Only**: Requires Windows and Microsoft Word integration
6. **Configuration Flexibility**: Settings stored in JSON, easily customizable
7. **Modular Architecture**: Can run different versions (v1.0, v2.1, v2.2, v2.3)
8. **Batch Processing**: Designed for high-volume document handling
9. **Printer Integration**: Sophisticated print queue management via pywin32
10. **Extensible Design**: Easy to add new processing rules and features

