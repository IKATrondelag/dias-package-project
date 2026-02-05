"""
File Processor for DIAS Package Creator.
Handles file operations: copying, checksums, mime-type detection.
"""

import hashlib
import mimetypes
import shutil
from pathlib import Path
from typing import Callable, Dict, Any, Optional, List

from .env_config import config


class FileProcessor:
    """
    Handles file processing operations for DIAS packages.
    - Recursive directory scanning
    - Secure file copying
    - Checksum calculation (MD5/SHA256)
    - MIME-type detection
    """
    
    # Chunk size for reading large files (from config)
    CHUNK_SIZE = config.FILE_PROCESSOR_CHUNK_SIZE
    
    def __init__(self):
        """Initialize the file processor."""
        # Initialize mimetypes
        mimetypes.init()
        
    def scan_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Recursively scan a directory and gather file information.
        
        Args:
            directory_path: Path to the directory to scan.
            
        Returns:
            List of file information dictionaries.
        """
        files_info = []
        root_path = Path(directory_path)
        
        if not root_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
            
        if root_path.is_file():
            # Single file
            info = self.analyze_file(str(root_path))
            if info:
                files_info.append(info)
        else:
            # Directory
            for file_path in root_path.rglob('*'):
                if file_path.is_file():
                    info = self.analyze_file(str(file_path))
                    if info:
                        # Store relative path
                        info['relative_path'] = str(file_path.relative_to(root_path))
                        files_info.append(info)
                        
        return files_info
        
    def analyze_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a single file and gather metadata.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Dictionary with file information, or None if file doesn't exist.
        """
        try:
            path = Path(file_path)
            
            if not path.exists() or not path.is_file():
                return None
                
            stat = path.stat()
            
            return {
                'id': f"FILE_{path.stem}_{hash(str(path)) & 0xFFFFFF:06x}",
                'name': path.name,
                'path': str(path),
                'relative_path': path.name,
                'size': stat.st_size,
                'mimetype': self.get_mimetype(str(path)),
                'created': stat.st_ctime,
                'modified': stat.st_mtime
            }
        except (OSError, IOError) as e:
            return None
            
    def copy_file(self, source: str, destination: str, 
                  preserve_metadata: bool = True) -> bool:
        """
        Copy a file to destination.
        
        Args:
            source: Source file path.
            destination: Destination file path.
            preserve_metadata: Whether to preserve file metadata.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Ensure destination directory exists
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if preserve_metadata:
                shutil.copy2(source, destination)
            else:
                shutil.copy(source, destination)
                
            return True
        except (OSError, IOError, shutil.Error) as e:
            return False
            
    def copy_with_checksum(self, source: str, destination: str,
                           algorithm: str = 'SHA256',
                           progress_callback: Optional[Callable[[float], None]] = None) -> Optional[Dict[str, Any]]:
        """
        Copy a file and calculate checksum simultaneously.
        
        Args:
            source: Source file path.
            destination: Destination file path.
            algorithm: Hash algorithm ('MD5', 'SHA256', 'SHA512').
            progress_callback: Optional callback for progress updates (0-1).
            
        Returns:
            Dictionary with file info including checksum, or None on failure.
        """
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return None
                
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Select hash algorithm
            if algorithm.upper() == 'MD5':
                hasher = hashlib.md5()
            elif algorithm.upper() == 'SHA512':
                hasher = hashlib.sha512()
            else:
                hasher = hashlib.sha256()
                algorithm = 'SHA256'
                
            file_size = source_path.stat().st_size
            bytes_copied = 0
            
            with open(source, 'rb') as src, open(destination, 'wb') as dst:
                while True:
                    chunk = src.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                        
                    hasher.update(chunk)
                    dst.write(chunk)
                    
                    bytes_copied += len(chunk)
                    
                    if progress_callback and file_size > 0:
                        progress_callback(bytes_copied / file_size)
                        
            # Preserve metadata
            shutil.copystat(source, destination)
            
            # Get file info
            file_info = self.analyze_file(destination)
            if file_info:
                file_info['checksum'] = hasher.hexdigest()
                file_info['checksumtype'] = algorithm.upper()
                file_info['original_path'] = str(source_path)
                
            return file_info
            
        except (OSError, IOError) as e:
            return None
            
    def calculate_checksum(self, file_path: str, algorithm: str = 'SHA256',
                           progress_callback: Optional[Callable[[float], None]] = None) -> Optional[str]:
        """
        Calculate checksum for a file.
        
        Args:
            file_path: Path to the file.
            algorithm: Hash algorithm ('MD5', 'SHA256', 'SHA512').
            progress_callback: Optional callback for progress updates.
            
        Returns:
            Hexadecimal checksum string, or None on failure.
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return None
                
            # Select hash algorithm
            if algorithm.upper() == 'MD5':
                hasher = hashlib.md5()
            elif algorithm.upper() == 'SHA512':
                hasher = hashlib.sha512()
            else:
                hasher = hashlib.sha256()
                
            file_size = path.stat().st_size
            bytes_read = 0
            
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                        
                    hasher.update(chunk)
                    bytes_read += len(chunk)
                    
                    if progress_callback and file_size > 0:
                        progress_callback(bytes_read / file_size)
                        
            return hasher.hexdigest()
            
        except (OSError, IOError) as e:
            return None
            
    def get_mimetype(self, file_path: str) -> str:
        """
        Detect MIME type for a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            MIME type string (defaults to 'application/octet-stream').
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'
        
    def get_directory_size(self, directory_path: str) -> int:
        """
        Calculate total size of a directory.
        
        Args:
            directory_path: Path to the directory.
            
        Returns:
            Total size in bytes.
        """
        total_size = 0
        path = Path(directory_path)
        
        if path.is_file():
            return path.stat().st_size
            
        for file_path in path.rglob('*'):
            if file_path.is_file():
                try:
                    total_size += file_path.stat().st_size
                except (OSError, IOError):
                    pass
                    
        return total_size
        
    def verify_checksum(self, file_path: str, expected_checksum: str,
                        algorithm: str = 'SHA256') -> bool:
        """
        Verify file integrity by comparing checksums.
        
        Args:
            file_path: Path to the file.
            expected_checksum: Expected checksum value.
            algorithm: Hash algorithm used.
            
        Returns:
            True if checksums match, False otherwise.
        """
        actual_checksum = self.calculate_checksum(file_path, algorithm)
        
        if actual_checksum is None:
            return False
            
        return actual_checksum.lower() == expected_checksum.lower()
        
    def copy_directory(self, source: str, destination: str,
                       calculate_checksums: bool = True,
                       progress_callback: Optional[Callable[[int, int, str], None]] = None) -> List[Dict[str, Any]]:
        """
        Copy an entire directory with optional checksum calculation.
        
        Args:
            source: Source directory path.
            destination: Destination directory path.
            calculate_checksums: Whether to calculate checksums.
            progress_callback: Optional callback (current, total, filename).
            
        Returns:
            List of file information dictionaries.
        """
        source_path = Path(source)
        dest_path = Path(destination)
        files_info = []
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")
            
        # Get all items for progress tracking
        all_items = list(source_path.rglob('*'))
        file_count = sum(1 for f in all_items if f.is_file())
        current = 0
        
        for item in all_items:
            rel_path = item.relative_to(source_path)
            dest_item = dest_path / rel_path
            
            if item.is_dir():
                # Create empty directories to preserve structure
                dest_item.mkdir(parents=True, exist_ok=True)
            elif item.is_file():
                if progress_callback:
                    progress_callback(current, file_count, str(rel_path))
                    
                if calculate_checksums:
                    file_info = self.copy_with_checksum(str(item), str(dest_item))
                else:
                    if self.copy_file(str(item), str(dest_item)):
                        file_info = self.analyze_file(str(dest_item))
                    else:
                        file_info = None
                        
                if file_info:
                    file_info['relative_path'] = str(rel_path)
                    files_info.append(file_info)
                    
                current += 1
                
        return files_info
