#!/usr/bin/env python3
"""
Word Template Processor - Fills Word templates with job data and prints them
"""

import os
import logging
import tempfile
import time
import shutil
from pathlib import Path
from typing import Dict, Optional
import win32com.client as win32
from datetime import datetime
from error_logger import log_error, log_info, log_warning

class WordTemplateProcessor:
    """Processes Word templates by filling them with job data and printing"""

    def __init__(self, template_path: str = "templates/job_folder_template.docx"):
        """
        Initialize the template processor

        Args:
            template_path: Path to the Word template file
        """
        self.template_path = template_path

    def _get_word_application(self):
        """
        Get Word application instance with automatic cache clearing on AttributeError

        This fixes the common "module 'win32com.gen_py.00020905' has no attribute" error
        by clearing the corrupted COM type library cache and retrying.

        Returns:
            Word.Application COM object
        """
        try:
            # Try with gencache first (faster, early-bound)
            word_app = win32.gencache.EnsureDispatch('Word.Application')
            log_info("Word application created successfully with gencache")
            return word_app

        except AttributeError as e:
            # Cache is corrupted - immediately fall back to late-bound Dispatch
            # Don't try to rebuild cache as it may fail during AddModuleToCache
            log_warning(f"win32com cache corrupted (AttributeError: {str(e)}), using late-bound Dispatch", {
                'error': str(e),
                'error_location': 'gencache.EnsureDispatch or AddModuleToCache'
            })

            # Clear cache for next time (but don't try to rebuild now)
            try:
                gen_py_path = win32.gencache.GetGeneratePath()
                if os.path.exists(gen_py_path):
                    log_info(f"Clearing gen_py cache for next run", {'path': gen_py_path})
                    shutil.rmtree(gen_py_path, ignore_errors=True)
                    log_info("Cache cleared successfully - will rebuild on next run")
            except Exception as clear_error:
                log_warning(f"Could not clear cache, will try again later", {'error': str(clear_error)})

            # Use late-bound Dispatch (works without cache)
            word_app = win32.Dispatch('Word.Application')
            log_info("Word application created successfully with Dispatch (late-bound)")
            return word_app

        except Exception as e:
            # Other errors - try late-bound dispatch
            log_warning(f"gencache.EnsureDispatch failed, trying Dispatch", {
                'error': str(e)
            })
            word_app = win32.Dispatch('Word.Application')
            log_info("Word application created successfully with Dispatch")
            return word_app

    def fill_and_print_template(self, job_data: Dict, printer_name: Optional[str] = None) -> bool:
        """
        Fill template with job data and print it directly

        Args:
            job_data: Dictionary containing job information from CSV
            printer_name: Optional printer name to use (defaults to system default)

        Returns:
            True if successful, False otherwise
        """
        word_app = None
        doc = None

        try:
            # Check if template exists
            template_path_abs = Path(self.template_path).resolve()
            if not template_path_abs.exists():
                error_msg = f"Folder label template file not found: {template_path_abs}"
                logging.error(error_msg)
                log_error("template_file_not_found", FileNotFoundError(error_msg), {
                    'template_path': str(template_path_abs),
                    'order_number': job_data.get('OrderNumber', 'Unknown')
                })
                return False

            log_info(f"Starting folder label print for order {job_data.get('OrderNumber', 'Unknown')}", {
                'template': str(template_path_abs),
                'printer': printer_name or 'Default printer',
                'customer': job_data.get('Customer', ''),
                'job_reference': job_data.get('JobReference', ''),
                'delivery_area': job_data.get('DeliveryArea', ''),
                'designer': job_data.get('Designer', ''),
                'all_fields': list(job_data.keys())  # Show all available fields
            })

            # Start Word application with automatic cache clearing
            word_app = self._get_word_application()
            word_app.Visible = False
            word_app.DisplayAlerts = False

            # Disable screen updating for faster processing
            word_app.ScreenUpdating = False

            # Open template
            doc = word_app.Documents.Open(str(template_path_abs))
            log_info(f"Template opened successfully", {'order': job_data.get('OrderNumber', 'Unknown')})

            # CRITICAL: Wait for Word to fully initialize the document
            # This prevents "Call was rejected by callee" errors
            time.sleep(1)
            log_info(f"Document initialized, ready for processing", {'order': job_data.get('OrderNumber', 'Unknown')})

            # Fill in the template fields
            # Fill all bookmarks that exist in template
            self._fill_bookmark(doc, "Customer", job_data.get('Customer', ''))           # Customer → Customer
            self._fill_bookmark(doc, "OrderNumber", job_data.get('OrderNumber', ''))     # OrderNumber → OrderNumber
            self._fill_bookmark(doc, "LotSub", job_data.get('JobReference', ''))         # JobReference → LotSub
            self._fill_bookmark(doc, "Level", job_data.get('DeliveryArea', ''))          # DeliveryArea → Level

            log_info(f"Bookmarks filled successfully", {'order': job_data.get('OrderNumber', 'Unknown')})
            log_info(f"Filled values - Customer: {job_data.get('Customer', '')[:50]}, JobRef: {job_data.get('JobReference', '')[:50]}, Area: {job_data.get('DeliveryArea', '')[:50]}")

            # CRITICAL: Format the document to ensure it stays on ONE PAGE ONLY (sticker label printer)
            self._force_single_page(doc)

            # Print the document
            if printer_name:
                # Set active printer
                log_info(f"Setting active printer", {'printer': printer_name, 'order': job_data.get('OrderNumber', 'Unknown')})
                word_app.ActivePrinter = printer_name
                log_info(f"Active printer set", {'printer': word_app.ActivePrinter, 'order': job_data.get('OrderNumber', 'Unknown')})
            else:
                log_info(f"Using default printer", {'printer': word_app.ActivePrinter, 'order': job_data.get('OrderNumber', 'Unknown')})

            # Print the document with retry logic
            log_info(f"Sending document to printer", {'order': job_data.get('OrderNumber', 'Unknown')})

            # Retry logic for PrintOut command
            max_print_retries = 3
            print_retry_delay = 1.0
            print_success = False

            for print_attempt in range(max_print_retries):
                try:
                    doc.PrintOut(Background=False)
                    print_success = True
                    log_info(f"PrintOut command completed", {
                        'order': job_data.get('OrderNumber', 'Unknown'),
                        'attempt': print_attempt + 1
                    })
                    break  # Success!
                except Exception as print_error:
                    error_code = getattr(print_error, 'hresult', None) if hasattr(print_error, 'hresult') else None

                    # -2147418111 is "Call was rejected by callee" - Word is busy
                    if error_code == -2147418111 and print_attempt < max_print_retries - 1:
                        log_warning(f"Print command busy, retrying", {
                            'order': job_data.get('OrderNumber', 'Unknown'),
                            'attempt': print_attempt + 1,
                            'max_retries': max_print_retries
                        })
                        time.sleep(print_retry_delay)
                        continue  # Retry
                    else:
                        # Final attempt or different error - re-raise
                        raise print_error

            if not print_success:
                raise Exception("Failed to print after all retries")

            time.sleep(2)  # Give Word time to send the print job

            log_info(f"Successfully printed folder label", {'order': job_data.get('OrderNumber', 'Unknown')})

            return True

        except Exception as e:
            log_error("print_folder_label_template", e, {
                'order_number': job_data.get('OrderNumber', 'Unknown'),
                'template_path': self.template_path,
                'printer_name': printer_name,
                'customer': job_data.get('Customer', '')
            })
            return False

        finally:
            # Clean up
            try:
                if doc:
                    doc.Close(SaveChanges=False)
                if word_app:
                    # Re-enable screen updating before quitting
                    try:
                        word_app.ScreenUpdating = True
                    except:
                        pass
                    word_app.Quit()
            except:
                pass

    def _fill_bookmark(self, doc, bookmark_name: str, value: str):
        """
        Fill a bookmark in the Word document with retry logic for COM errors
        Forces text to shrink-to-fit for label printing (no vertical expansion)

        Args:
            doc: Word document object
            bookmark_name: Name of the bookmark to fill
            value: Text value to insert
        """
        max_retries = 3
        retry_delay = 0.5  # seconds

        for attempt in range(max_retries):
            try:
                if doc.Bookmarks.Exists(bookmark_name):
                    bookmark_range = doc.Bookmarks(bookmark_name).Range
                    bookmark_range.Text = str(value) if value else ""

                    # CRITICAL: Lock cell height to prevent expansion (overflow text will be clipped)
                    # This forces users to abbreviate text to fit within the label
                    try:
                        # If text is in a table cell, lock the row height
                        if bookmark_range.Information(12):  # wdWithInTable
                            cell = bookmark_range.Cells(1)
                            row = cell.Range.Rows(1)

                            # CRITICAL: Lock row to exact height (prevent vertical expansion)
                            # Text that doesn't fit will be clipped - forces better abbreviations
                            row.HeightRule = 1  # wdRowHeightExactly - do NOT expand
                            current_height = row.Height
                            row.Height = current_height
                            row.AllowBreakAcrossPages = False

                            # Remove spacing to maximize available space
                            for para in cell.Range.Paragraphs:
                                para.SpaceBefore = 0
                                para.SpaceAfter = 0
                                para.LineSpacingRule = 0  # wdLineSpaceSingle
                    except Exception as cell_error:
                        log_warning(f"Could not apply cell formatting", {
                            'bookmark': bookmark_name,
                            'error': str(cell_error)
                        })

                    # Recreate bookmark after filling (bookmarks are deleted when text is inserted)
                    doc.Bookmarks.Add(bookmark_name, bookmark_range)
                    log_info(f"Filled bookmark", {'bookmark': bookmark_name, 'value': value, 'attempt': attempt + 1})
                    return  # Success
                else:
                    log_warning(f"Bookmark not found in template", {'bookmark': bookmark_name, 'expected_value': value})
                    return  # No point retrying if bookmark doesn't exist
            except Exception as e:
                error_code = getattr(e, 'hresult', None) if hasattr(e, 'hresult') else None

                # -2147418111 is "Call was rejected by callee" - Word is busy
                if error_code == -2147418111 and attempt < max_retries - 1:
                    log_warning(f"Bookmark filling busy, retrying", {
                        'bookmark': bookmark_name,
                        'attempt': attempt + 1,
                        'max_retries': max_retries
                    })
                    time.sleep(retry_delay)
                    continue  # Retry
                else:
                    # Final attempt failed or different error
                    log_warning(f"Could not fill bookmark", {
                        'bookmark': bookmark_name,
                        'error': str(e),
                        'attempts': attempt + 1
                    })
                    return

    def _force_single_page(self, doc):
        """
        AGGRESSIVELY force document to stay on ONE PAGE ONLY for sticker label printer
        - Remove ALL page breaks
        - Lock all content to single page
        - Prevent any pagination
        """
        try:
            # Step 1: Remove ALL manual page breaks from entire document
            for paragraph in doc.Paragraphs:
                try:
                    paragraph.PageBreakBefore = False
                    paragraph.KeepTogether = True
                    paragraph.KeepWithNext = False  # Don't force keeps that might cause breaks
                    # Remove widow/orphan control which can cause breaks
                    paragraph.WidowControl = False
                except:
                    pass

            # Step 2: Lock ALL tables to single page with FIXED heights
            for table in doc.Tables:
                try:
                    # Force entire table to stay together
                    for row in table.Rows:
                        try:
                            # CRITICAL: Do not allow row to break across pages
                            row.AllowBreakAcrossPages = False
                            # Keep row together
                            row.Range.ParagraphFormat.KeepTogether = True
                            # Disable widow/orphan control
                            row.Range.ParagraphFormat.WidowControl = False

                            # CRITICAL FOR LABELS: Lock row to exact height (prevent vertical expansion)
                            # Use wdRowHeightExactly (1) to force exact height
                            try:
                                row.HeightRule = 1  # wdRowHeightExactly - do not expand
                                # Keep existing height from template
                                current_height = row.Height
                                row.Height = current_height
                            except:
                                pass
                        except:
                            pass

                    # Configure all cells for single-page printing
                    for row in table.Rows:
                        for cell in row.Cells:
                            try:
                                cell.WordWrap = True
                                # Force all paragraphs in cell to stay together
                                for para in cell.Range.Paragraphs:
                                    para.KeepTogether = True
                                    para.PageBreakBefore = False
                                    para.WidowControl = False
                            except:
                                pass
                except:
                    pass

            # Step 3: Search for and remove any hidden page break characters
            try:
                # Find and replace manual page breaks (^m) with nothing
                find_obj = doc.Content.Find
                find_obj.ClearFormatting()
                find_obj.Text = "^m"  # Manual page break code
                find_obj.Replacement.ClearFormatting()
                find_obj.Replacement.Text = ""
                find_obj.Execute(Replace=2)  # wdReplaceAll = 2

                # Find and replace section breaks
                find_obj.Text = "^b"  # Section break code
                find_obj.Replacement.Text = ""
                find_obj.Execute(Replace=2)
            except:
                pass

            # Step 4: Ensure document pagination is disabled
            try:
                # Set document to not paginate
                doc.Repaginate()
            except:
                pass

            log_info("Document FORCED to single page (sticker label mode)")

        except Exception as e:
            log_warning(f"Could not fully force document to single page", {
                'error': str(e)
            })

    def fill_template_to_file(self, job_data: Dict, output_path: str) -> bool:
        """
        Fill template and save to a file (alternative to direct printing)

        Args:
            job_data: Dictionary containing job information
            output_path: Path where to save the filled document

        Returns:
            True if successful, False otherwise
        """
        word_app = None
        doc = None

        try:
            # Check if template exists
            template_path_abs = Path(self.template_path).resolve()
            if not template_path_abs.exists():
                logging.error(f"Template file not found: {template_path_abs}")
                return False

            # Start Word application with automatic cache clearing
            word_app = self._get_word_application()
            word_app.Visible = False
            word_app.DisplayAlerts = False
            word_app.ScreenUpdating = False

            # Open template
            doc = word_app.Documents.Open(str(template_path_abs))

            # Wait for Word to initialize
            time.sleep(0.5)

            # Fill in the template fields
            # Fill all bookmarks that exist in template
            self._fill_bookmark(doc, "Customer", job_data.get('Customer', ''))           # Customer → Customer
            self._fill_bookmark(doc, "OrderNumber", job_data.get('OrderNumber', ''))     # OrderNumber → OrderNumber
            self._fill_bookmark(doc, "LotSub", job_data.get('JobReference', ''))         # JobReference → LotSub
            self._fill_bookmark(doc, "Level", job_data.get('DeliveryArea', ''))          # DeliveryArea → Level

            # Save to output path
            doc.SaveAs(str(Path(output_path).resolve()))

            logging.info(f"Successfully saved filled template to {output_path}")

            return True

        except Exception as e:
            logging.error(f"Failed to fill template: {e}")
            return False

        finally:
            # Clean up
            try:
                if doc:
                    doc.Close(SaveChanges=False)
                if word_app:
                    # Re-enable screen updating before quitting
                    try:
                        word_app.ScreenUpdating = True
                    except:
                        pass
                    word_app.Quit()
            except:
                pass


def print_folder_label(job_data: Dict, template_path: str = "templates/job_folder_template.docx",
                       printer_name: Optional[str] = None) -> bool:
    """
    Convenience function to print a folder label for a job

    Args:
        job_data: Job data dictionary (csv_data from order)
        template_path: Path to template file
        printer_name: Optional printer to use

    Returns:
        True if successful
    """
    processor = WordTemplateProcessor(template_path)
    return processor.fill_and_print_template(job_data, printer_name)
