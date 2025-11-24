# Document Manager v2.4 - Portable Deployment Guide

## What is Portable Deployment?

A **completely self-contained** version that runs from any location with ZERO installation:

✅ **No Python installation needed** - Python bundled
✅ **No dependencies needed** - All packages included
✅ **No admin rights needed** - Runs as regular user
✅ **No installation process** - Just copy and run
✅ **Works anywhere** - USB, OneDrive, network share, local drive
✅ **No conflicts** - Won't interfere with system Python
✅ **No antivirus issues** - Plain Python scripts, no .exe

Perfect for: Office environments, multiple computers, non-technical users, restricted machines

---

## Quick Start (For Users)

### If you received a portable package:

1. **Copy the folder** to your desired location:
   - USB drive: `E:\DocumentManager\`
   - OneDrive: `C:\Users\YourName\OneDrive\Apps\DocumentManager\`
   - Local: `C:\Apps\DocumentManager\`
   - Network: `\\server\share\DocumentManager\`

2. **Double-click:** `START_PORTABLE.bat`

3. **That's it!** The application runs immediately.

---

## Building the Portable Package (For Developers/IT)

### Prerequisites

- Windows PC with internet connection
- PowerShell (included in Windows)
- 500MB free disk space

### Build Steps

1. **Open PowerShell or Command Prompt** in the project folder:
   ```
   cd "C:\code\Document Manager"
   ```

2. **Run the build script:**
   ```
   BUILD_PORTABLE_PACKAGE.bat
   ```

   Or directly with PowerShell:
   ```powershell
   .\BUILD_PORTABLE_PACKAGE.ps1
   ```

3. **Wait 3-5 minutes** while it:
   - Downloads Python 3.11.9 portable (~25MB)
   - Installs PyQt5 (~200MB)
   - Installs pywin32 (~50MB)
   - Copies your application files
   - Configures everything

4. **Find your package** at: `portable-build\`

### What Gets Built

```
portable-build/              (~350-400MB total)
├── python/                  (~300MB - Portable Python + packages)
│   ├── python.exe
│   ├── python311.dll
│   ├── Lib/
│   │   ├── site-packages/
│   │   │   ├── PyQt5/       (GUI framework)
│   │   │   └── win32com/    (Word automation)
│   └── Scripts/
├── src/                     (~2MB - Your application code)
├── LABEL TEMPLATE/          (Word template)
├── START_PORTABLE.bat       (Main launcher)
├── SETUP_FOR_NEW_USER.bat   (First-time setup)
├── settings_v2_4_template.json
└── [documentation files]
```

---

## Deployment Methods

### Method 1: USB Drive (Best for Testing)

1. **Build portable package** (see above)
2. **Copy `portable-build` folder** to USB drive
3. **Rename** to `DocumentManager` (optional)
4. **Safely eject** USB drive
5. **Plug into any Windows PC**
6. **Run** `START_PORTABLE.bat`

**Benefits:**
- Works offline
- Take it anywhere
- Data travels with you
- No network needed

**Use case:** Field work, testing, personal use

---

### Method 2: OneDrive (Best for Teams)

1. **Build portable package**
2. **Copy to OneDrive** shared folder:
   ```
   C:\Users\YourName\OneDrive\Apps\DocumentManager\
   ```
3. **Wait for sync** (OneDrive icon shows green checkmark)
4. **Share folder** with team members (if using OneDrive for Business)
5. **Team members** run `START_PORTABLE.bat` from their synced folder

**Benefits:**
- Automatic updates (copy new files, OneDrive syncs)
- Shared database (2-3 concurrent users)
- Backup included (OneDrive versioning)
- Access from multiple computers

**Use case:** Small teams (2-5 people), shared database

**Important Notes:**
- Close app when not in use (prevents sync conflicts)
- OneDrive needs time to sync (~5 mins for initial 400MB)
- Each user runs their own instance
- Database supports 2-3 concurrent users safely

---

### Method 3: Network Share (Best for Organizations)

1. **Build portable package**
2. **IT copies to network share:**
   ```
   \\fileserver\apps\DocumentManager\
   ```
3. **Set permissions** (read/execute for users, write for DATA folder)
4. **Create desktop shortcut** for users:
   - Target: `\\fileserver\apps\DocumentManager\START_PORTABLE.bat`
   - Run: Normal window
5. **Users click shortcut** to run

**Benefits:**
- Centralized management
- Single source of truth
- IT controls updates
- Shared database for team

**Use case:** Departments, workgroups, enterprise deployment

**Network Requirements:**
- Moderate bandwidth (loads ~50MB on startup)
- Low latency (< 50ms response time)
- Persistent connection while app runs

---

### Method 4: Local Installation (Best for Single User)

1. **Build portable package**
2. **Copy to local drive:**
   ```
   C:\Apps\DocumentManager\
   ```
3. **Create desktop shortcut** to `START_PORTABLE.bat`
4. **Run from shortcut**

**Benefits:**
- Fastest performance
- No network dependency
- Full offline access
- Private data

**Use case:** Individual users, offline work, best performance

---

## First Time Setup

When a user runs `START_PORTABLE.bat` for the first time:

1. **Portable Python is detected automatically**
2. **Setup prompt appears** if no settings exist:
   ```
   Would you like to run setup now?
   ```
3. **If user chooses Yes:**
   - Creates `settings_v2_4.json` from template
   - Creates `DATA\` folder structure
   - Creates `DATA\BisTrack Exports\`
   - Creates `DATA\PDFs\`
   - Creates `DATA\Archive\`
   - Launches application

4. **If user chooses No:**
   - Manual setup required later
   - Run `SETUP_FOR_NEW_USER.bat` separately

---

## Updating the Portable Package

### Method A: Rebuild Entire Package (Safest)

When you have code changes:

1. **Pull latest from GitHub** (or update local files)
2. **Run** `BUILD_PORTABLE_PACKAGE.bat` again
3. **Deploy the new `portable-build` folder**

**Important:** Tell users to:
- Close the application
- Back up their `DATA\` folder (contains database)
- Copy new files
- Restore their `DATA\` folder if overwritten

### Method B: Update Just Source Code (Faster)

For Python code changes only (no dependency changes):

1. **Copy updated files** to portable package:
   ```batch
   xcopy /E /I /Y src portable-build\src
   copy /Y run_v2_4.py portable-build\
   ```

2. **Deploy just the updated files**

**Users don't need to do anything** - OneDrive syncs automatically

---

## Troubleshooting

### "Portable Python not found!"

**Cause:** `python\` folder missing or incomplete

**Solutions:**
- Wait for OneDrive/network sync to complete
- Check folder size (should be ~300MB)
- Rebuild portable package if corrupted
- Verify antivirus didn't quarantine files

---

### "Portable Python exists but won't run!"

**Cause:** Incomplete sync, corrupted files, or antivirus blocking

**Solutions:**
1. **Check file count** in `python\` folder (should be 50+ files)
2. **Check OneDrive sync** (green checkmark icon)
3. **Check antivirus logs** (whitelist the folder if needed)
4. **Rebuild portable package** on different machine

---

### "Application exited with error"

**Cause:** Missing dependencies or code issues

**Solutions:**
1. **Check error message** in console window
2. **Verify packages installed:**
   ```batch
   python\python.exe -m pip list
   ```
   Should show: PyQt5, pywin32
3. **Reinstall packages:**
   ```batch
   python\python.exe -m pip install --force-reinstall PyQt5 pywin32
   ```

---

### Slow startup from network share

**Cause:** Network loading Python files on every import

**Solution:**
- Copy to local drive for best performance
- Or optimize network (SMB3, 1Gbps+ connection)
- Or cache frequently used files locally

---

### Multiple users, database locked

**Cause:** SQLite has limited concurrent access

**Solutions:**
- Limit to 2-3 concurrent users
- Users close app when not in use
- Consider database upgrade for >3 users
- Use local copies with data sync instead

---

## Package Size Optimization

If 350MB is too large:

### Option 1: Remove Unused Libraries
Edit `BUILD_PORTABLE_PACKAGE.ps1` to install only what's needed:
```powershell
$packages = @("PyQt5", "pywin32")  # Minimal set
```

### Option 2: Use Python 3.10 (Smaller)
Change in build script:
```powershell
$PythonVersion = "3.10.11"  # ~50MB smaller
```

### Option 3: Compress for Distribution
Use 7-Zip or WinRAR:
- 350MB package → ~100MB compressed
- Users extract before running

---

## Security Considerations

### What's Safe

✅ **No executables** - Pure Python scripts
✅ **No code signing needed** - Interpreter is official Python
✅ **No admin rights** - Runs in user context
✅ **No system modifications** - Completely portable
✅ **Source visible** - Users can read Python code

### What to Watch

⚠ **Database on shared drive** - Anyone with access can read it
⚠ **Settings in plain text** - Passwords stored unencrypted
⚠ **No authentication** - App itself has no login

### Recommendations

1. **Use NTFS permissions** on network shares
2. **Don't store passwords** in settings files
3. **Encrypt sensitive data** in database if needed
4. **Use OneDrive Business** for access controls

---

## Performance Comparison

| Deployment | Startup Time | Running Performance | Updates |
|------------|--------------|---------------------|---------|
| **Portable - USB** | ~5 sec | Excellent | Manual copy |
| **Portable - Local** | ~3 sec | Excellent | Manual copy |
| **Portable - OneDrive** | ~6 sec | Excellent | Automatic sync |
| **Portable - Network** | ~10 sec | Good | Automatic |
| **System Python** | ~3 sec | Excellent | Git pull |

---

## FAQ

**Q: Can I use this on Mac or Linux?**
A: No, this package is Windows-only. Python itself is cross-platform, but pywin32 (Word automation) requires Windows.

**Q: Will this work on Windows 11?**
A: Yes! Works on Windows 10 and 11.

**Q: Can I customize Python version?**
A: Yes, edit `BUILD_PORTABLE_PACKAGE.ps1` and change `$PythonVersion`

**Q: Do I need to rebuild for each user?**
A: No! Build once, copy to all users.

**Q: Can users modify the code?**
A: Yes, Python source is included. Changes apply immediately on next run.

**Q: What if Python.org is blocked?**
A: Download Python manually, extract to `portable-build\python\`

**Q: Can I add more Python packages?**
A: Yes:
```batch
portable-build\python\python.exe -m pip install package_name
```

---

## Support

For issues:
1. Check this guide's Troubleshooting section
2. See DEPLOYMENT_README.md for general deployment help
3. Check Python and package versions:
   ```batch
   python\python.exe --version
   python\python.exe -m pip list
   ```

---

## Technical Details

### Python Embedded vs Standard

This package uses **Python Embedded Distribution**:
- Minimal size (~25MB vs ~100MB)
- No installer needed
- No registry modifications
- Pure portable
- Optimized for redistribution

### Package Structure

- `python311.dll` - Core Python runtime
- `Lib/` - Standard library modules
- `Lib/site-packages/` - Third-party packages (PyQt5, pywin32)
- Modified `python311._pth` - Enables site-packages

### Why This Works

1. All paths are relative (`%~dp0`)
2. Python finds libraries via `._pth` file
3. No environment variables needed
4. No PATH modifications required
5. No DLL conflicts with system Python

---

**Last Updated:** 2024-11-24
**Package Version:** v2.4
**Python Version:** 3.11.9
**Build Script:** BUILD_PORTABLE_PACKAGE.ps1
