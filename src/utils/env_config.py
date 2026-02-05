"""
Environment configuration loader for DIAS Package Creator.
Loads configuration from .env file and provides defaults.
"""

import os
from pathlib import Path
from typing import Optional, List

# Import platform utilities (but handle circular import)
# platform_utils will be loaded later if needed
_platform_utils = None

def _get_platform_utils():
    """Lazy load platform_utils to avoid circular imports."""
    global _platform_utils
    if _platform_utils is None:
        from . import platform_utils as pu
        _platform_utils = pu
    return _platform_utils


def _load_env_file():
    """Load .env file if it exists."""
    import sys
    
    # Determine base paths for .env file search
    env_paths = [
        Path.cwd() / '.env',
        Path(__file__).parent.parent.parent / '.env',
    ]
    
    # Add platform-specific user config directory
    if sys.platform == 'win32':
        appdata = os.environ.get('APPDATA')
        if appdata:
            env_paths.append(Path(appdata) / 'dias_package_creator' / '.env')
    elif sys.platform == 'darwin':
        env_paths.append(Path.home() / 'Library' / 'Preferences' / 'dias_package_creator' / '.env')
    else:
        xdg_config = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config:
            env_paths.append(Path(xdg_config) / 'dias_package_creator' / '.env')
        else:
            env_paths.append(Path.home() / '.config' / 'dias_package_creator' / '.env')
        # Also check legacy location
        env_paths.append(Path.home() / '.dias_package_creator' / '.env')
    
    for env_path in env_paths:
        if env_path.exists():
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, _, value = line.partition('=')
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key and key not in os.environ:
                                os.environ[key] = value
                return True
            except Exception:
                pass
    return False


# Load .env file on module import
_load_env_file()


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable with optional default."""
    return os.environ.get(key, default)


def get_env_int(key: str, default: int) -> int:
    """Get environment variable as integer."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_env_float(key: str, default: float) -> float:
    """Get environment variable as float."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def get_env_list(key: str, default: Optional[List[str]] = None) -> List[str]:
    """Get environment variable as comma-separated list."""
    value = os.environ.get(key)
    if value is None:
        return default or []
    return [item.strip() for item in value.split(',') if item.strip()]


def get_env_bool(key: str, default: bool) -> bool:
    """Get environment variable as boolean."""
    value = os.environ.get(key)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')


def _get_package_version() -> str:
    """Get version from pyproject.toml via importlib.metadata, with fallback."""
    try:
        from importlib.metadata import version
        return version('dias-package-creator')
    except Exception:
        return '1.0.0'


class AppConfig:
    """Application configuration from environment variables."""
    
    # Application settings
    APP_NAME = get_env('APP_NAME', 'DIAS Package Creator')
    APP_VERSION = get_env('APP_VERSION', _get_package_version())
    APP_AUTHOR = get_env('APP_AUTHOR', 'DIAS Package Creator Team')
    
    # DIAS/PREMIS metadata defaults
    PRESERVATION_PLATFORM = get_env('PRESERVATION_PLATFORM', 'Preservation platform ESSArch')
    CHECKSUM_ORIGINATOR = get_env('CHECKSUM_ORIGINATOR', 'ESSArch')
    LINKING_AGENT = get_env('LINKING_AGENT', 'ESSArch')
    LOG_CREATION_EVENT_TYPE = get_env('LOG_CREATION_EVENT_TYPE', '10000')
    
    # Schema locations
    METS_INFO_SCHEMA_LOCATION = get_env(
        'METS_INFO_SCHEMA_LOCATION',
        'http://www.loc.gov/METS/ http://schema.arkivverket.no/METS/info.xsd'
    )
    METS_SIP_SCHEMA_LOCATION = get_env(
        'METS_SIP_SCHEMA_LOCATION',
        'http://www.loc.gov/METS/ http://schema.arkivverket.no/METS/mets.xsd'
    )
    METS_PROFILE = get_env('METS_PROFILE', 'http://xml.ra.se/METS/RA_METS_eARD.xml')
    PREMIS_SCHEMA_LOCATION = get_env(
        'PREMIS_SCHEMA_LOCATION',
        'http://arkivverket.no/standarder/PREMIS http://schema.arkivverket.no/PREMIS/v2.0/DIAS_PREMIS.xsd'
    )
    PREMIS_VERSION = get_env('PREMIS_VERSION', '2.0')
    OBJECT_IDENTIFIER_TYPE = get_env('OBJECT_IDENTIFIER_TYPE', 'NO/RA')
    
    # File processing settings
    DISK_SPACE_SAFETY_MARGIN = get_env_float('DISK_SPACE_SAFETY_MARGIN', 1.5)
    PACKAGE_SIZE_MULTIPLIER = get_env_float('PACKAGE_SIZE_MULTIPLIER', 3.0)
    SHA256_CHUNK_SIZE = get_env_int('SHA256_CHUNK_SIZE', 65536)
    FILE_PROCESSOR_CHUNK_SIZE = get_env_int('FILE_PROCESSOR_CHUNK_SIZE', 8 * 1024 * 1024)
    
    # Logging settings
    LOG_DIRECTORY = get_env('LOG_DIRECTORY', '')
    LOG_LEVEL = get_env('LOG_LEVEL', 'DEBUG')
    LOG_MAX_AGE_DAYS = get_env_int('LOG_MAX_AGE_DAYS', 30)
    LOG_MAX_FILES = get_env_int('LOG_MAX_FILES', 50)
    
    # GUI default values
    DEFAULT_ARCHIVIST_ORGANIZATIONS = get_env_list(
        'DEFAULT_ARCHIVIST_ORGANIZATIONS',
        ['5014 Frøya Kommune', '5011 Hemne Kommune', '5045 Grong Kommune']
    )
    DEFAULT_CREATOR_ORGANIZATIONS = get_env_list(
        'DEFAULT_CREATOR_ORGANIZATIONS',
        ['IKA Trøndelag', 'IKA Oslo og Viken', 'IKA Hordaland', 'IKA Møre og Romsdal']
    )
    DEFAULT_SYSTEM_NAMES = get_env_list(
        'DEFAULT_SYSTEM_NAMES',
        ['Visma Familia', 'Acos', 'Elements', 'ePhorte', 'ESA', 'Public 360']
    )
    DEFAULT_CONTENT_FORMATS = get_env_list(
        'DEFAULT_CONTENT_FORMATS',
        ['SIARD', 'ADDML', 'NOARK-5', 'PDF/A', 'XML']
    )
    DEFAULT_PRESERVATION_ORGANIZATION = get_env('DEFAULT_PRESERVATION_ORGANIZATION', 'KDRS')
    
    @classmethod
    def get_log_directory(cls) -> Path:
        """Get the configured log directory path (platform-aware)."""
        if cls.LOG_DIRECTORY:
            return Path(cls.LOG_DIRECTORY)
        
        # Use platform-specific log directory
        try:
            pu = _get_platform_utils()
            return pu.get_user_log_dir('dias_package_creator')
        except ImportError:
            # Fallback if platform_utils not available
            import sys
            if sys.platform == 'win32':
                appdata = os.environ.get('APPDATA')
                if appdata:
                    return Path(appdata) / 'dias_package_creator' / 'logs'
                return Path.home() / 'AppData' / 'Roaming' / 'dias_package_creator' / 'logs'
            elif sys.platform == 'darwin':
                return Path.home() / 'Library' / 'Logs' / 'dias_package_creator'
            else:
                return Path.home() / '.dias_package_creator' / 'logs'


# Create singleton instance
config = AppConfig()
