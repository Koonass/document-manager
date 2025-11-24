# Microsoft Teams Deployment Guide - Document Manager

## Why Teams is Perfect for You

Since you're already using Teams for shared spreadsheets, you have:
- ✅ Users already have the channel synced
- ✅ Permissions already set up
- ✅ OneDrive sync already working
- ✅ No additional sharing needed
- ✅ Infrastructure proven to work

**This will be the easiest deployment method!**

---

## Quick Deployment (10 Minutes Total)

### Step 1: Find Your Teams Folder (2 minutes)

**Method 1: Through Teams**
1. Open Microsoft Teams
2. Go to your team channel (the one with the shared spreadsheet)
3. Click "Files" tab
4. Look at the folder location in File Explorer
5. That's your deployment location!

**Method 2: Through File Explorer**
1. Open File Explorer
2. Navigate to: `OneDrive - [YourCompany]`
3. Look for folders named: `[TeamName] - [ChannelName]`
4. Example: `Engineering - General` or `Operations - Files`
5. That's your Teams folder!

**Example paths:**
```
C:\Users\YourName\OneDrive - CompanyName\Engineering - General
C:\Users\YourName\OneDrive - CompanyName\Operations - General
C:\Users\YourName\OneDrive - CompanyName\IT Department - Files
```

### Step 2: Deploy Application (5 minutes)

**Run the deployment script:**
```batch
cd C:\code\Document Manager
DEPLOY_TO_ONEDRIVE.bat
```

**When prompted for path, enter:**
```
C:\Users\YourName\OneDrive - CompanyName\[TeamName - Channel]\Apps\DocumentManager
```

**Example:**
```
C:\Users\YourName\OneDrive - CompanyName\Engineering - General\Apps\DocumentManager
```

**The script will:**
- Copy all application files
- Create DATA folder structure
- Configure settings with relative paths
- Set everything up automatically

### Step 3: Notify Team Members (1 minute)

Send this message in your Teams channel:

```
Hi Team,

Document Manager is now available in our Files!

📁 Location: Files tab → Apps → DocumentManager

Setup (3 minutes, one-time):
1. Make sure Files tab is synced (should already be if you access our spreadsheet)
2. Navigate to: OneDrive - CompanyName\[TeamName - Channel]\Apps\DocumentManager
3. Double-click: SETUP_PYTHON_DEPS.bat (installs Python packages)
4. Right-click START_APP.bat → Send to → Desktop (create shortcut)
5. Rename shortcut to "Document Manager"

Daily use: Double-click "Document Manager" shortcut on your desktop

Everyone will share the same database automatically!
```

### Step 4: Test with First User (2 minutes)

1. Have one team member follow the setup steps
2. They create desktop shortcut
3. Launch application
4. Import some test data
5. Close application

### Step 5: Test with Second User (2 minutes)

1. Have another team member set up (after OneDrive syncs)
2. They create desktop shortcut
3. Launch application
4. **Verify they see the test data from first user** ✅
5. Everyone is now sharing the database!

---

## Folder Structure in Teams

After deployment, your Teams Files will look like:

```
Teams → [Your Channel] → Files
├── (your existing files and folders)
├── (your shared spreadsheet)
└── Apps/
    └── DocumentManager/
        ├── START_APP.bat           ← Users shortcut to this
        ├── SETUP_PYTHON_DEPS.bat
        ├── run_v2_3.py
        ├── settings_v2_3.json
        ├── requirements.txt
        ├── src/
        ├── LABEL TEMPLATE/
        ├── DATA/
        │   ├── document_manager_v2.1.db    ← Shared database
        │   ├── BisTrack Exports/
        │   ├── PDFs/
        │   └── Archive/
        └── Documentation/
```

---

## Each User Setup (3 Minutes)

### Prerequisites
✅ Member of the Teams channel (already done!)
✅ Files tab synced (already done if using shared spreadsheet!)
✅ Python installed (check: `python --version`)

### One-Time Setup Steps

**1. Verify Sync (30 seconds)**
Open File Explorer and navigate to:
```
OneDrive - CompanyName\[TeamName - Channel]\Apps\DocumentManager
```

If you see the files, you're ready! OneDrive is already syncing.

**2. Install Python Dependencies (2 minutes)**
- Navigate to the DocumentManager folder
- Double-click `SETUP_PYTHON_DEPS.bat`
- Wait for installation to complete
- Window will show "SUCCESS!" when done

**3. Create Desktop Shortcut (30 seconds)**
- Right-click `START_APP.bat`
- Select "Send to" → "Desktop (create shortcut)"
- On desktop, rename shortcut to "Document Manager"

