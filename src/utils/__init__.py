# DIAS Package Creator - Utilities Module
"""
Utility functions and classes for file processing.
"""

from .file_processor import FileProcessor
from .config_loader import ConfigLoader
from .logging_config import setup_logging, cleanup_old_logs, log_memory_usage, get_memory_usage
from .env_config import config, AppConfig
from .platform_utils import (
    is_frozen,
    get_application_path,
    get_resource_path,
    get_user_data_dir,
    get_user_config_dir,
    get_user_log_dir,
    get_platform_info,
    open_file_explorer,
)

__all__ = [
    'FileProcessor', 'ConfigLoader', 'setup_logging', 'cleanup_old_logs', 
    'log_memory_usage', 'get_memory_usage', 'config', 'AppConfig',
    'is_frozen', 'get_application_path', 'get_resource_path',
    'get_user_data_dir', 'get_user_config_dir', 'get_user_log_dir',
    'get_platform_info', 'open_file_explorer',
]
