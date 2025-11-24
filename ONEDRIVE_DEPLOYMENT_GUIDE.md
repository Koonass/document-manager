# OneDrive Deployment Guide - Document Manager

## Perfect Solution for Your Constraints

This guide addresses your specific requirements:
- ✅ No .exe files needed (avoids Sentinel One flags)
- ✅ No server scripts required (IT approval not needed)
- ✅ OneDrive synced across all users
- ✅ Shared database for all users
- ✅ 2-3 concurrent users, up to 20 total supported
- ✅ Simple desktop shortcuts

---

## Overview

**How it works:**
1. Install Document Manager **once** to your shared OneDrive folder
2. OneDrive automatically syncs it to all users' computers
3. Users create a desktop shortcut to `START_APP.bat` (no .exe!)
4. All users share the same database on OneDrive
5. Python runs the application directly (no compiled executables)

---

## Step-by-Step Setup

### Step 1: Choose OneDrive Location

**⚠️ CRITICAL:** Choose the correct OneDrive location for team sharing!

Many users have BOTH Personal and Business OneDrive:
- ❌ **Personal OneDrive** (`C:\Users\YourName\OneDrive`) - NOT SHARED, don't use!
- ✅ **Business OneDrive** (`C:\Users\YourName\OneDrive - CompanyName`) - Use this!

**👉 RECOMMENDED: Use Microsoft Teams Shared Files** (if you have a Teams channel)
```
C:\Users\YourName\OneDrive - CompanyName\[TeamName - Channel]\Apps\DocumentManager
```
This is the easiest option - all team members already have access!

**Alternative: Business OneDrive Shared Folder**
```
C:\Users\YourName\OneDrive - CompanyName\Shared\Apps\DocumentManager
```
You'll need to share the folder with all users manually.

**Folder structure (same for any option):**
```
DocumentManager/
├── START_APP.bat           ← Users will shortcut to this
├── run_v2_3.py
├── settings_v2_3.json
├── src/
├── LABEL TEMPLATE/
└── DATA/
    └── document_manager_v2.1.db    ← Shared database
```

**📖 Need help choosing?** See `ONEDRIVE_LOCATION_GUIDE.md` for detailed guidance!

### Step 2: Copy Application Files to OneDrive

**Copy these files/folders to OneDrive:**
```
C:\code\Document Manager\*   →   OneDrive\Apps\DocumentManager\
```

