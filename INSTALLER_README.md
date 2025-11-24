# Single-File Installer - Document Manager

## Overview

This will create a **single .exe installer** that contains your entire Document Manager application. When users run this .exe on their network, it will:

1. Show a GUI installer window
2. Let them choose installation location
3. Extract all application files
4. Install Python dependencies
5. Create desktop shortcuts
6. Done!

## How to Build the Installer

### Method 1: Double-click (Easy)

Simply double-click: **`BUILD_INSTALLER.bat`**

That's it! Wait 3-5 minutes, and you'll have `DocumentManager_Installer.exe` in the `dist` folder.

### Method 2: Command Line

```batch
python create_installer.py
```

## What Gets Created

The installer will create a file called:

```
dist/DocumentManager_Installer.exe
```

This is your single-file installer! It will be approximately **30-50 MB** in size.

## What's Included in the Installer

- Complete application (run_v2_3.py + all src/ files)
- Label template (Contract_Lumber_Label_Template.docx)
- Configuration files (settings, presets)
- Requirements.txt for dependencies
- Documentation files
- Sample data and files
- GUI installer with progress tracking
- Automatic dependency installation
- Desktop shortcut creation

## Requirements to Build the Installer

- Python 3.x installed
- Internet connection (to download PyInstaller)
- All Document Manager files in current directory

## Using the Installer (For End Users)

1. Copy `DocumentManager_Installer.exe` to target machine
2. Double-click to run
3. Choose installation location (default: `C:\Users\[username]\Document Manager`)
4. Click "Install"
5. Wait for installation to complete
6. Launch from desktop shortcut or batch file

## Network Deployment

Since your network doesn't like .exe files:

1. **Get approval** for this specific installer.exe
2. OR temporarily disable restrictions
3. OR use PowerShell bypass:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\DocumentManager_Installer.exe
   ```

## Troubleshooting

### "PyInstaller not found"
- The script will automatically install it on first run

### "Python not found"
- Install Python 3.7+ from python.org
- Make sure Python is in your PATH

### Installer is too large
- This is normal (30-50 MB includes Python runtime)
- Alternative: Use network share instead

### Build fails
- Check that all required files exist (run_v2_3.py, src/, etc.)
- Make sure no files are open in other programs
- Try running as Administrator

## What Happens During Installation

1. **User runs .exe** - GUI window opens
2. **Choose location** - User selects install directory
3. **Extract files** - All application files extracted
4. **Install dependencies** - `pip install -r requirements.txt` runs
5. **Create shortcuts** - Desktop + folder shortcuts created
6. **Complete** - User can launch application immediately

## File Size Comparison

| Method | Size | Pros | Cons |
|--------|------|------|------|
| Single .exe installer | 30-50 MB | One file, easy distribution | Larger file |
| Zip archive | 5-10 MB | Smaller | Manual setup required |
| Network share | N/A | Centralized | Requires network access |

## Advanced Options

If you need to customize the installer:

1. Edit `create_installer.py`
2. Modify the `items_to_copy` list to include/exclude files
3. Change the installer GUI in the `installer_main.py` template
4. Rebuild with `BUILD_INSTALLER.bat`

## Support

If you encounter issues:

1. Check that Python is installed and in PATH
2. Ensure all application files are present
3. Run `BUILD_INSTALLER.bat` as Administrator
4. Check the console output for specific errors

---

**Ready?** Just double-click **`BUILD_INSTALLER.bat`** and wait!
