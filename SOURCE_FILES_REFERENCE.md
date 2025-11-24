# Document Manager - Source Files Reference Guide

Complete file-by-file documentation of all 30 Python modules and supporting files.

## Core Application Modules

### Entry Points (Launchers)
| File | Lines | Purpose |
|------|-------|---------|
| `run_app.py` | 26 | V1.0 launcher - initializes main.py |
| `run_v2_1.py` | 36 | V2.1 launcher - enhanced database support |
| `run_v2_2.py` | 45 | V2.2 launcher - statistics calendar |
| `run_v2_3.py` | 63 | V2.3 launcher - enhanced view + batch print (LATEST) |

### Main Application Windows
| File | Lines | Purpose |
|------|-------|---------|
| `src/main.py` | 238 | V1.0 - Basic CSV-PDF correlation with weekday calendar |
| `src/main_redesign.py` | 450 | Alternative V1.0 redesign |
| `src/main_v2_1.py` | 580 | V2.1 - Enhanced DB relationships |
| `src/main_v2_2.py` | 700 | V2.2 - Statistics calendar integration |
| `src/main_v2_3.py` | 1200+ | V2.3 - Main window with expanded view, batch processing (LATEST) |

### PDF Processing
| File | Lines | Purpose |
|------|-------|---------|
| `src/pdf_processor.py` | 213 | Extract sales order numbers from PDFs using regex and PyPDF2 |

### Database Management
| File | Lines | Purpose |
|------|-------|---------|
| `src/database_manager.py` | 330 | V1.0 basic database operations for tracking processed files |
| `src/enhanced_database_manager.py` | 520 | V2.0 enhanced with relationship tracking |
| `src/enhanced_database_v2.py` | 780 | V2.1+ database with relationships, history, processing logs, WAL mode |

### Relationship Management
| File | Lines | Purpose |
|------|-------|---------|
| `src/relationship_manager.py` | 430 | Links CSV orders to PDFs, tracks changes, manages status |

### Calendar & UI Widgets
| File | Lines | Purpose |
|------|-------|---------|
| `src/calendar_widget.py` | 310 | Basic weekday-only calendar widget (V1.0) |
| `src/two_week_calendar_widget.py` | 560 | Two-week calendar view alternative |
| `src/statistics_calendar_widget.py` | 830 | 10-box statistics calendar (V2.2+) with daily totals |
| `src/enhanced_expanded_view.py` | 950 | Detailed order view with categorization (Green/Red/Gray) - V2.3 |
| `src/enhanced_search_view.py` | 610 | Advanced search and filtering interface |

### Document/Label Processing
| File | Lines | Purpose |
|------|-------|---------|
| `src/word_template_processor.py` | 520 | Modify Word .docx templates, auto-fill fields, generate labels |
| `src/verify_template.py` | 180 | Validate template file structure and field mappings |

### Printing & Print Management
| File | Lines | Purpose |
|------|-------|---------|
| `src/print_preset_manager.py` | 300 | Load/save printer preset configurations |
| `src/print_preset_ui.py` | 390 | UI for configuring printer presets |
| `src/printer_setup_wizard.py` | 750 | Automated printer discovery and setup |
| `src/batch_print_with_presets.py` | 810 | Batch printing using preset configurations |
| `src/advanced_print_manager.py` | 560 | Advanced printing features and options |
| `src/network_printer_manager.py` | 430 | Network printer detection and management |
| `src/network_batch_print.py` | 590 | Batch printing for network printers |
| `src/print_diagnostics.py` | 330 | Printer troubleshooting and diagnostics |

### Archive & Data Management
| File | Lines | Purpose |
|------|-------|---------|
| `src/archive_manager.py` | 340 | Move processed PDFs to archive, store metadata |
| `src/user_preferences.py` | 220 | Manage user settings and preferences |

### Utilities & Support
| File | Lines | Purpose |
|------|-------|---------|
| `src/error_logger.py` | 130 | Centralized error logging system |
| `src/log_viewer.py` | 180 | View and search application logs |

### Package Init
| File | Lines | Purpose |
|------|-------|---------|
| `src/__init__.py` | 1 | Package initialization (mostly empty) |

