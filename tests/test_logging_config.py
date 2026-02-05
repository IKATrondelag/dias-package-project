"""
Tests for logging_config.py
Tests for logging configuration functionality.
"""

import pytest
import tempfile
import os
import logging
from pathlib import Path
from src.utils.logging_config import setup_logging, cleanup_old_logs, get_memory_usage, log_memory_usage


def _cleanup_logging_handlers():
    """Remove all handlers from root logger to release file handles."""
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)


class TestSetupLogging:
    """Tests for setup_logging function."""
    
    def test_setup_logging_creates_directory(self):
        """Test that setup_logging creates log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            try:
                log_file = setup_logging(log_dir=str(log_dir))
                assert log_dir.exists()
                assert log_file is not None
            finally:
                _cleanup_logging_handlers()
            
    def test_setup_logging_returns_log_file_path(self):
        """Test that setup_logging returns log file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            try:
                log_file = setup_logging(log_dir=str(log_dir))
                assert isinstance(log_file, Path)
                assert str(log_file).endswith('.log')
                assert 'dias_package_creator_' in str(log_file)
            finally:
                _cleanup_logging_handlers()
            
    def test_setup_logging_creates_log_file(self):
        """Test that log file is created after setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            try:
                log_file = setup_logging(log_dir=str(log_dir))
                
                # Trigger some logging
                logger = logging.getLogger("test_setup")
                logger.info("Test message")
                
                # File should exist
                assert os.path.exists(log_file)
            finally:
                _cleanup_logging_handlers()
            
    def test_setup_logging_with_custom_level(self):
        """Test setup_logging with custom log level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            try:
                log_file = setup_logging(log_dir=str(log_dir), log_level=logging.WARNING)
                assert log_file is not None
            finally:
                _cleanup_logging_handlers()


class TestCleanupOldLogs:
    """Tests for cleanup_old_logs function."""
    
    def test_cleanup_nonexistent_directory(self):
        """Test cleanup on non-existent directory doesn't raise."""
        # Should not raise
        cleanup_old_logs(log_dir="/nonexistent/path")
        
    def test_cleanup_empty_directory(self):
        """Test cleanup on empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            # Should not raise
            cleanup_old_logs(log_dir=str(log_dir))


class TestMemoryUsage:
    """Tests for memory usage functions."""
    
    def test_get_memory_usage_returns_tuple(self):
        """Test that get_memory_usage returns a tuple."""
        result = get_memory_usage()
        assert isinstance(result, tuple)
        assert len(result) == 2
        
    def test_get_memory_usage_returns_floats(self):
        """Test that get_memory_usage returns float values."""
        rss, vms = get_memory_usage()
        assert isinstance(rss, (int, float))
        assert isinstance(vms, (int, float))
        
    def test_log_memory_usage(self):
        """Test log_memory_usage function."""
        logger = logging.getLogger("test_memory")
        # Should not raise
        log_memory_usage(logger, "Test memory")

