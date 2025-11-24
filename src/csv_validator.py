#!/usr/bin/env python3
"""
CSV Validator - Validate CSV data quality and SKU verification
Checks for errors before uploading to BisTrack import folder
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set
from csv_processor import CSVProcessor

class ValidationError:
    """Represents a validation error found in CSV"""

    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'

    def __init__(self, line_number: int, severity: str, field: str, message: str,
                 current_value: any, suggested_fix: Optional[str] = None):
        self.line_number = line_number
        self.severity = severity
        self.field = field
        self.message = message
        self.current_value = current_value
        self.suggested_fix = suggested_fix
        self.fixed = False

    def __repr__(self):
        return f"Line {self.line_number}: {self.severity.upper()} - {self.message}"


class CSVValidator:
    """Validates CSV files for BisTrack import"""

    def __init__(self, products_file_path: Optional[Path] = None):
        """
        Initialize validator

        Args:
            products_file_path: Path to products/SKU master file (optional)
        """
        self.products_file = products_file_path
        self.valid_skus: Set[str] = set()
        self.sku_descriptions: Dict[str, str] = {}

        # Load products file if provided
        if products_file_path and products_file_path.exists():
            self.load_products_file(products_file_path)

    def load_products_file(self, products_file: Path):
        """
        Load products/SKU master file

        Expected format:
        SKU,Description,Active
        J1400-4500s-BC,'BCI 4500s 1.75" X 14"',1
        """
        try:
            logging.info(f"Loading products file: {products_file.name}")

            with open(products_file, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()

            # Skip header
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue

                parts = [p.strip().strip('"') for p in line.split(',')]

                if len(parts) >= 2:
                    sku = parts[0]
                    description = parts[1]
                    active = parts[2] if len(parts) >= 3 else '1'

                    # Only load active SKUs
                    if active == '1' or active.lower() == 'true':
                        self.valid_skus.add(sku)
                        self.sku_descriptions[sku] = description

            logging.info(f"Loaded {len(self.valid_skus)} valid SKUs from products file")

        except Exception as e:
            logging.error(f"Error loading products file: {e}")

    def validate_csv(self, csv_path: Path, strict_mode: bool = False) -> List[ValidationError]:
        """
        Validate CSV file

        Args:
            csv_path: Path to CSV file
            strict_mode: If True, warnings are treated as errors

        Returns:
            List of validation errors found
        """
        errors = []

        try:
            processor = CSVProcessor()

            # Parse CSV structure
            structure = processor.parse_csv_structure(csv_path)

            # Check for critical structure errors
            if structure.get('has_errors', False):
                for msg in structure.get('error_messages', []):
                    errors.append(ValidationError(
                        line_number=0,
                        severity=ValidationError.ERROR,
                        field='file',
                        message=f"File structure error: {msg}",
                        current_value=None
                    ))

            # Check if order number found
            if not structure.get('order_number'):
                errors.append(ValidationError(
                    line_number=3,
                    severity=ValidationError.ERROR,
                    field='Job Description',
                    message="Order number not found in Job Description field",
                    current_value=None
                ))

            # Get material lines
            materials = processor.get_material_lines(csv_path)

            if len(materials) == 0:
                errors.append(ValidationError(
                    line_number=0,
                    severity=ValidationError.ERROR,
                    field='materials',
                    message="No material lines found in CSV",
                    current_value=None
                ))
                return errors

            # Validate each material line
            for material in materials:
                line_errors = self._validate_material_line(material, strict_mode)
                errors.extend(line_errors)

            # Summary
            error_count = len([e for e in errors if e.severity == ValidationError.ERROR])
            warning_count = len([e for e in errors if e.severity == ValidationError.WARNING])

            logging.info(f"Validation complete: {error_count} errors, {warning_count} warnings")

            return errors

        except Exception as e:
            logging.error(f"Error validating CSV {csv_path.name}: {e}")
            errors.append(ValidationError(
                line_number=0,
                severity=ValidationError.ERROR,
                field='file',
                message=f"Validation failed: {str(e)}",
                current_value=None
            ))
            return errors

    def _validate_material_line(self, material: Dict, strict_mode: bool) -> List[ValidationError]:
        """Validate a single material line"""
        errors = []
        line_num = material.get('line_number', 0)

        # Validate SKU
        sku = material.get('sku', '').strip()
        if not sku:
            errors.append(ValidationError(
                line_number=line_num,
                severity=ValidationError.ERROR,
                field='SKU',
                message="SKU is empty",
                current_value=None
            ))
        elif self.valid_skus and sku not in self.valid_skus:
            # SKU not in products file
            suggested = self._find_similar_sku(sku)
            errors.append(ValidationError(
                line_number=line_num,
                severity=ValidationError.WARNING if not strict_mode else ValidationError.ERROR,
                field='SKU',
                message=f"SKU '{sku}' not found in products file",
                current_value=sku,
                suggested_fix=suggested
            ))

        # Validate Quantity
        qty = material.get('qty', '').strip()
        if not qty:
            errors.append(ValidationError(
                line_number=line_num,
                severity=ValidationError.ERROR,
                field='QTY',
                message="Quantity is empty",
                current_value=None,
                suggested_fix='1'
            ))
        elif not self._is_numeric(qty):
            errors.append(ValidationError(
                line_number=line_num,
                severity=ValidationError.ERROR,
                field='QTY',
                message=f"Quantity '{qty}' is not numeric",
                current_value=qty,
                suggested_fix='1'
            ))
        elif float(qty) <= 0:
            errors.append(ValidationError(
                line_number=line_num,
                severity=ValidationError.WARNING,
                field='QTY',
                message=f"Quantity '{qty}' is zero or negative",
                current_value=qty,
                suggested_fix='1'
            ))
        elif float(qty) > 9999:
            errors.append(ValidationError(
                line_number=line_num,
                severity=ValidationError.WARNING,
                field='QTY',
                message=f"Quantity '{qty}' seems unusually high",
                current_value=qty
            ))

        # Validate Material description
        material_desc = material.get('material', '').strip()
        if not material_desc:
            errors.append(ValidationError(
                line_number=line_num,
                severity=ValidationError.WARNING,
                field='MATERIAL',
                message="Material description is empty",
                current_value=None
            ))
        elif len(material_desc) > 100:
            errors.append(ValidationError(
                line_number=line_num,
                severity=ValidationError.INFO,
                field='MATERIAL',
                message=f"Material description is very long ({len(material_desc)} chars, may be truncated)",
                current_value=material_desc,
                suggested_fix=material_desc[:100]
            ))

        # Validate Length
        length = material.get('length', '').strip()
        if length and not self._is_valid_length(length):
            errors.append(ValidationError(
                line_number=line_num,
                severity=ValidationError.INFO,
                field='LENGTH',
                message=f"Length format '{length}' may be invalid",
                current_value=length
            ))

        return errors

    def _is_numeric(self, value: str) -> bool:
        """Check if value is numeric"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def _is_valid_length(self, length: str) -> bool:
        """
        Validate length format
        Expected: XX-XX-XX or numbers
        """
        if not length:
            return True  # Empty is ok

        # Pattern: 12-6-0 or 12 or 12-6
        pattern = r'^\d+(-\d+)*$'
        return bool(re.match(pattern, length))

    def _find_similar_sku(self, sku: str) -> Optional[str]:
        """
        Find similar SKU in products file (fuzzy match)
        Uses simple string similarity
        """
        if not self.valid_skus:
            return None

        sku_upper = sku.upper()

        # Exact match (case-insensitive)
        for valid_sku in self.valid_skus:
            if valid_sku.upper() == sku_upper:
                return valid_sku

        # Partial match - SKU starts with same prefix
        prefix = sku_upper[:5] if len(sku_upper) >= 5 else sku_upper
        matches = [s for s in self.valid_skus if s.upper().startswith(prefix)]

        if matches:
            return matches[0]  # Return first match

        # Find SKUs with similar characters
        # This is a simple similarity check
        max_score = 0
        best_match = None

        for valid_sku in list(self.valid_skus)[:100]:  # Check first 100 to avoid slowness
            score = self._similarity_score(sku_upper, valid_sku.upper())
            if score > max_score and score > 0.7:  # 70% similarity threshold
                max_score = score
                best_match = valid_sku

        return best_match

    def _similarity_score(self, str1: str, str2: str) -> float:
        """
        Simple similarity score between two strings
        Returns value 0-1
        """
        if not str1 or not str2:
            return 0.0

        # Count matching characters
        matches = sum(1 for a, b in zip(str1, str2) if a == b)
        max_len = max(len(str1), len(str2))

        return matches / max_len if max_len > 0 else 0.0

    def get_validation_summary(self, errors: List[ValidationError]) -> Dict:
        """
        Get summary of validation results

        Returns dict with counts of errors, warnings, info
        """
        summary = {
            'total': len(errors),
            'errors': 0,
            'warnings': 0,
            'info': 0,
            'can_upload': True
        }

        for error in errors:
            if error.severity == ValidationError.ERROR:
                summary['errors'] += 1
            elif error.severity == ValidationError.WARNING:
                summary['warnings'] += 1
            elif error.severity == ValidationError.INFO:
                summary['info'] += 1

        # Can only upload if no errors
        summary['can_upload'] = summary['errors'] == 0

        return summary

    def auto_fix_errors(self, csv_path: Path, errors: List[ValidationError]) -> Path:
        """
        Apply auto-fixes to CSV and save as new file

        Args:
            csv_path: Original CSV path
            errors: List of errors with suggested fixes

        Returns:
            Path to fixed CSV file
        """
        try:
            processor = CSVProcessor()

            # Read original CSV
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()

            # Get materials
            materials = processor.get_material_lines(csv_path)

            # Create fixes map: line_number -> {field: fixed_value}
            fixes_map = {}
            for error in errors:
                if error.suggested_fix and not error.fixed:
                    if error.line_number not in fixes_map:
                        fixes_map[error.line_number] = {}
                    fixes_map[error.line_number][error.field] = error.suggested_fix
                    error.fixed = True

            # Apply fixes to materials
            for material in materials:
                line_num = material['line_number']
                if line_num in fixes_map:
                    for field, fix_value in fixes_map[line_num].items():
                        if field == 'SKU':
                            material['sku'] = fix_value
                        elif field == 'QTY':
                            material['qty'] = fix_value
                        elif field == 'MATERIAL':
                            material['material'] = fix_value

            # Rebuild CSV with fixes
            # Keep header lines (first 5 lines), then add fixed materials
            fixed_lines = lines[:5]  # Header lines

            # Add material header if not present
            if 'LABEL' not in fixed_lines[4]:
                fixed_lines.append("LABEL,LENGTH,SKU,MATERIAL,QTY REQ'D\n")

            # Add fixed materials
            for material in materials:
                line = f'{material["label"]},{material["length"]},{material["sku"]},"{material["material"]}",{material["qty"]}\n'
                fixed_lines.append(line)

            # Add EOF marker
            fixed_lines.append('<EOF>,,,,\n')

            # Save to new file
            fixed_path = csv_path.with_stem(csv_path.stem + '_cleaned')

            with open(fixed_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)

            logging.info(f"Created cleaned CSV: {fixed_path.name}")

            return fixed_path

        except Exception as e:
            logging.error(f"Error auto-fixing CSV: {e}")
            raise
