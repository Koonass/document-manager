#!/usr/bin/env python3
"""
Update all 'unknown' attachment reasons to 'manual_attachment' in the database
"""

import sqlite3
from pathlib import Path

db_path = "document_manager_v2.1.db"

print("=" * 80)
print("UPDATING ATTACHMENT REASONS FROM 'unknown' TO 'manual_attachment'")
print("=" * 80)

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()

    # Check current unknown reasons
    cursor.execute("""
        SELECT COUNT(*) FROM pdf_change_history
        WHERE reason = 'unknown'
    """)
    count = cursor.fetchone()[0]

    print(f"\nFound {count} records with reason='unknown'")

    if count > 0:
        # Update unknown to manual_attachment
        cursor.execute("""
            UPDATE pdf_change_history
            SET reason = 'manual_attachment'
            WHERE reason = 'unknown'
        """)

        conn.commit()
        print(f"✅ Updated {cursor.rowcount} records to 'manual_attachment'")
    else:
        print("No updates needed")

print("\n" + "=" * 80)
