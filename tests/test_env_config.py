"""
Tests for environment configuration (AppConfig and helper functions).
"""

import os
import unittest

from src.utils.env_config import (
    get_env, get_env_int, get_env_float, get_env_bool, get_env_list,
    AppConfig, _get_package_version
)


class TestGetEnv(unittest.TestCase):
    """Tests for get_env helper."""
    
    def test_returns_default_when_not_set(self):
        key = 'DIAS_TEST_UNSET_VAR_12345'
        self.assertEqual(get_env(key, 'fallback'), 'fallback')
    
    def test_returns_env_value_when_set(self):
        key = 'DIAS_TEST_ENV_VAR'
        os.environ[key] = 'custom_value'
        try:
            self.assertEqual(get_env(key, 'fallback'), 'custom_value')
        finally:
            del os.environ[key]


class TestGetEnvInt(unittest.TestCase):
    """Tests for get_env_int helper."""
    
    def test_returns_default_when_not_set(self):
        self.assertEqual(get_env_int('DIAS_TEST_INT_UNSET', 42), 42)
    
    def test_parses_int_from_env(self):
        os.environ['DIAS_TEST_INT'] = '99'
        try:
            self.assertEqual(get_env_int('DIAS_TEST_INT', 0), 99)
        finally:
            del os.environ['DIAS_TEST_INT']
    
    def test_returns_default_on_invalid_int(self):
        os.environ['DIAS_TEST_INT_BAD'] = 'not_a_number'
        try:
            self.assertEqual(get_env_int('DIAS_TEST_INT_BAD', 42), 42)
        finally:
            del os.environ['DIAS_TEST_INT_BAD']


class TestGetEnvFloat(unittest.TestCase):
    """Tests for get_env_float helper."""
    
    def test_returns_default_when_not_set(self):
        self.assertAlmostEqual(get_env_float('DIAS_TEST_FLOAT_UNSET', 1.5), 1.5)
    
    def test_parses_float_from_env(self):
        os.environ['DIAS_TEST_FLOAT'] = '3.14'
        try:
            self.assertAlmostEqual(get_env_float('DIAS_TEST_FLOAT', 0.0), 3.14, places=2)
        finally:
            del os.environ['DIAS_TEST_FLOAT']


class TestGetEnvBool(unittest.TestCase):
    """Tests for get_env_bool helper."""
    
    def test_returns_default_when_not_set(self):
        self.assertFalse(get_env_bool('DIAS_TEST_BOOL_UNSET', False))
    
    def test_true_values(self):
        for val in ('true', 'True', '1', 'yes', 'on'):
            os.environ['DIAS_TEST_BOOL'] = val
            try:
                self.assertTrue(get_env_bool('DIAS_TEST_BOOL', False), f"Expected True for '{val}'")
            finally:
                del os.environ['DIAS_TEST_BOOL']
    
    def test_false_values(self):
        for val in ('false', '0', 'no', 'off', 'random'):
            os.environ['DIAS_TEST_BOOL'] = val
            try:
                self.assertFalse(get_env_bool('DIAS_TEST_BOOL', True), f"Expected False for '{val}'")
            finally:
                del os.environ['DIAS_TEST_BOOL']


class TestGetEnvList(unittest.TestCase):
    """Tests for get_env_list helper."""
    
    def test_returns_default_when_not_set(self):
        default = ['a', 'b']
        self.assertEqual(get_env_list('DIAS_TEST_LIST_UNSET', default), default)
    
    def test_parses_comma_separated(self):
        os.environ['DIAS_TEST_LIST'] = 'x,y,z'
        try:
            self.assertEqual(get_env_list('DIAS_TEST_LIST', []), ['x', 'y', 'z'])
        finally:
            del os.environ['DIAS_TEST_LIST']
    
    def test_strips_whitespace(self):
        os.environ['DIAS_TEST_LIST'] = ' a , b , c '
        try:
            self.assertEqual(get_env_list('DIAS_TEST_LIST', []), ['a', 'b', 'c'])
        finally:
            del os.environ['DIAS_TEST_LIST']


class TestAppConfig(unittest.TestCase):
    """Tests for AppConfig class."""
    
    def test_app_name_default(self):
        self.assertEqual(AppConfig.APP_NAME, 'DIAS Package Creator')
    
    def test_app_version_is_string(self):
        self.assertIsInstance(AppConfig.APP_VERSION, str)
        self.assertGreater(len(AppConfig.APP_VERSION), 0)
    
    def test_sha256_chunk_size_positive(self):
        self.assertGreater(AppConfig.SHA256_CHUNK_SIZE, 0)
    
    def test_disk_space_safety_margin_positive(self):
        self.assertGreater(AppConfig.DISK_SPACE_SAFETY_MARGIN, 0)
    
    def test_log_max_age_days_positive(self):
        self.assertGreater(AppConfig.LOG_MAX_AGE_DAYS, 0)
    
    def test_get_log_directory_returns_path(self):
        from pathlib import Path
        log_dir = AppConfig.get_log_directory()
        self.assertIsInstance(log_dir, Path)
    
    def test_default_organizations_are_lists(self):
        self.assertIsInstance(AppConfig.DEFAULT_ARCHIVIST_ORGANIZATIONS, list)
        self.assertIsInstance(AppConfig.DEFAULT_CREATOR_ORGANIZATIONS, list)
        self.assertIsInstance(AppConfig.DEFAULT_SYSTEM_NAMES, list)
        self.assertIsInstance(AppConfig.DEFAULT_CONTENT_FORMATS, list)


class TestGetPackageVersion(unittest.TestCase):
    """Tests for the _get_package_version helper."""
    
    def test_returns_string(self):
        version = _get_package_version()
        self.assertIsInstance(version, str)
        self.assertGreater(len(version), 0)
    
    def test_version_format(self):
        """Version should look like a semver string."""
        version = _get_package_version()
        # Should contain at least one dot (e.g., "1.0.0" or fallback "1.0.0")
        self.assertIn('.', version)


if __name__ == '__main__':
    unittest.main()
