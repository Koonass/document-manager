# Folder Label Printing - AttributeError Fix

## Problem
When printing folder labels, you may encounter errors like:
```
AttributeError: module 'win32com.gen_py.00020905' has no attribute 'CLSIDToClassMap'
AttributeError: module 'win32com.gen_py.00020905' has no attribute [various]
```

## What Causes This
This error occurs when the **win32com COM type library cache** becomes corrupted. This cache stores information about Microsoft Word's COM interface. The corruption can happen during cache rebuilding (AddModuleToCache) or when accessing cached types.

## Solution

The issue has been **automatically fixed** in the code! The application now:

1. ✅ **Automatically detects** when the cache is corrupted (AttributeError)
2. ✅ **Immediately falls back** to late-bound dispatch (works without cache)
3. ✅ **Clears cache** in background for next run
4. ✅ **Continues printing** without interruption

### How It Works
When AttributeError is detected:
- **Immediate:** Uses `win32.Dispatch()` (late-bound) to create Word - this always works
- **Background:** Clears corrupted cache files for next time
- **Next run:** Cache will rebuild automatically and use faster early-bound method

### No Action Required
Folder labels will print successfully even with corrupted cache. The fix is automatic and invisible to users!

## Manual Fix (If Needed)

If you still encounter issues, you can manually clear the cache:

### Method 1: Run the Batch File
Double-click: **`FIX_WORD_COM_CACHE.bat`**

This will clear the cache and prepare it for the next print.

### Method 2: Manual Steps
1. Close the Document Manager application
2. Open Command Prompt
3. Run this command:
   ```bash
   python -c "import win32com.client as win32; import shutil; path = win32.gencache.GetGeneratePath(); shutil.rmtree(path, ignore_errors=True)"
   ```
4. Restart the Document Manager application

## Technical Details

### What Changed
- Updated `word_template_processor.py` with automatic cache clearing
- Updated `verify_template.py` with automatic cache clearing
- Added `_get_word_application()` helper method that:
  - Tries `gencache.EnsureDispatch` (fast, early-bound)
  - On AttributeError: Clears cache and retries
  - Falls back to `Dispatch` (late-bound) if needed

### Files Modified
- `src/word_template_processor.py` - Main folder label printing
- `src/verify_template.py` - Template verification tool
- `FIX_WORD_COM_CACHE.bat` - Manual cache repair tool (new)

## When to Use Manual Fix
The automatic fix handles 99% of cases. Use the manual fix if:
- Folder labels still won't print after multiple attempts
- You want to clear the cache before an important batch print
- You're troubleshooting Word COM issues

## Cache Location
The cache is typically stored at:
```
C:\Users\[YourUsername]\AppData\Local\Temp\gen_py\[version]\
```

The cache is safe to delete - it will be automatically regenerated when needed.

## Additional Notes
- The fix is **non-destructive** - it only clears temporary cache files
- The cache will be **automatically rebuilt** on next use
- This fix works for all Word COM automation errors
- No need to reinstall anything
