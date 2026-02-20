"""
Logging configuration for DIAS Package Creator.
Sets up file and console logging with appropriate levels.
"""

import logging
import logging.handlers
import uuid
from datetime import datetime
from pathlib import Path

from .env_config import config


class CorrelationIdFilter(logging.Filter):
    """
    Injects a correlation ID into log records.
    """
    def __init__(self, name=''):
        super().__init__(name)
        self.correlation_id = str(uuid.uuid4())

    def filter(self, record):
        record.correlation_id = self.correlation_id
        return True


def setup_logging(log_dir=None, log_level=None):
    """
    Configure logging for the application.
    
    Args:
        log_dir: Directory for log files. Defaults to config value.
        log_level: Logging level. Defaults to config value.
    """
    # Determine log level from config if not provided
    if log_level is None:
        log_level = getattr(logging, config.LOG_LEVEL, logging.DEBUG)
    
    # Determine log directory from config if not provided
    if log_dir is None:
        log_dir = config.get_log_directory()
    else:
        log_dir = Path(log_dir)
    
    # Create log directory
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'dias_package_creator_{timestamp}.log'
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Add correlation ID filter
    correlation_filter = CorrelationIdFilter()
    
    # File handler - detailed logging with rotation (10 MB max, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.addFilter(correlation_filter)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [CorrID: %(correlation_id)s] - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler - less verbose
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.addFilter(correlation_filter)
    console_formatter = logging.Formatter(
        '%(levelname)s: [%(correlation_id)s] %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Log startup
    root_logger.info("="*70)
    root_logger.info("DIAS Package Creator - Logging Started")
    root_logger.info(f"Log file: {log_file}")
    root_logger.info(f"Log level: {logging.getLevelName(log_level)}")
    root_logger.info("="*70)
    
    return log_file


def cleanup_old_logs(log_dir=None, max_age_days=None, max_files=None):
    """
    Clean up old log files.
    
    Args:
        log_dir: Directory containing log files
        max_age_days: Maximum age of log files in days (from config if not provided)
        max_files: Maximum number of log files to keep (from config if not provided)
    """
    if log_dir is None:
        log_dir = config.get_log_directory()
    else:
        log_dir = Path(log_dir)
    
    if max_age_days is None:
        max_age_days = config.LOG_MAX_AGE_DAYS
    
    if max_files is None:
        max_files = config.LOG_MAX_FILES
    
    if not log_dir.exists():
        return
    
    logger = logging.getLogger(__name__)
    
    # Get all log files
    log_files = sorted(
        [f for f in log_dir.glob('dias_package_creator_*.log')],
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    
    removed = 0
    
    # Remove files older than max_age_days
    import time
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 60 * 60
    
    for log_file in log_files:
        file_age = current_time - log_file.stat().st_mtime
        if file_age > max_age_seconds:
            try:
                log_file.unlink()
                removed += 1
                logger.debug(f"Removed old log file: {log_file.name}")
            except Exception as e:
                logger.warning(f"Could not remove {log_file.name}: {e}")
    
    # Keep only max_files most recent logs
    if len(log_files) > max_files:
        for log_file in log_files[max_files:]:
            try:
                log_file.unlink()
                removed += 1
                logger.debug(f"Removed excess log file: {log_file.name}")
            except Exception as e:
                logger.warning(f"Could not remove {log_file.name}: {e}")
    
    if removed > 0:
        logger.info(f"Cleaned up {removed} old log files")


def get_memory_usage():
    """
    Get current memory usage of the process (cross-platform).
    
    Returns:
        Tuple of (rss_mb, vms_mb) - resident and virtual memory in MB
    """
    from .platform_utils import get_memory_usage as platform_get_memory_usage
    return platform_get_memory_usage()


def log_memory_usage(logger, message="Memory usage"):
    """
    Log current memory usage.
    
    Args:
        logger: Logger instance
        message: Message prefix
    """
    rss, vms = get_memory_usage()
    if rss > 0:
        logger.debug(f"{message}: RSS={rss:.2f} MB, VMS={vms:.2f} MB")
