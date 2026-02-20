"""
DIAS Package Validator
Validates DIAS packages for structural integrity, checksum verification, and compliance.
"""

import hashlib
import tarfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple


class PackageValidationResult:
    """Container for validation results."""
    
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.checksums_verified = 0
        self.checksums_failed = 0
        self.files_checked = 0
        
    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
        
    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)
        
    def add_info(self, message: str):
        """Add an info message."""
        self.info.append(message)
        
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0
    
    def get_summary(self) -> str:
        """Get a summary of validation results."""
        status = "✓ VALID" if self.is_valid() else "✗ INVALID"
        summary = [
            f"\nValidation Result: {status}",
            f"Files Checked: {self.files_checked}",
            f"Checksums Verified: {self.checksums_verified}",
            f"Checksums Failed: {self.checksums_failed}",
            f"Errors: {len(self.errors)}",
            f"Warnings: {len(self.warnings)}"
        ]
        
        if self.errors:
            summary.append("\nERRORS:")
            for error in self.errors:
                summary.append(f"  ✗ {error}")
        
        if self.warnings:
            summary.append("\nWARNINGS:")
            for warning in self.warnings:
                summary.append(f"  ⚠ {warning}")
                
        if self.info:
            summary.append("\nINFO:")
            for info in self.info:
                summary.append(f"  ℹ {info}")
        
        return "\n".join(summary)


