"""
Unit tests for validation module.
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path

from src.utils.validation import (
    ValidationError,
    ValidationResult,
    InputValidator
)


class TestValidationError(unittest.TestCase):
    """Tests for ValidationError class."""
    
    def test_create_error(self):
        """Test creating a validation error."""
        error = ValidationError("Test error", "ERROR", "test_field")
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.level, "ERROR")
        self.assertEqual(error.field, "test_field")
        
    def test_string_representation(self):
        """Test string representation of error."""
        error = ValidationError("Test error", "ERROR", "test_field")
        self.assertEqual(str(error), "[ERROR] test_field: Test error")
        
        error_no_field = ValidationError("Test error", "ERROR")
        self.assertEqual(str(error_no_field), "[ERROR] Test error")


class TestValidationResult(unittest.TestCase):
    """Tests for ValidationResult class."""
    
    def test_empty_result_is_valid(self):
        """Test empty result is valid."""
        result = ValidationResult()
        self.assertTrue(result.is_valid())
        self.assertFalse(result.has_warnings())
        
    def test_add_error(self):
        """Test adding errors."""
        result = ValidationResult()
        result.add_error("Test error", "field1")
        
        self.assertFalse(result.is_valid())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].message, "Test error")
        
    def test_add_warning(self):
        """Test adding warnings."""
        result = ValidationResult()
        result.add_warning("Test warning", "field1")
        
        self.assertTrue(result.is_valid())  # Warnings don't affect validity
        self.assertTrue(result.has_warnings())
        self.assertEqual(len(result.warnings), 1)
        
    def test_get_messages(self):
        """Test getting messages."""
        result = ValidationResult()
        result.add_error("Error 1")
        result.add_warning("Warning 1")
        result.add_info("Info 1")
        
        all_messages = result.get_all_messages()
        self.assertEqual(len(all_messages), 3)
        
        error_messages = result.get_error_messages()
        self.assertEqual(len(error_messages), 1)
        self.assertEqual(error_messages[0], "Error 1")


class TestInputValidator(unittest.TestCase):
    """Tests for InputValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files and directories
        self.test_file = Path(self.test_dir) / "test_file.txt"
        self.test_file.write_text("Test content")
        
        self.test_subdir = Path(self.test_dir) / "subdir"
        self.test_subdir.mkdir()
        (self.test_subdir / "file1.txt").write_text("Content 1")
        (self.test_subdir / "file2.txt").write_text("Content 2")
        
        self.empty_dir = Path(self.test_dir) / "empty"
        self.empty_dir.mkdir()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
        
    def test_validate_source_path_valid_file(self):
        """Test validating a valid source file."""
        result = InputValidator.validate_source_path(str(self.test_file))
        self.assertTrue(result.is_valid())
        
    def test_validate_source_path_valid_directory(self):
        """Test validating a valid source directory."""
        result = InputValidator.validate_source_path(str(self.test_subdir))
        self.assertTrue(result.is_valid())
        
    def test_validate_source_path_empty_directory(self):
        """Test validating an empty directory."""
        result = InputValidator.validate_source_path(str(self.empty_dir))
        self.assertTrue(result.is_valid())  # Valid but has warning
        self.assertTrue(result.has_warnings())
        
    def test_validate_source_path_missing(self):
        """Test validating a missing source path."""
        result = InputValidator.validate_source_path("/nonexistent/path")
        self.assertFalse(result.is_valid())
        self.assertTrue(any("does not exist" in e.message for e in result.errors))
        
    def test_validate_source_path_empty_string(self):
        """Test validating an empty string."""
        result = InputValidator.validate_source_path("")
        self.assertFalse(result.is_valid())
        self.assertTrue(any("required" in e.message for e in result.errors))
        
    def test_validate_output_path_valid(self):
        """Test validating a valid output path."""
        result = InputValidator.validate_output_path(str(self.test_dir))
        self.assertTrue(result.is_valid())
        
    def test_validate_output_path_missing(self):
        """Test validating output path that doesn't exist."""
        new_path = str(Path(self.test_dir) / "new_output")
        result = InputValidator.validate_output_path(new_path)
        # Should be valid if parent exists
        self.assertTrue(result.is_valid())
        
    def test_validate_output_path_empty(self):
        """Test validating empty output path."""
        result = InputValidator.validate_output_path("")
        self.assertFalse(result.is_valid())
        
    def test_calculate_source_size_file(self):
        """Test calculating size of a single file."""
        size = InputValidator.calculate_source_size(str(self.test_file))
        self.assertEqual(size, len("Test content"))
        
    def test_calculate_source_size_directory(self):
        """Test calculating size of a directory."""
        size = InputValidator.calculate_source_size(str(self.test_subdir))
        expected = len("Content 1") + len("Content 2")
        self.assertEqual(size, expected)
        
    def test_calculate_source_size_nonexistent(self):
        """Test calculating size of nonexistent path."""
        size = InputValidator.calculate_source_size("/nonexistent/path")
        self.assertEqual(size, 0)
        
    def test_get_disk_space(self):
        """Test getting disk space information."""
        total, used, free = InputValidator.get_disk_space(str(self.test_dir))
        
        # Should return valid values
        self.assertGreater(total, 0)
        self.assertGreater(free, 0)
        self.assertGreater(used, 0)
        # Note: total may not exactly equal used + free due to filesystem overhead
        self.assertAlmostEqual(total, used + free, delta=total * 0.1)  # Within 10%
        
    def test_validate_disk_space_sufficient(self):
        """Test disk space validation with sufficient space."""
        # Use a small file that won't exceed disk space
        result = InputValidator.validate_disk_space(
            str(self.test_file),
            str(self.test_dir)
        )
        # Should pass (small file, plenty of space)
        self.assertTrue(result.is_valid())
        
    def test_validate_package_name_valid(self):
        """Test validating a valid package name."""
        result = InputValidator.validate_package_name("test_package_2024")
        self.assertTrue(result.is_valid())
        
    def test_validate_package_name_empty(self):
        """Test validating an empty package name."""
        result = InputValidator.validate_package_name("")
        self.assertFalse(result.is_valid())
        
    def test_validate_package_name_invalid_chars(self):
        """Test validating package name with invalid characters."""
        result = InputValidator.validate_package_name("test/package:name")
        self.assertFalse(result.is_valid())
        self.assertTrue(any("invalid characters" in e.message for e in result.errors))
        
    def test_validate_package_name_too_long(self):
        """Test validating package name that's too long."""
        long_name = "a" * 300
        result = InputValidator.validate_package_name(long_name)
        self.assertFalse(result.is_valid())
        self.assertTrue(any("too long" in e.message for e in result.errors))
        
    def test_validate_metadata_valid(self):
        """Test validating valid metadata."""
        metadata = {
            'label': 'Test Package',
            'archivist_organization': 'Test Archive',
            'system_name': 'Test System',
            'creator_organization': 'Test Creator',
            'submission_agreement': 'AGR-001'
        }
        result = InputValidator.validate_metadata(metadata)
        self.assertTrue(result.is_valid())
        
    def test_validate_metadata_missing_required(self):
        """Test validating metadata with missing required fields."""
        metadata = {
            'label': 'Test Package',
            # Missing other required fields
        }
        result = InputValidator.validate_metadata(metadata)
        self.assertFalse(result.is_valid())
        self.assertGreater(len(result.errors), 0)
        
    def test_validate_metadata_invalid_date(self):
        """Test validating metadata with invalid date format."""
        metadata = {
            'label': 'Test Package',
            'archivist_organization': 'Test Archive',
            'system_name': 'Test System',
            'creator_organization': 'Test Creator',
            'submission_agreement': 'AGR-001',
            'start_date': 'not-a-date'
        }
        result = InputValidator.validate_metadata(metadata)
        self.assertTrue(result.is_valid())  # Invalid date is a warning, not error
        self.assertTrue(result.has_warnings())
        
    def test_validate_metadata_valid_date(self):
        """Test validating metadata with valid ISO date."""
        metadata = {
            'label': 'Test Package',
            'archivist_organization': 'Test Archive',
            'system_name': 'Test System',
            'creator_organization': 'Test Creator',
            'submission_agreement': 'AGR-001',
            'start_date': '2024-01-15'
        }
        result = InputValidator.validate_metadata(metadata)
        self.assertTrue(result.is_valid())
        
    def test_validate_all_comprehensive(self):
        """Test comprehensive validation of all inputs."""
        metadata = {
            'label': 'Test Package',
            'archivist_organization': 'Test Archive',
            'system_name': 'Test System',
            'creator_organization': 'Test Creator',
            'submission_agreement': 'AGR-001'
        }
        
        result = InputValidator.validate_all(
            source_path=str(self.test_file),
            output_path=str(self.test_dir),
            package_name="test_package",
            metadata=metadata
        )
        
        # Should have info messages about disk space
        self.assertGreater(len(result.info), 0)
        
        # Should be valid overall
        self.assertTrue(result.is_valid())


if __name__ == '__main__':
    unittest.main()