**4. Launch and Test (30 seconds)**
- Double-click "Document Manager" shortcut
- Application should start
- You should see data from other users (if any imported)

**Done!** You're now using the shared database.

---

## Advantages of Teams Deployment

### Compared to Other Options

| Feature | Teams | Regular OneDrive | Network Server |
|---------|-------|------------------|----------------|
| Permissions already set | ✅ Yes | ❌ Must share manually | ❌ IT approval needed |
| Already synced | ✅ Yes | ❌ Must sync folder | ❌ Must connect |
| Users have access | ✅ Automatic | ❌ Must invite | ❌ IT setup |
| Works like spreadsheet | ✅ Same method | 🟡 Similar | ❌ Different |
| Easy updates | ✅ Update once | ✅ Update once | ❌ Deploy to server |
| No IT approval | ✅ None needed | ✅ None needed | ❌ Required |
| No .exe files | ✅ None | ✅ None | ✅ None |

### Your Specific Benefits

Since you **already use Teams for shared spreadsheet:**
- ✅ Users know how to access Teams files
- ✅ OneDrive sync already working and tested
- ✅ Channel permissions already correct
- ✅ No new infrastructure needed
- ✅ Same access pattern as spreadsheet
- ✅ Users comfortable with the workflow

---

## Syncing Behavior

**Just like your shared spreadsheet:**

### When User A Makes Changes:
1. User A saves in Document Manager
2. Database file updates
3. OneDrive detects change
4. File syncs to cloud (usually within seconds)
5. Cloud syncs to all other users' computers
6. User B sees changes when they open the app

### Concurrent Usage:
- **2-3 users at once:** Works perfectly ✅
- **Up to 20 total users:** Fully supported ✅
- SQLite with WAL mode handles this well
- OneDrive file locking prevents conflicts

**Same behavior as your Teams spreadsheet!**

---

## Updating the Application

**When you need to update (add features, fix bugs):**

### Option 1: Update in Place
1. Close your Document Manager
2. Navigate to Teams Files → Apps → DocumentManager
3. Replace the files you updated
4. OneDrive syncs to everyone automatically
5. Notify team in Teams channel: "Document Manager updated, please restart"

### Option 2: Use Deployment Script Again
```batch
cd C:\code\Document Manager
DEPLOY_TO_ONEDRIVE.bat
```
- Choose same Teams path
- Confirm overwrite
- Files update automatically
- Users restart application

**Just like updating your shared spreadsheet!**

---

## Troubleshooting

### "I don't see the DocumentManager folder"

**Cause:** Files tab not synced or wrong channel

**Solution:**
1. Open Teams → Go to your channel
2. Click "Files" tab
3. Click "Sync" button at top
4. Wait for OneDrive to sync
5. Check File Explorer again

---

### "Application won't start"

**Cause:** Python dependencies not installed

**Solution:**
1. Navigate to DocumentManager folder
2. Double-click `SETUP_PYTHON_DEPS.bat` again
3. Check for error messages
4. Verify Python installed: `python --version`

---

### "I don't see other users' data"

**Cause:** OneDrive hasn't synced yet

**Solution:**
1. Check OneDrive icon in system tray
2. Should show green checkmark (synced)
3. If syncing, wait 1-2 minutes
4. Right-click OneDrive icon → View sync status
5. Restart Document Manager

**Same as waiting for spreadsheet updates!**

---

### "Database locked error"

**Cause:** Multiple users saving at exact same moment

**Solution:**
1. Try again in 10 seconds (usually resolves itself)
2. If persists: Close app on all computers
3. Wait 30 seconds for sync
4. Restart application

**Rare with 2-3 concurrent users**

---

## Security and Compliance

### Using Teams Shared Files

**Permissions:**
- ✅ Controlled by Teams channel membership
- ✅ Same security as your shared spreadsheet
- ✅ Company IT manages Teams access
- ✅ Can remove user access through Teams

**Data Storage:**
- ✅ Stored in Microsoft 365 cloud
- ✅ Encrypted in transit and at rest
- ✅ Backed up by Microsoft
- ✅ Company data retention policies apply
- ✅ Audit logs available through Microsoft 365

