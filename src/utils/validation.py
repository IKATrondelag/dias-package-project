"""
Validation utilities for DIAS Package Creator.
Handles input validation and disk space checking.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

from .env_config import config


class ValidationError:
    """Represents a validation error or warning."""
    
    def __init__(self, message: str, level: str = "ERROR", field: str = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message.
            level: Severity level (ERROR, WARNING, INFO).
            field: Field name that caused the error.
        """
        self.message = message
        self.level = level
        self.field = field
        
    def __str__(self):
        if self.field:
            return f"[{self.level}] {self.field}: {self.message}"
        return f"[{self.level}] {self.message}"
        
    def __repr__(self):
        return f"ValidationError(message='{self.message}', level='{self.level}', field='{self.field}')"


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.info: List[ValidationError] = []
        
    def add_error(self, message: str, field: str = None):
        """Add an error message."""
        self.errors.append(ValidationError(message, "ERROR", field))
        
    def add_warning(self, message: str, field: str = None):
        """Add a warning message."""
        self.warnings.append(ValidationError(message, "WARNING", field))
        
    def add_info(self, message: str, field: str = None):
        """Add an info message."""
        self.info.append(ValidationError(message, "INFO", field))
        
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0
        
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0
        
    def get_all_messages(self) -> List[str]:
        """Get all messages as strings."""
        messages = []
        messages.extend([str(e) for e in self.errors])
        messages.extend([str(w) for w in self.warnings])
        messages.extend([str(i) for i in self.info])
        return messages
        
    def get_error_messages(self) -> List[str]:
        """Get only error messages."""
        return [e.message for e in self.errors]
        
    def get_warning_messages(self) -> List[str]:
        """Get only warning messages."""
        return [w.message for w in self.warnings]


