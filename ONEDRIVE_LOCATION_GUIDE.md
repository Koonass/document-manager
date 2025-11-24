# OneDrive Location Guide - Critical Setup Information

## The Personal vs Business OneDrive Problem

**CRITICAL:** Many users have TWO OneDrive folders:

1. **Personal OneDrive**
   ```
   C:\Users\YourName\OneDrive
   ```
   - ❌ **NOT SHARED** between company users
   - ❌ **Private to individual user**
   - ❌ **Don't use this for team deployment!**

2. **Business/Company OneDrive**
   ```
   C:\Users\YourName\OneDrive - CompanyName
   ```
   - ✅ **CAN BE SHARED** with company users
   - ✅ **Managed by company IT**
   - ✅ **Use this for team deployment**

---

## Which OneDrive Should You Use?

### Option 1: Business OneDrive - Shared Folder (RECOMMENDED)

**Best for:** 2-20 users in the same company

**Location:**
```
C:\Users\YourName\OneDrive - CompanyName\Shared\DocumentManager
or
C:\Users\YourName\OneDrive - CompanyName\Apps\DocumentManager
```

**Setup:**
1. Create a folder in your Business OneDrive
2. Right-click folder → Share → Add your team members
3. Give them "Can edit" permissions
4. Deploy application to this shared folder
5. Each user will see it in their Business OneDrive

**Advantages:**
- ✅ Truly shared across all users
- ✅ Managed by company
- ✅ Company-controlled access
- ✅ Backed up by company IT

---

### Option 2: Microsoft Teams Shared Files (BETTER FOR TEAMS)

**Best for:** Existing Teams channel with your users

**Location:**
```
C:\Users\YourName\OneDrive - CompanyName\TeamName - Channel\Apps\DocumentManager
or
C:\Users\YourName\CompanyName\TeamName - Documents\Apps\DocumentManager
```

**Setup:**
1. Go to your Teams channel → Files tab
2. Click "Open in SharePoint" or "Sync"
3. Files sync to your local computer
4. Deploy application to the synced folder
5. All team members with access will sync automatically

**Advantages:**
- ✅ Automatic access control (existing Teams members)
- ✅ No need to individually share
- ✅ Already synced for team members
- ✅ Integrated with Teams

**This is probably your BEST option!**

---

### Option 3: SharePoint Document Library

**Best for:** Formal company deployments

**Location:**
```
C:\Users\YourName\CompanyName\SiteName - Documents\Apps\DocumentManager
```

**Setup:**
1. Create SharePoint site or use existing one
2. Add users to site permissions
3. Sync document library to local computer
4. Deploy application to synced folder
5. Users sync the library to their computers

**Advantages:**
- ✅ Enterprise-grade permissions
- ✅ IT-managed
- ✅ Audit logs
- ✅ Version history

---

## How to Check Which OneDrive You Have

### Method 1: File Explorer

1. Open File Explorer
2. Look in left sidebar under "OneDrive"
3. You'll see:
   ```
   OneDrive - Personal           ← Don't use for team
   OneDrive - CompanyName        ← Use this!
   ```

### Method 2: Command Prompt

```batch
echo Personal: %OneDrive%
echo Business: %OneDriveCommercial%
dir /b "%USERPROFILE%\OneDrive*"
```

### Method 3: OneDrive Settings

1. Right-click OneDrive icon in system tray
2. Click "Settings"
3. Look at "Account" tab
4. Shows both Personal and Business accounts

---

## Deployment Decision Tree

**START HERE:**

1. **Do you have a Teams channel for your users?**
   - YES → Use Option 2 (Teams Shared Files) ← **EASIEST**
   - NO → Go to question 2

2. **Do you have Business OneDrive?**
   - YES → Use Option 1 (Business OneDrive Shared Folder)
   - NO → Go to question 3

3. **Do you have SharePoint access?**
   - YES → Use Option 3 (SharePoint)
   - NO → Contact IT for proper shared storage solution

**NEVER use Personal OneDrive for team deployments!**

---

## Step-by-Step: Teams Shared Files (Recommended)

### For Administrator (You)

**Step 1: Find Your Teams Folder**
```batch
# Open File Explorer
# Navigate to: OneDrive - CompanyName
# Look for folders like: "TeamName - ChannelName"
```

**Step 2: Deploy Application**
```batch
# Run the deployment script
cd C:\code\Document Manager
DEPLOY_TO_ONEDRIVE.bat

# When prompted, choose the Teams folder path
# Example: C:\Users\YourName\OneDrive - CompanyName\Engineering - General\Apps\DocumentManager
```

**Step 3: Notify Team Members**
Send this message to your team:

```
Hi Team,

Document Manager is now available in our Teams folder!

Setup (one-time, 3 minutes):
1. Open Teams → [Channel Name] → Files tab
2. Click "Sync" button (if not already synced)
3. Wait for OneDrive sync to complete
4. Navigate to: OneDrive - CompanyName\[TeamName - Channel]\Apps\DocumentManager
5. Double-click: SETUP_PYTHON_DEPS.bat
6. Create desktop shortcut to: START_APP.bat

Daily use: Double-click "Document Manager" shortcut

Questions? See ONEDRIVE_QUICK_START.md in the folder.
```