**Compliance:**
- ✅ No .exe files (won't trigger Sentinel One)
- ✅ No server installation needed
- ✅ No IT approval required
- ✅ Uses existing approved infrastructure
- ✅ Same compliance as Teams spreadsheet

---

## Monitoring and Maintenance

### Check OneDrive Sync Status

**System Tray Icon:**
- 🟢 Green checkmark: All synced
- 🔄 Blue arrows: Syncing
- ⚠️ Yellow warning: Sync issue
- ❌ Red X: Not syncing

**View Sync Progress:**
1. Right-click OneDrive icon
2. Click "View sync status"
3. See what's syncing

### Database File Monitoring

**Normal files you'll see:**
```
DATA/
├── document_manager_v2.1.db         ← Main database
├── document_manager_v2.1.db-wal     ← Write-ahead log (WAL)
├── document_manager_v2.1.db-shm     ← Shared memory
└── (these 3 files sync together)
```

**Watch for conflict files:**
```
document_manager_v2.1 (UserName's conflicted copy).db
```

If you see these:
1. Everyone close the application
2. Delete conflict copies
3. Keep the newest main database
4. Restart application

---

## Best Practices

### For All Users

**1. Close When Not Using**
- Don't leave app running idle
- Close it when done for the day
- Reduces chance of sync conflicts
- **Same as you do with spreadsheet!**

**2. Save Regularly**
- Application auto-saves to database
- OneDrive syncs automatically
- No manual save needed
- **Just like spreadsheet auto-save!**

**3. Check Sync Before Closing**
- Glance at OneDrive icon before closing
- Make sure it's synced (green checkmark)
- Ensures your changes uploaded

### For You (Administrator)

**1. Monitor Teams Channel**
- Check for user questions
- Watch for sync issues
- Respond to problems quickly

**2. Keep Backup**
- Periodically copy DATA folder elsewhere
- Store backup on different location
- In case of corruption (rare)

**3. Update Carefully**
- Test updates locally first
- Update when users not active
- Notify in Teams before/after
- Monitor for issues after update

---

## Comparison to Your Spreadsheet

### How It's Similar

| Spreadsheet Behavior | Document Manager Behavior |
|---------------------|---------------------------|
| Open from Teams Files | Open from desktop shortcut (points to Teams Files) |
| Multiple users edit | Multiple users can use (2-3 at once) |
| Auto-saves changes | Auto-saves to database |
| OneDrive syncs | OneDrive syncs database |
| Others see changes | Others see changes when they open app |
| Conflict if simultaneous | Conflict handled by SQLite (rare) |
| Access via Teams permissions | Access via Teams permissions |

### How It's Different

| Spreadsheet | Document Manager |
|-------------|------------------|
| Opens in Excel/web | Opens as desktop application |
| One file (.xlsx) | Multiple files (Python app + database) |
| Edit in real-time | Edit independently, syncs via database |
| Cloud processing | Local processing (faster) |
| Limited by Excel | Full custom application |

**But same ease of use and access!**

---

## Quick Reference

### File Locations

**On Your Computer:**
```
C:\Users\[YourName]\OneDrive - CompanyName\[Team - Channel]\Apps\DocumentManager\
```

**Desktop Shortcut:**
```
C:\Users\[YourName]\Desktop\Document Manager.lnk
```

**Shared Database:**
```
Apps\DocumentManager\DATA\document_manager_v2.1.db
```

### Important Files

| File | Purpose |
|------|---------|
| `START_APP.bat` | Launch application |
| `SETUP_PYTHON_DEPS.bat` | Install Python packages (one-time) |
| `settings_v2_3.json` | Configuration |
| `DATA\document_manager_v2.1.db` | Shared database (syncs) |

### Commands

**Deploy application:**
```batch
cd C:\code\Document Manager
DEPLOY_TO_ONEDRIVE.bat
```

**User setup:**
```batch
# In DocumentManager folder:
SETUP_PYTHON_DEPS.bat
# Then create desktop shortcut to START_APP.bat
```

**Check Python:**
```batch
python --version
```

---

## Summary

### What Makes This Perfect for You

✅ **Already using Teams** - No new infrastructure
✅ **Already synced** - Files tab already working
✅ **Permissions set** - Channel members already have access
✅ **Proven reliable** - Works with your spreadsheet
✅ **Simple deployment** - One script, one notification
✅ **No IT needed** - Uses existing approved tools
✅ **No .exe files** - Won't trigger Sentinel One
✅ **2-3 concurrent users** - Perfect for your team size
✅ **Up to 20 total users** - Scales as needed

### Next Steps

1. **Now:** Run `DEPLOY_TO_ONEDRIVE.bat`
2. **Choose:** Your Teams channel path
3. **Notify:** Team members in Teams
4. **Test:** With 2 users first
5. **Roll out:** To rest of team

**Just like deploying your shared spreadsheet, but even better!**

---

## Support

**For more information:**
- See: `ONEDRIVE_QUICK_START.md`
- See: `ONEDRIVE_DEPLOYMENT_GUIDE.md`
- See: `ONEDRIVE_LOCATION_GUIDE.md`

**Questions?**
Ask in your Teams channel - your team is already there!
