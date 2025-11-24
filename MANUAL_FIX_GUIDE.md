# Manual Fix for Missing Dependencies

## Problem

`pip install` shows "requirements satisfied" but `START_APP.bat` reports "missing dependencies".

**Cause:** You have multiple Python installations. `pip` installs to one Python, but `START_APP.bat` runs a different Python.

---

## Solution: Use Python's `-m pip` to ensure correct installation

### Step 1: Find which Python START_APP.bat will use

Open Command Prompt and test each command in order:

```cmd
python --version
py --version
python3 --version
```

The **first one that works** is what START_APP.bat will use.

### Step 2: Install packages to that specific Python

Replace `<python-command>` with the command from Step 1:

#### If `python` worked:
```cmd
python -m pip install --upgrade pip
python -m pip install pandas PyPDF2 pywin32 lxml
python -m pywin32_postinstall -install
```

#### If `py` worked:
```cmd
py -m pip install --upgrade pip
py -m pip install pandas PyPDF2 pywin32 lxml
py -m pywin32_postinstall -install
```

#### If `python3` worked:
```cmd
python3 -m pip install --upgrade pip
python3 -m pip install pandas PyPDF2 pywin32 lxml
python3 -m pywin32_postinstall -install
```

### Step 3: Verify installation

Using the same command:

```cmd
python -c "import pandas; import PyPDF2; import win32com.client; import lxml; print('All packages OK!')"
```

### Step 4: Run the application

```cmd
START_APP.bat
```

---

## Alternative: Use the full Python path

### Find your Python installation:

```cmd
where /R C:\ python.exe
```

This shows all Python installations. Pick the one you want (usually in `AppData\Local\Programs\Python`).

### Install to specific Python:

```cmd
"C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe" -m pip install pandas PyPDF2 pywin32 lxml
"C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe" -m pywin32_postinstall -install
```

### Update START_APP.bat:

Edit `START_APP.bat` and change line 171 to use the full path:

```batch
"C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe" run_v2_3.py
```

---

## Common Scenarios

### Scenario 1: "pip" installs to Python 2.7 (old)

**Problem:** `pip` defaults to old Python 2.7
**Solution:** Use `python3 -m pip` instead of `pip`

```cmd
python3 -m pip install pandas PyPDF2 pywin32 lxml
```

### Scenario 2: Multiple Python 3.x versions

**Problem:** You have Python 3.10, 3.11, and 3.12 installed
**Solution:** Use `py -3.12` to specify version

```cmd
py -3.12 -m pip install pandas PyPDF2 pywin32 lxml
py -3.12 run_v2_3.py
```

### Scenario 3: Corporate environment with restricted pip

**Problem:** `pip install` blocked by corporate policy
**Solution:** Ask IT to whitelist these packages or use `--user` flag

```cmd
python -m pip install --user pandas PyPDF2 pywin32 lxml
```

---

## Verification Commands

### Check Python executable path:
```cmd
python -c "import sys; print(sys.executable)"
```

### Check where pip installs:
```cmd
pip show pandas
```
Look for "Location:" in the output.

### Check if packages are importable:
```cmd
python -c "import pandas; import PyPDF2; import win32com.client; import lxml; print('SUCCESS')"
```

### List all installed packages:
```cmd
python -m pip list
```

---

## Still Having Issues?

### Use the automated tools:

1. **Diagnose the problem:**
   ```cmd
   DIAGNOSE_PYTHON.bat
   ```

2. **Fix automatically:**
   ```cmd
   FIX_DEPENDENCIES.bat
   ```

### Or run the app directly:

Find out which Python START_APP.bat uses, then run directly:

```cmd
python run_v2_3.py
```

This will show the actual error message, which is more helpful than "missing dependencies".

---

## Understanding the Error

When you see "missing dependencies" from START_APP.bat, the actual error is usually:

```
ModuleNotFoundError: No module named 'pandas'
```

This means that specific Python can't find the module, even if pip says it's installed (because pip installed it to a different Python).

**The fix:** Always use `python -m pip` (not just `pip`) to ensure packages go to the right place.
