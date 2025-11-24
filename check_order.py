#!/usr/bin/env python3
"""
Quick script to check order 4033090 in the database
"""

import sqlite3
import json
from pathlib import Path

db_path = "document_manager_v2.1.db"

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()

    # Find the order
    print("=" * 80)
    print("SEARCHING FOR ORDER 4033090")
    print("=" * 80)

    cursor.execute("""
        SELECT relationship_id, order_number, pdf_path, created_date, updated_date, processed
        FROM relationships
        WHERE order_number LIKE '%4033090%'
    """)

    relationships = cursor.fetchall()

    if not relationships:
        print("\nNo relationships found for order 4033090")
    else:
        for rel in relationships:
            rel_id, order_num, pdf_path, created, updated, processed = rel
            print(f"\nFound relationship:")
            print(f"  Relationship ID: {rel_id}")
            print(f"  Order Number: {order_num}")
            print(f"  PDF Path: {pdf_path}")
            print(f"  Created: {created}")
            print(f"  Updated: {updated}")
            print(f"  Processed: {processed}")

            # Check if PDF exists
            if pdf_path:
                pdf_exists = Path(pdf_path).exists()
                print(f"  PDF Exists: {pdf_exists}")
                if not pdf_exists:
                    print(f"  ⚠️  WARNING: PDF file not found at: {pdf_path}")

            # Get change history
            print(f"\n  PDF Change History:")
            cursor.execute("""
                SELECT action, old_pdf_path, new_pdf_path, reason, timestamp
                FROM pdf_change_history
                WHERE relationship_id = ?
                ORDER BY timestamp
            """, (rel_id,))

            changes = cursor.fetchall()
            if not changes:
                print("    No change history")
            else:
                for change in changes:
                    action, old_path, new_path, reason, timestamp = change
                    print(f"    [{timestamp}] {action.upper()}")
                    print(f"      Reason: {reason}")
                    if old_path:
                        print(f"      Old: {old_path}")
                    if new_path:
                        print(f"      New: {new_path}")
                    print()

print("\n" + "=" * 80)
