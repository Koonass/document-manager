# Version 2.4 - Pre-Deployment Testing Checklist

## ⚠️ DO NOT DEPLOY TO PRODUCTION YET

**Current Production Version:** v2.3 (Stable)
**Testing Version:** v2.4 (Development/Testing)
**Test Environment:** C:\code\Document Manager

---

## Testing Status

### ✅ Completed Features
- [x] CSV file detection and scanning
- [x] CSV order number extraction
- [x] CSV database storage
- [x] CSV status display in calendar (larger, centered)
- [x] CSV column in order cards
- [x] Folder label printing AttributeError fix
- [x] "Process CSVs" sidebar button
- [x] CSV Processing View (separate from PDF)
- [x] "Shipping Schedule" sidebar button
- [x] Shipping Schedule View (date-grouped)
- [x] Select All functionality in CSV view
- [x] Double-click to open CSV files

### 🔄 Features to Test

#### CSV Detection & Matching
- [ ] CSV files are found in tests folder
- [ ] Order numbers extracted from CSV filenames
- [ ] Order numbers extracted from CSV content (Job Description field)
- [ ] CSVs matched to correct orders in database
- [ ] CSV counts display in calendar day boxes
- [ ] CSV status shows correctly in order cards

#### CSV Processing View
- [ ] "📦 Process CSVs" button opens view
- [ ] CSVs grouped correctly (Ready/Errors/Needs Validation)
- [ ] Select All button works
- [ ] Individual checkbox selection works
- [ ] Double-click opens CSV in Excel/default app
- [ ] CSV File column shows filenames
- [ ] CSV Status column shows validation status

#### CSV Validation
- [ ] "🔍 Validate Selected" button works
- [ ] Validation checks SKUs against products master
- [ ] Validation results displayed correctly
- [ ] Database updated with validation status
- [ ] View refreshes after validation

#### CSV Upload to BisTrack
- [ ] "📤 Upload to BisTrack" button works
- [ ] Only validated CSVs can be uploaded
- [ ] Upload confirmation dialog appears
- [ ] Files copied to BisTrack import folder
- [ ] Database updated with upload status
- [ ] View refreshes after upload

#### Shipping Schedule View
- [ ] "📅 View Shipping Schedule" button works
- [ ] Orders grouped by date required
- [ ] All columns display correctly (Order, Customer, Job Ref, Designer, PDF Status, CSV Status)
- [ ] CSV status column shows correctly
- [ ] Double-click opens PDFs
- [ ] Read-only (no edit controls)

#### Folder Label Printing
- [ ] Folder labels print without AttributeError
- [ ] COM cache auto-clears if corrupted
- [ ] FIX_WORD_COM_CACHE.bat works manually
- [ ] Retries work on "Call was rejected by callee" errors

#### Database Compatibility
- [ ] CSV data persists after app restart
- [ ] No conflicts between EnhancedDatabaseV2 and EnhancedDatabaseManager
- [ ] processing_log inserts work correctly
- [ ] CSV queries return correct data

#### UI/UX Polish
- [ ] CSV status removed from PDF-only views
- [ ] PDF status removed from CSV-only views
- [ ] CSV counts in calendar are larger and centered
- [ ] All buttons have correct colors and icons
- [ ] Views are read-only where intended

---

## Known Issues to Fix Before Deployment

### Critical (Must Fix)
- [ ] None currently identified

### Important (Should Fix)
- [ ] Test CSV validation with real BisTrack CSV files
- [ ] Verify BisTrack import folder path configuration
- [ ] Test with multiple CSV files for same order
- [ ] Test CSV processing with 50+ orders

### Nice to Have (Can Fix Later)
- [ ] Add progress indicator for batch CSV validation
- [ ] Add CSV processing history view
- [ ] Add ability to re-validate CSVs

---

## Test Scenarios

### Scenario 1: New User First Time Setup
1. Fresh database (no existing data)
2. Run SYNC with HTML file containing orders
3. Place CSV files in tests folder
4. Run SYNC again
5. Verify CSVs matched to orders
6. Open Process CSVs view
7. Validate CSVs
8. Upload to BisTrack

**Expected Result:** Everything works smoothly, no errors

### Scenario 2: Existing v2.3 User Upgrade
1. Use existing v2.3 database with orders
2. Update to v2.4 code
3. Run SYNC
4. CSV detection should work with existing orders
5. No data loss

**Expected Result:** Backward compatible, CSVs detected and matched

### Scenario 3: CSV Filename vs Content Order Numbers
1. CSV filename: 4098014.csv
2. CSV content Job Description: 4098014
3. Both should match to same order

**Expected Result:** Order number extracted correctly from either source

### Scenario 4: Missing CSV
1. Order exists in database
2. No CSV file exists
3. Calendar should show "0" for CSV count
4. Order card should show "❌ No CSV"

**Expected Result:** Handles missing CSVs gracefully

### Scenario 5: Folder Label Printing After Cache Clear
1. Manually delete COM cache
2. Try to print folder label
3. Should auto-clear cache and succeed

**Expected Result:** Auto-recovers from cache corruption

---

## Performance Testing

- [ ] Test with 100+ orders in database
- [ ] Test CSV validation with 50+ CSVs
- [ ] Test Shipping Schedule with 2-week period (30+ orders)
- [ ] Test sync with large HTML file (500+ orders)
- [ ] Check memory usage during CSV processing
- [ ] Check app startup time

---

## Configuration Testing

### Required Settings
- [ ] `pdf_path` - Where PDFs and CSVs are stored
- [ ] `products_file_path` - Products master CSV for validation
- [ ] `bistrack_import_folder` - Where validated CSVs are uploaded
- [ ] `db_path` - Database location

### Settings to Verify
- [ ] BisTrack import folder path is correct
- [ ] Products master CSV exists and is readable
- [ ] CSV files in correct folder (same as PDFs)

---

## Deployment Readiness Checklist

Before deploying v2.4 to production user:

### Code Quality
- [ ] All features tested and working
- [ ] No critical bugs identified
- [ ] Error handling tested
- [ ] Logging is comprehensive
- [ ] No placeholder/debug code remaining

### Documentation
- [ ] User guide updated for CSV features
- [ ] Admin guide updated for configuration
- [ ] Troubleshooting guide created
- [ ] Release notes written

### Backup Plan
- [ ] v2.3 backup created
- [ ] Database backup instructions ready
- [ ] Rollback procedure documented
- [ ] Support contact information ready

### User Communication
- [ ] Release notes sent to user
- [ ] Training scheduled (if needed)
- [ ] Support availability confirmed
- [ ] Feedback mechanism in place

---

## When to Deploy

Deploy v2.4 to production when:
1. ✅ All "Must Fix" issues resolved
2. ✅ All test scenarios pass
3. ✅ User has been notified and agreed
4. ✅ Backup and rollback plan ready
5. ✅ Support is available for issues

**Target Deployment Date:** TBD (after testing complete)

---

## Testing Notes

Use this section to record findings during testing:

```
Date: ___________
Tester: ___________
Test Environment: ___________

Findings:
-
-
-

Issues Found:
-
-
-

```