---

## Configuration & Data Files

### Settings Files (Version Specific)
| File | Purpose |
|------|---------|
| `settings.json` | V1.0 configuration template |
| `settings_v2.json` | V2.1 configuration template |
| `settings_v2_2.json` | V2.2 configuration template |
| `settings_v2_3.json` | V2.3 configuration template (CURRENT) |

### Printer Configuration
| File | Content |
|------|---------|
| `print_presets.json` | 3 printer presets (Standard Plot, 11x17 Only, 24x36 Only) |

### Runtime Data (Created at Runtime)
| File | Created By | Purpose |
|------|-----------|---------|
| `document_manager_v2.1.db` | enhanced_database_v2.py | SQLite database (relationships, history, logs) |
| `document_manager.log` | logging module | Application debug and error logs |
| `archive/` | archive_manager.py | Processed PDFs and metadata |

---

## Supporting Files & Directories

### Documentation
| File | Purpose |
|------|---------|
| `README.md` | Project overview and basic usage |
| `INSTALLER_REQUIREMENTS.md` | Detailed installer specifications |
| `QUICK_INSTALLER_SUMMARY.txt` | Quick reference guide |
| `SOURCE_FILES_REFERENCE.md` | This file - complete file reference |

### Resource Files
| File/Folder | Purpose |
|-----------|---------|
| `LABEL TEMPLATE/Contract_Lumber_Label_Template.docx` | Word template for shipping labels |
| `DESIGN FILES/Template.docx` | Design reference template |
| `docs/` | Additional documentation |
| `sample csv/` | Example CSV data for testing |
| `samples/sample csv/` | Additional sample CSV files |
| `samples/sample plots/` | Sample PDF files for testing |
| `assets/` | Application assets (images, icons) |
| `config/` | Configuration templates |

---

## Dependency Graph

### Critical Dependencies
```
main_v2_3.py
├─ requires─→ pdf_processor.py ─────────────┐
├─ requires─→ enhanced_database_v2.py ──────┐
├─ requires─→ relationship_manager.py ──────┤
├─ requires─→ statistics_calendar_widget.py ├─ requires PyPDF2, pandas, lxml
├─ requires─→ enhanced_expanded_view.py ────┤
├─ requires─→ word_template_processor.py ───┤
├─ requires─→ batch_print_with_presets.py ──┤
├─ requires─→ archive_manager.py ───────────┤
├─ requires─→ user_preferences.py ──────────┘
└─ requires─→ print_preset_manager.py
```

### Database Dependencies
```
enhanced_database_v2.py
├─ provides─→ Tables: relationships, pdf_change_history, processing_log, ...
├─ used by─→ relationship_manager.py
├─ used by─→ main_v2_3.py
└─ used by─→ archive_manager.py
```

### PDF Processing Dependencies
```
pdf_processor.py (uses PyPDF2)
├─ extract_sales_order() ──→ filename extraction
├─ extract_from_filename() ──→ regex patterns
├─ extract_from_content() ──→ PDF text extraction
└─ scan_folder() ──→ batch processing
```

---

## Data Flow Between Modules

### Import Workflow
```
User Action: Import CSV
        ↓
main_v2_3.py: filedialog.askopenfilename()
        ↓
pandas.read_csv() [built-in]
        ↓
enhanced_database_v2.py: store_csv_data()
        ↓
SQLite INSERT into relationships table
```

### PDF Sync Workflow
```
User Action: Sync PDF Folder
        ↓
main_v2_3.py: filedialog.askdirectory()
        ↓
pdf_processor.py: scan_folder()
  ├─ extract_from_filename() [regex]
  └─ extract_from_content() [PyPDF2]
        ↓
relationship_manager.py: create_relationships()
        ↓
enhanced_database_v2.py: store_relationships()
        ↓
Calendar Widget: display results
```

### Printing Workflow
```
User Action: Print All (Green Category)
        ↓
enhanced_expanded_view.py: print_all_clicked()
        ↓
batch_print_with_presets.py: batch_print()
        ↓
word_template_processor.py: generate_label()
        ↓
printer_setup_wizard.py / network_printer_manager.py
        ↓
pywin32: send to Windows print queue
        ↓
archive_manager.py: move_to_archive()
        ↓
enhanced_database_v2.py: mark_processed()
```

