# Document Manager - Network Deployment Setup Guide

## Overview

This guide explains how to deploy Document Manager V2.3 to a network share for 3-5 users, avoiding executable distribution and network access issues.

**Benefits of this approach:**
- ✅ No executable files to distribute
- ✅ No network access blocking issues
- ✅ Centralized updates (update once, affects all users)
- ✅ Separate testing and production environments
- ✅ Simple batch file launchers
- ✅ Full printer access maintained

---

## Quick Start (Already Set Up)

If the network deployment is already configured, users just need to:

1. **Navigate to production folder:**
   - `\\SERVER\Apps\DocumentManager\PRODUCTION\`

2. **Double-click:**
   - `START_APP.bat`

3. **First-time setup only:**
   - If prompted for dependencies: `python -m pip install -r requirements.txt`

That's it! The application launches with full printer and network path access.

---

## Initial Network Setup (IT/Admin)

### Option A: Simple Local Setup (Current)

For local development or small-scale testing:

1. **Your current setup is ready to use**
   - Just run `START_APP.bat` to launch
   - Run `START_APP_TEST.bat` for testing new features

2. **When testing changes:**
   - Make changes to code
   - Test with `START_APP_TEST.bat`
   - When satisfied, changes are already in your working version

### Option B: Full Network Deployment (3-5 Users)

For deploying to multiple users on a network:

#### Step 1: Create Network Share Structure

```
\\SERVER\Apps\DocumentManager\
├── PRODUCTION\              ← Users run this (stable version)
├── TESTING\                 ← Developer tests here (your sandbox)
└── DATA\                    ← Shared data (optional)
```

**PowerShell commands:**
```powershell
# Create directory structure on network share
$basePath = "\\SERVER\Apps\DocumentManager"
New-Item -Path "$basePath\PRODUCTION" -ItemType Directory -Force
New-Item -Path "$basePath\TESTING" -ItemType Directory -Force
New-Item -Path "$basePath\DATA" -ItemType Directory -Force
New-Item -Path "$basePath\BACKUPS" -ItemType Directory -Force
```

#### Step 2: Copy Application Files

**Copy to PRODUCTION folder:**
```
\\SERVER\Apps\DocumentManager\PRODUCTION\
├── START_APP.bat           ← User launcher (production)
├── run_v2_3.py             ← Main application entry
├── requirements.txt        ← Python dependencies
├── src\                    ← All Python modules
│   ├── main_v2_3.py
│   ├── enhanced_database_v2.py
│   ├── advanced_print_manager.py
│   └── ... (all .py files)
├── LABEL TEMPLATE\         ← Word template
│   └── Contract_Lumber_Label_Template.docx
├── settings_v2_3.json      ← Application settings
└── network_printers.json   ← Printer configuration
```

**Copy to TESTING folder:**
- Same structure as PRODUCTION
- Use `START_APP_TEST.bat` launcher (includes warnings)

#### Step 3: Set Permissions

**Required permissions:**
- **PRODUCTION folder:** Read/Execute for all users, Write for IT/Admin only
- **TESTING folder:** Read/Write for developer/IT only
- **DATA folder:** Read/Write for all users (if using shared data)
- **BACKUPS folder:** Write for IT/Admin only

**PowerShell example:**
```powershell
# Grant users read access to PRODUCTION
$acl = Get-Acl "\\SERVER\Apps\DocumentManager\PRODUCTION"
$permission = "DOMAIN\DocumentManagerUsers","Read,ReadAndExecute","ContainerInherit,ObjectInherit","None","Allow"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
$acl.SetAccessRule($accessRule)
Set-Acl "\\SERVER\Apps\DocumentManager\PRODUCTION" $acl
```

#### Step 4: Configure Shared Database (REQUIRED for multi-user)

**IMPORTANT:** For multiple users to share data, all installations MUST point to the same database file.

**Edit `settings_v2_3.json` in PRODUCTION folder (or in each user's installation):**
```json
{
  "html_path": "\\\\SERVER\\Data\\DocumentManager\\Bistrack Exports",
  "pdf_path": "\\\\SERVER\\Data\\DocumentManager\\PDFs",
  "archive_path": "\\\\SERVER\\Data\\DocumentManager\\Archive",
  "db_path": "\\\\SERVER\\Apps\\DocumentManager\\DATA\\document_manager_v2.1.db",
  "version": "2.3.0"
}
```

**Key Points:**
- `db_path` specifies where the shared database file is stored
- All users must have read/write access to the database file location
- Use UNC paths (\\\\SERVER\\Share\\...) for network locations
- The database uses WAL mode for better concurrent access (2-3 users safe, up to 10 users supported)
- If `db_path` is not specified or is a relative path, each installation creates its own local database

**Database Location Recommendations:**
- ✅ **Recommended:** `\\\\SERVER\\Apps\\DocumentManager\\DATA\\document_manager_v2.1.db` (centralized with application)
- ✅ **Alternative:** `\\\\SERVER\\SharedData\\DocumentManager\\document_manager_v2.1.db` (separate data location)
- ❌ **Not Recommended:** Local paths like `C:\\...` (creates separate databases per user)

#### Step 5: Test Before User Rollout

1. **Test from a different computer:**
   - Navigate to `\\SERVER\Apps\DocumentManager\PRODUCTION\`
   - Run `START_APP.bat`
   - Verify it launches correctly
   - Test printer functionality
   - Test network path access

2. **Verify Python dependency installation:**
   ```batch
   python -m pip install -r requirements.txt
   ```

---

## Daily Workflow

### For Users (End Users)

**Starting the application:**

1. **Option A - Direct Launch:**
   - Navigate to: `\\SERVER\Apps\DocumentManager\PRODUCTION\`
   - Double-click: `START_APP.bat`

2. **Option B - Desktop Shortcut (Recommended):**
   - Right-click on desktop → New → Shortcut
   - Location: `\\SERVER\Apps\DocumentManager\PRODUCTION\START_APP.bat`
   - Name: "Document Manager"
   - Click Finish
   - Now double-click desktop icon to launch

**When updates are available:**
- Close the application
- Re-run `START_APP.bat` (or desktop shortcut)
- Updates are automatically applied

### For Developer (You)

#### Testing Workflow

**When making changes:**

1. **Edit code in TESTING folder** (or your local development folder)
   ```
   C:\code\Document Manager\  (your current location)
   or
   \\SERVER\Apps\DocumentManager\TESTING\
   ```

2. **Test changes:**
   ```batch
   # Run the testing launcher
   START_APP_TEST.bat
   ```

3. **Verify functionality:**
   - Test all modified features
   - Check printer functionality
   - Verify database operations
   - Test with real data

4. **Iterate as needed:**
   - Make more changes
   - Test again with `START_APP_TEST.bat`
   - Repeat until satisfied

#### Deployment Workflow

**When ready to deploy tested changes:**

1. **Run deployment script:**
   ```batch
   # For network deployment (if configured)
   DEPLOY_TO_PRODUCTION.bat
   ```

2. **Review what will be deployed:**
   - Script shows all files to be copied
   - Settings and database are NOT overwritten

3. **Confirm deployment:**
   - Type `yes` when prompted
   - Script creates automatic backup

4. **Notify users:**
   - Send message: "Document Manager updated, please restart the app"
   - Users close and re-run `START_APP.bat`

#### Rollback (If Needed)

**If deployment causes issues:**

1. **Locate backup:**
   ```
   \\SERVER\Apps\DocumentManager\BACKUPS\backup_YYYY-MM-DD_HH-MM\
   ```

2. **Restore files:**
   ```batch
   # Copy backup files back to PRODUCTION
   xcopy "\\SERVER\Apps\DocumentManager\BACKUPS\backup_2024-10-30_14-30\*" ^
         "\\SERVER\Apps\DocumentManager\PRODUCTION\" /E /Y
   ```

3. **Notify users to restart**

---

## Configuration

### Application Settings

**File:** `settings_v2_3.json`

**Local Installation (single user):**
```json
{
  "html_path": "C:\\Users\\SharedFolder\\Bistrack Exports",
  "pdf_path": "C:\\Users\\SharedFolder\\PDFs",
  "archive_path": "C:\\Users\\SharedFolder\\Archive",
  "db_path": "document_manager_v2.1.db",
  "version": "2.3.0"
}
```

**Network Installation (multiple users with shared database):**
```json
{
  "html_path": "\\\\SERVER\\Share\\Bistrack Exports",
  "pdf_path": "\\\\SERVER\\Share\\PDFs",
  "archive_path": "\\\\SERVER\\Share\\Archive",
  "db_path": "\\\\SERVER\\Apps\\DocumentManager\\DATA\\document_manager_v2.1.db",
  "version": "2.3.0"
}
```

**Important Notes:**
- Network paths use double backslashes in JSON
- `db_path` determines where the database is stored
- For shared installations, all users must point to the same `db_path`
- Ensure all users have read/write permissions to the database file location

### Printer Configuration

**File:** `network_printers.json`

Managed centrally by IT. Users' preferences stored separately in `user_preferences.json`.

**Setup printers:**
```batch
# Run printer setup wizard
run_printer_setup.bat
```

**Diagnostic tool:**
```batch
# Test printer connectivity
run_diagnostics.bat
```

---

## Python Requirements

### User Workstations

**Each user needs:**
- Python 3.8 or higher
- Required packages (installed once per user)

**One-time setup per user:**
```batch
# Navigate to PRODUCTION folder
cd \\SERVER\Apps\DocumentManager\PRODUCTION

