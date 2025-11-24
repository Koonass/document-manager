# Deployment Package - Version 2.4.1

## ⚠️ DO NOT DEPLOY YET - TESTING IN PROGRESS

**Current Production Version:** v2.3 (Stable)
**This Version:** v2.4.1 (Development/Testing)
**Status:** Under testing, not ready for production

**See:** `V2_4_TESTING_CHECKLIST.md` for testing requirements before deployment

---

## What's New in This Update

### 🆕 New Features
1. **CSV Processing View** - Separate view for validating and uploading CSV files to BisTrack
2. **Shipping Schedule View** - Date-grouped read-only schedule of all orders
3. **Improved CSV Display** - Larger, centered CSV counts in calendar
4. **Automatic COM Cache Fix** - Folder label printing errors auto-repair

### 🐛 Bug Fixes
1. Fixed CSV files not being found/matched to orders
2. Fixed database compatibility issues with CSV tracking
3. Fixed "AttributeError: module 'win32com.gen_py.00020905'" in folder label printing
4. Removed CSV status from PDF-only views (cleaner display)
5. Removed PDF status from CSV-only views (cleaner display)

---

## Files to Deploy

### 📁 MODIFIED Files (Replace Existing)

Copy these files from your development folder to the user's installation:

```
src/
  ├── enhanced_expanded_view.py          ⬅️ REPLACE
  ├── main_v2_4.py                       ⬅️ REPLACE
  ├── statistics_calendar_widget.py      ⬅️ REPLACE
  ├── word_template_processor.py         ⬅️ REPLACE
  ├── verify_template.py                 ⬅️ REPLACE
  └── enhanced_database_manager.py       ⬅️ REPLACE
```

### 📄 NEW Files (Add to Installation)

Copy these NEW files to the user's installation:

```
src/
  ├── csv_batch_processor.py             ⬅️ NEW
  └── shipping_schedule_view.py          ⬅️ NEW

Root Directory/
  ├── FIX_WORD_COM_CACHE.bat             ⬅️ NEW (Optional helper tool)
  └── FOLDER_LABEL_PRINTING_FIX.md       ⬅️ NEW (Optional documentation)
```

---

## Step-by-Step Deployment

### For Local Installation (Same Machine)

1. **Backup Current Version**
   ```
   - Copy the user's entire "Document Manager" folder
   - Rename to "Document Manager - Backup [Date]"
   ```

2. **Copy Modified Files**
   ```
   Copy from: C:\code\Document Manager\src\
   Copy to:   [User's Installation]\src\

   Files to copy:
   - enhanced_expanded_view.py
   - main_v2_4.py
   - statistics_calendar_widget.py
   - word_template_processor.py
   - verify_template.py
   - enhanced_database_manager.py
   ```

3. **Copy New Files**
   ```
   Copy from: C:\code\Document Manager\src\
   Copy to:   [User's Installation]\src\

   Files to copy:
   - csv_batch_processor.py
   - shipping_schedule_view.py
   ```

4. **Copy Optional Tools**
   ```
   Copy from: C:\code\Document Manager\
   Copy to:   [User's Installation]\

   Files to copy:
   - FIX_WORD_COM_CACHE.bat (optional)
   - FOLDER_LABEL_PRINTING_FIX.md (optional)
   ```

5. **Test the Installation**
   - Run the application
   - Click "SYNC DATA" to verify CSV matching works
   - Check that new buttons appear in sidebar

---

### For OneDrive/Network Deployment

1. **Update OneDrive Shared Folder**
   ```
   Navigate to: OneDrive\Document Manager\

   Replace these files in src\ folder:
   - enhanced_expanded_view.py
   - main_v2_4.py
   - statistics_calendar_widget.py
   - word_template_processor.py
   - verify_template.py
   - enhanced_database_manager.py

   Add these NEW files to src\ folder:
   - csv_batch_processor.py
   - shipping_schedule_view.py

   Add to root folder (optional):
   - FIX_WORD_COM_CACHE.bat
   - FOLDER_LABEL_PRINTING_FIX.md
   ```

2. **Notify Users**
   - Send email/message to users
   - Tell them to close the app and restart
   - OneDrive will sync the new files automatically

---

## Quick Copy Commands (Windows)

### If deploying from C:\code\Document Manager to user installation:

```batch
REM Set the user's installation path
set USER_PATH=C:\Users\[USERNAME]\OneDrive\Document Manager

REM Copy modified files
copy "C:\code\Document Manager\src\enhanced_expanded_view.py" "%USER_PATH%\src\"
copy "C:\code\Document Manager\src\main_v2_4.py" "%USER_PATH%\src\"
copy "C:\code\Document Manager\src\statistics_calendar_widget.py" "%USER_PATH%\src\"
copy "C:\code\Document Manager\src\word_template_processor.py" "%USER_PATH%\src\"
copy "C:\code\Document Manager\src\verify_template.py" "%USER_PATH%\src\"
copy "C:\code\Document Manager\src\enhanced_database_manager.py" "%USER_PATH%\src\"

REM Copy new files
copy "C:\code\Document Manager\src\csv_batch_processor.py" "%USER_PATH%\src\"
copy "C:\code\Document Manager\src\shipping_schedule_view.py" "%USER_PATH%\src\"

REM Copy optional tools
copy "C:\code\Document Manager\FIX_WORD_COM_CACHE.bat" "%USER_PATH%\"
copy "C:\code\Document Manager\FOLDER_LABEL_PRINTING_FIX.md" "%USER_PATH%\"

echo Deployment complete!
```

---

## Verification Checklist

After deployment, verify these features work:

- [ ] SYNC DATA finds and matches CSV files
- [ ] Calendar shows CSV counts (larger and centered)
- [ ] "📦 Process CSVs" button appears in sidebar
- [ ] Clicking "Process CSVs" opens CSV processing view
- [ ] CSV processing view shows CSVs grouped by validation status
- [ ] "Select All" button works in CSV view
- [ ] Double-click CSV opens the file
- [ ] "📅 View Shipping Schedule" button appears in sidebar
- [ ] Shipping schedule shows orders grouped by date
- [ ] Folder label printing works without AttributeError
- [ ] PDF expanded view does NOT show CSV status column
- [ ] CSV processing view does NOT show PDF status column

---

## Rollback Instructions

If issues occur, restore from backup:

1. Close the Document Manager application
2. Delete the updated files
3. Copy files from backup folder
4. Restart the application

---

## Database Compatibility

✅ **No database changes required** - The update is backward compatible with existing databases.

---

## Python Dependencies

No new dependencies required. All features use existing packages:
- tkinter (built-in)
- win32com (already installed)
- sqlite3 (built-in)
- pathlib (built-in)

---

## Support Contact

If users encounter issues after deployment:
1. Check that ALL files were copied correctly
2. Run FIX_WORD_COM_CACHE.bat if folder labels won't print
3. Delete and recreate the database if CSV matching fails
4. Contact support with error logs

---

## Version Info

- **Version**: 2.4.1
- **Release Date**: 2025-11-14
- **Compatibility**: Windows 10/11, Python 3.8+
- **Database**: Backward compatible with v2.4.0
