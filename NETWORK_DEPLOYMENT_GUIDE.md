# Network Deployment Guide

## Document Manager - Network Printer System v2.0

This guide is for IT administrators deploying the Document Manager application in a multi-user network environment.

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Initial Setup (IT Admin)](#initial-setup-it-admin)
5. [User Deployment](#user-deployment)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Overview

The new network printer system provides:

- **Centralized Configuration**: IT sets up printers once, applies to all users
- **Auto-Discovery**: Automatically detects network printers
- **User Preferences**: Per-user settings without modifying network config
- **Clear Error Messages**: Helpful messages when printers are offline/unavailable
- **Diagnostic Tools**: Built-in tools for troubleshooting

### Architecture

```
┌─────────────────────────────────────────┐
│  network_printers.json                  │  ← Network-wide config (IT manages)
│  - Printer definitions                  │
│  - Template path                        │
│  - Centralized for all users            │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  user_preferences.json                  │  ← Per-user settings
│  - Default copies                       │
│  - Preferred printers                   │
│  - Last preset used                     │
└─────────────────────────────────────────┘
```

---

## System Requirements

### Server/Network Requirements
- Windows Server or network-accessible shared folder
- Network printers properly configured and accessible
- Shared network location for:
  - Application files
  - Configuration files (network_printers.json)
  - Folder label template (.docx)

### Client Requirements
- Windows 10/11
- Python 3.8 or higher
- Required Python packages:
  - `pywin32` (Windows COM interface)
  - `PyPDF2` (PDF handling)
  - `tkinter` (UI - usually included with Python)
- Network access to printers
- Read access to shared application folder

---

## Pre-Deployment Checklist

### Before You Begin

- [ ] All network printers are installed and configured
- [ ] Printers are accessible from client machines
- [ ] Large format plotter (24×36) is network-accessible
- [ ] Label printer is configured
- [ ] Folder label template (.docx) is created with proper bookmarks
- [ ] Shared network folder is created for application
- [ ] Users have read access to shared folder

### Printer Verification

Test each printer from a client machine:

```cmd
# List all available printers
wmic printer get name

# Test print to specific printer
# (Replace PRINTER_NAME with actual printer name)
notepad /p "\\PRINTER_NAME" testfile.txt
```

---

## Initial Setup (IT Admin)

### Step 1: Install Application

1. **Copy application to shared network location**
   ```
   \\SERVER\SharedApps\DocumentManager\
   ```

2. **Verify folder structure:**
   ```
   DocumentManager/
   ├── run_v2_3.py
   ├── printer_diagnostics.py
   ├── src/
   │   ├── network_printer_manager.py
   │   ├── printer_setup_wizard.py
   │   ├── network_batch_print.py
   │   ├── user_preferences.py
   │   └── ... (other modules)
   ├── DESIGN FILES/
   │   └── Template.docx (folder label template)
   └── requirements.txt
   ```

3. **Install Python dependencies:**
   ```cmd
   cd \\SERVER\SharedApps\DocumentManager
   pip install -r requirements.txt
   ```

### Step 2: Run Printer Diagnostics

1. **Launch diagnostic tool:**
   ```cmd
   python printer_diagnostics.py
   ```

2. **Review the Overview tab:**
   - Check "Available Printers" count
   - Verify all expected printers are listed
   - Note any missing printers

3. **Review the Available Printers tab:**
   - Verify printer categorization
   - Test connection to critical printers

### Step 3: Run Setup Wizard

1. **Click "Run Setup Wizard"** in diagnostics tool, or run directly:
   ```cmd
   python -c "from src.printer_setup_wizard import run_setup_wizard; run_setup_wizard()"
   ```

2. **Follow wizard steps:**

   **Step 1 - Welcome**
   - Read the overview
   - Click "Next"

   **Step 2 - Discover Printers**
   - Review discovered printers
   - Verify expected printers are found
   - Note categorization (24×36, 11×17, Label, Other)

   **Step 3 - Configure 11×17 Printers**
   - Select all standard printers (11×17 / Tabloid)
   - First selected becomes default
   - Click "Next"

   **Step 4 - Configure 24×36 Printers**
   - Select large format printer(s)
   - IMPORTANT: Verify plotter is selected
   - First selected becomes default
   - Click "Next"

   **Step 5 - Configure Label Printers**
   - Select folder label printer
   - Typically a label printer or standard printer
   - Click "Next"

   **Step 6 - Template Path**
   - Click "Browse"
   - Navigate to: `\\SERVER\SharedApps\DocumentManager\DESIGN FILES\Template.docx`
   - Verify path is network-accessible
   - Click "Next"

   **Step 7 - Review & Save**
   - Review all selections
   - Verify printer names are correct
   - Click "Finish & Save"

3. **Verify configuration file created:**
   ```
   network_printers.json should exist in app folder
   ```

### Step 4: Test Configuration

1. **In diagnostics tool, go to "Connection Tests" tab**

2. **Click "Run Connection Tests"**

3. **Verify all printers show "✓ SUCCESS"**

4. **If any failures:**
   - Check printer name spelling
   - Verify printer is online
   - Test from Windows print dialog
   - Re-run setup wizard if needed

### Step 5: Configure Template

1. **Open template in Word:**
   ```
   \\SERVER\SharedApps\DocumentManager\DESIGN FILES\Template.docx
   ```

2. **Verify bookmarks exist:**
   - `OrderNumber`
   - `Customer`
   - `LotSub`
   - `Level`

3. **Test bookmark access:**
   ```cmd
   python src\verify_template.py
   ```

### Step 6: Set File Permissions

1. **Network config (read-only for users):**
   ```
   network_printers.json → Read-only for users, Full control for IT
   ```

2. **Template (read-only for users):**
   ```
   Template.docx → Read-only for users
   ```

3. **Application files:**
   ```
   All .py files → Read & Execute for users
   ```

4. **User data folder (write access):**
   ```
   Create: \\SERVER\SharedApps\DocumentManager\UserData\
   Users need: Read/Write access
   ```

---

## User Deployment

### Option A: Network Share (Recommended)

Users run application from shared network location:

1. **Create desktop shortcut for users:**
   ```
   Target: \\SERVER\SharedApps\DocumentManager\run_v2_3.py
   Start in: \\SERVER\SharedApps\DocumentManager
   ```

2. **User preferences stored locally:**
   ```
   C:\Users\[USERNAME]\AppData\Local\DocumentManager\user_preferences.json
   ```

### Option B: Local Installation

Copy application to each user's machine:

1. **Copy to local drive:**
   ```
   C:\Program Files\DocumentManager\
   ```

2. **Copy network_printers.json to local app folder**

3. **Update template path to network location:**
   ```json
   {
     "template_path": "\\\\SERVER\\SharedApps\\DocumentManager\\DESIGN FILES\\Template.docx"
   }
   ```

### First Run (Users)

1. **Launch application**

2. **Application will:**
   - Load network printer configuration
   - Create user preferences file
   - Verify printer availability
   - Show warning if printers offline

3. **User can now:**
   - Select orders
   - Configure print jobs
   - Print to network printers

---

## Troubleshooting

### Issue: "No printers detected"

**Cause:** Network printers not installed on client machine

**Solution:**
```cmd
# Add network printer manually
rundll32 printui.dll,PrintUIEntry /in /n "\\SERVER\PRINTER_NAME"
```

### Issue: "Printer offline" or "Not available"

**Cause:** Printer is offline, renamed, or client lost connection

**Solution:**
1. Check printer status in Windows
2. Verify network connectivity
3. Run diagnostics tool: `python printer_diagnostics.py`
4. Test printer connection in "Connection Tests" tab
5. If printer was renamed, re-run setup wizard

### Issue: "Template not found"

**Cause:** Template path incorrect or user lacks access

**Solution:**
1. Verify template path in network_printers.json
2. Check file exists at that path
3. Verify user has read access to file
4. Update path if needed:
   ```cmd
   python printer_diagnostics.py
   # Then "Run Setup Wizard" → Update template path
   ```

### Issue: "Large format plotter not receiving data"

**Cause:** Multiple possible issues

**Solution:**
1. **Run diagnostics:**
   ```cmd
   python printer_diagnostics.py
   ```

2. **Check "Available Printers" tab:**
   - Is plotter listed?
   - What is its status?
   - Is it categorized as "24×36"?

3. **Test connection:**
   - Select plotter in list
   - Click "Test Selected Printer"

4. **Check printer driver:**
   - Some plotters require specific drivers
   - Verify correct driver is installed
   - Check printer properties in Windows

5. **Check print queue:**
   - Open Devices & Printers
   - Right-click plotter → "See what's printing"
   - Look for stuck jobs

6. **Verify scaling settings:**
   - The system sends "Scale to Fit" command
   - Some plotters ignore this if driver doesn't support it
   - May need printer-specific configuration

### Issue: "Permission denied" errors

**Cause:** User lacks file access

**Solution:**
- Verify user has read access to app folder
- Check template file permissions
- Ensure network_printers.json is readable

### Issue: "Print jobs slow or timing out"

**Cause:** Network latency or slow print server

**Solution:**
1. Check network speed
2. Increase timeout in code (default 60s):
   ```python
   # In network_batch_print.py, line ~XXX
   success, error = print_with_timeout(
       pdf_path,
       printer_name,
       timeout=120  # Increase to 120 seconds
   )
   ```

---

## Maintenance

### Updating Printer Configuration

**When printers are added/removed/renamed:**

1. **Run diagnostics tool:**
   ```cmd
   python printer_diagnostics.py
   ```

2. **Click "Run Setup Wizard"**

3. **Update printer selections**

4. **Save configuration**

5. **Test all printers**

### Updating Template

**When template needs changes:**

1. **Edit template:**
   ```
   \\SERVER\SharedApps\DocumentManager\DESIGN FILES\Template.docx
   ```

2. **Ensure bookmarks remain intact:**
   - OrderNumber
   - Customer
   - LotSub
   - Level

3. **Verify template:**
   ```cmd
   python src\verify_template.py
   ```

### Monitoring

**Regular checks (monthly):**

- [ ] Run printer diagnostics
- [ ] Test connection to all printers
- [ ] Verify template accessible
- [ ] Check error logs for issues
- [ ] Review user feedback

### Log Files

**Error logs location:**
```
document_manager_v2.3.log
print_errors.log
```

**Review logs for:**
- Printer connection failures
- Template errors
- Print job timeouts
- PDF file not found errors

---

## Quick Reference

### Commands

```bash
# Run diagnostics
python printer_diagnostics.py

# Run setup wizard
python -c "from src.printer_setup_wizard import run_setup_wizard; run_setup_wizard()"

# Verify template
python src/verify_template.py

# Run application
python run_v2_3.py
```

### File Locations

```
network_printers.json          # Network printer config (IT manages)
user_preferences.json          # Per-user settings
document_manager_v2.3.log      # Application log
print_errors.log               # Print error log
```

### Support

For issues not covered in this guide:

1. Run diagnostics tool
2. Export diagnostic report
3. Check log files
4. Contact application support with:
   - Diagnostic report
   - Error log files
   - Description of issue
   - Steps to reproduce

---

## Version History

- **v2.0** - Network deployment architecture
  - Centralized printer configuration
  - Auto-discovery
  - Setup wizard
  - Diagnostic tools

---

**Last Updated:** October 2025
**Document Version:** 2.0
