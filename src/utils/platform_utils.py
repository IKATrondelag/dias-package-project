"""
Platform utilities for DIAS Package Creator.
Provides cross-platform compatibility functions for Windows, macOS, and Linux.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple


def is_frozen() -> bool:
    """
    Check if the application is running as a frozen executable (PyInstaller, cx_Freeze, etc.).
    
    Returns:
        True if running as frozen executable, False otherwise.
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_application_path() -> Path:
    """
    Get the application's base path, handling both development and frozen modes.
    
    In development: Returns the project root directory.
    When frozen: Returns the directory containing the executable.
    
    Returns:
        Path to the application base directory.
    """
    if is_frozen():
        # Running as frozen executable
        # sys._MEIPASS is the temp directory where PyInstaller extracts files
        # For the actual executable location, use sys.executable
        return Path(sys.executable).parent
    else:
        # Running in development mode
        return Path(__file__).parent.parent.parent


def get_resource_path(relative_path: str) -> Path:
    """
    Get the absolute path to a resource file, handling both development and frozen modes.
    
    When frozen with PyInstaller, resources are extracted to a temp directory (_MEIPASS).
    
    Args:
        relative_path: Path relative to the application root.
        
    Returns:
        Absolute path to the resource.
    """
    if is_frozen():
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent.parent
    
    return base_path / relative_path


def get_user_data_dir(app_name: str = "dias_package_creator") -> Path:
    """
    Get the appropriate user data directory for the current platform.
    
    Windows: %APPDATA%/app_name
    macOS: ~/Library/Application Support/app_name
    Linux: ~/.app_name
    
    Args:
        app_name: Name of the application (used as directory name).
        
    Returns:
        Path to user data directory.
    """
    if sys.platform == 'win32':
        # Windows: Use APPDATA environment variable
        appdata = os.environ.get('APPDATA')
        if appdata:
            return Path(appdata) / app_name
        else:
            return Path.home() / 'AppData' / 'Roaming' / app_name
    elif sys.platform == 'darwin':
        # macOS: Use Library/Application Support
        return Path.home() / 'Library' / 'Application Support' / app_name
    else:
        # Linux and others: Use hidden directory in home
        return Path.home() / f'.{app_name}'


def get_user_config_dir(app_name: str = "dias_package_creator") -> Path:
    """
    Get the appropriate user config directory for the current platform.
    
    Windows: %APPDATA%/app_name
    macOS: ~/Library/Preferences/app_name
    Linux: ~/.config/app_name
    
    Args:
        app_name: Name of the application.
        
    Returns:
        Path to user config directory.
    """
    if sys.platform == 'win32':
        appdata = os.environ.get('APPDATA')
        if appdata:
            return Path(appdata) / app_name
        else:
            return Path.home() / 'AppData' / 'Roaming' / app_name
    elif sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Preferences' / app_name
    else:
        # Linux: Use XDG_CONFIG_HOME or default to ~/.config
        xdg_config = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config:
            return Path(xdg_config) / app_name
        else:
            return Path.home() / '.config' / app_name


def get_user_log_dir(app_name: str = "dias_package_creator") -> Path:
    """
    Get the appropriate user log directory for the current platform.
    
    Windows: %APPDATA%/app_name/logs
    macOS: ~/Library/Logs/app_name
    Linux: ~/.local/share/app_name/logs or ~/.app_name/logs
    
    Args:
        app_name: Name of the application.
        
    Returns:
        Path to user log directory.
    """
    if sys.platform == 'win32':
        appdata = os.environ.get('APPDATA')
        if appdata:
            return Path(appdata) / app_name / 'logs'
        else:
            return Path.home() / 'AppData' / 'Roaming' / app_name / 'logs'
    elif sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Logs' / app_name
    else:
        # Linux: Use XDG_DATA_HOME or default
        xdg_data = os.environ.get('XDG_DATA_HOME')
        if xdg_data:
            return Path(xdg_data) / app_name / 'logs'
        else:
            return Path.home() / f'.{app_name}' / 'logs'


def get_temp_dir() -> Path:
    """
    Get a cross-platform temporary directory.
    
    Returns:
        Path to temp directory.
    """
    import tempfile
    return Path(tempfile.gettempdir())


def normalize_path(path: str) -> str:
    """
    Normalize a path string for the current platform.
    Converts forward/backward slashes to the appropriate separator.
    
    Args:
        path: Path string to normalize.
        
    Returns:
        Normalized path string.
    """
    return str(Path(path))


def get_memory_usage() -> Tuple[float, float]:
    """
    Get current memory usage of the process in a cross-platform way.
    
    Returns:
        Tuple of (rss_mb, vms_mb) - resident and virtual memory in MB.
        Returns (0, 0) if unable to determine.
    """
    # Try psutil first (works on all platforms if installed)
    try:
        import psutil
        process = psutil.Process()
        mem_info = process.memory_info()
        return (mem_info.rss / (1024 * 1024), mem_info.vms / (1024 * 1024))
    except ImportError:
        pass
    
    # Windows fallback using ctypes
    if sys.platform == 'win32':
        try:
            import ctypes
            from ctypes import wintypes
            
            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]
            
            GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
            GetProcessMemoryInfo = ctypes.windll.psapi.GetProcessMemoryInfo
            
            pmc = PROCESS_MEMORY_COUNTERS()
            pmc.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            
            if GetProcessMemoryInfo(GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
                return (pmc.WorkingSetSize / (1024 * 1024), pmc.PagefileUsage / (1024 * 1024))
        except Exception:
            pass
    
    # Unix fallback using resource module
    else:
        try:
            import resource
            import platform
            
            usage = resource.getrusage(resource.RUSAGE_SELF)
            # maxrss is in KB on Linux, bytes on macOS
            if platform.system() == 'Darwin':
                return (usage.ru_maxrss / (1024 * 1024), 0)
            else:
                return (usage.ru_maxrss / 1024, 0)
        except Exception:
            pass
    
    return (0, 0)


def open_file_explorer(path: str) -> bool:
    """
    Open a file explorer window at the specified path (cross-platform).
    
    Args:
        path: Directory path to open.
        
    Returns:
        True if successful, False otherwise.
    """
    import subprocess
    
    try:
        path = str(Path(path).resolve())
        
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.run(['open', path], check=True)
        else:
            # Linux - try common file managers
            subprocess.run(['xdg-open', path], check=True)
        
        return True
    except Exception:
        return False


def get_platform_info() -> dict:
    """
    Get information about the current platform.
    
    Returns:
        Dictionary with platform information.
    """
    import platform
    
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
        'is_frozen': is_frozen(),
        'is_windows': sys.platform == 'win32',
        'is_macos': sys.platform == 'darwin',
        'is_linux': sys.platform.startswith('linux'),
    }
