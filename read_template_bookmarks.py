#!/usr/bin/env python3
"""
Read and display all bookmarks from the Word template
"""
import win32com.client as win32

template_path = r"C:\code\Document Manager\LABEL TEMPLATE\Contract_Lumber_Label_Template.docx"

print(f"Reading template: {template_path}")
print("=" * 80)

try:
    # Start Word
    word_app = win32.gencache.EnsureDispatch('Word.Application')
    word_app.Visible = False
    word_app.DisplayAlerts = False

    # Open template
    doc = word_app.Documents.Open(template_path)

    # Get bookmarks
    bookmarks = doc.Bookmarks

    print(f"\nFound {bookmarks.Count} bookmarks in template:\n")

    if bookmarks.Count > 0:
        for i in range(1, bookmarks.Count + 1):
            bookmark = bookmarks(i)
            bookmark_name = bookmark.Name
            print(f"  {i}. '{bookmark_name}'")
    else:
        print("  WARNING: NO BOOKMARKS FOUND!")
        print("\n  This template doesn't have any bookmarks.")
        print("  You need to add bookmarks in Word for the fields you want to fill.")

    # Close without saving
    doc.Close(SaveChanges=False)
    word_app.Quit()

    print("\n" + "=" * 80)
    print("SUCCESS: Done!")

except Exception as e:
    print(f"\nERROR: {e}")
    try:
        word_app.Quit()
    except:
        pass
