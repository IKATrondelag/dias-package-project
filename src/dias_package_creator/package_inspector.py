"""
DIAS Package Inspector
Generates human-readable descriptions of DIAS packages by analyzing XML metadata.
"""

import tarfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional


class PackageDescription:
    """Container for package description information."""
    
    def __init__(self) -> None:
        self.aic_uuid: Optional[str] = None
        self.aip_uuid: Optional[str] = None
        self.sip_uuid: Optional[str] = None
        self.label: Optional[str] = None
        self.package_type: Optional[str] = None
        self.record_status: Optional[str] = None
        self.create_date: Optional[str] = None
        
        # Agents
        self.archivist: List[str] = []
        self.creator: List[str] = []
        self.producer: List[str] = []
        self.submitter: List[str] = []
        self.ipowner: List[str] = []
        self.preservation: List[str] = []
        
        # Alternative record IDs
        self.submission_agreement: Optional[str] = None
        self.start_date: Optional[str] = None
        self.end_date: Optional[str] = None
        
        # File information
        self.total_files: int = 0
        self.total_size: int = 0
        self.content_files: List[Dict] = []
        
        # Archive information
        self.archive_name: Optional[str] = None
        self.archive_size: int = 0
        self.archive_checksum: Optional[str] = None
        
    def format_size(self, size_bytes: int) -> str:
        """Format bytes as human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def get_summary(self) -> str:
        """Generate a human-readable summary of the package."""
        lines = []
        
        # Header
        lines.append("═" * 70)
        lines.append("DIAS PACKAGE DESCRIPTION")
        lines.append("═" * 70)
        lines.append("")
        
        # Basic Information
        lines.append("PACKAGE INFORMATION")
        lines.append("─" * 70)
        if self.label:
            lines.append(f"Title: {self.label}")
        if self.package_type:
            lines.append(f"Type: {self.package_type}")
        if self.record_status:
            lines.append(f"Status: {self.record_status}")
        if self.create_date:
            lines.append(f"Created: {self.create_date}")
        lines.append("")
        
        # UUIDs
        lines.append("IDENTIFIERS")
        lines.append("─" * 70)
        if self.aic_uuid:
            lines.append(f"AIC UUID: {self.aic_uuid}")
        if self.aip_uuid:
            lines.append(f"AIP UUID: {self.aip_uuid}")
        if self.sip_uuid:
            lines.append(f"SIP UUID: {self.sip_uuid}")
        lines.append("")
        
        # Agreement and Dates
        if self.submission_agreement or self.start_date or self.end_date:
            lines.append("AGREEMENT & COVERAGE")
            lines.append("─" * 70)
            if self.submission_agreement:
                lines.append(f"Submission Agreement: {self.submission_agreement}")
            if self.start_date and self.end_date:
                lines.append(f"Content Period: {self.start_date} to {self.end_date}")
            elif self.start_date:
                lines.append(f"Start Date: {self.start_date}")
            elif self.end_date:
                lines.append(f"End Date: {self.end_date}")
            lines.append("")
        
        # Agents
        if any([self.archivist, self.creator, self.producer, self.submitter, 
                self.ipowner, self.preservation]):
            lines.append("RESPONSIBLE PARTIES")
            lines.append("─" * 70)
            if self.archivist:
                lines.append(f"Archivist: {', '.join(self.archivist)}")
            if self.creator:
                lines.append(f"Creator: {', '.join(self.creator)}")
            if self.producer:
                lines.append(f"Producer: {', '.join(self.producer)}")
            if self.submitter:
                lines.append(f"Submitter: {', '.join(self.submitter)}")
            if self.ipowner:
                lines.append(f"IP Owner: {', '.join(self.ipowner)}")
            if self.preservation:
                lines.append(f"Preservation: {', '.join(self.preservation)}")
            lines.append("")
        
        # Archive Information
        if self.archive_name:
            lines.append("ARCHIVE")
            lines.append("─" * 70)
            lines.append(f"Archive File: {self.archive_name}")
            if self.archive_size:
                lines.append(f"Archive Size: {self.format_size(self.archive_size)}")
            if self.archive_checksum:
                lines.append(f"SHA-256: {self.archive_checksum}")
            lines.append("")
        
        # Content Summary
        if self.content_files or self.total_files:
            lines.append("CONTENT SUMMARY")
            lines.append("─" * 70)
            lines.append(f"Total Files: {self.total_files}")
            if self.total_size:
                lines.append(f"Total Size: {self.format_size(self.total_size)}")
            
            if self.content_files:
                lines.append("")
                lines.append("Content Files:")
                for i, file_info in enumerate(self.content_files[:20], 1):  # Show first 20
                    name = file_info.get('name', 'Unknown')
                    size = file_info.get('size', 0)
                    lines.append(f"  {i}. {name} ({self.format_size(size)})")
                
                if len(self.content_files) > 20:
                    lines.append(f"  ... and {len(self.content_files) - 20} more files")
            lines.append("")
        
        lines.append("═" * 70)
        
        return "\n".join(lines)


class DIASPackageInspector:
    """Inspector for analyzing DIAS package structure and metadata."""
    
    NAMESPACES = {
        'mets': 'http://www.loc.gov/METS/',
        'premis': 'http://arkivverket.no/standarder/PREMIS',
        'xlink': 'http://www.w3.org/1999/xlink'
    }
    
    def __init__(self, log_callback=None):
        """
        Initialize inspector.
        
        Args:
            log_callback: Optional callback for progress logging.
        """
        self.log_callback = log_callback
    
    def _log(self, message: str, level: str = "INFO"):
        """Log a message."""
        if self.log_callback:
            self.log_callback(message, level)
    
    def inspect_package(self, package_path: str) -> PackageDescription:
        """
        Inspect a DIAS package and generate a description.
        
        Args:
            package_path: Path to the AIC directory.
            
        Returns:
            PackageDescription object.
        """
        desc = PackageDescription()
        package_root = Path(package_path)
        
        if not package_root.exists():
            self._log(f"Package not found: {package_path}", "ERROR")
            return desc
        
        # Get AIC UUID from directory name
        desc.aic_uuid = package_root.name
        self._log(f"Inspecting package: {desc.aic_uuid}")
        
        # Read info.xml at AIC level
        info_xml = package_root / "info.xml"
        if info_xml.exists():
            self._log("Reading info.xml...")
            self._read_info_xml(info_xml, desc)
        
        # Find AIP directory
        aip_dirs = [d for d in package_root.iterdir() if d.is_dir()]
        if aip_dirs:
            aip_dir = aip_dirs[0]
            desc.aip_uuid = aip_dir.name
            self._log(f"Found AIP: {desc.aip_uuid}")
            
            # Check content directory for tar file
            content_dir = aip_dir / "content"
            if content_dir.exists():
                tar_files = list(content_dir.glob("*.tar"))
                if tar_files:
                    tar_path = tar_files[0]
                    desc.archive_name = tar_path.name
                    desc.archive_size = tar_path.stat().st_size
                    desc.sip_uuid = tar_path.stem
                    
                    self._log(f"Reading archive: {tar_path.name}")
                    self._read_tar_archive(tar_path, desc)
        
        self._log("Inspection complete")
        return desc
    
    def _read_info_xml(self, xml_path: Path, desc: PackageDescription):
        """Read info.xml and extract metadata."""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            ns = self.NAMESPACES
            
            # Get basic attributes
            desc.label = root.get('LABEL')
            desc.package_type = root.get('TYPE')
            
            # Get metsHdr information
            mets_hdr = root.find('.//mets:metsHdr', ns)
            if mets_hdr is not None:
                desc.create_date = mets_hdr.get('CREATEDATE')
                desc.record_status = mets_hdr.get('RECORDSTATUS')
                
                # Extract agents
                agents = mets_hdr.findall('.//mets:agent', ns)
                for agent in agents:
                    role = agent.get('ROLE')
                    name_elem = agent.find('.//mets:name', ns)
                    if name_elem is not None and name_elem.text:
                        name = name_elem.text.strip()
                        
                        if role == 'ARCHIVIST':
                            desc.archivist.append(name)
                        elif role == 'CREATOR':
                            desc.creator.append(name)
                        elif role == 'OTHER':
                            other_role = agent.get('OTHERROLE')
                            if other_role == 'PRODUCER':
                                desc.producer.append(name)
                            elif other_role == 'SUBMITTER':
                                desc.submitter.append(name)
                        elif role == 'IPOWNER':
                            desc.ipowner.append(name)
                        elif role == 'PRESERVATION':
                            desc.preservation.append(name)
                
                # Extract altRecordID
                alt_records = mets_hdr.findall('.//mets:altRecordID', ns)
                for alt in alt_records:
                    alt_type = alt.get('TYPE')
                    if alt.text:
                        if alt_type == 'SUBMISSIONAGREEMENT':
                            desc.submission_agreement = alt.text.strip()
                        elif alt_type == 'STARTDATE':
                            desc.start_date = alt.text.strip()
                        elif alt_type == 'ENDDATE':
                            desc.end_date = alt.text.strip()
            
            # Get file information from fileSec if present
            files = root.findall('.//mets:file', ns)
            if files:
                for file_elem in files:
                    checksum = file_elem.get('CHECKSUM')
                    if checksum:
                        desc.archive_checksum = checksum
                        break
            
        except Exception as e:
            self._log(f"Error reading info.xml: {e}", "ERROR")
    
    def _read_tar_archive(self, tar_path: Path, desc: PackageDescription):
        """Read tar archive and extract file information."""
        try:
            with tarfile.open(tar_path, 'r') as tar:
                members = tar.getmembers()
                
                # Find mets.xml in archive
                mets_member = None
                for member in members:
                    if member.name.endswith('mets.xml'):
                        mets_member = member
                        break
                
                # Read mets.xml from archive
                if mets_member:
                    self._read_mets_from_tar(tar, mets_member, desc)
                
                # Count content files (exclude metadata files)
                metadata_files = {'mets.xml', 'log.xml', 'premis.xml', 'mets.xsd', 
                                'DIAS_PREMIS.xsd', 'premis.xsd'}
                
                for member in members:
                    if member.isfile():
                        filename = member.name.split('/')[-1]
                        
                        # Check if it's in content directory
                        if '/content/' in member.name and filename not in metadata_files:
                            desc.content_files.append({
                                'name': filename,
                                'path': member.name,
                                'size': member.size
                            })
                            desc.total_size += member.size
                
                desc.total_files = len(desc.content_files)
                
        except Exception as e:
            self._log(f"Error reading tar archive: {e}", "ERROR")
    
    def _read_mets_from_tar(self, tar: tarfile.TarFile, member: tarfile.TarInfo, 
                           desc: PackageDescription):
        """Read mets.xml from tar archive."""
        try:
            f = tar.extractfile(member)
            if f is None:
                return
            
            content = f.read()
            root = ET.fromstring(content)
            ns = self.NAMESPACES
            
            # If we don't have basic info yet, try to get it from mets.xml
            if not desc.label:
                desc.label = root.get('LABEL')
            if not desc.package_type:
                desc.package_type = root.get('TYPE')
            
            # Get additional file information
            files = root.findall('.//mets:file', ns)
            for file_elem in files:
                flocat = file_elem.find('.//mets:FLocat', ns)
                if flocat is not None:
                    href = flocat.get('{http://www.w3.org/1999/xlink}href', '')
                    # This gives us more detailed file references
                    pass
            
        except Exception as e:
            self._log(f"Error reading mets.xml from archive: {e}", "ERROR")
    
    def export_description(self, desc: PackageDescription, output_path: str):
        """
        Export package description to a text file.
        
        Args:
            desc: PackageDescription object.
            output_path: Path to save description.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(desc.get_summary())
            f.write(f"\n\nGenerated: {datetime.now().isoformat()}\n")
