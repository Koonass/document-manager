# Document Manager V2.3 - Helper Tools Guide

## Quick Reference of All Available Tools

### Installation & Setup Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **INSTALL.bat** | Automated installation | First-time setup - installs all packages |
| **START_APP.bat** | Launch application | Every time you want to run the app |
| **FIX_DEPENDENCIES.bat** | Fix missing packages | When app says "missing dependencies" |
| **DIAGNOSE_PYTHON.bat** | Find Python issues | When packages seem installed but app won't run |

### Printer & Label Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **LIST_ALL_PRINTERS.bat** | Show available printers | Before configuring printer settings |
| **diagnose_label_printing.py** | Check label setup | When folder labels won't print |
| **FIX_BOOKMARK_MISMATCH.py** | Fix template bookmarks | When diagnose shows bookmark errors |
| **verify_template.py** | Check Word template | Verify template has correct bookmarks |

### Package Building Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **CREATE_DISTRIBUTION_PACKAGE.bat** | Build clean installer | Creating package for distribution |

### Documentation Files

| File | Content |
|------|---------|
| **QUICK_FIX_DEPENDENCIES.txt** | Fast solution for missing dependencies |
| **INSTALLATION_INSTRUCTIONS.md** | Complete installation guide |
| **MANUAL_FIX_GUIDE.md** | Detailed troubleshooting for Python/pip issues |
| **FOLDER_PRINTING_GUIDE.md** | How to set up folder label printing |
| **LABEL_PRINTING_TROUBLESHOOTING.md** | Common label printing issues |
| **CLEAN_INSTALLATION_PACKAGE.md** | How to create distribution packages |
| **QUICK_START.md** | Quick reference for users and IT |
| **SUMMARY_OF_CHANGES.md** | What was fixed and changed |
| **HELPER_TOOLS_GUIDE.md** | This file - overview of all tools |

---

## Common Scenarios

### Scenario 1: First Time Installation

```
1. INSTALL.bat          → Install packages
2. START_APP.bat        → Run application
3. Configure paths      → In application settings
4. LIST_ALL_PRINTERS.bat → See available printers (optional)
```

### Scenario 2: "Missing Dependencies" Error

```
Option A (Fast):
  1. FIX_DEPENDENCIES.bat → Fixes automatically

Option B (Diagnostic):
  1. DIAGNOSE_PYTHON.bat → See the problem
  2. FIX_DEPENDENCIES.bat → Fix it
```

### Scenario 3: Label Printing Not Working

```
1. diagnose_label_printing.py → Identify the issue
2. FIX_BOOKMARK_MISMATCH.py   → Fix if needed
3. LIST_ALL_PRINTERS.bat      → Verify printer exists
4. Test in application        → Print one label
```

### Scenario 4: Deploying to Multiple Computers

```
1. CREATE_DISTRIBUTION_PACKAGE.bat → Build clean package
2. Copy folder to target machines
3. Each user runs INSTALL.bat
4. Each user runs START_APP.bat
```

---

## Tool Details

### INSTALL.bat
**What it does:**
- Searches for Python installation
- Upgrades pip
- Installs pandas, PyPDF2, pywin32, lxml
- Runs pywin32 post-install
- Creates START_APP.bat
- Verifies installation

**Run as:** Administrator (recommended)

**Output:** Creates START_APP.bat

---

### FIX_DEPENDENCIES.bat
**What it does:**
- Finds which Python START_APP.bat will use
- Installs packages to that specific Python
- Updates START_APP.bat with correct path
- Verifies all packages work

**When needed:**
- pip says "requirements satisfied" but app won't run
- After installing a new Python version
- When switching between Python installations

**Run as:** Normal user (or Administrator if permission issues)

---

### DIAGNOSE_PYTHON.bat
**What it does:**
- Shows all Python commands (python, python3, py)
- Lists which Python each command uses
- Tests if packages are installed in each Python
- Finds all Python installations on C: drive
- Identifies mismatches

**Output:** Diagnostic report showing where packages are vs where app looks

**Use when:** You want to understand the problem before fixing

---

### LIST_ALL_PRINTERS.bat
**What it does:**
- Lists all printers installed on computer
- Shows default printer
- Displays printer comments/descriptions

**Use when:**
- Configuring folder printer in application
- Troubleshooting "printer not found" errors
- Verifying printer name spelling