---

### For Team Members

**Step 1: Sync Teams Files (if not already synced)**
1. Open Microsoft Teams
2. Go to your team channel
3. Click "Files" tab
4. Click "Sync" button at top
5. Wait for OneDrive to finish syncing

**Step 2: Verify Location**
Open File Explorer and navigate to:
```
OneDrive - CompanyName\[TeamName - Channel]\Apps\DocumentManager
```

If you see the files, you're ready!

**Step 3: Setup (one-time)**
1. Double-click `SETUP_PYTHON_DEPS.bat`
2. Wait for Python packages to install
3. Right-click `START_APP.bat` → Send to → Desktop (create shortcut)
4. Rename shortcut to "Document Manager"

**Step 4: Use Daily**
Double-click "Document Manager" desktop icon

---

## Troubleshooting Path Issues

### "I don't see the application files after deployment"

**Cause:** Files deployed to wrong OneDrive

**Solution:**
1. Check which OneDrive has the files:
   ```batch
   dir /s "%USERPROFILE%\OneDrive*\Apps\DocumentManager"
   ```
2. If in Personal OneDrive, redeploy to Business OneDrive
3. Delete from Personal OneDrive to avoid confusion

---

### "Other users can't see the files"

**Cause:** Deployed to personal or non-shared location

**Solution:**
1. **If using Business OneDrive:**
   - Right-click folder → Share → Add team members
   - Give "Can edit" permissions

2. **If using Teams:**
   - Ensure all users have access to the Teams channel
   - Users must sync the Files tab

3. **If using SharePoint:**
   - Check site permissions
   - Ensure all users added to site

---

### "Users see different OneDrive paths"

**Cause:** Normal! Each user's path is slightly different

**Solution:** This is expected!

**Your path:**
```
C:\Users\JohnDoe\OneDrive - CompanyName\Apps\DocumentManager
```

**Another user's path:**
```
C:\Users\JaneSmith\OneDrive - CompanyName\Apps\DocumentManager
```

**Both point to the SAME cloud location!**

The files are the same, database is shared, everything syncs correctly.

---

## Permissions Required

### Minimum Permissions for Users

**Business OneDrive Shared Folder:**
- "Can edit" permission on the shared folder
- Must accept share invitation
- OneDrive sync enabled

**Teams Shared Files:**
- Member of the Teams channel
- Files tab synced to local computer
- OneDrive sync enabled

**SharePoint:**
- "Contribute" permission on document library
- Library synced to local computer
- OneDrive sync enabled

---

## Security Considerations

### Business OneDrive
- ✅ Company-managed security
- ✅ Can revoke user access
- ✅ Audit logs available
- ✅ Data loss prevention policies apply
- ✅ Encrypted by Microsoft

### Personal OneDrive
- ❌ Personal account (not company-managed)
- ❌ Cannot centrally control access
- ❌ No company audit logs
- ❌ Not suitable for company data
- ❌ **Never use for team deployments!**

---

## Summary: Correct Path Examples

### ✅ CORRECT - Business OneDrive Shared
```
C:\Users\YourName\OneDrive - CompanyName\Shared\Apps\DocumentManager
C:\Users\YourName\OneDrive - CompanyName\Apps\DocumentManager
```

### ✅ CORRECT - Teams Shared Files (Best!)
```
C:\Users\YourName\OneDrive - CompanyName\Engineering - General\Apps\DocumentManager
C:\Users\YourName\CompanyName\TeamSite - Documents\Apps\DocumentManager
```

### ✅ CORRECT - SharePoint Synced
```
C:\Users\YourName\CompanyName\IT Department - Documents\Apps\DocumentManager
```

### ❌ WRONG - Personal OneDrive
```
C:\Users\YourName\OneDrive\Apps\DocumentManager  ← DON'T USE!
```

---

## Quick Deployment Command

For Teams shared folder deployment:

```batch
cd C:\code\Document Manager
DEPLOY_TO_ONEDRIVE.bat
```

When prompted, enter your Teams folder path:
```
C:\Users\YourName\OneDrive - CompanyName\[TeamName - Channel]\Apps\DocumentManager
```

The script will:
- Detect both Personal and Business OneDrive
- Recommend Business over Personal
- Let you choose or enter custom path
- Warn if path looks like Personal OneDrive

---

## Need Help?

**Can't find the right OneDrive path?**
1. Open Teams → Your channel → Files tab
2. Click "Open in SharePoint"
3. Look at the URL or folder path
4. Use that location for deployment

**Still confused?**
- Contact your IT department
- Ask which shared storage to use
- Mention you need "shared folder access for 20 users"

**Technical support:**
- See: ONEDRIVE_DEPLOYMENT_GUIDE.md
- See: ONEDRIVE_QUICK_START.md
