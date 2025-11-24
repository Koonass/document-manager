# Folder Label Printing Guide

## Overview

The Document Manager supports automatic folder label printing using Microsoft Word templates. When enabled, the system will fill a Word template with order information and print it to your selected printer.

## How It Works

### Data Mapping

The system maps order data to Word template bookmarks as follows:

| Template Bookmark | Order Field | Description |
|------------------|-------------|-------------|
| `builder` | Customer | The customer/builder name |
| `Lot / subdivision` | JobReference | The lot or subdivision reference |
| `floors` | DeliveryArea | The delivery area/floors |
| `designer` | Designer | The designer name |
| `OrderNumber` | OrderNumber | Order number (optional) |
| `DatePrinted` | Auto-generated | Current date/time (optional) |

### Process Flow

1. **Enable Folder Printer**: Check the "Folder Printer" option in the Print Settings
2. **Select Printer**: Choose which printer to use for folder labels
3. **Create Batch**: Select orders and click "Print All"
4. **Automated Process**:
   - Template is opened in Word (hidden)
   - Bookmarks are filled with order data
   - Document is sent to selected printer
   - Word closes automatically

## Setting Up Your Template

### Step 1: Verify Template Location

The default template location is:
```
C:\code\Document Manager\DESIGN FILES\Template.docx
```

You can change this in Settings > File Locations.

### Step 2: Add Bookmarks to Your Template

1. **Open Template in Microsoft Word**
   - Open `Template.docx` in Microsoft Word

2. **Add Bookmarks for Each Field**

   For each field you want to populate:

   a. **Select the text** where the data should appear (e.g., select the placeholder "BUILDER NAME HERE")

   b. **Insert Bookmark**:
      - Go to **Insert** tab
      - Click **Bookmark**
      - Type the bookmark name (see table below)
      - Click **Add**

   c. **Required Bookmarks**:
      - `builder` - for Customer name
      - `Lot / subdivision` - for Job Reference/Lot (note: includes space and slash)
      - `floors` - for Delivery Area
      - `designer` - for Designer name

   d. **Optional Bookmarks**:
      - `OrderNumber` - for Order Number
      - `DatePrinted` - for Print Timestamp

3. **Save Template**
   - Save the template file
   - Keep it as a `.docx` file

### Step 3: Verify Template Setup

Run the verification script to check if all bookmarks are correctly set up:

```bash
cd "C:\code\Document Manager"
python src/verify_template.py
```

This will show you:
- ✓ Which bookmarks are present
- ❌ Which bookmarks are missing
- ⚪ Which optional bookmarks are available

### Example Output (Correct Setup):

```
======================================================================
Word Template Verification
======================================================================
Template: C:\code\Document Manager\DESIGN FILES\Template.docx

Found 6 bookmark(s) in template

Existing bookmarks in template:
  • builder
  • Lot / subdivision
  • floors
  • designer
  • OrderNumber
  • DatePrinted

Required bookmarks for folder labels:
  ✓ builder              (Customer name)
  ✓ Lot / subdivision    (Job reference/lot)
  ✓ floors               (Delivery area)
  ✓ designer             (Designer name)

Optional bookmarks:
  ✓ OrderNumber          (Order number)
  ✓ DatePrinted          (Print timestamp)

======================================================================
✅ TEMPLATE SETUP COMPLETE
======================================================================

All required bookmarks are present!
The template is ready to use for folder label printing.
```

## Using Folder Printing

### In the Enhanced Expanded View

1. **Open a Day's Orders**
   - Click on any day in the calendar

2. **Configure Print Settings**
   - Scroll to the "Print Settings" section
   - Check **"Folder Printer"** checkbox
   - Select your printer from the dropdown
   - Configure other printers as needed (11x17, 24x36)

3. **Select Orders to Print**
   - Check the boxes next to orders you want to print
   - Orders can be from any category (Green, Red, or Gray)

4. **Print**
   - Click **"🖨️ Print All"** button
   - Review the batch in the confirmation dialog
   - Click **"Start Printing"**

### What Happens During Printing

The system will:
1. Process each checked order
2. For each enabled printer:
   - **11x17 Printer**: Print the PDF plot
   - **24x36 Printer**: Print the PDF plot
   - **Folder Printer**: Fill template and print folder label
3. Mark orders as processed
4. Show completion summary

### Print Settings Are Saved

Your printer selections and settings are automatically saved for next time, so you only need to configure them once.

## Troubleshooting

### Folder Labels Not Printing

**Check the log file** for detailed error messages:
- Location: `document_manager_v2.3.log`
- Look for lines starting with "Folder label" or "bookmark"

**Common Issues:**

1. **Template not found**
   ```
   ✗ Folder label template file not found
   ```
   **Solution**: Check Settings > File Locations and verify the template path

2. **Bookmarks missing**
   ```
   ⚠ Bookmark 'builder' not found in template
   ```
   **Solution**: Run `verify_template.py` and add missing bookmarks

3. **Printer not available**
   ```
   Failed to set active printer
   ```
   **Solution**: Verify the printer name and that it's installed on your system

4. **Word/COM errors**
   ```
   Failed to start Word application
   ```
   **Solution**:
   - Ensure Microsoft Word is installed
   - Try installing pywin32: `pip install pywin32`
   - Close any open Word instances

### Detailed Logging

When folder printing is enabled, you'll see detailed logs like:

```
Starting folder label print for order 4079038
  Template: C:\code\Document Manager\DESIGN FILES\Template.docx
  Printer: HP LaserJet Pro M404n
  Customer: DR Horton Atlanta West
  JobReference: 201390 -2nd EWP -SALISBURY
  DeliveryArea: Flowery Branch GA
  Designer: Ashley Bowen
  Template opened successfully
    ✓ Filled bookmark 'builder' = 'DR Horton Atlanta West'
    ✓ Filled bookmark 'Lot / subdivision' = '201390 -2nd EWP -SALISBURY'
    ✓ Filled bookmark 'floors' = 'Flowery Branch GA'
    ✓ Filled bookmark 'designer' = 'Ashley Bowen'
  Bookmarks filled successfully
  Setting active printer to: HP LaserJet Pro M404n
  Sending document to printer...
✓ Successfully printed folder label for order 4079038
```

## Technical Details

### Implementation Files

- **`src/word_template_processor.py`**: Core template processing logic
- **`src/enhanced_expanded_view.py`**: Integration with batch printing
- **`src/verify_template.py`**: Template verification utility

### Requirements

- Microsoft Word installed on the system
- `pywin32` Python package
- Write permissions to template directory

### Printer Selection

The folder printer dropdown shows all installed printers on your system. You can select any printer, but typically you'll use a standard letter-size printer for folder labels.

## Tips & Best Practices

1. **Test with One Order First**
   - Select a single order
   - Enable only the folder printer
   - Verify the output before batch printing

2. **Template Design**
   - Use a simple, readable font
   - Leave enough space for long customer/job names
   - Consider using a table layout for organization

3. **Bookmark Naming**
   - Bookmark names are **case-sensitive**
   - Include spaces exactly as shown: `Lot / subdivision`
   - Don't change bookmark names after setup

4. **Performance**
   - Word opens/closes for each folder label
   - Expect ~2-5 seconds per label
   - Don't interrupt the process while printing

## Support

If you encounter issues:

1. Run the verification script: `python src/verify_template.py`
2. Check the log file: `document_manager_v2.3.log`
3. Ensure Microsoft Word is properly installed
4. Verify printer is online and accessible

---

**Version**: 2.3.0
**Last Updated**: October 2025
