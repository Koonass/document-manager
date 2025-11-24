#!/usr/bin/env python3
"""
Enhanced Search View - Search results displayed in an expanded view card format
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Any, Optional, Callable
import subprocess
import platform
import os
import logging

class SearchResultsSection(tk.Frame):
    def __init__(self, parent, title: str, color: str, orders: List[Dict], **kwargs):
        super().__init__(parent, **kwargs)

        self.title = title
        self.color = color
        self.orders = orders
        self.on_pdf_attach = None
        self.on_refresh_needed = None

        self.setup_section()

    def setup_section(self):
        """Create the search results section with header and order list"""
        # Configure main frame
        self.configure(bg='#ffffff', relief='solid', borderwidth=1)

        # Header frame
        header_frame = tk.Frame(self, bg=self.color, height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Header title with count
        header_label = tk.Label(
            header_frame,
            text=f"{self.title} ({len(self.orders)})",
            font=("Segoe UI", 16, "bold"),
            bg=self.color,
            fg='white'
        )
        header_label.pack(side=tk.LEFT, padx=15, pady=10)

        # Print All button for green category
        if self.color == '#27ae60':  # Green category
            self.print_all_btn = tk.Button(
                header_frame,
                text="🖨️ Print All",
                command=self.print_all_pdfs,
                font=("Segoe UI", 9, "bold"),
                bg='#34495e',
                fg='white',
                border=0,
                padx=15,
                pady=5,
                cursor='hand2'
            )
            self.print_all_btn.pack(side=tk.RIGHT, padx=15, pady=7)

        # Orders list frame
        if self.orders:
            self.create_orders_list()
        else:
            # Empty state
            empty_label = tk.Label(
                self,
                text="No orders in this category",
                font=("Segoe UI", 10, "italic"),
                bg='#ffffff',
                fg='#7f8c8d'
            )
            empty_label.pack(pady=20)

    def create_orders_list(self):
        """Create the detailed orders list"""
        # Create treeview frame
        tree_frame = tk.Frame(self, bg='#ffffff')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Define columns
        columns = ('Order', 'Customer', 'Job Ref', 'Designer', 'Date Required', 'PDF Status', 'Actions')

        # Configure style for larger text
        style = ttk.Style()
        style.configure("Search.Treeview", rowheight=25, font=("Segoe UI", 11))
        style.configure("Search.Treeview.Heading", font=("Segoe UI", 12, "bold"))

        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=min(len(self.orders), 8), style="Search.Treeview")

        # Configure tags for link styling
        self.tree.tag_configure("pdf_link", foreground="#0066cc", font=("Segoe UI", 11, "underline"))
        self.tree.tag_configure("browse_button", foreground="#ffffff", background="#3498db")

        # Configure columns
        column_widths = {
            'Order': 100,
            'Customer': 150,
            'Job Ref': 120,
            'Designer': 100,
            'Date Required': 120,
            'PDF Status': 100,
            'Actions': 80
        }

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Populate orders
        for order in self.orders:
            self.add_order_to_tree(order)

        # Bind events
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        self.tree.bind('<Motion>', self.on_tree_motion)
        self.tree.bind('<Button-3>', self.on_tree_right_click)  # Right-click

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_order_to_tree(self, order: Dict):
        """Add an order to the tree view"""
        csv_data = order.get('csv_data', {})

        # Show PDF status with attachment method indicator
        if order.get('pdf_path'):
            attachment_method = order.get('attachment_method')
            if attachment_method == 'manual':
                pdf_status = "✅ 📎 Manual"
            elif attachment_method == 'automatic':
                pdf_status = "✅ Auto"
            else:
                pdf_status = "✅ Has PDF"
        else:
            pdf_status = "❌ No PDF"

        values = (
            csv_data.get('OrderNumber', ''),
            csv_data.get('Customer', ''),
            csv_data.get('JobReference', ''),
            csv_data.get('Designer', ''),
            csv_data.get('DateRequired', ''),
            pdf_status,
            "📁 Browse"
        )

        # Determine tags for styling
        tags = []
        if order.get('pdf_path'):
            tags.append("pdf_link")

        item_id = self.tree.insert('', tk.END, values=values, tags=tags)

        # Store order data in a separate dictionary
        if not hasattr(self, 'order_data_map'):
            self.order_data_map = {}
        self.order_data_map[item_id] = order

    def on_tree_motion(self, event):
        """Handle mouse motion over tree items for cursor changes"""
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if item and (column == '#6' or column == '#7'):  # PDF Status or Actions column
            # Change cursor to hand for clickable items
            self.tree.config(cursor='hand2')
        else:
            self.tree.config(cursor='')

    def on_tree_double_click(self, event):
        """Handle double-click on tree item"""
        if not self.tree.selection():
            return

        item = self.tree.selection()[0]
        column = self.tree.identify_column(event.x)

        # Get order data from our mapping
        if not hasattr(self, 'order_data_map') or item not in self.order_data_map:
            return

        order_data = self.order_data_map[item]

        if column == '#6':  # PDF Status column
            if order_data.get('pdf_path'):
                self.view_pdf(order_data['pdf_path'])
        elif column == '#7':  # Actions column
            self.browse_for_pdf(order_data, item)

    def view_pdf(self, pdf_path: str):
        """Open PDF in default viewer"""
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', pdf_path))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(pdf_path)
            else:  # linux variants
                subprocess.call(('xdg-open', pdf_path))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF:\n{str(e)}")

    def browse_for_pdf(self, order_data: Dict, tree_item):
        """Browse for PDF file to attach/replace"""
        order_number = order_data.get('csv_data', {}).get('OrderNumber', '')

        file_path = filedialog.askopenfilename(
            title=f"Select PDF for Order {order_number}",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if file_path:
            # Update order data
            order_data['pdf_path'] = file_path
            order_data['has_pdf'] = True

            # Notify parent about PDF attachment
            if self.on_pdf_attach:
                success = self.on_pdf_attach(order_data, file_path)

                if success:
                    messagebox.showinfo("Success", f"PDF attached to order {order_number}")

                    # Trigger refresh of the search view
                    if self.on_refresh_needed:
                        self.on_refresh_needed()
                else:
                    messagebox.showerror("Error", "Failed to attach PDF")

    def on_tree_right_click(self, event):
        """Handle right-click on tree item to show context menu"""
        # Identify the item under the cursor
        item = self.tree.identify_row(event.y)

        if not item:
            return

        # Select the item
        self.tree.selection_set(item)

        # Get order data from our mapping
        if not hasattr(self, 'order_data_map') or item not in self.order_data_map:
            return

        order_data = self.order_data_map[item]
        pdf_path = order_data.get('pdf_path')

        # Create context menu
        context_menu = tk.Menu(self, tearoff=0)

        # Menu options based on whether order has PDF (green and gray categories only)
        if pdf_path:
            context_menu.add_command(
                label="📧 Email PDF",
                command=lambda: self.email_pdf(order_data, pdf_path)
            )
            context_menu.add_command(
                label="💾 Save PDF As",
                command=lambda: self.save_pdf_as(order_data, pdf_path)
            )
            context_menu.add_command(
                label="🖨️ Print PDF",
                command=lambda: self.print_pdf(pdf_path)
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="👁️ View PDF",
                command=lambda: self.view_pdf(pdf_path)
            )
        else:
            # Red category - no PDF
            context_menu.add_command(
                label="📎 Attach PDF",
                command=lambda: self.browse_for_pdf(order_data, item)
            )

        # Show menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def print_pdf(self, pdf_path: str):
        """Print the PDF file"""
        try:
            if platform.system() == 'Windows':
                # Use Windows print command
                subprocess.run(['start', '/print', pdf_path], shell=True, check=True)
                messagebox.showinfo("Print", "PDF sent to default printer")
            else:
                messagebox.showinfo("Print", "Please use your system's print dialog to print the PDF after viewing it.")
                self.view_pdf(pdf_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not print PDF:\n{str(e)}")

    def email_pdf(self, order_data: Dict, pdf_path: str):
        """Open email client with PDF information"""
        try:
            order_number = order_data.get('csv_data', {}).get('OrderNumber', '')
            customer = order_data.get('csv_data', {}).get('Customer', '')

            if platform.system() == 'Windows':
                # Create mailto link with order information
                mailto_url = f"mailto:?subject=Order {order_number} - {customer}&body=Please find attached PDF for order {order_number}"
                subprocess.run(['start', mailto_url], shell=True)
                messagebox.showinfo("Email", f"Email client opened.\n\nPlease manually attach the PDF file:\n{pdf_path}")
            else:
                messagebox.showinfo("Email", f"Please manually attach this PDF to your email:\n{pdf_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open email client:\n{str(e)}")

    def save_pdf_as(self, order_data: Dict, pdf_path: str):
        """Save PDF to a different location"""
        if not pdf_path or not os.path.exists(pdf_path):
            messagebox.showerror("Error", "PDF file not found")
            return

        order_number = order_data.get('csv_data', {}).get('OrderNumber', '')

        save_path = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialname=f"Order_{order_number}.pdf"
        )

        if save_path:
            try:
                import shutil
                shutil.copy2(pdf_path, save_path)
                messagebox.showinfo("Success", f"PDF saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save PDF:\n{str(e)}")

    def print_all_pdfs(self):
        """Print all PDFs in this category (green only)"""
        if self.color != '#27ae60':  # Only for green category
            return

        pdfs_to_print = []
        for order in self.orders:
            if order.get('pdf_path'):
                pdfs_to_print.append(order)

        if not pdfs_to_print:
            messagebox.showinfo("Print All", "No PDFs to print in this category")
            return

        # Confirm print action
        result = messagebox.askyesno(
            "Print All PDFs",
            f"This will print {len(pdfs_to_print)} PDFs and mark them as processed.\n\n"
            f"Continue with batch printing?"
        )

        if result:
            self.execute_batch_print(pdfs_to_print)

    def execute_batch_print(self, orders_to_print: List[Dict]):
        """Execute batch printing and mark as processed"""
        successful_prints = 0
        failed_prints = 0

        for order in orders_to_print:
            try:
                pdf_path = order.get('pdf_path')
                if pdf_path and os.path.exists(pdf_path):

                    if platform.system() == 'Windows':
                        # Use Windows print command
                        subprocess.run(['start', '/print', pdf_path], shell=True, check=True)
                        successful_prints += 1
                    else:
                        # For non-Windows, just log the action
                        logging.info(f"Print requested for {pdf_path}")
                        successful_prints += 1

                else:
                    failed_prints += 1
                    logging.warning(f"PDF not found for printing: {pdf_path}")

            except Exception as e:
                failed_prints += 1
                logging.error(f"Failed to print PDF {order.get('pdf_path', '')}: {e}")

        # Show results
        if successful_prints > 0:
            messagebox.showinfo(
                "Batch Print Complete",
                f"Successfully sent {successful_prints} PDFs to printer.\n"
                f"Failed: {failed_prints}\n\n"
                f"These orders will now be marked as processed."
            )

            # Mark orders as processed (callback to parent)
            if hasattr(self, 'on_mark_processed'):
                self.on_mark_processed(orders_to_print)

            # Trigger refresh
            if self.on_refresh_needed:
                self.on_refresh_needed()
        else:
            messagebox.showerror("Print Failed", f"Failed to print any PDFs. Check the log for details.")

class EnhancedSearchView(tk.Toplevel):
    def __init__(self, parent, search_term: str, search_results: List[Dict], pdf_processor, relationship_manager, archive_manager=None):
        super().__init__(parent)

        self.search_term = search_term
        self.search_results = search_results
        self.pdf_processor = pdf_processor
        self.relationship_manager = relationship_manager
        self.archive_manager = archive_manager

        # Callbacks
        self.on_statistics_refresh = None

        self.setup_dialog()

    def setup_dialog(self):
        """Create the enhanced search view dialog"""
        self.title(f"Search Results: '{self.search_term}'")
        self.geometry("1200x800")
        self.configure(bg='#ecf0f1')
        self.transient(self.master)
        self.grab_set()

        # Header frame
        header_frame = tk.Frame(self, bg='#e67e22', height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Search term and statistics
        search_label = tk.Label(
            header_frame,
            text=f"Search Results for: '{self.search_term}'",
            font=("Segoe UI", 18, "bold"),
            bg='#e67e22',
            fg='white'
        )
        search_label.pack(pady=15)

        # Summary statistics
        self.summary_label = tk.Label(
            header_frame,
            text="",
            font=("Segoe UI", 10),
            bg='#e67e22',
            fg='#ffffff'
        )
        self.summary_label.pack()

        # Search controls frame
        search_controls_frame = tk.Frame(header_frame, bg='#e67e22')
        search_controls_frame.pack(pady=(10, 0))

        # New search entry
        self.new_search_var = tk.StringVar()
        new_search_entry = tk.Entry(
            search_controls_frame,
            textvariable=self.new_search_var,
            font=("Segoe UI", 11),
            width=30
        )
        new_search_entry.pack(side=tk.LEFT, padx=(0, 10))
        new_search_entry.bind('<Return>', self.perform_new_search)

        new_search_btn = tk.Button(
            search_controls_frame,
            text="🔍 New Search",
            command=self.perform_new_search,
            font=("Segoe UI", 10, "bold"),
            bg='#d35400',
            fg='white',
            border=0,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        new_search_btn.pack(side=tk.LEFT)

        # Main content area with categories
        self.content_frame = tk.Frame(self, bg='#ecf0f1')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create category sections
        self.create_category_sections()

        # Close button
        close_btn = tk.Button(
            self,
            text="Close",
            command=self.destroy,
            font=("Segoe UI", 11),
            bg='#95a5a6',
            fg='white',
            border=0,
            padx=25,
            pady=8
        )
        close_btn.pack(pady=(0, 20))

    def create_category_sections(self):
        """Create the categorized search results sections"""
        # Categorize search results
        green_orders = [order for order in self.search_results
                       if (order.get('has_pdf', False) or order.get('pdf_path'))
                       and not order.get('processed', False)]
        gray_orders = [order for order in self.search_results
                      if (order.get('has_pdf', False) or order.get('pdf_path'))
                      and order.get('processed', False)]
        red_orders = [order for order in self.search_results
                     if not (order.get('has_pdf', False) or order.get('pdf_path'))]

        # Update summary
        total = len(self.search_results)
        summary_text = f"Found {total} results | Ready: {len(green_orders)} | Processed: {len(gray_orders)} | No PDF: {len(red_orders)}"
        self.summary_label.config(text=summary_text)

        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Create category sections
        if green_orders:
            green_section = SearchResultsSection(
                self.content_frame,
                "✅ Ready to Print",
                "#27ae60",
                green_orders
            )
            green_section.on_pdf_attach = self.handle_pdf_attachment
            green_section.on_refresh_needed = self.refresh_view
            green_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        if gray_orders:
            gray_section = SearchResultsSection(
                self.content_frame,
                "📋 Previously Processed",
                "#95a5a6",
                gray_orders
            )
            gray_section.on_pdf_attach = self.handle_pdf_attachment
            gray_section.on_refresh_needed = self.refresh_view
            gray_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        if red_orders:
            red_section = SearchResultsSection(
                self.content_frame,
                "❌ Orders without PDFs",
                "#e74c3c",
                red_orders
            )
            red_section.on_pdf_attach = self.handle_pdf_attachment
            red_section.on_refresh_needed = self.refresh_view
            red_section.pack(fill=tk.BOTH, expand=True)

        # If no results
        if not self.search_results:
            empty_label = tk.Label(
                self.content_frame,
                text=f"No results found for '{self.search_term}'\n\nTry searching for:\n• Order numbers\n• Customer names\n• Job references\n• Designer names",
                font=("Segoe UI", 12),
                bg='#ecf0f1',
                fg='#7f8c8d',
                justify=tk.LEFT
            )
            empty_label.pack(expand=True, pady=50)

    def perform_new_search(self, event=None):
        """Perform a new search"""
        new_search_term = self.new_search_var.get().strip()
        if not new_search_term:
            return

        try:
            # Import the database manager (you may need to adjust this import)
            from enhanced_database_v2 import EnhancedDatabaseV2
            db_manager = EnhancedDatabaseV2()

            new_results = db_manager.search_relationships(new_search_term, 'general')

            if new_results:
                # Update the current view
                self.search_term = new_search_term
                self.search_results = new_results
                self.title(f"Search Results: '{self.search_term}'")
                self.create_category_sections()
                self.new_search_var.set("")  # Clear search field
            else:
                messagebox.showinfo("Search Results", f"No results found for '{new_search_term}'")

        except Exception as e:
            logging.error(f"New search failed: {e}")
            messagebox.showerror("Search Error", f"Search failed: {str(e)}")

    def handle_pdf_attachment(self, order_data: Dict, pdf_path: str) -> bool:
        """Handle PDF attachment to an order"""
        try:
            order_number = order_data.get('csv_data', {}).get('OrderNumber', '')
            relationship = self.relationship_manager.get_relationship_by_order(order_number)

            if relationship:
                success = self.relationship_manager.update_relationship_pdf(
                    relationship['relationship_id'],
                    pdf_path,
                    "manual_attachment"
                )

                if success:
                    # Update local data
                    for order in self.search_results:
                        if order.get('csv_data', {}).get('OrderNumber') == order_number:
                            order['pdf_path'] = pdf_path
                            order['has_pdf'] = True
                            break

                    logging.info(f"PDF manually attached to order {order_number}")
                    return True

            return False

        except Exception as e:
            logging.error(f"Failed to handle PDF attachment: {e}")
            return False

    def refresh_view(self):
        """Refresh the search view"""
        self.create_category_sections()

        # Notify parent to refresh statistics
        if self.on_statistics_refresh:
            self.on_statistics_refresh()

    def set_statistics_refresh_callback(self, callback):
        """Set callback for refreshing parent statistics"""
        self.on_statistics_refresh = callback