# Folder Label Printing Troubleshooting Guide

## For Remote User Support

This guide helps diagnose and fix folder label printing issues when working with a remote user on a different network.

---

## Quick Diagnostic (For Remote User)

**STEP 1:** Have the remote user run the diagnostic script:

1. Navigate to the Document Manager folder
2. Double-click: **`DIAGNOSE_LABEL_PRINTING.bat`**
3. Wait for the diagnostic to complete
4. Share the generated **`diagnostic_report.txt`** file

This will check:
- ✓ Template file location
- ✓ Print preset configuration
- ✓ Template bookmarks
- ✓ Code configuration

---

## Common Issues & Solutions

### Issue #1: BOOKMARK MISMATCH ⚠️ CRITICAL

**Symptom:** Labels print blank or with no data filled in

**Diagnosis:** The template bookmarks don't match what the code expects

**The Problem:**
- **CODE** looks for: `OrderNumber`, `Customer`, `LotSub`, `Level`
- **DOCUMENTATION** says to use: `builder`, `Lot / subdivision`, `floors`, `designer`
- If the template was created following the documentation, the code won't find the bookmarks!

**Solution A - Fix the Code (Recommended for Remote Deployment):**

Have the user apply this code fix:

1. Open: `src/word_template_processor.py`

2. Find lines 83-86 (inside `fill_and_print_template` method):
   ```python
   # CURRENT CODE (INCORRECT):
   self._fill_bookmark(doc, "OrderNumber", job_data.get('OrderNumber', ''))
   self._fill_bookmark(doc, "Customer", job_data.get('Customer', ''))
   self._fill_bookmark(doc, "LotSub", job_data.get('JobReference', ''))
   self._fill_bookmark(doc, "Level", job_data.get('DeliveryArea', ''))
   ```

3. Replace with:
   ```python
   # FIXED CODE (matches documentation):
   self._fill_bookmark(doc, "builder", job_data.get('Customer', ''))
   self._fill_bookmark(doc, "Lot / subdivision", job_data.get('JobReference', ''))
   self._fill_bookmark(doc, "floors", job_data.get('DeliveryArea', ''))
   self._fill_bookmark(doc, "designer", job_data.get('Designer', ''))
   self._fill_bookmark(doc, "OrderNumber", job_data.get('OrderNumber', ''))  # Optional
   ```

4. Find lines 340-343 (inside `fill_template_to_file` method) and make the same changes

5. Save the file

6. Restart the application

**Solution B - Fix the Template:**

If you prefer to update the template instead:

1. Open: `LABEL TEMPLATE/Contract_Lumber_Label_Template.docx` in Microsoft Word

2. For each field, select the text and add bookmarks:
   - Select text → **Insert** tab → **Bookmark**
   - Add these exact bookmark names:
     - `OrderNumber` (for order number)
     - `Customer` (for customer/builder name)
     - `LotSub` (for job reference/lot)
     - `Level` (for delivery area/floors)

3. Save the template

4. Run `DIAGNOSE_LABEL_PRINTING.bat` again to verify

---

### Issue #2: NO PRINTER CONFIGURED ⚠️

**Symptom:** Label printing is enabled but nothing prints

**Diagnosis:** `print_presets.json` shows `"folder_label_printer": ""`

**Solution:**

Have the user configure the printer through the UI:

1. Open the Document Manager application
2. Open any day's orders (click a date on the calendar)
3. Scroll down to **Print Settings** section
4. Check the **"Folder Printer"** checkbox
5. Select a printer from the **dropdown menu**
6. The setting saves automatically
7. Try printing a test label

**Alternative - Manual Configuration:**

If the UI doesn't work, edit `print_presets.json`:

1. Open: `print_presets.json`
2. Find the preset (e.g., "Standard Plot")
3. Change:
   ```json
   "folder_label_enabled": true,
   "folder_label_printer": ""
   ```
4. To:
   ```json
   "folder_label_enabled": true,
   "folder_label_printer": "HP LaserJet Pro M404n"
   ```
   (Use the exact printer name from Windows)

5. Save and restart the application

---

### Issue #3: TEMPLATE FILE NOT FOUND ⚠️

**Symptom:** Error: "Folder label template file not found"

**Diagnosis:** Template file is missing or in wrong location

**Solution:**

Verify the template exists at:
```
C:\code\Document Manager\LABEL TEMPLATE\Contract_Lumber_Label_Template.docx
```

