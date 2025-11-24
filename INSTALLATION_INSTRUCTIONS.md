# Document Manager V2.3 - Installation Instructions

## Prerequisites

- Windows operating system
- Python 3.8 or higher installed (does NOT need to be added to PATH)
- Microsoft Word installed (for folder label printing)

## Installation Steps

### Step 1: Locate Your Python Installation

If Python is not in your PATH, you need to find where Python is installed. Common locations:

```
C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python312\python.exe
C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python311\python.exe
C:\Python312\python.exe
C:\Program Files\Python312\python.exe
```

To find Python on your system, open Command Prompt and run:

```cmd
where /R C:\ python.exe
```

This will search your C: drive for python.exe. Note down the full path.

### Step 2: Install Required Packages

Once you have the full path to python.exe, open Command Prompt **as Administrator** and run:

```cmd
"C:\Full\Path\To\python.exe" -m pip install --upgrade pip
"C:\Full\Path\To\python.exe" -m pip install -r requirements.txt
```

**Example** (replace with your actual Python path):

```cmd
"C:\Users\mkung\AppData\Local\Programs\Python\Python312\python.exe" -m pip install --upgrade pip
"C:\Users\mkung\AppData\Local\Programs\Python\Python312\python.exe" -m pip install -r requirements.txt
```

### Step 3: Verify Installation

Test that all packages are installed correctly:

```cmd
"C:\Full\Path\To\python.exe" -c "import pandas; import PyPDF2; import win32com.client; import lxml; print('All packages installed successfully!')"
```

### Step 4: Run the Application

#### Option A: Using the full Python path

```cmd
cd "C:\code\Document Manager"
"C:\Full\Path\To\python.exe" run_v2_3.py
```

#### Option B: Create a shortcut batch file

Create a file named `START_APP.bat` in the Document Manager folder with:

```batch
@echo off
"C:\Full\Path\To\python.exe" run_v2_3.py
pause
```

Replace `C:\Full\Path\To\python.exe` with your actual Python path, then double-click `START_APP.bat` to run the application.

## Quick Install Script

For convenience, you can create an `INSTALL.bat` file:

```batch
@echo off
echo ============================================
echo Document Manager V2.3 - Installation
echo ============================================
echo.

:: Replace this with your Python path
set PYTHON_PATH="C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"

echo Checking Python installation...
%PYTHON_PATH% --version
if errorlevel 1 (
    echo ERROR: Python not found at %PYTHON_PATH%
    echo Please edit this file and set the correct PYTHON_PATH
    pause
    exit /b 1
)

echo.
echo Upgrading pip...
%PYTHON_PATH% -m pip install --upgrade pip

echo.
echo Installing requirements...
%PYTHON_PATH% -m pip install -r requirements.txt

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo You can now run the application with:
echo   %PYTHON_PATH% run_v2_3.py
echo.
pause
```

## Troubleshooting

### "Requirements satisfied" but app says "missing dependencies"

**Problem:** Multiple Python installations - pip installs to one, app runs with another.

**Solution:** Use `python -m pip` instead of just `pip`:

```cmd
python -m pip install pandas PyPDF2 pywin32 lxml
```

**Or run the automated fix:**
```cmd
FIX_DEPENDENCIES.bat
```

**Or diagnose which Python has the issue:**
```cmd
DIAGNOSE_PYTHON.bat
```

### "Python is not recognized as an internal or external command"

This means Python is not in your PATH. Use the full path to python.exe as shown above.

### "No module named 'pandas'" (or similar)

The required packages are not installed. Follow Step 2 to install them using `python -m pip`.

### "Access is denied" during pip install

Run Command Prompt as Administrator (right-click → Run as Administrator).

### pywin32 Installation Issues

If pywin32 fails to install, try:

```cmd
"C:\Full\Path\To\python.exe" -m pip install pywin32==305
"C:\Full\Path\To\python.exe" -m pip install pywin32 --force-reinstall
```

After installation, run the post-install script:

```cmd
"C:\Full\Path\To\python.exe" -m pywin32_postinstall -install
```

## Folder Label Printing Setup

After installation, to enable folder label printing:

1. Ensure the Word template is in the correct location:
   - `LABEL TEMPLATE\Contract_Lumber_Label_Template.docx`

2. Run the diagnostic to verify setup:
   ```cmd
   "C:\Full\Path\To\python.exe" diagnose_label_printing.py
   ```

3. Open the template in Word and verify bookmarks exist:
   - `builder` (for Customer name)
   - `Lot / subdivision` (for Job Reference)
   - `floors` (for Delivery Area)
   - `designer` (for Designer name)
   - `OrderNumber` (optional)

4. In the application, configure your printer:
   - Go to Print Settings
   - Enable "Folder Printer"
   - Select your printer from the dropdown

## Network/Shared Installation

If deploying to multiple computers via OneDrive or network share:

1. Install Python on each target machine
2. Run the installation batch file on each machine
3. Update the settings file paths to point to shared locations:
   - Edit `settings_v2_3.json`
   - Set `html_path` to network/OneDrive path
   - Set `pdf_path` to network/OneDrive path
   - Set `db_path` to shared database location

See `NETWORK_DEPLOYMENT_GUIDE.md` for more details.

## Support

For issues or questions:
- Check the log file: `document_manager_v2.3.log`
- Run diagnostics: `diagnose_label_printing.py`
- Review troubleshooting guides in the documentation
