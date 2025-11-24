# OneDrive Quick Start - 5 Minute Setup

## For Administrator (First Setup)

### 1. Choose the RIGHT OneDrive (IMPORTANT!)

**⚠️ Critical: Do you have BOTH Personal and Business OneDrive?**

Most users have TWO OneDrive folders:
- ❌ `C:\Users\YourName\OneDrive` (Personal - NOT shared with team!)
- ✅ `C:\Users\YourName\OneDrive - CompanyName` (Business - Use this!)

**👉 BEST OPTION: Microsoft Teams Shared Folder**
If you have a Teams channel with your users, deploy there:
```
C:\Users\YourName\OneDrive - CompanyName\[TeamName - Channel]\Apps\DocumentManager
```

**Alternative: Business OneDrive Shared Folder**
```
C:\Users\YourName\OneDrive - CompanyName\Shared\Apps\DocumentManager
```

**📖 Not sure which to use?** See `ONEDRIVE_LOCATION_GUIDE.md`

### 2. Deploy Files (5 minutes)

**Easy Way - Use Deployment Script:**
```batch
cd C:\code\Document Manager
DEPLOY_TO_ONEDRIVE.bat
```
The script will:
- Detect both Personal and Business OneDrive
- Help you choose the correct location
- Copy all necessary files
- Set up folder structure

**Manual Way - Copy Files:**
```batch
# Copy to your chosen location
C:\code\Document Manager\*  →  [Your OneDrive Location]\Apps\DocumentManager\

Include:
✅ START_APP.bat
✅ SETUP_PYTHON_DEPS.bat
✅ run_v2_3.py
✅ settings_v2_3_onedrive_example.json
✅ requirements.txt
✅ src\ folder
✅ LABEL TEMPLATE\ folder
✅ Documentation files

Exclude:
❌ venv\ folder
❌ __pycache__\ folders
❌ .git\ folder
❌ Any .exe files
```

### 3. Create DATA Folder
```
OneDrive\Apps\DocumentManager\
└── DATA\
    ├── BisTrack Exports\    (create empty)
    ├── PDFs\                (create empty)
    └── Archive\             (create empty)
```

### 4. Configure Settings
```batch
# Rename example settings file:
settings_v2_3_onedrive_example.json  →  settings_v2_3.json

# File already configured with relative paths - no editing needed!
```

### 5. Wait for Sync
- Check OneDrive icon in system tray
- Wait for green checkmark (all files synced)

---

## For Each User (One-Time Setup)

### 1. Verify Python (30 seconds)
Open Command Prompt and type:
```batch
python --version
```

**Should show:** Python 3.8.x or higher

**If not found:** Download from https://python.org (check "Add to PATH")

### 2. Install Dependencies (2 minutes)
Navigate to OneDrive folder and run:
```batch
# Option 1: Double-click this file
SETUP_PYTHON_DEPS.bat

# Option 2: Manual command
cd "%USERPROFILE%\OneDrive\Apps\DocumentManager"
pip install -r requirements.txt
```

### 3. Create Desktop Shortcut (30 seconds)
**Easy Method:**
1. Open File Explorer → Navigate to OneDrive\Apps\DocumentManager\
2. Right-click `START_APP.bat`
3. Send to → Desktop (create shortcut)
4. Rename shortcut to "Document Manager"

**Command Method:**
```batch
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\Document Manager.lnk');$s.TargetPath='%USERPROFILE%\OneDrive\Apps\DocumentManager\START_APP.bat';$s.WorkingDirectory='%USERPROFILE%\OneDrive\Apps\DocumentManager';$s.Save()"
```

### 4. Test It!
Double-click "Document Manager" on desktop - should launch!

---

## Daily Usage

**To Start:** Double-click "Document Manager" desktop icon
**To Close:** Click X button in application
**That's it!**

---

## Key Points

✅ **No .exe files** - Won't trigger Sentinel One
✅ **No IT approval needed** - Runs from OneDrive
✅ **Automatic updates** - Admin updates once, syncs to all
✅ **Shared database** - Everyone sees same data
✅ **2-3 concurrent users supported** - Works perfectly for your team

---

## Troubleshooting

**App won't start?**
→ Run `SETUP_PYTHON_DEPS.bat` again

**Changes not syncing?**
→ Check OneDrive icon (system tray) - should show synced

**Database locked error?**
→ Close app on all computers, wait 30 seconds, reopen

---

## File Locations

**On Your Computer:**
- Application: `C:\Users\[You]\OneDrive\Apps\DocumentManager\`
- Shortcut: `C:\Users\[You]\Desktop\Document Manager.lnk`

**Synced Across Everyone:**
- Database: `OneDrive\Apps\DocumentManager\DATA\document_manager_v2.1.db`
- All app files automatically synced via OneDrive

---

## Support

**For detailed setup:** See `ONEDRIVE_DEPLOYMENT_GUIDE.md`
**For settings help:** See `settings_v2_3_onedrive_example.json`
**For general questions:** See `README.md`
