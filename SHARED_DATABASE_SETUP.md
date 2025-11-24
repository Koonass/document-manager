# Shared Database Setup Guide

## Quick Answer to Your Question

**Q: If I install this individually on each user's machine, will that create an individual database per install rather than a shared one?**

**A: By default, YES** - each installation creates its own local database. However, you can easily configure all installations to use a **shared network database** by setting the `db_path` in the settings file.

---

## Solution: Configure Shared Database

### Step 1: Choose a Network Location for the Database

Pick a location on your network share where the database will live. All users need read/write access to this location.

**Examples:**
- `\\SERVER\SharedData\DocumentManager\document_manager_v2.1.db`
- `\\SERVER\Apps\DocumentManager\DATA\document_manager_v2.1.db`
- `Z:\DocumentManager\document_manager_v2.1.db` (if using mapped drives)

### Step 2: Update settings_v2_3.json

**On each user's installation**, edit the `settings_v2_3.json` file:

```json
{
  "html_path": "\\\\SERVER\\SharedData\\DocumentManager\\Bistrack Exports",
  "pdf_path": "\\\\SERVER\\SharedData\\DocumentManager\\PDFs",
  "archive_path": "\\\\SERVER\\SharedData\\DocumentManager\\Archive",
  "db_path": "\\\\SERVER\\SharedData\\DocumentManager\\document_manager_v2.1.db",
  "version": "2.3.0"
}
```

**Critical:** The `db_path` value must be **identical** on all installations.

### Step 3: Set Permissions