---

## Configuration Inheritance

### Settings Manager Chain
```
V2.3 Settings (main_v2_3.py)
├─ Class: SettingsManagerV23
├─ File: settings_v2_3.json
├─ Default paths handled by SettingsManagerV23
├─ Fallback: SettingsManagerV22 (if available)
├─ Fallback: SettingsManager (V1.0)
└─ Hardcoded defaults (last resort)
```

### Printer Configuration Chain
```
print_presets.json
├─ "Standard Plot" (default)
│  ├─ printer_11x17_enabled: true
│  ├─ printer_24x36_enabled: true
│  └─ folder_label_enabled: true
├─ "11x17 Only"
│  ├─ printer_11x17_enabled: true
│  ├─ printer_24x36_enabled: false
│  └─ folder_label_enabled: true
└─ "24x36 Only"
   ├─ printer_11x17_enabled: false
   ├─ printer_24x36_enabled: true
   └─ folder_label_enabled: true
```

---

## Module Sizes & Complexity

### Code Volume
```
Total Source Code: 14,514 lines across 30 modules

By Category:
  Main Applications (5 versions):     2,650 lines
  PDF & Database Processing:          2,420 lines
  Calendar & UI Widgets:              2,700 lines
  Printing & Presets:                 3,800 lines
  Archive & Support:                  2,944 lines

Largest Modules:
  1. main_v2_3.py              1,200+ lines
  2. enhanced_expanded_view.py    950 lines
  3. statistics_calendar_widget.py 830 lines
  4. enhanced_database_v2.py      780 lines
  5. printer_setup_wizard.py      750 lines
```

---

## How to Extend the Application

### Adding a New Feature
1. **UI Component**: Add method to main_v2_3.py or create new widget file
2. **Business Logic**: Create new module or extend existing (e.g., archive_manager.py)
3. **Database**: Update enhanced_database_v2.py with new table if needed
4. **Configuration**: Add settings to settings_v2_3.json and SettingsManagerV23
5. **Testing**: Add test with sample data

### Adding a New Printer Preset
1. Edit `print_presets.json`
2. Add new preset object with enabled flags and copy counts
3. Restart application or use printer_setup_wizard.py

### Adding a New Order Field to Labels
1. Edit `LABEL TEMPLATE/Contract_Lumber_Label_Template.docx` in Word
2. Add merge field: Insert → Field → Merge Field
3. Update `word_template_processor.py` field mapping dictionary

### Modifying PDF Extraction Logic
1. Edit `pdf_processor.py`
2. Update `order_patterns` list with new regex patterns
3. Adjust validation in `validate_order_number()`

---

## Key Algorithms & Patterns

### Sales Order Extraction (pdf_processor.py)
1. **Pattern Matching**: Try common patterns (SO:, Sales Order:, etc.)
2. **Fallback 7-digit**: Look for exactly 7-digit sequences
3. **Content Fallback**: Extract from PDF text if filename fails
4. **Validation**: Ensure 3-20 chars, has digits, not all same char

### Relationship Creation (relationship_manager.py)
1. **Generate UUID**: Unique relationship_id
2. **Find CSV Match**: Search CSV data for matching order
3. **Store Metadata**: Save complete CSV row as JSON
4. **Track History**: Create initial pdf_change_history entry

### Calendar Display (statistics_calendar_widget.py)
1. **Weekly Grid**: 7-column grid (Mon-Fri visible, Sat-Sun hidden)
2. **Statistics**: Count processed/unprocessed per day
3. **Color Coding**: Color boxes based on counts
4. **Interactive**: Expand details on click

### Database Synchronization (enhanced_database_v2.py)
1. **WAL Mode**: Write-Ahead Logging for network compatibility
2. **Transactions**: Atomic operations for data integrity
3. **Relationships**: Normalize data to avoid duplicates
4. **Audit Trail**: Track all changes via history tables

---

## Error Handling Strategy