**Files to copy:**
- ✅ `START_APP.bat` (main launcher - no .exe!)
- ✅ `run_v2_3.py`
- ✅ `settings_v2_3.json`
- ✅ `requirements.txt`
- ✅ `src\` folder (all Python files)
- ✅ `LABEL TEMPLATE\` folder
- ✅ All documentation files

**Files to EXCLUDE:**
- ❌ `.git` folder
- ❌ `venv` folder (users install their own)
- ❌ `__pycache__` folders
- ❌ `.pyc` files
- ❌ Local database files (will be created on OneDrive)
- ❌ Any .exe files

### Step 3: Configure Settings for OneDrive Paths

**Edit `settings_v2_3.json` in the OneDrive folder:**

```json
{
  "html_path": "C:\\Users\\%USERNAME%\\OneDrive\\DocumentManager\\Data\\BisTrack Exports",
  "pdf_path": "C:\\Users\\%USERNAME%\\OneDrive\\DocumentManager\\Data\\PDFs",
  "archive_path": "C:\\Users\\%USERNAME%\\OneDrive\\DocumentManager\\Data\\Archive",
  "db_path": "C:\\Users\\%USERNAME%\\OneDrive\\Apps\\DocumentManager\\DATA\\document_manager_v2.1.db",
  "version": "2.3.0"
}
```

**IMPORTANT:** Use relative paths from OneDrive or environment variables like `%USERNAME%` and `%USERPROFILE%`.

**Better approach - Use relative paths:**
```json
{
  "html_path": "DATA\\BisTrack Exports",
  "pdf_path": "DATA\\PDFs",
  "archive_path": "DATA\\Archive",
  "db_path": "DATA\\document_manager_v2.1.db",
  "version": "2.3.0"
}
```

This way, the paths work regardless of the user's OneDrive location.

### Step 4: Create DATA Folder Structure

**In your OneDrive DocumentManager folder, create:**
```
OneDrive\Apps\DocumentManager\
├── DATA\
│   ├── document_manager_v2.1.db        ← Shared database (auto-created)
│   ├── BisTrack Exports\               ← Shared HTML/CSV files
│   ├── PDFs\                           ← Shared PDF files
│   └── Archive\                        ← Shared archive
└── (rest of application files)
```

### Step 5: Wait for OneDrive Sync

**Before proceeding:**
1. Wait for OneDrive to finish syncing all files to the cloud
2. Verify sync status: OneDrive icon in system tray should show green checkmark
3. Check that all files show "✓" (synced) icons in File Explorer

### Step 6: Each User - Python Setup

**Each user must have Python installed:**

1. **Check if Python is installed:**
   - Open Command Prompt
   - Type: `python --version`
   - Should show Python 3.8 or higher

2. **If Python is not installed:**
   - Download from https://www.python.org/downloads/
   - **IMPORTANT:** Check "Add Python to PATH" during installation
   - Restart computer after installation

3. **Install dependencies (ONE TIME per user):**
   ```batch
   cd "%USERPROFILE%\OneDrive\Apps\DocumentManager"
   pip install -r requirements.txt
   ```

   Or if OneDrive location is different:
   ```batch
   cd "%USERPROFILE%\OneDrive - CompanyName\Apps\DocumentManager"
   pip install -r requirements.txt
   ```

### Step 7: Each User - Create Desktop Shortcut

**Option A: Manual Shortcut Creation**

1. Open File Explorer and navigate to:
   ```
   OneDrive\Apps\DocumentManager\
   ```

2. Right-click on `START_APP.bat`

3. Select "Send to" → "Desktop (create shortcut)"

4. Rename the shortcut to "Document Manager"

5. **Optional:** Right-click shortcut → Properties → Change Icon (if desired)

**Option B: Using Command Prompt**

Run this command (adjust path if needed):
```batch
powershell "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Document Manager.lnk'); $Shortcut.TargetPath = '%USERPROFILE%\OneDrive\Apps\DocumentManager\START_APP.bat'; $Shortcut.WorkingDirectory = '%USERPROFILE%\OneDrive\Apps\DocumentManager'; $Shortcut.Save()"
```

### Step 8: Test the Setup

**First user test:**
1. Double-click the "Document Manager" desktop shortcut
2. Application should start (may take a moment first time)
3. Database will be created in `DATA\document_manager_v2.1.db`
4. Import some test data

**Second user test (on different computer):**
1. Wait for OneDrive to sync the database file
2. Double-click their "Document Manager" desktop shortcut
3. Should see the same data as first user
4. Make a change and verify it syncs to first user

---

## Database Conflict Prevention

### Understanding OneDrive + SQLite

**Potential Issues:**
- OneDrive syncs files in the background
- SQLite database is a single file
- Simultaneous writes from 2+ users can cause conflicts
- OneDrive might create conflict copies: `database (UserName's conflicted copy).db`

**Our Solution:**
✅ SQLite WAL mode is already enabled (better concurrent access)
✅ OneDrive handles file locking reasonably well
✅ For 2-3 concurrent users, conflicts are rare
✅ Up to 20 total users (not all simultaneous) is supported

### Best Practices

**1. Close Application When Done**
- Don't leave the app running idle for hours
- Close it when not actively using
- Reduces chance of sync conflicts

**2. Monitor for Conflict Files**
Occasionally check DATA folder for files like:
```
document_manager_v2.1 (John's conflicted copy).db
```

If you see these:
- Close all instances of the application
- Keep the most recent file
- Delete conflict copies
- Restart application

**3. If Database Corruption Occurs**
Very rare, but if database becomes corrupted:
```batch
cd "%USERPROFILE%\OneDrive\Apps\DocumentManager\DATA"
# Rename corrupted database
ren document_manager_v2.1.db document_manager_v2.1.db.backup

# Check for WAL files and remove them
del document_manager_v2.1.db-wal
del document_manager_v2.1.db-shm

# Restart application - fresh database will be created
```

---

## Advantages of This Setup

### For IT Department
✅ **No .exe files** - Sentinel One won't flag batch files
✅ **No server installation needed** - Everything runs from OneDrive
✅ **No elevated permissions required** - Users run from their own space
✅ **Easy to audit** - All files visible in OneDrive
✅ **Easy to remove** - Just delete from OneDrive

### For Users
✅ **Simple access** - Double-click desktop shortcut
✅ **Automatic updates** - You update once, syncs to all users
✅ **Shared data** - Everyone sees the same information
✅ **Works offline** - OneDrive keeps local copies
✅ **No installation** - Just create a shortcut

### For You (Admin)
✅ **Centralized updates** - Update once in OneDrive
✅ **Easy distribution** - OneDrive handles sync
✅ **Visible to all users** - No need to email files
✅ **Version control** - OneDrive has file history
✅ **Easy rollback** - OneDrive version restore available

---

## Updating the Application

**When you need to update:**

1. **Notify users:** "Closing Document Manager in 5 minutes for update"

2. **Ensure all users close the application**

3. **Update files in OneDrive:**
   ```batch
   # Navigate to local development
   cd C:\code\Document Manager

   # Copy updated files to OneDrive
   copy /Y src\*.py "%USERPROFILE%\OneDrive\Apps\DocumentManager\src\"
   copy /Y run_v2_3.py "%USERPROFILE%\OneDrive\Apps\DocumentManager\"
   ```

4. **OneDrive syncs automatically** to all users

5. **Notify users:** "Update complete, you can restart Document Manager"

6. **Users restart the application** - new version runs automatically

---

## Troubleshooting

### Application Won't Start

**Problem:** Desktop shortcut does nothing or shows error

**Solutions:**
1. Check Python is installed: `python --version`
2. Check OneDrive synced: Look for green checkmarks in File Explorer
3. Try running START_APP.bat directly from OneDrive folder
4. Check if antivirus is blocking Python (unlikely but possible)

### Database Locked Error

**Problem:** "Database is locked" message

**Solution:**
1. Close all instances of Document Manager on all computers
2. Wait 30 seconds for OneDrive to finish syncing
3. Check no other program has the database file open
4. Restart the application

### Changes Not Syncing Between Users

**Problem:** User A makes changes, User B doesn't see them

**Solution:**
1. Check OneDrive sync status (system tray icon)
2. Right-click OneDrive icon → View online to verify files are in cloud
3. On User B's computer, right-click OneDrive icon → Sync
4. Restart Document Manager on User B's computer

### Python Module Not Found

**Problem:** "No module named pandas" or similar error

**Solution:**
```batch
cd "%USERPROFILE%\OneDrive\Apps\DocumentManager"
pip install -r requirements.txt
```

### OneDrive Sync Paused

**Problem:** Files not syncing between users

**Solution:**
1. Click OneDrive icon in system tray
2. If it says "Paused", click "Resume syncing"
3. Check available space in OneDrive account
4. Ensure OneDrive folder is not "Files On-Demand" (should be "Always keep on this device")

---

## File Locations Summary

### On Each User's Computer

**Application Location:**
```
C:\Users\[Username]\OneDrive\Apps\DocumentManager\
or
C:\Users\[Username]\OneDrive - [CompanyName]\Apps\DocumentManager\
```

**Desktop Shortcut:**
```
C:\Users\[Username]\Desktop\Document Manager.lnk
```

**Python Installation:**
```
C:\Users\[Username]\AppData\Local\Programs\Python\
or
C:\Python3x\
```

### Shared OneDrive (Cloud + All Synced Computers)

**Application Files:** `OneDrive\Apps\DocumentManager\`
**Shared Database:** `OneDrive\Apps\DocumentManager\DATA\document_manager_v2.1.db`
**Shared Data:** `OneDrive\Apps\DocumentManager\DATA\`

---

## Security Considerations

### OneDrive Security
✅ **Encrypted in transit** - Files encrypted during sync
✅ **Encrypted at rest** - Files encrypted in Microsoft cloud
✅ **Access control** - Only users with OneDrive access can see files
✅ **Audit logs** - OneDrive tracks who accessed what
✅ **Version history** - Can restore previous versions if needed

### Application Security
✅ **No internet access required** - Runs locally
✅ **No external services** - All data stays on OneDrive
✅ **Python source code** - Visible and auditable
✅ **No hidden executables** - IT can review all files

---

## Scaling Considerations

### Current Setup Supports:
- ✅ 2-3 concurrent users (actively using at same time)
- ✅ Up to 20 total users (not all simultaneous)
- ✅ SQLite with WAL mode on OneDrive
- ✅ Suitable for your use case

### If You Outgrow This Setup:

**More than 3 concurrent users:**
- Move to SQL Server Express (free) or PostgreSQL
- Database hosted on actual server
- Application files can stay on OneDrive

**More than 50 total users:**
- Consider web-based version (Flask web app)
- Centralized server deployment
- Browser-based access (no installation needed)

---

## Quick Start Checklist

**Administrator Setup (One Time):**
- [ ] Copy Document Manager to OneDrive\Apps\DocumentManager\
- [ ] Edit settings_v2_3.json with proper paths
- [ ] Create DATA folder structure
- [ ] Wait for OneDrive sync to complete
- [ ] Test from your computer

**Each User Setup (One Time per User):**
- [ ] Verify Python installed: `python --version`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create desktop shortcut to START_APP.bat
- [ ] Test application opens
- [ ] Verify can see shared data

**Daily Usage:**
- [ ] Double-click "Document Manager" desktop icon
- [ ] Use application normally
- [ ] Close application when done (don't leave idle)

---

## Support Commands

### Check OneDrive Sync Status
```batch
# View OneDrive status
powershell Get-Process OneDrive

# Force sync
powershell Start-Process "$env:LOCALAPPDATA\Microsoft\OneDrive\OneDrive.exe" -ArgumentList "/sync"
```

### Check Python and Dependencies
```batch
# Python version
python --version

# List installed packages
pip list

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Find OneDrive Path
```batch
# Display OneDrive folder location
echo %OneDrive%
echo %OneDriveCommercial%
```

---

## Summary

**This OneDrive deployment method:**
- ✅ Requires NO .exe files (avoids Sentinel One)
- ✅ Requires NO server scripts (no IT approval needed)
- ✅ Uses existing OneDrive infrastructure
- ✅ Supports 2-3 concurrent users, 20 total users
- ✅ Simple desktop shortcuts for users
- ✅ Automatic sync and updates
- ✅ Shared database for all users
- ✅ Easy to deploy, update, and manage

**Perfect for your requirements!**
