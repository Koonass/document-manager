# Document Manager V2.4 - Release Notes

## What's New in V2.4

### BisTrack CSV Import Management

Document Manager V2.4 adds complete CSV file management for BisTrack material imports, including:

- **Automatic Order Matching**: Scans CSV files and extracts order numbers from filenames or file content
- **SKU Validation**: Validates material SKUs against a products master file
- **Data Quality Checks**: Verifies quantities, required fields, and data formats
- **Auto-Fix Suggestions**: Provides automatic corrections for common errors
- **Upload to BisTrack**: Copies validated CSVs to BisTrack import folder
- **Database Tracking**: Tracks CSV validation status and history

## How to Use

### 1. Run V2.4

Double-click **START_V2_4.bat** to launch the application.

### 2. Configure CSV Settings (First Time Setup)

1. Click **⚙️ Settings** in the main window
2. Scroll down to the new CSV settings:
   - **Products Master File**: Browse to your SKU master CSV file
     - Format: `SKU,Description,Active`
     - Example: `J1400-4500s-BC,"BCI 4500s 1.75"" X 14""",1`
   - **BisTrack Import Folder**: Browse to your BisTrack import folder location
3. Click **Save**

### 3. Access BisTrack CSV Manager

Click the new **📦 BisTrack CSVs** button in the Quick Views sidebar.

### 4. CSV Workflow

1. **Scan**: CSV files are automatically scanned from your PDF folder
2. **Validate**: Click "✓ Validate" or "✓ Validate All" to check files
3. **Review Results**:
   - ✅ **Valid**: Ready to upload
   - ⚠️ **Warnings**: Can upload but has warnings
   - ❌ **Errors**: Must fix before uploading
4. **Auto-Fix**: Click "🔧 Auto-Fix" to apply suggested corrections
5. **Upload**: Click "📤 Upload to BisTrack" to copy to import folder

## CSV File Format

CSV files are expected in the iStruct export format:

```csv
Contract Lumber,,,,
Date Issued:,18/02/2025,,,
Job Description:,4116780,,,
Job Path:,HH-109-HF-2,,,
LABEL,LENGTH,SKU,MATERIAL,QTY REQ'D
R2,35-0-0,J1400-4500s-BC,"BCI 4500s 1.75"" X 14""",1
...
<EOF>,,,,
```

## Validation Checks

The validator checks for:

### Errors (Must Fix)
- Empty SKU or Quantity fields
- Non-numeric quantities
- Missing order number

### Warnings (Recommended to Fix)
- SKU not found in products file
- Zero or negative quantities
- Unusually high quantities (>9999)

### Info (Informational)
- Very long material descriptions
- Invalid length formats

## Products Master File

Create a CSV file with your valid SKUs:

```csv
SKU,Description,Active
J1400-4500s-BC,"BCI 4500s 1.75"" X 14""",1
J1400-6000s-BC,"BCI 6000s 2.313"" X 14""",1
L0950-17517E-BC,"Versa-Lam LVL 1.8E 2650 SP 1.75"" X 9.5""",1
```

- **Active = 1**: SKU is valid
- **Active = 0**: SKU is inactive (won't be validated)

## Features Preserved from V2.3

All existing features from V2.3 are intact:

- Enhanced calendar view with daily statistics
- Category-based order management (Ready/Missing/Processed)
- Batch PDF printing with automatic archiving
- Real-time PDF attachment and status updates
- Unmatched PDFs viewer
- Printer configuration
- Archive management

## Files Created

- **run_v2_4.py**: Application launcher
- **src/main_v2_4.py**: Main application with CSV features
- **src/csv_processor.py**: CSV scanning and order extraction
- **src/csv_validator.py**: Data validation and SKU checking
- **src/csv_cleanup_dialog.py**: CSV management UI
- **src/enhanced_database_manager.py**: Database with CSV tracking
- **settings_v2_4.json**: Settings file (auto-created)
- **START_V2_4.bat**: Quick launch script

## Testing

A sample CSV file is available in `sample csv/HH-109-HF-2.csv` along with a products master file for testing.

You can also run **TEST_CSV_FEATURES.bat** to test just the CSV dialog without the full application.

## Troubleshooting

### "CSV Folder Not Set" Error
- Configure the PDF folder path in Settings (CSVs are stored with PDFs)

### SKU Validation Skipped
- Configure the Products Master File path in Settings

### No CSVs Found
- Ensure CSV files are in the same folder as your PDFs
- Check that files have `.csv` extension

## Support

For issues or questions, refer to the main README files or previous documentation.

---

**Version**: 2.4.0
**Release Date**: 2025
**Based on**: V2.3 (stable)