class InputValidator:
    """Validates input for package creation."""
    
    # Safety margin for disk space (from config)
    DISK_SPACE_SAFETY_MARGIN = config.DISK_SPACE_SAFETY_MARGIN
    
    # Estimated overhead factor for package creation (from config)
    PACKAGE_SIZE_MULTIPLIER = config.PACKAGE_SIZE_MULTIPLIER
    
    @staticmethod
    def validate_source_path(source_path: str) -> ValidationResult:
        """
        Validate source path exists and is accessible.
        
        Args:
            source_path: Path to validate.
            
        Returns:
            ValidationResult with any errors or warnings.
        """
        result = ValidationResult()
        
        if not source_path or not source_path.strip():
            result.add_error("Source path is required", "source_path")
            return result
            
        source = Path(source_path)
        
        if not source.exists():
            result.add_error(f"Source path does not exist: {source_path}", "source_path")
            return result
            
        if not os.access(source_path, os.R_OK):
            result.add_error(f"Source path is not readable: {source_path}", "source_path")
            return result
            
        # Check if source is empty
        if source.is_dir():
            try:
                items = list(source.rglob('*'))
                files = [f for f in items if f.is_file()]
                
                if not files:
                    result.add_warning("Source directory is empty", "source_path")
                else:
                    result.add_info(f"Source contains {len(files)} file(s)", "source_path")
                    
            except PermissionError:
                result.add_error(f"Permission denied accessing source directory", "source_path")
        else:
            # Single file
            file_size = source.stat().st_size
            result.add_info(f"Source file size: {file_size / (1024*1024):.2f} MB", "source_path")
            
        return result
        
    @staticmethod
    def validate_output_path(output_path: str) -> ValidationResult:
        """
        Validate output path exists and is writable.
        
        Args:
            output_path: Path to validate.
            
        Returns:
            ValidationResult with any errors or warnings.
        """
        result = ValidationResult()
        
        if not output_path or not output_path.strip():
            result.add_error("Output path is required", "output_path")
            return result
            
        output = Path(output_path)
        
        # If path doesn't exist, check parent directory
        if not output.exists():
            parent = output.parent
            if not parent.exists():
                result.add_error(f"Parent directory does not exist: {parent}", "output_path")
                return result
                
            if not os.access(parent, os.W_OK):
                result.add_error(f"Parent directory is not writable: {parent}", "output_path")
                return result
        else:
            # Path exists
            if not output.is_dir():
                result.add_error(f"Output path is not a directory: {output_path}", "output_path")
                return result
                
            if not os.access(output_path, os.W_OK):
                result.add_error(f"Output directory is not writable: {output_path}", "output_path")
                return result
                
        return result
        
    @staticmethod
    def calculate_source_size(source_path: str) -> int:
        """
        Calculate total size of source files in bytes.
        
        Args:
            source_path: Path to source file or directory.
            
        Returns:
            Total size in bytes.
        """
        source = Path(source_path)
        
        if not source.exists():
            return 0
            
        if source.is_file():
            return source.stat().st_size
        else:
            # Directory - sum all files
            try:
                total = 0
                for item in source.rglob('*'):
                    if item.is_file():
                        try:
                            total += item.stat().st_size
                        except (OSError, PermissionError):
                            # Skip files we can't access
                            continue
                return total
            except (OSError, PermissionError):
                return 0
                
    @staticmethod
    def get_disk_space(path: str) -> Tuple[int, int, int]:
        """
        Get disk space information for a path.
        
        Args:
            path: Path to check (file or directory).
            
        Returns:
            Tuple of (total, used, free) in bytes.
        """
        try:
            # Get the actual path or its parent if it doesn't exist
            check_path = Path(path)
            if not check_path.exists():
                check_path = check_path.parent
                while not check_path.exists() and check_path.parent != check_path:
                    check_path = check_path.parent
                    
            stat = shutil.disk_usage(str(check_path))
            return (stat.total, stat.used, stat.free)
        except (OSError, PermissionError):
            return (0, 0, 0)
            
    @staticmethod
    def validate_disk_space(source_path: str, output_path: str) -> ValidationResult:
        """
        Validate sufficient disk space for package creation.
        
        The package creation requires:
        1. Space for copying source files
        2. Space for XML metadata files
        3. Space for temporary SIP structure (uncompressed)
        4. Space for final tar archive
        
        This function estimates ~2.5x source size is needed for the complete process,
        plus a 20% safety margin.
        
        Args:
            source_path: Path to source files.
            output_path: Path where package will be created.
            
        Returns:
            ValidationResult with disk space check results.
        """
        result = ValidationResult()
        
        # Calculate source size
        source_size = InputValidator.calculate_source_size(source_path)
        
        if source_size == 0:
            result.add_warning("Could not determine source size", "disk_space")
            return result
            
        # Estimate required space (2.5x source + 20% safety margin)
        estimated_package_size = source_size * InputValidator.PACKAGE_SIZE_MULTIPLIER
        required_space = int(estimated_package_size * InputValidator.DISK_SPACE_SAFETY_MARGIN)
        
        # Get available disk space on output path
        total, used, free = InputValidator.get_disk_space(output_path)
        
        if total == 0:
            result.add_warning("Could not determine available disk space", "disk_space")
            return result
            
        # Convert to human-readable sizes
        source_mb = source_size / (1024 * 1024)
        required_mb = required_space / (1024 * 1024)
        required_gb = required_space / (1024 * 1024 * 1024)
        free_mb = free / (1024 * 1024)
        free_gb = free / (1024 * 1024 * 1024)
        
        result.add_info(f"Source size: {source_mb:.2f} MB", "disk_space")
        result.add_info(f"Estimated package size: {estimated_package_size / (1024*1024):.2f} MB", "disk_space")
        result.add_info(f"Required space (with safety margin): {required_gb:.2f} GB", "disk_space")
        result.add_info(f"Available space: {free_gb:.2f} GB", "disk_space")
        
        # Check if sufficient space
        if free < required_space:
            shortage = (required_space - free) / (1024 * 1024 * 1024)
            result.add_error(
                f"Insufficient disk space. Need {required_gb:.2f} GB but only {free_gb:.2f} GB available. "
                f"Short by {shortage:.2f} GB.",
                "disk_space"
            )
        elif free < required_space * 1.2:
            # Error if less than 1.2x required space (too risky)
            margin_needed = (required_space * 1.2) / (1024 * 1024 * 1024)
            result.add_error(
                f"Disk space too low for safe operation. Need at least {margin_needed:.2f} GB "
                f"but only {free_gb:.2f} GB available. Package creation may fail during tar archive creation.",
                "disk_space"
            )
        elif free < required_space * 1.5:
            # Warning if less than 1.5x required space
            result.add_warning(
                f"Low disk space. Recommended to have at least {(required_space * 1.5) / (1024*1024*1024):.2f} GB free. "
                f"Currently have {free_gb:.2f} GB available. Consider using a drive with more space.",
                "disk_space"
            )
        else:
            result.add_info("Sufficient disk space available", "disk_space")
            
        return result
        
    @staticmethod
    def validate_package_name(package_name: str) -> ValidationResult:
        """
        Validate package name.
        
        Args:
            package_name: Package name to validate.
            
        Returns:
            ValidationResult with any errors or warnings.
        """
        result = ValidationResult()
        
        if not package_name or not package_name.strip():
            result.add_error("Package name is required", "package_name")
            return result
            
        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        found_invalid = [c for c in invalid_chars if c in package_name]
        
        if found_invalid:
            result.add_error(
                f"Package name contains invalid characters: {', '.join(found_invalid)}",
                "package_name"
            )
            
        # Check length
        if len(package_name) > 255:
            result.add_error("Package name is too long (max 255 characters)", "package_name")
            
        return result
        
    @staticmethod
    def validate_metadata(metadata: Dict) -> ValidationResult:
        """
        Validate package metadata.
        
        Args:
            metadata: Metadata dictionary to validate.
            
        Returns:
            ValidationResult with any errors or warnings.
        """
        result = ValidationResult()
        
        # Required fields
        required_fields = {
            'label': 'Label/Title',
            'archivist_organization': 'Archivist Organization',
            'system_name': 'System/Software Name',
            'creator_organization': 'Creator Organization',
            'submission_agreement': 'Submission Agreement ID'
        }
        
        for field, display_name in required_fields.items():
            value = metadata.get(field)
            if not value or not str(value).strip():
                result.add_error(f"{display_name} is required", field)
                
        # Validate dates if present
        date_fields = ['start_date', 'end_date', 'transfer_date']
        for field in date_fields:
            value = metadata.get(field)
            if value and value.strip():
                # Basic ISO date format check (YYYY-MM-DD)
                if not InputValidator._is_valid_iso_date(value):
                    result.add_warning(
                        f"{field} should be in ISO format (YYYY-MM-DD)",
                        field
                    )
                    
        return result
        
    @staticmethod
    def _is_valid_iso_date(date_str: str) -> bool:
        """Check if string is a valid ISO date (YYYY-MM-DD)."""
        from datetime import datetime
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
        
    @staticmethod
    def validate_all(source_path: str, output_path: str, package_name: str, 
                     metadata: Dict) -> ValidationResult:
        """
        Perform all validations for package creation.
        
        Args:
            source_path: Path to source files.
            output_path: Path where package will be created.
            package_name: Name for the package.
            metadata: Package metadata dictionary.
            
        Returns:
            Combined ValidationResult with all validation checks.
        """
        combined = ValidationResult()
        
        # Validate source path
        source_result = InputValidator.validate_source_path(source_path)
        combined.errors.extend(source_result.errors)
        combined.warnings.extend(source_result.warnings)
        combined.info.extend(source_result.info)
        
        # Validate output path
        output_result = InputValidator.validate_output_path(output_path)
        combined.errors.extend(output_result.errors)
        combined.warnings.extend(output_result.warnings)
        combined.info.extend(output_result.info)
        
        # Validate disk space (only if source and output are valid)
        if source_result.is_valid() and output_result.is_valid():
            space_result = InputValidator.validate_disk_space(source_path, output_path)
            combined.errors.extend(space_result.errors)
            combined.warnings.extend(space_result.warnings)
            combined.info.extend(space_result.info)
        
        # Validate package name
        name_result = InputValidator.validate_package_name(package_name)
        combined.errors.extend(name_result.errors)
        combined.warnings.extend(name_result.warnings)
        combined.info.extend(name_result.info)
        
        # Validate metadata
        metadata_result = InputValidator.validate_metadata(metadata)
        combined.errors.extend(metadata_result.errors)
        combined.warnings.extend(metadata_result.warnings)
        combined.info.extend(metadata_result.info)
        
        return combined
