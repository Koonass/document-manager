# How to Run on Work Machine (Python Not in PATH)

## Quick Options - Try These in Order

### Option 1: PowerShell Script (Recommended)
Right-click `run_printer_setup.ps1` → **"Run with PowerShell"**

If it says "execution policy" error:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass -Force
```
Then try again.

---

### Option 2: Batch File
Double-click: `run_printer_setup.bat`

The updated batch file searches common Python locations automatically.

---

### Option 3: Python Launcher (if installed)
Open Command Prompt in this folder, then:
```cmd
py printer_diagnostics.py
```

The `py` launcher comes with Python and doesn't require PATH.

---

### Option 4: Direct Python Path
If you know where Python is installed:

**Example if Python is at `C:\Python311\`:**
```cmd
C:\Python311\python.exe printer_diagnostics.py
```

**To find Python location:**
```cmd
where python
py -0p
dir C:\Python* /s /b | findstr python.exe
```

---

### Option 5: File Association
If `.py` files open with Python automatically:
- Just **double-click** `printer_diagnostics.py`

---

### Option 6: Create Custom Shortcut

1. Right-click Desktop → New → Shortcut
2. **Target:**
   ```
   "C:\Python311\python.exe" "C:\code\Document Manager\printer_diagnostics.py"
   ```
   (Replace paths with your actual locations)
3. **Name:** "Printer Setup"
4. Save and double-click anytime

---

## If Nothing Works

See: **`MANUAL_RUN_INSTRUCTIONS.txt`** for detailed troubleshooting.

---

## What Happens When It Runs?

The **Printer Diagnostics Tool** window will open with 4 tabs:

1. **Overview** - Shows system status
2. **Available Printers** - Lists all printers
3. **Configuration** - Shows current config
4. **Connection Tests** - Test printer connections

**Click "Run Setup Wizard"** to configure your printers!

---

## After Setup Completes

You'll have a `network_printers.json` file with your printer configuration.

Then run your main application normally:
- `py run_v2_3.py` (if py launcher works)
- `C:\Python311\python.exe run_v2_3.py` (direct path)
- Or double-click `run_v2_3.py` if file associations work

---

## Quick Test

Try this in Command Prompt to test if any Python works:
```cmd
python --version
py --version
C:\Python311\python.exe --version
```

If **any** of those show a Python version, you can use that command!

---

## Need Help?

1. Open **`MANUAL_RUN_INSTRUCTIONS.txt`** for detailed methods
2. Check **`WORK_MACHINE_QUICKSTART.md`** for setup steps
3. See **`NETWORK_DEPLOYMENT_GUIDE.md`** for full IT guide