If missing:
1. Check if it's in: `DESIGN FILES/Template.docx`
2. Copy it to: `LABEL TEMPLATE/Contract_Lumber_Label_Template.docx`
3. Or update `src/main_v2_3.py` line 32 to point to the correct location

---

### Issue #4: WORD/COM ERRORS

**Symptom:** Errors about "win32com" or "Word.Application"

**Solution:**

1. Verify Microsoft Word is installed
2. Install pywin32:
   ```bash
   pip install pywin32
   ```
3. Close all Word instances
4. Try again

If using portable Python:
```bash
cd "C:\code\Document Manager"
python -m pip install pywin32
```

---

## Remote Troubleshooting Workflow

### Step 1: Gather Information
Ask the remote user to run: **`DIAGNOSE_LABEL_PRINTING.bat`**

Have them send you:
- `diagnostic_report.txt`
- `print_presets.json`
- `document_manager_v2.3.log` (last 100 lines)

### Step 2: Identify the Issue
Review the diagnostic report for:
- ❌ CRITICAL ISSUES
- ⚠️ WARNINGS

### Step 3: Apply Fixes Remotely

**For Code Changes:**
- Send the updated `word_template_processor.py` file
- Or provide line-by-line edit instructions

**For Configuration Changes:**
- Send updated `print_presets.json`
- Or walk through UI configuration

**For Template Changes:**
- Request they share the template file
- Send back the corrected version
- Or provide Word bookmark instructions

### Step 4: Verify the Fix
Have them run:
1. `DIAGNOSE_LABEL_PRINTING.bat` again
2. Test print a single label
3. Share results

---

## Testing Label Printing

### Test with Single Order:

1. Open Document Manager
2. Click on a day with orders
3. **Check only ONE order**
4. In Print Settings:
   - ✓ Enable "Folder Printer"
   - Select the printer
   - ✗ Disable other printers (11x17, 24x36)
5. Click **"Print All"**
6. Check the printer output

### Check the Logs:

Location: `document_manager_v2.3.log`

Look for:
```
Starting folder label print for order [number]
  Template: [path]
  Printer: [name]
  Customer: [name]
  JobReference: [reference]
  ✓ Filled bookmark 'Customer' = '[value]'
  ...
✓ Successfully printed folder label
```

If you see:
```
⚠ Bookmark 'Customer' not found in template
```
→ Bookmark mismatch issue (see Issue #1)

---

## Files to Check/Share for Remote Support

| File | Purpose | When to Check |
|------|---------|---------------|
| `diagnostic_report.txt` | Generated diagnostic output | First step - always |
| `print_presets.json` | Printer configuration | Printer not configured |
| `document_manager_v2.3.log` | Application logs | Any printing errors |
| `LABEL TEMPLATE/Contract_Lumber_Label_Template.docx` | Template file | Bookmark issues |
| `src/word_template_processor.py` | Code that fills bookmarks | Bookmark mismatch |

---

## Quick Reference: Expected Bookmarks

**If template was created from DOCUMENTATION:**
- `builder`
- `Lot / subdivision` (includes space and slash!)
- `floors`
- `designer`
- `OrderNumber` (optional)
- `DatePrinted` (optional)

**If template uses CODE bookmark names:**
- `OrderNumber`
- `Customer`
- `LotSub`
- `Level`

**The CODE and DOCUMENTATION must match!**

---

## Remote Deployment Checklist

Before deploying to a remote user:

- [ ] Run `DIAGNOSE_LABEL_PRINTING.bat` on the deployment machine
- [ ] Verify template exists and has correct bookmarks
- [ ] Verify printer is configured in presets
- [ ] Test print one label successfully
- [ ] Verify Microsoft Word is installed
- [ ] Verify pywin32 is installed (`pip list | grep pywin32`)
- [ ] Include troubleshooting documentation
- [ ] Provide contact method for support

---

## Support Contact Template

When reaching out for help, provide:

1. **Diagnostic report** (from `DIAGNOSE_LABEL_PRINTING.bat`)
2. **Error description:** What happens when you try to print?
3. **Expected behavior:** What should happen?
4. **Log excerpt:** Last 50 lines of `document_manager_v2.3.log`
5. **System info:**
   - Windows version
   - Python version (`python --version`)
   - Word version
   - Network setup (standalone/shared drive)

---

## Version Information

- **Document Manager Version:** 2.3.0
- **Last Updated:** 2025-11-12
- **Created For:** Remote deployment troubleshooting