---

### diagnose_label_printing.py
**What it does:**
- Checks if template files exist
- Verifies Word template bookmarks
- Checks print preset configuration
- Identifies bookmark mismatches
- Validates code configuration

**How to run:**
```cmd
python diagnose_label_printing.py
```

**Output:** Detailed report with specific issues found

---

### FIX_BOOKMARK_MISMATCH.py
**What it does:**
- Backs up word_template_processor.py
- Updates bookmark names in code
- Matches code to template bookmarks
- Verifies changes

**How to run:**
```cmd
python FIX_BOOKMARK_MISMATCH.py
```

**Interactive:** Asks for confirmation before making changes

**Creates:** Backup file with timestamp

---

### verify_template.py
**What it does:**
- Opens Word template
- Lists all bookmarks found
- Checks required bookmarks
- Shows which are missing
- Validates template is ready

**How to run:**
```cmd
python src\verify_template.py
```

**Requires:** Microsoft Word installed

---

### CREATE_DISTRIBUTION_PACKAGE.bat
**What it does:**
- Creates "Document_Manager_v2.3_Distribution" folder
- Copies only essential files (14 core + docs)
- Excludes test files, backups, old versions
- Creates README_FIRST.txt
- Shows file list

**Use when:** Creating package to distribute to other users

**Output:** Clean folder ready to ZIP and share

---

## File Locations Reference

### Where things are:

```
Document Manager/
│
├── *.bat                    ← Helper tools (double-click these)
├── *.py                     ← Python scripts (run with: python <script>.py)
├── *.md                     ← Documentation (read in text editor)
├── *.txt                    ← Quick guides (read in notepad)
│
├── src/                     ← Application source code
│   ├── main_v2_3.py        ← Main application
│   ├── word_template_processor.py ← Label printing logic
│   └── *.py                ← Other modules
│
├── LABEL TEMPLATE/          ← Word template for labels
│   └── Contract_Lumber_Label_Template.docx
│
├── settings_v2_3.json      ← User settings (auto-created)
├── document_manager_v2.3.log ← Error log (auto-created)
└── archive/                ← Processed orders (auto-created)
```

---

## Quick Command Reference

### Installation Commands

```cmd
REM Full installation
INSTALL.bat

REM Fix dependencies only
FIX_DEPENDENCIES.bat

REM Manual installation
python -m pip install pandas PyPDF2 pywin32 lxml
python -m pywin32_postinstall -install
```

### Running the Application

```cmd
REM Normal way
START_APP.bat

REM Manual way
python run_v2_3.py

REM With specific Python version
py -3.12 run_v2_3.py
```

### Diagnostics

```cmd
REM Check Python issues
DIAGNOSE_PYTHON.bat

REM Check label printing
python diagnose_label_printing.py

REM List printers
LIST_ALL_PRINTERS.bat

REM Verify template
python src\verify_template.py
```

### Verification

```cmd
REM Check Python version
python --version

REM Check if packages installed
python -c "import pandas; import PyPDF2; import win32com.client; import lxml; print('All OK')"

REM Check where Python is
python -c "import sys; print(sys.executable)"

REM List all packages
python -m pip list
```

---

## Getting Help

### If you're stuck:

1. **Check the log file:**
   ```
   document_manager_v2.3.log
   ```

2. **Run diagnostics:**
   ```cmd
   DIAGNOSE_PYTHON.bat
   python diagnose_label_printing.py
   ```

3. **Read the quick fix:**
   ```
   QUICK_FIX_DEPENDENCIES.txt
   ```

4. **Check detailed guides:**
   - MANUAL_FIX_GUIDE.md
   - INSTALLATION_INSTRUCTIONS.md
   - FOLDER_PRINTING_GUIDE.md

---

## Tips

### Always use `python -m pip` not just `pip`
This ensures packages install to the correct Python.

### Run batch files by double-clicking
Don't run them from a terminal unless instructed.

### Check the log file for errors
Most errors are logged to `document_manager_v2.3.log`

### Keep backups
Tools that modify files create `.backup_*` files automatically.

### Use the automated tools first
Try FIX_DEPENDENCIES.bat before manual troubleshooting.

---

**Last Updated:** November 2024
**Version:** 2.3.0
