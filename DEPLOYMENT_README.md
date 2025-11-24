# Document Manager v2.4 - Deployment Guide

## Quick Start for New Users

This application is now **portable** and works for any user automatically!

### First Time Setup (3 minutes)

1. **Copy/sync this entire folder** to your location:
   - OneDrive: `C:\Users\YourName\OneDrive\Apps\DocumentManager\`
   - Local: `C:\Apps\DocumentManager\`
   - Network: `\\server\share\DocumentManager\`

2. **Run the setup script** (choose one):

   **Option A - Batch file (easiest):**
   ```
   Double-click: SETUP_FOR_NEW_USER.bat
   ```

   **Option B - Python script (more detailed):**
   ```
   python setup_new_deployment.py
   ```

3. **That's it!** The setup script will:
   - Create your settings file from template
   - Create the DATA folder structure
   - Validate everything is ready
   - Launch the application

### What Gets Created

```
DocumentManager/
├── DATA/                    ← Created automatically
│   ├── document_manager_v2.1.db (auto-created on first run)
│   ├── BisTrack Exports/   ← Put your HTML files here
│   ├── PDFs/                ← Generated PDFs saved here
│   └── Archive/             ← Archived records here
├── settings_v2_4.json       ← Created from template
└── LABEL TEMPLATE/          ← Must contain Word template
```

### After Setup

**Regular use:**
- Just run: `START_V2_4.bat`
- Or: `python run_v2_4.py`

**Updating to new version:**
1. Pull latest from GitHub (or copy new files)
2. Your DATA folder and settings are preserved
3. Run again!

## Multi-User Deployments

### OneDrive Deployment

Perfect for 2-3 users working from different computers:

1. **Primary user** runs setup once
2. OneDrive syncs to other users
3. **Each user** runs `SETUP_FOR_NEW_USER.bat` on their first use
4. Everyone shares the same DATA and database
5. Each user gets their own printer settings

**Important:**
- Close app when not in use to prevent sync conflicts
- Database supports 2-3 concurrent users
- All users see the same records

### Network Share Deployment

For shared access on company network:

1. IT places files on network share: `\\server\apps\DocumentManager\`
2. Each user runs setup on first use
3. Works from any computer
4. Shared database for team access

## Troubleshooting

### "Python not found"
- Install Python from python.org
- Or use portable Python (see PORTABLE_PYTHON_SETUP.md)

### "Template not found"
- Ensure `LABEL TEMPLATE\Contract_Lumber_Label_Template.docx` exists
- Get the template from your team
- Label printing won't work without it

### "Missing packages"
```bash
pip install PyQt5 pywin32
```

### Database locked
- Another user has the app open
- Close the app when not using it
- OneDrive needs time to sync

## Version Control & Updates

This project is on GitHub: https://github.com/Koonass/document-manager

**To get updates:**
```bash
cd "C:\code\Document Manager"
git pull origin master
```

Then deploy the updated files to your users via OneDrive or network share.

## Technical Details

### Why This Works for Multiple Users

1. **Relative paths** - Settings use `DATA\` not `C:\code\`
2. **Auto-detection** - Scripts find files relative to their location
3. **Template settings** - Each deployment copies from template
4. **No hardcoded usernames** - Works for any Windows user

### File Types

- **Source code** (src/) - Python modules
- **Launchers** (.bat files) - Windows batch scripts
- **Configuration** (.json) - Settings and presets
- **Documentation** (.md, .txt) - Guides and help
- **Template** (.docx) - Word document for labels

### What NOT to Commit to Git

The `.gitignore` excludes:
- User databases (*.db)
- User settings (settings_v2_4.json)
- Virtual environments (venv/)
- Test data (samples/, tests/html/)
- Portable Python (python/)

Keep these template files IN git:
- settings_v2_4_template.json
- settings_v2_3_onedrive_example.json

## Support

- Documentation: See DOCUMENTATION_INDEX.md
- Issues: Check existing .md files for specific topics
- Printer issues: PRINTER_TROUBLESHOOTING.txt
- Label issues: LABEL_PRINTING_TROUBLESHOOTING.md