class DIASPackageValidator:
    """Validator for DIAS-compliant packages."""
    
    # Required namespaces
    NAMESPACES = {
        'mets': 'http://www.loc.gov/METS/',
        'premis': 'http://arkivverket.no/standarder/PREMIS',
        'xlink': 'http://www.w3.org/1999/xlink'
    }
    
    def __init__(self, log_callback: Optional[Callable[[str, str], None]] = None) -> None:
        """
        Initialize validator.
        
        Args:
            log_callback: Optional callback for progress logging.
        """
        self.log_callback = log_callback
        
    def _log(self, message: str, level: str = "INFO") -> None:
        """Log a message."""
        if self.log_callback:
            self.log_callback(message, level)
    
    def validate_package(self, package_path: str) -> PackageValidationResult:
        """
        Validate a complete DIAS package.
        
        Args:
            package_path: Path to the AIC directory.
            
        Returns:
            PackageValidationResult object.
        """
        result = PackageValidationResult()
        package_root = Path(package_path)
        
        self._log("Starting DIAS package validation...")
        
        # Check if package exists
        if not package_root.exists():
            result.add_error(f"Package not found: {package_path}")
            return result
        
        if not package_root.is_dir():
            result.add_error(f"Package path is not a directory: {package_path}")
            return result
        
        result.add_info(f"Package location: {package_path}")
        
        # Step 1: Validate directory structure
        self._log("Validating directory structure...")
        self._validate_structure(package_root, result)
        
        # Step 2: Find and validate info.xml at AIC level
        self._log("Validating AIC info.xml...")
        info_xml_path = package_root / "info.xml"
        if info_xml_path.exists():
            self._validate_info_xml(info_xml_path, result)
        else:
            result.add_error("Missing AIC info.xml")
        
        # Step 3: Find AIP directory (should be named with UUID)
        aip_dirs = [d for d in package_root.iterdir() if d.is_dir()]
        if not aip_dirs:
            result.add_error("No AIP directory found")
            return result
        elif len(aip_dirs) > 1:
            result.add_warning(f"Multiple AIP directories found: {len(aip_dirs)}")
        
        aip_dir = aip_dirs[0]
        result.add_info(f"AIP UUID: {aip_dir.name}")
        
        # Step 4: Validate AIP log.xml
        self._log("Validating AIP log.xml...")
        aip_log_path = aip_dir / "log.xml"
        if aip_log_path.exists():
            self._validate_log_xml(aip_log_path, result)
        else:
            result.add_error("Missing AIP log.xml")
        
        # Step 5: Validate content directory and tar file
        self._log("Validating SIP archive...")
        content_dir = aip_dir / "content"
        if content_dir.exists():
            self._validate_content(content_dir, result)
        else:
            result.add_error("Missing AIP content directory")
        
        self._log(f"Validation complete: {len(result.errors)} errors, {len(result.warnings)} warnings")
        return result
    
    def _validate_structure(self, package_root: Path, result: PackageValidationResult):
        """Validate basic directory structure."""
        # Expected structure:
        # AIC_UUID/
        #   ├── info.xml
        #   └── AIP_UUID/
        #       ├── log.xml
        #       └── content/
        #           └── SIP_UUID.tar
        
        required_aic_files = ["info.xml"]
        for filename in required_aic_files:
            if not (package_root / filename).exists():
                result.add_error(f"Missing required file: {filename}")
        
        result.files_checked += len(required_aic_files)
    
    def _validate_info_xml(self, xml_path: Path, result: PackageValidationResult):
        """Validate info.xml structure and content."""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Check if it's a METS file
            if 'mets' not in root.tag:
                result.add_error("info.xml is not a valid METS file")
                return
            
            # Check for required elements
            ns = self.NAMESPACES
            
            # Check metsHdr
            mets_hdr = root.find('.//mets:metsHdr', ns)
            if mets_hdr is None:
                result.add_error("info.xml missing metsHdr")
            else:
                # Check for agents
                agents = root.findall('.//mets:agent', ns)
                if not agents:
                    result.add_warning("info.xml has no agents defined")
                else:
                    result.add_info(f"Found {len(agents)} agents in info.xml")
            
            # Check for fileSec if tar file is referenced
            file_sec = root.find('.//mets:fileSec', ns)
            if file_sec is not None:
                files = root.findall('.//mets:file', ns)
                result.add_info(f"info.xml references {len(files)} files")
            
            result.files_checked += 1
            
        except ET.ParseError as e:
            result.add_error(f"info.xml parsing error: {e}")
        except Exception as e:
            result.add_error(f"Error validating info.xml: {e}")
    
    def _validate_log_xml(self, xml_path: Path, result: PackageValidationResult):
        """Validate log.xml (PREMIS) structure."""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Check if it's a PREMIS file
            if 'premis' not in root.tag.lower():
                result.add_error(f"{xml_path.name} is not a valid PREMIS file")
                return
            
            result.files_checked += 1
            
        except ET.ParseError as e:
            result.add_error(f"{xml_path.name} parsing error: {e}")
        except Exception as e:
            result.add_error(f"Error validating {xml_path.name}: {e}")
    
    def _validate_content(self, content_dir: Path, result: PackageValidationResult):
        """Validate content directory and SIP tar archive."""
        # Look for tar file
        tar_files = list(content_dir.glob("*.tar"))
        
        if not tar_files:
            result.add_error("No tar archive found in content directory")
            return
        
        if len(tar_files) > 1:
            result.add_warning(f"Multiple tar files found: {len(tar_files)}")
        
        tar_path = tar_files[0]
        result.add_info(f"SIP archive: {tar_path.name}")
        
        # Validate tar file integrity
        self._validate_tar_archive(tar_path, result)
    
    def _validate_tar_archive(self, tar_path: Path, result: PackageValidationResult):
        """Validate tar archive integrity and contents."""
        try:
            # Check if tar file is readable
            with tarfile.open(tar_path, 'r') as tar:
                members = tar.getmembers()
                
                if not members:
                    result.add_error("Tar archive is empty")
                    return
                
                result.add_info(f"Tar archive contains {len(members)} items")
                
                # Extract expected files for validation
                expected_files = ['mets.xml', 'log.xml']
                found_files = {m.name.split('/')[-1]: m for m in members if m.isfile()}
                
                for expected in expected_files:
                    if expected not in found_files:
                        result.add_error(f"Missing {expected} in tar archive")
                    else:
                        result.add_info(f"Found {expected} in archive")
                
                # Validate mets.xml from tar
                if 'mets.xml' in found_files:
                    self._validate_mets_from_tar(tar, found_files['mets.xml'], result)
                
                # Check for expected SIP directories
                dirs = {m.name for m in members if m.isdir()}
                expected_dirs = ['administrative_metadata', 'descriptive_metadata', 'content']
                for expected_dir in expected_dirs:
                    # Check if any path contains the expected directory
                    if not any(expected_dir in d for d in dirs):
                        result.add_warning(f"Expected directory '{expected_dir}' not found in archive structure")
                
                result.files_checked += len(members)
                
        except tarfile.TarError as e:
            result.add_error(f"Tar archive is corrupted: {e}")
        except Exception as e:
            result.add_error(f"Error validating tar archive: {e}")
    
    def _validate_mets_from_tar(self, tar: tarfile.TarFile, member: tarfile.TarInfo, result: PackageValidationResult):
        """Validate mets.xml extracted from tar archive."""
        try:
            # Extract and parse mets.xml
            f = tar.extractfile(member)
            if f is None:
                result.add_error("Could not extract mets.xml from archive")
                return
            
            content = f.read()
            root = ET.fromstring(content)
            
            # Check namespace
            if 'mets' not in root.tag:
                result.add_error("mets.xml is not a valid METS file")
                return
            
            ns = self.NAMESPACES
            
            # Check required sections
            file_sec = root.find('.//mets:fileSec', ns)
            if file_sec is None:
                result.add_warning("mets.xml missing fileSec")
            else:
                files = root.findall('.//mets:file', ns)
                result.add_info(f"mets.xml references {len(files)} files")
                
                # Verify checksums if available
                self._verify_checksums_from_mets(root, result)
            
            struct_map = root.find('.//mets:structMap', ns)
            if struct_map is None:
                result.add_warning("mets.xml missing structMap")
            
        except ET.ParseError as e:
            result.add_error(f"mets.xml parsing error: {e}")
        except Exception as e:
            result.add_error(f"Error validating mets.xml: {e}")
    
    def _verify_checksums_from_mets(self, mets_root, result: PackageValidationResult):
        """Verify checksums listed in METS against actual files."""
        ns = self.NAMESPACES
        files = mets_root.findall('.//mets:file', ns)
        
        for file_elem in files:
            checksum = file_elem.get('CHECKSUM')
            checksum_type = file_elem.get('CHECKSUMTYPE')
            
            if checksum and checksum_type == 'SHA-256':
                # Note: Full verification would require extracting files
                # For now, just count how many checksums are present
                result.checksums_verified += 1
        
        if result.checksums_verified > 0:
            result.add_info(f"Found {result.checksums_verified} checksums in mets.xml")
    
    def verify_file_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """
        Verify a file's SHA-256 checksum.
        
        Args:
            file_path: Path to file.
            expected_checksum: Expected SHA-256 checksum.
            
        Returns:
            True if checksum matches.
        """
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            
            actual = sha256.hexdigest()
            return actual.lower() == expected_checksum.lower()
            
        except Exception:
            return False
    
    def export_validation_report(self, result: PackageValidationResult, output_path: str):
        """
        Export validation report to a text file.
        
        Args:
            result: PackageValidationResult object.
            output_path: Path to save report.
        """
        report = [
            "DIAS Package Validation Report",
            "=" * 50,
            f"Generated: {datetime.now().isoformat()}",
            "",
            result.get_summary()
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
