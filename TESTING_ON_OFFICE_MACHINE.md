# Testing on Office Machine - Error Reporting Guide

## Before You Start

The print system now has comprehensive error logging. All errors are automatically saved to log files that you can share for debugging.

## Initial Setup on Office Machine

1. **Copy the entire folder** to the office computer
2. **Install Python dependencies** (if not already done):
   ```
   pip install pywin32 PyPDF2 python-docx
   ```

## Step 1: Run Diagnostics (DO THIS FIRST!)

**Before testing the actual application, run the diagnostic tool:**

1. Open Command Prompt or PowerShell
2. Navigate to the project folder:
   ```
   cd "C:\code\Document Manager"
   ```
3. Run the diagnostic script:
   ```
   python src\print_diagnostics.py
   ```
4. **This will create a file called `print_diagnostic_report.txt`**
5. **Send me this file** - it contains:
   - System information
   - Available printers and their details
   - Module installation status
   - Preset configuration
   - Database status

## Step 2: Test the Application

### Test 1: Open Preset Manager

1. Run the application: `python run_v2_3.py`
2. Open any day from the calendar
3. Click **⚙️ Manage Presets**
4. **What to check**:
   - Do you see the 3 default presets on the left?
   - When you click a preset, does the right side show the editor?
   - Can you see your printers in the dropdowns?

**If something doesn't work**, send me:
- Screenshot of what you see
- File: `print_errors.log` (created automatically)

### Test 2: Configure a Preset

1. In Preset Manager, click "Standard Plot"
2. **11×17 Printer**:
   - Check "Enabled"
   - Select a printer from dropdown
   - Set copies to 1
3. **24×36 Printer**:
   - Check "Enabled"
   - Select a printer from dropdown
   - Set copies to 1
4. **Folder Label**:
   - Check "Print folder labels"
   - Select a printer from dropdown
5. Click **💾 Save Changes**

**If errors occur**, send me `print_errors.log`

### Test 3: Test Print (Small Batch First!)

1. Close Preset Manager
2. **Select just 1-2 orders** (check their checkboxes)
3. Click **📋 Create Batch**
4. Select your preset
5. Click **Review & Print**
6. Watch the progress dialog

**Important**:
- If it works, great! Try more orders.
- If it fails, don't panic - error is logged

## Error Files to Send Me

When something goes wrong, send me these files:

### 1. Diagnostic Report (Always send this first)
- **File**: `print_diagnostic_report.txt`
- **Location**: Project root folder
- **How to create**: Run `python src\print_diagnostics.py`

### 2. Error Log (Send when errors occur)
- **File**: `print_errors.log`
- **Location**: Project root folder
- **Created automatically** when errors happen

### 3. Screenshots
- What the Preset Manager looks like
- Any error dialogs that appear
- The progress dialog if it hangs/freezes

## Common Issues and What to Check

### "No printers detected"
- **Check**: Is the print spooler service running?
  - Open Services (services.msc)
  - Look for "Print Spooler"
  - Make sure it's "Running"
- **Check**: Can you print from other applications (Notepad, Word)?
- **Send me**: The diagnostic report

### Preset Manager is blank
- **Check**: Did you click on a preset name in the left list?
- **Send me**:
  - Screenshot
  - print_errors.log

### Print jobs timing out
- **This is normal** for slow print servers!
- The timeout is 60 seconds per job
- **Send me**:
  - print_errors.log (will show which printers are slow)
  - Let me know the printer model

### "Module not found" errors
- **Run**: `pip install pywin32 PyPDF2 python-docx`
- **Send me**: The exact error message

## Quick Test Checklist

Use this to quickly test everything:

- [ ] Run diagnostic script - sent report
- [ ] Open application - works
- [ ] Open Preset Manager - shows 3 presets
- [ ] Click preset - shows editor with dropdowns
- [ ] See printers in dropdowns - yes/no
- [ ] Save preset changes - works
- [ ] Select 1 order - checkbox works
- [ ] Create batch - dialog appears
- [ ] Select preset - shows in dialog
- [ ] Click Review & Print - progress shows
- [ ] Print completes or shows specific error

## How to Send Me The Files

### Method 1: Copy File Contents
1. Open `print_diagnostic_report.txt` in Notepad
2. Select All (Ctrl+A)
3. Copy (Ctrl+C)
4. Paste into your message to me

Do the same for `print_errors.log`

### Method 2: Attach Files
Just attach both files to your message

## What I Need When Reporting Issues

Please include:
1. **Diagnostic report** (print_diagnostic_report.txt)
2. **Error log** (print_errors.log) - if errors occurred
3. **Screenshots** - if UI looks wrong
4. **Description**: What were you doing when the error happened?
5. **Printer details**: What printer models are you using?

## Advanced: Clearing Logs

If you want to start fresh:
```
del print_errors.log
del print_diagnostic_report.txt
```

Then re-run your tests.

## Questions to Answer (Helps me debug faster)

1. What version of Windows?
2. Are printers network printers or local USB?
3. Do printers have special scripts/drivers installed?
4. Can you print PDFs from Adobe Reader to these printers?
5. Does the print server require authentication?

---

**Remember**: Errors are GOOD during testing! They help me fix issues. The more detail you provide, the faster I can solve problems.
