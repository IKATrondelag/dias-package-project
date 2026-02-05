"""
Unit tests for platform utilities.
Tests cross-platform compatibility functions.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

from src.utils.platform_utils import (
    is_frozen,
    get_application_path,
    get_resource_path,
    get_user_data_dir,
    get_user_config_dir,
    get_user_log_dir,
    get_temp_dir,
    normalize_path,
    get_memory_usage,
    get_platform_info,
)


class TestPlatformUtils(unittest.TestCase):
    """Tests for platform utility functions."""
    
    def test_is_frozen(self):
        """Test is_frozen returns False in development mode."""
        # In test environment, we're not frozen
        self.assertFalse(is_frozen())
    
    def test_get_application_path(self):
        """Test get_application_path returns valid path."""
        app_path = get_application_path()
        self.assertIsInstance(app_path, Path)
        self.assertTrue(app_path.exists())
    
    def test_get_resource_path(self):
        """Test get_resource_path returns valid path."""
        # Test with a known file
        resource_path = get_resource_path('app.py')
        self.assertIsInstance(resource_path, Path)
        # In development, this should point to the actual file
        if not is_frozen():
            self.assertTrue(resource_path.exists())
    
    def test_get_user_data_dir(self):
        """Test get_user_data_dir returns platform-appropriate path."""
        data_dir = get_user_data_dir('test_app')
        self.assertIsInstance(data_dir, Path)
        
        if sys.platform == 'win32':
            # Windows: should be in APPDATA
            self.assertIn('test_app', str(data_dir))
        elif sys.platform == 'darwin':
            # macOS: should be in Library/Application Support
            self.assertIn('Library', str(data_dir))
            self.assertIn('Application Support', str(data_dir))
        else:
            # Linux: should be in home with dot prefix
            self.assertIn('.test_app', str(data_dir))
    
    def test_get_user_config_dir(self):
        """Test get_user_config_dir returns platform-appropriate path."""
        config_dir = get_user_config_dir('test_app')
        self.assertIsInstance(config_dir, Path)
        
        if sys.platform == 'win32':
            self.assertIn('test_app', str(config_dir))
        elif sys.platform == 'darwin':
            self.assertIn('Library', str(config_dir))
        else:
            # Linux: should use .config or XDG_CONFIG_HOME
            home = str(Path.home())
            self.assertTrue(str(config_dir).startswith(home))
    
    def test_get_user_log_dir(self):
        """Test get_user_log_dir returns platform-appropriate path."""
        log_dir = get_user_log_dir('test_app')
        self.assertIsInstance(log_dir, Path)
        
        if sys.platform == 'win32':
            self.assertIn('logs', str(log_dir))
        elif sys.platform == 'darwin':
            self.assertIn('Library', str(log_dir))
            self.assertIn('Logs', str(log_dir))
        else:
            self.assertIn('logs', str(log_dir))
    
    def test_get_temp_dir(self):
        """Test get_temp_dir returns valid temp directory."""
        temp_dir = get_temp_dir()
        self.assertIsInstance(temp_dir, Path)
        self.assertTrue(temp_dir.exists())
        self.assertTrue(temp_dir.is_dir())
    
    def test_normalize_path_forward_slashes(self):
        """Test normalize_path handles forward slashes."""
        result = normalize_path('path/to/file')
        self.assertIsInstance(result, str)
        # Result should be a valid path for current platform
        self.assertTrue(len(result) > 0)
    
    def test_normalize_path_mixed_slashes(self):
        """Test normalize_path handles mixed slashes."""
        result = normalize_path('path/to\\file')
        self.assertIsInstance(result, str)
    
    def test_get_memory_usage(self):
        """Test get_memory_usage returns tuple of numbers."""
        rss, vms = get_memory_usage()
        # Should return numeric values (int or float)
        self.assertIsInstance(rss, (int, float))
        self.assertIsInstance(vms, (int, float))
        # Memory values should be non-negative
        self.assertGreaterEqual(rss, 0)
        self.assertGreaterEqual(vms, 0)
    
    def test_get_platform_info(self):
        """Test get_platform_info returns expected keys."""
        info = get_platform_info()
        self.assertIsInstance(info, dict)
        
        expected_keys = [
            'system', 'release', 'version', 'machine', 
            'python_version', 'is_frozen', 'is_windows', 
            'is_macos', 'is_linux'
        ]
        
        for key in expected_keys:
            self.assertIn(key, info)
        
        # Check boolean flags match platform
        if sys.platform == 'win32':
            self.assertTrue(info['is_windows'])
            self.assertFalse(info['is_macos'])
            self.assertFalse(info['is_linux'])
        elif sys.platform == 'darwin':
            self.assertFalse(info['is_windows'])
            self.assertTrue(info['is_macos'])
            self.assertFalse(info['is_linux'])
        elif sys.platform.startswith('linux'):
            self.assertFalse(info['is_windows'])
            self.assertFalse(info['is_macos'])
            self.assertTrue(info['is_linux'])


class TestEnvConfigPlatform(unittest.TestCase):
    """Tests for environment config platform awareness."""
    
    def test_log_directory_is_platform_aware(self):
        """Test that log directory uses platform-appropriate location."""
        from src.utils.env_config import AppConfig
        
        log_dir = AppConfig.get_log_directory()
        self.assertIsInstance(log_dir, Path)
        
        # Log directory path should be absolute
        self.assertTrue(log_dir.is_absolute())


if __name__ == '__main__':
    unittest.main()
