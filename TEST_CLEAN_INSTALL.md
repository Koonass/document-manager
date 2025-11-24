# Clean Installation Test - Document Manager v2.4

## Purpose
Verify that a brand new user can install and run the application with zero manual configuration.

## Test Environment Setup

### Step 1: Create Fresh Test Location
Choose ONE of these locations for testing:

**Option A - OneDrive Test:**
```
C:\Users\[YourName]\OneDrive\Apps\DocumentManager-Test\
```

**Option B - Local Test:**
```
C:\Apps\DocumentManager-Test\
```

**Option C - Network Share Test:**
```
\\server\share\DocumentManager-Test\
```

### Step 2: Copy Files
From your development folder (`C:\code\Document Manager`):

**What to copy:**
- ✅ `src/` folder (entire folder)
- ✅ `LABEL TEMPLATE/` folder (with .docx file)
- ✅ All `.bat` files
- ✅ All `.py` files in root
- ✅ `settings_v2_4_template.json` (important!)
- ✅ `requirements.txt`
- ✅ `.gitignore`
- ✅ All documentation (.md, .txt files)

**What NOT to copy (if they exist):**
- ❌ `DATA/` folder
- ❌ `settings_v2_4.json` (only copy the template)
- ❌ `venv/` folder
- ❌ `__pycache__/` folders
- ❌ `*.db` files
- ❌ `samples/`, `tests/`, `archive/` folders
- ❌ `python/` portable Python folder

### Step 3: Run Setup Script

Navigate to your test folder and run:
```
SETUP_FOR_NEW_USER.bat
```

## Test Checklist

### Phase 1: Installation
- [ ] Setup script starts without errors
- [ ] Settings file created from template
- [ ] DATA folder created
- [ ] DATA\BisTrack Exports\ created
- [ ] DATA\PDFs\ created
- [ ] DATA\Archive\ created
- [ ] Template validated successfully
- [ ] Python found and version displayed
- [ ] Application launches

### Phase 2: First Run
- [ ] Application window opens
- [ ] No error dialogs on startup
- [ ] Database created in DATA\ folder
- [ ] Can navigate UI without crashes

### Phase 3: Basic Operations
- [ ] Can import a CSV file
  - Copy a sample CSV to `DATA\BisTrack Exports\`
  - Click "Sync" or import button
  - Verify record appears in database

- [ ] Can view record details
  - Click on imported record
  - Expanded view opens
  - Data displays correctly

- [ ] Can generate label (if template is present)
  - Click "Print Label" or similar
  - Word opens with populated template
  - Close Word

- [ ] Can close application
  - Close application normally
  - No error messages

### Phase 4: Persistence
- [ ] Reopen application (using START_V2_4.bat)
- [ ] Previous data still present
- [ ] No re-initialization required
- [ ] Settings preserved

### Phase 5: Multi-User Test (Optional)
If you have access to another user account:

- [ ] Log in as different Windows user
- [ ] Access same OneDrive folder
- [ ] Run SETUP_FOR_NEW_USER.bat
- [ ] Application works for second user
- [ ] Both users see same database records

## Expected Results

### Files Created During Setup:
```
DocumentManager-Test/
├── DATA/                          ← Created by setup
│   ├── document_manager_v2.1.db  ← Created on first run
│   ├── BisTrack Exports/         ← Created by setup
│   ├── PDFs/                     ← Created by setup
│   └── Archive/                  ← Created by setup
├── settings_v2_4.json            ← Created by setup (copy of template)
└── [all other files unchanged]
```

### Settings File Verification
Open `settings_v2_4.json` and verify paths are RELATIVE:
```json
{
  "html_path": "DATA\\BisTrack Exports",    ← Should be relative
  "pdf_path": "DATA\\PDFs",                 ← Should be relative
  "archive_path": "DATA\\Archive",          ← Should be relative
  "db_path": "DATA\\document_manager_v2.1.db"  ← Should be relative
}
```

❌ BAD (will fail for other users):
```json
{
  "html_path": "C:/code/Document Manager/DATA/..."  ← Absolute path!
}
```

## Common Issues & Solutions

### Issue: "Python not found"
**Solution:**
- Install Python from python.org
- Or use portable Python setup
- Or ensure Python is in PATH

### Issue: "Template not found"
**Solution:**
- Ensure `LABEL TEMPLATE\Contract_Lumber_Label_Template.docx` exists
- Label printing won't work without it (but app should still run)

### Issue: "Module not found" errors
**Solution:**
```bash
pip install PyQt5 pywin32
```

### Issue: "Database locked"
**Solution:**
- Close any other instances of the app
- Check OneDrive isn't syncing at that moment
- Wait a few seconds and try again

## Success Criteria

✅ **Installation succeeds if:**
1. Setup script completes without fatal errors
2. Application launches successfully
3. Can import and view CSV data
4. Data persists after closing/reopening
5. No absolute paths in settings file

✅ **Multi-user ready if:**
1. Second user can run setup
2. Second user sees same database records
3. Both users can work with the application
4. No file permission errors

## Test Results

**Date:** _________________

**Tester:** _________________

**Test Location:** _________________

**Result:** ☐ PASS  ☐ FAIL

**Notes:**
___________________________________________________________________________
___________________________________________________________________________
___________________________________________________________________________

**Issues Found:**
___________________________________________________________________________
___________________________________________________________________________
___________________________________________________________________________

**Next Steps:**
___________________________________________________________________________
___________________________________________________________________________
___________________________________________________________________________
