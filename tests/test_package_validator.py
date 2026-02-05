"""
Tests for DIAS Package Validator.
Tests PackageValidationResult and basic validator structure validation.
"""

import os
import shutil
import tempfile
import unittest

from src.dias_package_creator.package_validator import PackageValidationResult, DIASPackageValidator


class TestPackageValidationResult(unittest.TestCase):
    """Tests for PackageValidationResult container."""
    
    def test_empty_result_is_valid(self):
        """An empty result should be valid (no errors)."""
        result = PackageValidationResult()
        self.assertTrue(result.is_valid())
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 0)
        self.assertEqual(len(result.info), 0)
    
    def test_add_error(self):
        """Adding an error should make the result invalid."""
        result = PackageValidationResult()
        result.add_error("Missing file")
        self.assertFalse(result.is_valid())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0], "Missing file")
    
    def test_add_warning(self):
        """Adding a warning should not make the result invalid."""
        result = PackageValidationResult()
        result.add_warning("Optional field missing")
        self.assertTrue(result.is_valid())
        self.assertEqual(len(result.warnings), 1)
    
    def test_add_info(self):
        """Adding info should not affect validity."""
        result = PackageValidationResult()
        result.add_info("Processing started")
        self.assertTrue(result.is_valid())
        self.assertEqual(len(result.info), 1)
    
    def test_initial_counters(self):
        """Checksum counters should start at zero."""
        result = PackageValidationResult()
        self.assertEqual(result.checksums_verified, 0)
        self.assertEqual(result.checksums_failed, 0)
        self.assertEqual(result.files_checked, 0)
    
    def test_get_summary_valid(self):
        """Summary should show VALID when no errors."""
        result = PackageValidationResult()
        result.add_info("All good")
        summary = result.get_summary()
        self.assertIn("VALID", summary)
        self.assertIn("Errors: 0", summary)
    
    def test_get_summary_invalid(self):
        """Summary should show INVALID when errors exist."""
        result = PackageValidationResult()
        result.add_error("Missing info.xml")
        result.add_warning("Extra file found")
        summary = result.get_summary()
        self.assertIn("INVALID", summary)
        self.assertIn("Missing info.xml", summary)
        self.assertIn("Extra file found", summary)
    
    def test_get_summary_counters(self):
        """Summary should report checksum counters."""
        result = PackageValidationResult()
        result.checksums_verified = 5
        result.checksums_failed = 1
        result.files_checked = 10
        summary = result.get_summary()
        self.assertIn("Checksums Verified: 5", summary)
        self.assertIn("Checksums Failed: 1", summary)
        self.assertIn("Files Checked: 10", summary)


class TestDIASPackageValidator(unittest.TestCase):
    """Tests for DIASPackageValidator."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_messages = []
        self.validator = DIASPackageValidator(
            log_callback=lambda msg, level="INFO": self.log_messages.append((msg, level))
        )
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_validate_nonexistent_path(self):
        """Validating a nonexistent path should produce an error."""
        result = self.validator.validate_package(os.path.join(self.temp_dir, "nonexistent"))
        self.assertFalse(result.is_valid())
        self.assertTrue(any("not found" in e.lower() for e in result.errors))
    
    def test_validate_empty_directory(self):
        """Validating an empty directory should produce structural errors."""
        result = self.validator.validate_package(self.temp_dir)
        self.assertFalse(result.is_valid())
        # Should report missing info.xml
        self.assertTrue(any("info.xml" in e.lower() for e in result.errors))
    
    def test_validate_missing_aip_directory(self):
        """A package with info.xml but no AIP subdirectory should report errors."""
        # Create minimal info.xml
        info_xml = os.path.join(self.temp_dir, "info.xml")
        with open(info_xml, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?><mets></mets>')
        
        result = self.validator.validate_package(self.temp_dir)
        self.assertFalse(result.is_valid())
    
    def test_export_validation_report(self):
        """Exporting a validation report should create a text file."""
        result = PackageValidationResult()
        result.add_info("Test validation")
        
        report_path = os.path.join(self.temp_dir, "report.txt")
        self.validator.export_validation_report(result, report_path)
        
        self.assertTrue(os.path.exists(report_path))
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("VALID", content)


if __name__ == '__main__':
    unittest.main()