Ensure all users have **read and write** permissions to:
1. The database file location (e.g., `\\SERVER\SharedData\DocumentManager\`)
2. The database file itself (once created)

**Windows Permission Check:**
```batch
# Test write access from each user's computer
echo test > \\SERVER\SharedData\DocumentManager\test.txt
del \\SERVER\SharedData\DocumentManager\test.txt
```

### Step 4: Test with Multiple Users

1. **User 1** launches the application - database is created at the network location
2. **User 2** launches the application - should connect to the same database
3. **Verify:** Changes made by User 1 should be visible to User 2

---

## Installation Options

### Option A: Centralized Installation (Recommended)

Install the application **once** on a network share, and all users run it from there.

**Structure:**
```
\\SERVER\Apps\DocumentManager\
├── run_v2_3.py
├── settings_v2_3.json  ← Configure db_path here (ONE TIME)
├── src\
└── LABEL TEMPLATE\
```

**Each user:**
- Creates a desktop shortcut to `\\SERVER\Apps\DocumentManager\START_APP.bat`
- Runs the application from the network location
- Shares the same database automatically

**Benefits:**
- ✅ Update once, affects all users
- ✅ No need to configure db_path per user
- ✅ Guaranteed everyone uses the same database

### Option B: Individual Installations with Shared Database

Install the application separately on each user's machine, but configure all to use the same database.

**On each user's machine:**
```
C:\Users\Username\DocumentManager\
├── run_v2_3.py
├── settings_v2_3.json  ← Configure db_path (EACH USER)
├── src\
└── LABEL TEMPLATE\
```

**Each user's settings_v2_3.json must have:**
```json
{
  "db_path": "\\\\SERVER\\SharedData\\DocumentManager\\document_manager_v2.1.db"
}
```

**Benefits:**
- ✅ Each user has local copy of application files
- ✅ Faster application startup (no network file access for code)
- ⚠️ Must update each installation separately

---

## Technical Details

### Database Concurrency

**SQLite with WAL Mode:**
- ✅ **Supports:** 2-3 concurrent users safely
- ✅ **Maximum:** Up to 10 users (your use case)
- ✅ **WAL mode is automatically enabled** in the database manager
- ⚠️ **Note:** SQLite on network shares works but has limitations

**Performance Considerations:**
- Read operations are fast (multiple users can read simultaneously)
- Write operations are serialized (one at a time)
- Network latency may add slight delays
- For 2-3 concurrent users, performance is excellent
- For 10 total users (not all concurrent), performance is acceptable

### Upgrade Path (If Needed Later)

If you grow beyond 10 users or need better concurrency:
- Upgrade to **SQL Server Express** (free, supports more users)
- Or use **PostgreSQL** (free, excellent concurrent write performance)
- The application can be updated to support these databases if needed

---

## Troubleshooting

### Issue: "Database is locked" errors

**Cause:** Multiple users trying to write simultaneously, or network latency issues.

**Solutions:**
1. **Ensure WAL mode is enabled** (it should be by default)
2. **Check network connectivity** - slow networks cause lock timeouts
3. **Verify file permissions** - users need write access
4. **Close and reopen** the application
5. **Reduce concurrent writes** - coordinate who saves at the same time

### Issue: Users see different data

**Cause:** Each user is using a different database file.

**Solution:**
1. Check `settings_v2_3.json` on each user's installation
2. Ensure `db_path` is **exactly the same** on all installations
3. Use UNC paths (`\\SERVER\...`), not mapped drives (unless all users map to the same drive letter)

### Issue: Can't create database at network location

**Cause:** Permission issues or invalid path.

**Solutions:**
1. **Test the path** - Can you manually create a file there?
   ```batch
   echo test > \\SERVER\SharedData\DocumentManager\test.txt
   ```
2. **Check permissions** - Do you have read/write access?
3. **Verify server name** - Can you access `\\SERVER` from File Explorer?
4. **Check folder exists** - Create the folder structure if needed:
   ```batch
   mkdir \\SERVER\SharedData\DocumentManager
   ```

### Issue: Application slow to start

**Cause:** Loading application files from network (Option A) or database on slow network.

**Solutions:**
1. **Option A users:** Ensure good network speed to server
2. **Option B users:** Consider local installation with shared database only
3. **Both:** Check network latency: `ping SERVER`
4. **Both:** Ensure database location is on fast storage (SSD preferred)

---

## Summary

### What You Need to Do

For your use case (2-3 concurrent users, ~10 total users):

1. ✅ **Choose installation option:**
   - **Recommended:** Centralized installation (Option A)
   - **Alternative:** Individual installations (Option B)

2. ✅ **Set up network share:**
   - Create folder: `\\SERVER\SharedData\DocumentManager`
   - Set permissions: Read/Write for all users

3. ✅ **Configure database path:**
   - Edit `settings_v2_3.json`
   - Set: `"db_path": "\\\\SERVER\\SharedData\\DocumentManager\\document_manager_v2.1.db"`
   - Ensure all users have the same value

4. ✅ **Test:**
   - User 1 launches app, imports data
   - User 2 launches app, sees same data
   - Verify changes sync between users

### What You Get

- ✅ Single shared database
- ✅ All users see the same data
- ✅ Changes are immediately visible to all users
- ✅ Supports 2-3 concurrent users safely
- ✅ Supports up to 10 total users
- ✅ No additional database server needed
- ✅ Uses SQLite with WAL mode for better concurrency

---

## Example: Complete Network Setup

**Network structure:**
```
\\OFFICE-SERVER\Apps\
└── DocumentManager\
    ├── run_v2_3.py
    ├── settings_v2_3.json
    ├── src\
    └── LABEL TEMPLATE\

\\OFFICE-SERVER\SharedData\
└── DocumentManager\
    ├── document_manager_v2.1.db        ← Shared database
    ├── document_manager_v2.1.db-wal     ← WAL file (auto-created)
    ├── document_manager_v2.1.db-shm     ← Shared memory (auto-created)
    ├── Bistrack Exports\                ← CSV/HTML files
    ├── PDFs\                            ← PDF files
    └── Archive\                         ← Archived files
```

**settings_v2_3.json:**
```json
{
  "html_path": "\\\\OFFICE-SERVER\\SharedData\\DocumentManager\\Bistrack Exports",
  "pdf_path": "\\\\OFFICE-SERVER\\SharedData\\DocumentManager\\PDFs",
  "archive_path": "\\\\OFFICE-SERVER\\SharedData\\DocumentManager\\Archive",
  "db_path": "\\\\OFFICE-SERVER\\SharedData\\DocumentManager\\document_manager_v2.1.db",
  "version": "2.3.0"
}
```

**Each user:**
- Double-clicks: `\\OFFICE-SERVER\Apps\DocumentManager\START_APP.bat`
- Application loads from network
- Database is shared automatically
- All users see the same data in real-time

---

## Questions?

**Need help?** Check the full deployment guide: `NETWORK_DEPLOYMENT_SETUP_GUIDE.md`

**Example settings:** See `settings_v2_3_network_example.json` for a template
