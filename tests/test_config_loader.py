"""
Tests for config_loader.py
Tests for YAML configuration loading functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.utils.config_loader import ConfigLoader


class TestConfigLoader:
    """Tests for ConfigLoader class."""
    
    def test_init_default(self):
        """Test ConfigLoader initialization with no arguments."""
        loader = ConfigLoader()
        assert loader.config_path is None
        assert loader.config_data == {}
        
    def test_init_with_path(self):
        """Test ConfigLoader initialization with specific path."""
        loader = ConfigLoader(config_path="/some/path/config.yml")
        assert loader.config_path == "/some/path/config.yml"
        
    def test_load_defaults_no_file(self):
        """Test load_defaults when no config file exists."""
        loader = ConfigLoader(config_path="/nonexistent/path/config.yml")
        defaults = loader.load_defaults()
        assert defaults == {}
        
    def test_load_defaults_valid_yaml(self):
        """Test loading a valid YAML config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("""
metadata:
  package_type: SIP
  label: Test Package
  record_status: NEW
  archivist_organization: Test Archive
  creator_organization: Test Creator
  submission_agreement: SA-001
  start_date: "2024-01-01"
  end_date: "2024-12-31"

options:
  package_types:
    - SIP
    - AIP
    - DIP
""")
            config_path = f.name
            
        try:
            loader = ConfigLoader(config_path=config_path)
            defaults = loader.load_defaults()
            
            assert defaults['package_type'] == 'SIP'
            assert defaults['label'] == 'Test Package'
            assert defaults['record_status'] == 'NEW'
            assert defaults['archivist_organization'] == 'Test Archive'
            assert defaults['creator_organization'] == 'Test Creator'
            assert defaults['submission_agreement'] == 'SA-001'
            assert defaults['start_date'] == '2024-01-01'
            assert defaults['end_date'] == '2024-12-31'
            assert 'package_types_options' in defaults
            assert defaults['package_types_options'] == ['SIP', 'AIP', 'DIP']
        finally:
            os.unlink(config_path)
            
    def test_load_defaults_empty_yaml(self):
        """Test loading an empty YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("")
            config_path = f.name
            
        try:
            loader = ConfigLoader(config_path=config_path)
            defaults = loader.load_defaults()
            assert defaults == {}
        finally:
            os.unlink(config_path)
            
    def test_load_defaults_invalid_yaml(self):
        """Test loading an invalid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("{{invalid: yaml: content:")
            config_path = f.name
            
        try:
            loader = ConfigLoader(config_path=config_path)
            defaults = loader.load_defaults()
            # Should return empty dict on error, not raise
            assert defaults == {}
        finally:
            os.unlink(config_path)
            
    def test_load_defaults_stores_in_config_data(self):
        """Test that load_defaults stores data in config_data attribute."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("""
metadata:
  label: Test Label
""")
            config_path = f.name
            
        try:
            loader = ConfigLoader(config_path=config_path)
            defaults = loader.load_defaults()
            
            assert loader.config_data == defaults
            assert loader.config_data['label'] == 'Test Label'
        finally:
            os.unlink(config_path)
            
    def test_find_config_file_specific_path(self):
        """Test _find_config_file with specific path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("test: value")
            config_path = f.name
            
        try:
            loader = ConfigLoader(config_path=config_path)
            found = loader._find_config_file()
            assert found is not None
            assert str(found) == config_path
        finally:
            os.unlink(config_path)
            
    def test_find_config_file_missing_specific_path(self):
        """Test _find_config_file when specific path doesn't exist."""
        loader = ConfigLoader(config_path="/nonexistent/config.yml")
        found = loader._find_config_file()
        assert found is None
        
    def test_all_metadata_fields(self):
        """Test that all expected metadata fields are extracted."""
        all_fields = [
            'package_type', 'label', 'record_status',
            'archivist_organization', 'system_name', 'system_version', 'system_format',
            'creator_organization', 'producer_organization', 'producer_individual',
            'producer_software', 'submitter_organization', 'submitter_individual',
            'ipowner_organization', 'preservation_organization',
            'submission_agreement', 'related_aic_id', 'related_package_id', 'start_date', 'end_date'
        ]
        
        yaml_content = "metadata:\n"
        for field in all_fields:
            yaml_content += f"  {field}: test_{field}\n"
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            config_path = f.name
            
        try:
            loader = ConfigLoader(config_path=config_path)
            defaults = loader.load_defaults()
            
            for field in all_fields:
                assert field in defaults, f"Field {field} not found"
                assert defaults[field] == f"test_{field}"
        finally:
            os.unlink(config_path)


class TestConfigLoaderDefaultPaths:
    """Tests for default config file search paths."""
    
    def test_default_config_paths(self):
        """Test that DEFAULT_CONFIG_PATHS contains expected values."""
        expected = [
            'dias_config.yml',
            'dias_config.yaml',
            '.dias_config.yml',
            '.dias_config.yaml',
        ]
        assert ConfigLoader.DEFAULT_CONFIG_PATHS == expected