### Application-Level (main_v2_3.py)
- Try/except blocks around user actions
- Messagebox dialogs for user-facing errors
- Logging at ERROR and WARNING levels

### Module-Level (individual modules)
- Validation before database operations
- File existence checks before opening
- Type checking for inputs

### Database-Level (enhanced_database_v2.py)
- SQL error catching and logging
- Automatic table creation on first run
- WAL mode for crash recovery

### User Feedback
- Status bar messages (quick feedback)
- Messagebox dialogs (confirmation/errors)
- Log file for debugging (detailed)

---

## Performance Considerations

### PDF Extraction
- Processes one PDF at a time
- Caches results to database
- Limited to first 3 pages per PDF (scanning only)

### Database Queries
- Indexed on order_number for fast lookups
- WAL mode allows concurrent reads
- Archived data kept separate from active

### UI Responsiveness
- Long operations (PDF scan) show progress
- Calendar limited to 2-week display
- Detail view lazy-loads on demand

---

## Security & Data Integrity

### File System
- Relative paths for portability
- Archive folder keeps processed files
- Metadata stored alongside archives

### Database
- SQLite encrypted optional (not implemented)
- WAL mode provides crash recovery
- Foreign keys enforce referential integrity

### User Input
- File dialogs only (no text input validation needed)
- Settings loaded from JSON (no code execution)
- PDF filenames validated before database storage

---

## Maintenance & Troubleshooting

### Common Issues & Fixes
| Issue | File | Solution |
|-------|------|----------|
| PDF not extracting order | pdf_processor.py | Check filename format or PDF structure |
| Database locked | enhanced_database_v2.py | Check for network issues or concurrent access |
| Template not found | word_template_processor.py | Verify LABEL TEMPLATE folder structure |
| Printer not appearing | printer_setup_wizard.py | Check Windows printer settings |
| Settings not saving | user_preferences.py | Check file permissions on settings_v2_3.json |

### Debug Logging
- Log file: `document_manager.log`
- Detailed operation logs in processing_log table
- PDF extraction attempts logged

---

## Version Progression

### From V1.0 to V2.3
```
V1.0 (2023-Q3)
├─ Basic CSV-PDF matching
├─ Simple weekday calendar
└─ Database tracking

V2.1 (2023-Q4)
├─ Add relationship_manager.py
├─ Enhanced database schema
├─ Unique relationship IDs
└─ PDF change history

V2.2 (2024-Q1)
├─ Add statistics_calendar_widget.py
├─ 10-box calendar display
├─ Daily statistics
└─ Color-coded boxes

V2.3 (2024-Q3) ← CURRENT
├─ Add enhanced_expanded_view.py
├─ Categorized order display (Green/Red/Gray)
├─ Batch processing
├─ PDF attachment UI
├─ Auto label generation
└─ Network printer support
```

---

## File Checklist for Deployment

For building a complete installation package:

### Required (14 files minimum)
- [x] run_v2_3.py
- [x] src/__init__.py
- [x] src/main_v2_3.py
- [x] src/pdf_processor.py
- [x] src/enhanced_database_v2.py
- [x] src/relationship_manager.py
- [x] src/statistics_calendar_widget.py
- [x] src/enhanced_expanded_view.py
- [x] src/word_template_processor.py
- [x] src/batch_print_with_presets.py
- [x] src/archive_manager.py
- [x] src/printer_setup_wizard.py
- [x] LABEL TEMPLATE/Contract_Lumber_Label_Template.docx
- [x] requirements.txt
- [x] settings_v2_3.json
- [x] print_presets.json

### Highly Recommended (10 additional files)
- [ ] src/network_printer_manager.py
- [ ] src/print_preset_manager.py
- [ ] src/print_diagnostics.py
- [ ] src/error_logger.py
- [ ] src/log_viewer.py
- [ ] src/user_preferences.py
- [ ] src/archive_manager.py (backup)
- [ ] README.md
- [ ] INSTALLER_REQUIREMENTS.md
- [ ] sample csv/ folder

### Optional (for complete package)
- [ ] src/main_v2_1.py and src/main_v2_2.py (legacy)
- [ ] samples/ folder
- [ ] docs/ folder
- [ ] DESIGN FILES/ folder

