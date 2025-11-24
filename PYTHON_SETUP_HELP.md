# Python Setup Help - Fixing "python is not recognized"

## Quick Fix - Try These Commands

Open **Command Prompt** in the project folder and try each of these:

```batch
py src\print_diagnostics.py
```

If that doesn't work, try:
```batch
python3 src\print_diagnostics.py
```

If that doesn't work, try:
```batch
C:\Python312\python.exe src\print_diagnostics.py
```

---

## Finding Python on Your Computer

### Method 1: Using Windows Search
1. Press `Windows Key`
2. Type: **python**
3. Look for "Python 3.x" in results
4. Right-click → **Open file location**
5. Note the path (example: `C:\Python312\python.exe`)

### Method 2: Check Common Locations
Python is usually installed in one of these places:

**System-wide installs:**
- `C:\Python312\python.exe`
- `C:\Python311\python.exe`
- `C:\Python310\python.exe`
- `C:\Program Files\Python312\python.exe`

**User installs:**
- `C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe`

### Method 3: Use Windows Apps & Features
1. Open **Settings**
2. Go to **Apps** → **Apps & features**
3. Search for "Python"
4. If found, note the version

---

## Running Diagnostics Manually

Once you find Python, use the full path:

```batch
"C:\Python312\python.exe" src\print_diagnostics.py
```

Replace `C:\Python312\python.exe` with YOUR Python path.

---

## Is Python Actually Installed?

### Check if Python is installed:

1. Open **Command Prompt**
2. Try: `py --version`
3. Or try: `python --version`
4. Or try: `python3 --version`

**If you see a version number** (like `Python 3.12.0`), Python IS installed!

**If you see an error**, Python might not be installed.

---

## Installing Python (If Needed)

### For Office Machine:

**Option 1: Download from python.org**
1. Go to: https://www.python.org/downloads/
2. Download Python 3.11 or 3.12 (Windows installer)
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Install

**Option 2: Use Microsoft Store**
1. Open Microsoft Store
2. Search: "Python 3.12"
3. Click **Get** / **Install**
4. This automatically adds Python to PATH

---

## Adding Python to PATH (If Installed but Not Found)

If Python is installed but the command doesn't work:

### Windows 10/11:
1. Right-click **This PC** → **Properties**
2. Click **Advanced system settings**
3. Click **Environment Variables**
4. Under "System variables", find **Path**
5. Click **Edit**
6. Click **New**
7. Add the Python path (example: `C:\Python312`)
8. Also add: `C:\Python312\Scripts`
9. Click **OK** on all windows
10. **Close and reopen** Command Prompt

---

## Alternative: Create a Python Shortcut

If you don't want to mess with PATH:

1. Find `python.exe` on your computer
2. Right-click → **Create shortcut**
3. Move shortcut to the project folder
4. Rename to `python_local.exe`
5. Use it: `python_local src\print_diagnostics.py`

---

## Testing Your Python Setup

After fixing Python, test it:

```batch
# Test 1: Check Python version
python --version

# Test 2: Check if pip works
python -m pip --version

# Test 3: Run diagnostics
python src\print_diagnostics.py
```

All three should work without errors.

---

## Creating a Custom Run Script

If nothing else works, create `run_with_full_path.bat`:

```batch
@echo off
"C:\FULL\PATH\TO\python.exe" src\print_diagnostics.py
pause
```

Replace `C:\FULL\PATH\TO\python.exe` with your actual Python path.

Then double-click `run_with_full_path.bat`

---

## Still Having Issues?

### Send me:

1. **Screenshot** of the error message
2. **Output** of these commands:
   ```batch
   py --version
   python --version
   python3 --version
   where python
   where py
   ```
3. **Tell me**:
   - Did you install Python yourself?
   - Are you on a work computer with restrictions?
   - What Windows version? (Win 10 / Win 11)

---

## For IT Department / Admin

If Python needs to be installed on a work computer:

**Minimal install command (no admin required):**
```batch
# Download Python installer, then:
python-3.12.0.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
```

**Packages needed:**
```batch
python -m pip install pywin32 PyPDF2 python-docx
```

**Total disk space:** ~100MB for Python + packages

---

## Quick Reference Card

**Print this out and keep it handy:**

```
My Python Path: _________________________________

Commands that work for me:
[ ] python
[ ] py
[ ] python3
[ ] Full path: ________________________________

To run diagnostics:
1. Open Command Prompt
2. Navigate to: C:\code\Document Manager
3. Run: ______________________________________
        (fill in command that works)
```

---

## Common Scenarios

### Scenario 1: "It worked yesterday, now it doesn't"
- Windows update may have reset PATH
- Re-add Python to PATH (see instructions above)

### Scenario 2: "Python opens Microsoft Store"
- Windows 10/11 redirects Python to Store
- Either install from Store, or disable redirect:
  - Settings → Apps → Apps & features
  - Manage app execution aliases
  - Turn OFF Python redirects

### Scenario 3: "Multiple Python versions installed"
- Use `py -3.12` to specify version
- Or use full path to the version you want

### Scenario 4: "Work computer, no admin rights"
- Use Microsoft Store version (doesn't need admin)
- Or ask IT to install Python
- Or install Python to user directory (doesn't need admin)

---

**Remember:** Once you figure out what works, write it down! You'll need it again.