# Install dependencies
python -m pip install -r requirements.txt
```

**Required packages:**
- pandas (CSV/HTML processing)
- PyPDF2 (PDF text extraction)
- pywin32 (Windows printer/Word integration)
- lxml (HTML parsing)

### Checking Python Installation

**Verify Python is available:**
```batch
python --version
# Should show: Python 3.8.x or higher
```

**If Python not found:**
- Install from: https://python.org/downloads/
- During installation: **Check "Add Python to PATH"**

---

## Troubleshooting

### Common Issues

#### 1. "Python not found" Error

**Symptoms:**
- Launcher shows "ERROR: Python not found!"

**Solutions:**
- Install Python: https://python.org/downloads/
- During install, check "Add Python to PATH"
- Or edit `START_APP.bat` to add your Python path

#### 2. "Missing dependencies" Error

**Symptoms:**
- Application fails to start
- Error mentions "No module named pandas" or similar

**Solution:**
```batch
cd \\SERVER\Apps\DocumentManager\PRODUCTION
python -m pip install -r requirements.txt
```

#### 3. Network Path Access Issues

**Symptoms:**
- Cannot access `\\SERVER\...` paths
- "Access denied" errors

**Solutions:**
- Verify network connectivity
- Check folder permissions
- Ensure user is in correct security group
- Test with Windows Explorer first

#### 4. Printer Not Found

**Symptoms:**
- Printers not appearing in application
- Print jobs fail

**Solutions:**
```batch
# Run printer diagnostics
cd \\SERVER\Apps\DocumentManager\PRODUCTION
run_diagnostics.bat
```

- Verify printer is installed on user's computer
- Check network printer connectivity
- Re-run printer setup wizard: `run_printer_setup.bat`

#### 5. Database Lock Errors

**Symptoms:**
- "Database is locked" errors
- Application won't start

**Solutions:**
- Close all instances of the application
- WAL mode is now enabled (reduces locking)
- If persistent, check no one has database file open
- Restart application

#### 6. Application Won't Start After Update

**Symptoms:**
- Application worked before deployment
- Now fails to start

**Solutions:**
- Check error message in launcher window
- Verify all files copied correctly
- Rollback to backup if needed:
  ```batch
  # Restore from backup
  xcopy "\\SERVER\Apps\DocumentManager\BACKUPS\backup_LATEST\*" ^
        "\\SERVER\Apps\DocumentManager\PRODUCTION\" /E /Y
  ```

### Getting Help

**For IT/Admin:**
- Check deployment logs in `BACKUPS\` folder
- Verify file permissions on network share
- Test from a different user account

**For Users:**
- Run diagnostics: `run_diagnostics.bat`
- Save output and send to IT
- Include error messages from launcher

---

## Maintenance

### Regular Tasks

**Weekly:**
- Check backup folder size
- Clean old backups (keep last 5)

**After Each Deployment:**
- Verify users can access updated version
- Monitor for error reports
- Keep deployment notes

**Monthly:**
- Review printer configurations
- Update Python dependencies if needed:
  ```batch
  python -m pip install --upgrade -r requirements.txt
  ```

### Backup Management

**Automatic backups created by deployment script:**
```
\\SERVER\Apps\DocumentManager\BACKUPS\
├── backup_2024-10-25_09-30\
├── backup_2024-10-28_14-15\
└── backup_2024-10-30_11-45\
```

**Clean old backups:**
```batch
# Keep only last 5 backups, delete older ones manually
# Navigate to BACKUPS folder and remove old dated folders
```

---

## Comparison: Current Setup vs Network Deployment

| Feature | Current (Local) | Network Deployment |
|---------|----------------|-------------------|
| **Users** | Single user | 3-5 concurrent users |
| **Updates** | Edit directly | Deploy TESTING → PRODUCTION |
| **Testing** | Use TEST.bat | Separate TESTING folder |
| **Data Sharing** | Local database | Can share database on network |
| **Printer Access** | ✅ Full access | ✅ Full access |
| **Network Paths** | ✅ Works | ✅ Works |
| **Executables** | ❌ None needed | ❌ None needed |
| **Deployment** | N/A (single user) | Copy script with backups |

---

## Next Steps

### For Current Local Setup

You're ready to go! Just use:
- `START_APP.bat` - For normal use
- `START_APP_TEST.bat` - For testing changes

### For Network Deployment

1. **Plan deployment:**
   - Choose network share location
   - Identify user group (3-5 users)
   - Set up permissions

2. **Initial setup:**
   - Create folder structure
   - Copy files to PRODUCTION
   - Test from user workstation

3. **User onboarding:**
   - Provide network path
   - Create desktop shortcuts
   - Install Python dependencies

4. **Establish workflow:**
   - TESTING → Test → Deploy → Notify users

---

## Summary

**Current Status:**
- ✅ WAL mode enabled for database (better concurrent access)
- ✅ Production launcher created: `START_APP.bat`
- ✅ Testing launcher created: `START_APP_TEST.bat`
- ✅ Deployment script created: `DEPLOY_TO_PRODUCTION.bat`
- ✅ Ready for local testing or network deployment

**You can now:**
1. Launch locally without terminal: `START_APP.bat`
2. Test changes safely: `START_APP_TEST.bat`
3. Deploy to network when ready (follow network setup section)

**No executables, no network blocking, full functionality maintained!**
