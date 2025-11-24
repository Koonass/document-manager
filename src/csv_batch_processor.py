#!/usr/bin/env python3
"""
CSV Batch Processor - Validate and upload CSV files to BisTrack
Handles batch validation, error checking, and uploading to import folder
"""

import logging
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
from csv_validator import CSVValidator
from enhanced_database_manager import EnhancedDatabaseManager


class CSVBatchProcessor:
    def __init__(self, products_file_path: str = None, bistrack_import_folder: str = None, db_path: str = None):
        """
        Initialize CSV batch processor

        Args:
            products_file_path: Path to products master CSV for SKU validation
            bistrack_import_folder: Path to BisTrack import folder
            db_path: Path to database file
        """
        self.products_file = products_file_path
        self.import_folder = bistrack_import_folder
        self.db_path = db_path

        # Initialize validator if products file provided
        self.validator = None
        if products_file_path and Path(products_file_path).exists():
            self.validator = CSVValidator(products_file_path)
            logging.info(f"CSV Batch Processor initialized with products file: {products_file_path}")
        else:
            logging.warning("CSV Batch Processor initialized without products file - SKU validation disabled")

        # Initialize database manager
        self.db_manager = None
        if db_path:
            self.db_manager = EnhancedDatabaseManager(db_path)

    def validate_csv(self, csv_path: str) -> Dict:
        """
        Validate a single CSV file

        Returns dict with:
        - valid: bool
        - errors: List[str]
        - warnings: List[str]
        - material_count: int
        """
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'material_count': 0
        }

        if not self.validator:
            result['warnings'].append("SKU validation unavailable - products file not configured")
            result['valid'] = True  # Assume valid if no validator
            return result

        try:
            csv_path_obj = Path(csv_path)

            if not csv_path_obj.exists():
                result['errors'].append(f"File not found: {csv_path}")
                return result

            # Run validation
            validation_result = self.validator.validate_csv(csv_path_obj)

            result['valid'] = validation_result.get('is_valid', False)
            result['errors'] = validation_result.get('errors', [])
            result['warnings'] = validation_result.get('warnings', [])
            result['material_count'] = validation_result.get('material_count', 0)

            logging.info(f"Validated {csv_path_obj.name}: Valid={result['valid']}, Errors={len(result['errors'])}, Warnings={len(result['warnings'])}")

            return result

        except Exception as e:
            logging.error(f"Error validating CSV {csv_path}: {e}")
            result['errors'].append(f"Validation error: {str(e)}")
            return result

    def validate_batch(self, csv_paths: List[str]) -> Dict[str, Dict]:
        """
        Validate multiple CSV files

        Returns:
            Dict mapping csv_path -> validation_result
        """
        results = {}

        logging.info(f"Starting batch validation of {len(csv_paths)} CSV files")

        for csv_path in csv_paths:
            results[csv_path] = self.validate_csv(csv_path)

        # Update database with validation results
        if self.db_manager:
            for csv_path, result in results.items():
                if result['valid']:
                    status = 'valid'
                elif result['errors']:
                    status = 'has_errors'
                elif result['warnings']:
                    status = 'has_warnings'
                else:
                    status = 'not_validated'

                self.db_manager.update_csv_validation(
                    csv_path,
                    status,
                    result.get('errors', []) + result.get('warnings', [])
                )

        return results

    def upload_csv(self, csv_path: str) -> Tuple[bool, str]:
        """
        Upload a single CSV file to BisTrack import folder

        Returns:
            (success: bool, message: str)
        """
        if not self.import_folder:
            return False, "BisTrack import folder not configured"

        import_folder_path = Path(self.import_folder)

        if not import_folder_path.exists():
            return False, f"Import folder does not exist: {self.import_folder}"

        csv_path_obj = Path(csv_path)

        if not csv_path_obj.exists():
            return False, f"CSV file not found: {csv_path}"

        try:
            # Copy CSV to import folder
            destination = import_folder_path / csv_path_obj.name

            # Check if file already exists
            if destination.exists():
                logging.warning(f"File already exists in import folder: {destination.name}")
                # Optionally can add timestamp to filename or skip
                return False, f"File already exists in import folder: {destination.name}"

            shutil.copy2(csv_path, destination)
            logging.info(f"Uploaded CSV to BisTrack import folder: {destination.name}")

            # Update database
            if self.db_manager:
                self.db_manager.mark_csv_uploaded(csv_path)

            return True, f"Uploaded successfully to {destination}"

        except Exception as e:
            logging.error(f"Error uploading CSV {csv_path}: {e}")
            return False, f"Upload error: {str(e)}"

    def upload_batch(self, csv_paths: List[str], validate_first: bool = True) -> Dict[str, Tuple[bool, str]]:
        """
        Upload multiple CSV files to BisTrack import folder

        Args:
            csv_paths: List of CSV file paths to upload
            validate_first: Whether to validate before uploading

        Returns:
            Dict mapping csv_path -> (success, message)
        """
        results = {}

        logging.info(f"Starting batch upload of {len(csv_paths)} CSV files")

        # Validate first if requested
        if validate_first:
            validation_results = self.validate_batch(csv_paths)

            # Filter to only valid CSVs
            valid_csvs = [
                path for path, result in validation_results.items()
                if result['valid'] or not result['errors']  # Allow warnings
            ]

            if len(valid_csvs) < len(csv_paths):
                logging.warning(f"Only {len(valid_csvs)}/{len(csv_paths)} CSVs are valid for upload")

            csv_paths = valid_csvs

        # Upload each CSV
        for csv_path in csv_paths:
            results[csv_path] = self.upload_csv(csv_path)

        successful = sum(1 for success, _ in results.values() if success)
        logging.info(f"Batch upload complete: {successful}/{len(csv_paths)} successful")

        return results

    def get_validation_summary(self, validation_results: Dict[str, Dict]) -> str:
        """
        Generate a human-readable summary of validation results

        Args:
            validation_results: Dict from validate_batch

        Returns:
            Summary string
        """
        total = len(validation_results)
        valid = sum(1 for r in validation_results.values() if r['valid'])
        with_errors = sum(1 for r in validation_results.values() if r['errors'])
        with_warnings = sum(1 for r in validation_results.values() if r['warnings'] and not r['errors'])

        summary = f"Validation Results:\n"
        summary += f"  Total: {total}\n"
        summary += f"  ✓ Valid: {valid}\n"
        summary += f"  ❌ Errors: {with_errors}\n"
        summary += f"  ⚠️ Warnings: {with_warnings}\n"

        return summary

    def get_upload_summary(self, upload_results: Dict[str, Tuple[bool, str]]) -> str:
        """
        Generate a human-readable summary of upload results

        Args:
            upload_results: Dict from upload_batch

        Returns:
            Summary string
        """
        total = len(upload_results)
        successful = sum(1 for success, _ in upload_results.values() if success)
        failed = total - successful

        summary = f"Upload Results:\n"
        summary += f"  Total: {total}\n"
        summary += f"  ✓ Successful: {successful}\n"
        summary += f"  ❌ Failed: {failed}\n"

        return summary
