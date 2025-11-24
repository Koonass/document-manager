#!/usr/bin/env python3
"""
Enhanced Error Logger - Captures detailed errors for debugging
"""

import logging
import traceback
import sys
from datetime import datetime
from pathlib import Path


class ErrorLogger:
    """Enhanced error logger with file output and detailed formatting"""

    def __init__(self, log_file="print_errors.log"):
        self.log_file = log_file
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        # Create logger
        self.logger = logging.getLogger('PrintSystem')
        self.logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        self.logger.handlers = []

        # File handler - detailed logs
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler - important messages only
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def log_error(self, operation, error, context=None):
        """
        Log an error with full details

        Args:
            operation: What was being attempted (e.g., "print_pdf", "open_preset_manager")
            error: The exception object
            context: Dict with additional context (order_number, printer_name, etc.)
        """
        self.logger.error(f"OPERATION: {operation}")
        self.logger.error(f"ERROR: {type(error).__name__}: {str(error)}")

        if context:
            self.logger.error(f"CONTEXT: {context}")

        self.logger.error(f"TRACEBACK:\n{traceback.format_exc()}")
        self.logger.error("-" * 80)

    def log_info(self, message, context=None):
        """Log informational message"""
        if context:
            self.logger.info(f"{message} | Context: {context}")
        else:
            self.logger.info(message)

    def log_warning(self, message, context=None):
        """Log warning message"""
        if context:
            self.logger.warning(f"{message} | Context: {context}")
        else:
            self.logger.warning(message)

    def log_success(self, operation, context=None):
        """Log successful operation"""
        self.log_info(f"SUCCESS: {operation}", context)

    def get_recent_errors(self, lines=50):
        """Get recent error log entries"""
        try:
            if not Path(self.log_file).exists():
                return "No error log file found."

            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()

            # Get last N lines
            recent = all_lines[-lines:] if len(all_lines) > lines else all_lines

            return "".join(recent)
        except Exception as e:
            return f"Error reading log file: {e}"

    def clear_log(self):
        """Clear the error log"""
        try:
            if Path(self.log_file).exists():
                Path(self.log_file).unlink()
            self.setup_logging()  # Recreate handlers
            self.logger.info("Log file cleared")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear log: {e}")
            return False


# Global error logger instance
_error_logger = None


def get_error_logger():
    """Get or create global error logger instance"""
    global _error_logger
    if _error_logger is None:
        _error_logger = ErrorLogger()
    return _error_logger


def log_error(operation, error, context=None):
    """Convenience function to log error"""
    get_error_logger().log_error(operation, error, context)


def log_info(message, context=None):
    """Convenience function to log info"""
    get_error_logger().log_info(message, context)


def log_warning(message, context=None):
    """Convenience function to log warning"""
    get_error_logger().log_warning(message, context)


def log_success(operation, context=None):
    """Convenience function to log success"""
    get_error_logger().log_success(operation, context)
