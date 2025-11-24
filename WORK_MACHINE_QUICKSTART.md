# Quick Start - Work Machine Setup

## 🚀 First Time on Work Machine? Start Here!

---

## Step 1: Run Printer Diagnostics

**Double-click:** `run_printer_setup.bat`

This will:
- Open the printer diagnostics tool
- Show you all available printers
- Let you configure the system

---

## Step 2: Complete the Setup Wizard

In the diagnostics window:

1. **Click "Run Setup Wizard"** (purple button)

2. **Follow the 7 steps:**
   - Welcome → Click "Next"
   - Discover Printers → Review list, click "Next"
   - Select 11×17 Printers → Check standard printers, click "Next"
   - Select 24×36 Printers → **CHECK YOUR PLOTTER**, click "Next"
   - Select Label Printers → Check label printer, click "Next"
   - Template Path → Browse to your template file, click "Next"
   - Review → Verify everything, click "Finish & Save"

3. **Test Your Printers:**
   - Go to "Connection Tests" tab
   - Click "Run Connection Tests"
   - All should show ✓ SUCCESS

---

## Step 3: Try Printing

1. **Run your application:**
   ```
   python run_v2_3.py
   ```

2. **Select an order that has a PDF**

3. **Click "Print Selected Orders"**

4. **Configure your print job:**
   - Enable 11×17 printer ✓
   - Enable 24×36 printer ✓ (YOUR PLOTTER)
   - Enable Folder Label ✓
   - Set copies
   - Click "Start Printing"

5. **Watch the progress**
   - Should show each order printing
   - Check that plotter receives data
   - Verify formatting on printed page

---

## ✅ Success Checklist

After setup, you should have:

- [ ] `network_printers.json` file created
- [ ] All printers showing "✓ SUCCESS" in connection tests
- [ ] Successfully printed to 11×17 printer
- [ ] Successfully printed to 24×36 plotter (THE KEY ONE!)
- [ ] Successfully printed folder label
- [ ] Orders marked as processed after printing

---

## 🔧 Troubleshooting on Work Machine

### "No printers detected"

**Fix:** Printers not installed on this machine
```cmd
# Check if printers are installed
wmic printer get name
```

If your plotter isn't listed, you need to install it in Windows first.

---

### "Printer offline" for plotter

**Fix:** Check network connection to plotter

1. Open "Devices and Printers" in Windows
2. Find your large format plotter
3. Right-click → "See what's printing"
4. Check if it says "Offline" or "Ready"
5. If offline:
   - Check physical printer is on
   - Check network cable connected
   - Try printing test page from Windows

---

### "Not sending data to plotter"

**Fix:** Make sure you selected it in setup!

1. Run: `python printer_diagnostics.py`
2. Go to "Configuration" tab
3. Look for "24×36 Printers" section
4. Is your plotter listed there?
5. If not, run "Setup Wizard" again and **select your plotter** in step 4

---

### "PDF file not found"

**Fix:** PDF paths from home machine won't work here

The issue from before! PDFs attached on your home machine have paths like:
```
C:/code/Document Manager/samples/sample plots/file.pdf
```

But this path doesn't exist on work machine.

**Solution:** In the app, re-attach PDFs:
1. Find order
2. Right-click → Detach PDF
3. Right-click → Attach PDF
4. Browse to PDF location **on work machine**
5. Now the path will be correct

---

## 📁 Important Files (Created on Work Machine)

After setup, you'll have these files:

```
network_printers.json       ← Printer configuration (IT manages this)
user_preferences.json       ← Your personal settings
document_manager_v2.3.log   ← Application log (check for errors)
```

---

## 🆘 Still Having Issues?

1. **Export Diagnostic Report:**
   - Open `printer_diagnostics.py`
   - Click "Export Report"
   - Save the report
   - Review it for clues

2. **Check Logs:**
   - Open `document_manager_v2.3.log`
   - Look for errors related to printing
   - Search for your plotter name

3. **Test Individual Printer:**
   - In diagnostics, go to "Available Printers" tab
   - Find your plotter in the list
   - Select it
   - Click "Test Selected Printer"
   - Should say "Successfully connected"

---

## 📖 Full Documentation

For complete information, see:

- `NETWORK_DEPLOYMENT_GUIDE.md` - Complete IT guide
- `INTEGRATION_GUIDE.md` - Developer integration
- `NETWORK_PRINTING_IMPLEMENTATION_SUMMARY.md` - Overview of everything

---

## 🎯 Quick Reference

### Run Diagnostics
```bash
python printer_diagnostics.py
```

### Run Setup Wizard
```bash
python -c "from src.printer_setup_wizard import run_setup_wizard; run_setup_wizard()"
```

### Run Application
```bash
python run_v2_3.py
```

---

**After completing these steps, your plotter WILL receive data! 🎉**

The old issue was empty printer names in config. The new system ensures you actually select a printer. Problem solved!
