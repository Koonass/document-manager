# Building Portable Package with WinPython (Includes tkinter)

## Why WinPython?

The Python embedded distribution doesn't include **tkinter**, which Document Manager requires for its GUI. WinPython is a portable Python distribution that includes:

✅ Full Python interpreter
✅ tkinter (TCL/TK)
✅ pip and common packages
✅ Complete standard library
✅ Fully portable (no installation)

## Quick Start

### Step 1: Download WinPython

1. Go to: https://winpython.github.io/
2. Download: **WinPython 3.11.9.0 dot (64-bit)**
   - File size: ~50MB download
   - Choose the "**dot**" version (includes scientific packages)
   - Direct link: https://github.com/winpython/winpython/releases

3. Extract the downloaded `.exe` file (it's a self-extracting archive):
   - Run the downloaded file
   - Choose extract location (e.g., `C:\Temp\WinPython`)
   - Wait for extraction (~200MB extracted)

### Step 2: Build Portable Package

Run from your project directory:

```batch
BUILD_PORTABLE_WINPYTHON.bat
```

When prompted, enter the path to WinPython's python folder:
```
C:\Temp\WinPython\WPy64-31190\python-3.11.9.amd64
```

The script will:
1. Verify tkinter is present
2. Copy WinPython to `portable-build\python\`
3. Install pywin32
4. Copy application files
5. Create complete portable package

### Step 3: Test

```batch
cd portable-build
START_PORTABLE.bat
```

The application should launch with full GUI!

### Step 4: Deploy

Copy the entire `portable-build` folder to:
- USB drive
- OneDrive
- Network share

---

## Manual Build (Alternative)

If the batch script doesn't work:

### 1. Extract WinPython

```batch
# Extract WinPython-3.11.9.0dot.exe to C:\Temp\WinPython
# Navigate to the python folder inside
cd "C:\Temp\WinPython\WPy64-31190\python-3.11.9.amd64"
```

### 2. Copy Python

```batch
xcopy /E /I /Y "C:\Temp\WinPython\WPy64-31190\python-3.11.9.amd64" "C:\code\Document Manager\portable-build\python"
```

### 3. Install pywin32

```batch
cd "C:\code\Document Manager\portable-build"
python\python.exe -m pip install pywin32
python\Scripts\pywin32_postinstall.py -install
```

### 4. Copy Application Files

```batch
cd "C:\code\Document Manager"
xcopy /E /I /Y src "portable-build\src"
xcopy /E /I /Y "LABEL TEMPLATE" "portable-build\LABEL TEMPLATE"
copy /Y run_v2_4.py portable-build\
copy /Y run_v2_4_readonly.py portable-build\
copy /Y START_PORTABLE.bat portable-build\
copy /Y START_PORTABLE_READONLY.bat portable-build\
copy /Y settings_v2_4_template.json portable-build\
```

### 5. Test

```batch
cd portable-build
START_PORTABLE.bat
```

---

## Package Size

| Component | Size |
|-----------|------|
| WinPython (with tkinter) | ~200MB |
| pywin32 | ~50MB |
| Application code | ~5MB |
| **Total** | **~250-300MB** |

Larger than embedded Python (~200MB) but includes everything needed.

---

## Troubleshooting

### "tkinter not found"

Make sure you downloaded the **dot** version of WinPython, not the "Zero" version.

- ✅ WinPython-3.11.9.0**dot**.exe (includes tkinter)
- ❌ WinPython-3.11.9.0**zero**.exe (minimal, no tkinter)

### "python.exe not found"

The path should be to the inner `python-3.11.9.amd64` folder:

```
C:\Temp\WinPython\
└── WPy64-31190\
    └── python-3.11.9.amd64\    ← This folder!
        ├── python.exe
        ├── Lib\
        └── tcl\                (tkinter needs this)
```

### "Module 'win32com' not found"

Install pywin32 manually:

```batch
cd portable-build
python\python.exe -m pip install pywin32
python\python.exe python\Scripts\pywin32_postinstall.py -install
```

---

## Why Not Standard Python Installer?

The standard Python installer:
- Requires admin rights
- Modifies registry
- Not truly portable
- Harder to redistribute

WinPython:
- No admin rights needed
- No registry changes
- Truly portable
- Designed for USB deployment

---

## Alternative: Python.org Embeddable + Manual tkinter

If you prefer the smaller embedded Python, you can manually add tkinter:

1. Install Python 3.11.9 from python.org (temporarily)
2. Copy these to embedded Python:
   - `tcl/` folder
   - `DLLs/tcl86t.dll`
   - `DLLs/tk86t.dll`
   - `DLLs/_tkinter.pyd`
   - `Lib/tkinter/` folder
3. Uninstall temporary Python

But WinPython is much easier!

---

## Recommended Workflow

**For development/testing:**
```
Use system Python → Fast iteration
```

**For deployment:**
```
Build with WinPython → Portable package → USB/OneDrive
```

**For users:**
```
Copy folder → Run START_PORTABLE.bat → Works immediately
```

---

## Next Steps

After building:

1. **Test locally**
   ```
   cd portable-build
   START_PORTABLE.bat
   ```

2. **Copy to USB**
   ```
   xcopy /E /I /Y portable-build E:\DocumentManager
   ```

3. **Test on different computer**
   - Plug in USB
   - Run E:\DocumentManager\START_PORTABLE.bat
   - Should work immediately!

4. **Deploy to team**
   - Copy to OneDrive or network share
   - Users run START_PORTABLE.bat
   - Each user gets working application

---

## Summary

✅ **WinPython includes tkinter**
✅ **~250MB total size**
✅ **Fully portable**
✅ **No installation needed**
✅ **Works on any Windows PC**
✅ **Perfect for USB deployment**

Just download WinPython, run BUILD_PORTABLE_WINPYTHON.bat, and you're done!
