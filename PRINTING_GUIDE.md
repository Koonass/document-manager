# Batch Printing with Presets - User Guide

## Overview
The new preset-based printing system allows you to save common printer configurations and quickly batch print orders.

## Key Features

✅ **No color mode toggles** - Use your print server's pre-programmed scripts
✅ **User controls printer selection** - Send any PDF to any printer regardless of PDF size
✅ **Folder labels automatically skip processed orders** - No manual filtering needed
✅ **Timeout protection** - Won't hang on slow print servers (60 second timeout per job)
✅ **Progress tracking** - See which orders succeed/fail in real-time

## How to Use

### First Time Setup

1. **Run the application** (`run_v2_3.py`)
2. **Configure Printer Settings** (one-time setup):
   - Go to **Settings > Printer Settings**
   - Configure your 11×17, 24×36, and Folder Label printers
   - These are your base printer assignments

3. **Create Print Presets**:
   - Open a day with orders
   - Click **⚙️ Manage Presets** in the sidebar
   - You'll see 3 default presets:
     - **Standard Plot** (default)
     - **11x17 Only**
     - **24x36 Only**

4. **Edit a Preset**:
   - Click on a preset name to edit it
   - Configure:
     - **11×17 Printer**: Enable/disable, select print server script, set copies
     - **24×36 Printer**: Enable/disable, select print server script, set copies
     - **Folder Labels**: Enable/disable, select printer script
   - Click **💾 Save Changes**
   - Click **⭐ Set as Default** for your most-used preset

### Daily Workflow

1. **Open a day** from the calendar
2. **Check orders** you want to print (checkboxes in each category)
3. **Click "📋 Create Batch"**
4. **Select your preset**:
   - Choose from your saved presets (default is pre-selected)
   - Click **Review & Print**
5. **Monitor progress**:
   - Progress dialog shows which orders are printing
   - Can cancel remaining jobs if needed
6. **Done!** - Successful orders automatically marked as processed

## Important Notes

### Folder Labels Logic
- **Green category** (has PDF): ✅ Prints folder label if enabled
- **Red category** (no PDF): ✅ Prints folder label if enabled
- **Gray category** (processed): ❌ Skips folder label automatically

### PDF-to-Printer Matching
- **You choose** which printer to use
- Want to print a 24×36 PDF on the 11×17 printer? Enable 11×17 only in your preset
- Want both? Enable both printers in your preset

### Timeout Protection
- Each print job has a 60-second timeout
- If your print server is slow and times out, the job is marked as failed
- Failed jobs won't stop the batch - it continues with remaining orders

## Troubleshooting

**"No printers detected"**
- Check that printers are installed and accessible
- Make sure print server is online
- Try restarting the application

**Preset editor is blank**
- Click on a preset name in the left list
- If still blank, close and reopen the Manage Presets dialog

**Folder labels printing for processed orders**
- This shouldn't happen - folder labels automatically skip gray (processed) category
- If it does, report as a bug

**Print jobs timing out**
- Your print server may be slow
- Jobs marked as failed can be retried by creating a new batch with just those orders
- Consider increasing timeout if needed (currently 60 seconds per job)

## Tips

- Create presets for your common scenarios:
  - "Standard": Both printers + folder labels
  - "Reprints": Just PDFs, no folder labels
  - "Waterproof": 11×17 with waterproof script + folder labels

- Set your most-used preset as default to save clicks

- Can create as many presets as you need - just click **➕ New Preset**

- Preset changes are saved immediately - no need to restart the app
