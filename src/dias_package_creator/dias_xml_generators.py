"""
DIAS-compliant XML generators for info.xml, mets.xml, and log.xml (PREMIS).
Based on the DIAS package structure from Norwegian archives.
"""

import hashlib
import logging
import mimetypes
import os
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..utils.env_config import config

# Configure logging
logger = logging.getLogger(__name__)

VALID_PACKAGE_TYPES = {"SIP", "AIP", "DIP", "AIU", "AIC"}


def resolve_package_type(metadata: Dict[str, Any]) -> str:
    """Resolve and normalize package type from metadata with backward compatibility."""
    package_type = metadata.get('package_type') or metadata.get('type') or 'SIP'
    package_type = str(package_type).strip().upper()
    return package_type if package_type in VALID_PACKAGE_TYPES else 'SIP'


def resolve_record_relation_type(metadata: Dict[str, Any]) -> str:
    """Resolve semantic relation type for supplement/replacement records."""
    relation_type = str(metadata.get('relation_type', '')).strip().lower()
    if relation_type:
        return relation_type

    record_status = str(metadata.get('record_status', 'NEW')).strip().upper()
    return {
        'SUPPLEMENT': 'supplements',
        'REPLACEMENT': 'replaces'
    }.get(record_status, '')


def get_timestamp() -> str:
    """Get current timestamp in ISO format with timezone."""
    return datetime.now().astimezone().isoformat()


def generate_uuid() -> str:
    """Generate a new random UUID (uuid4 avoids leaking MAC address)."""
    return str(uuid.uuid4())


def calculate_sha256(file_path: str | Path) -> Optional[str]:
    """
    Calculate SHA-256 checksum for a file using streaming to avoid memory issues.
    Uses configurable chunk size for optimal performance with large files.
    """
    sha256_hash = hashlib.sha256()
    chunk_size = config.SHA256_CHUNK_SIZE
    path = Path(file_path)
    
    try:
        file_size = path.stat().st_size
        logger.debug(f"Calculating SHA-256 for {file_path} ({file_size / (1024*1024):.2f} MB)")
        
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                sha256_hash.update(chunk)
        
        checksum = sha256_hash.hexdigest()
        logger.debug(f"SHA-256 calculated: {checksum[:16]}...")
        return checksum
    except Exception as e:
        logger.error(f"Failed to calculate SHA-256 for {file_path}: {e}")
        return None


class DIASInfoGenerator:
    """
    Generator for info.xml (AIC-level METS) file.
    This is the top-level submission description at the AIC wrapper level.
    """
    
    NAMESPACES = {
        'mets': 'http://www.loc.gov/METS/',
        'xlink': 'http://www.w3.org/1999/xlink',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    def __init__(self):
        # Register namespaces
        for prefix, uri in self.NAMESPACES.items():
            ET.register_namespace(prefix, uri)
    
    def create_info_xml(self, metadata, aip_uuid, aic_uuid, tar_file_info=None):
        """
        Create info.xml for the AIC wrapper level.
        
        Args:
            metadata: Package metadata dictionary
            aip_uuid: UUID of the AIP package
            aic_uuid: UUID of the AIC wrapper
            tar_file_info: Information about the tar file (checksum, size, etc.)
        """
        mets_ns = self.NAMESPACES['mets']
        xlink_ns = self.NAMESPACES['xlink']
        xsi_ns = self.NAMESPACES['xsi']
        
        # Create root METS element
        root = ET.Element(f"{{{mets_ns}}}mets")
        root.set(f"{{{xsi_ns}}}schemaLocation", config.METS_INFO_SCHEMA_LOCATION)
        root.set("PROFILE", config.METS_PROFILE)
        root.set("LABEL", metadata.get('label', ''))
        root.set("TYPE", resolve_package_type(metadata))
        root.set("ID", f"ID{generate_uuid()}")
        root.set("OBJID", f"UUID:{aip_uuid}")
        
        # Create metsHdr
        self._create_mets_header(root, metadata, mets_ns)
        
        # Create fileSec (reference to the tar archive)
        if tar_file_info:
            self._create_file_section(root, tar_file_info, aip_uuid, mets_ns, xlink_ns)
        
        # Create structMap
        self._create_struct_map(root, tar_file_info, mets_ns)
        
        return root
    
    def _create_mets_header(self, root, metadata, mets_ns):
        """Create the metsHdr element with all agents."""
        mets_hdr = ET.SubElement(root, f"{{{mets_ns}}}metsHdr")
        mets_hdr.set("CREATEDATE", get_timestamp())
        mets_hdr.set("RECORDSTATUS", metadata.get('record_status', 'NEW'))
        
        # Add agents in the correct order as per DIAS specification
        self._add_agents(mets_hdr, metadata, mets_ns)
        
        # Add altRecordID elements
        self._add_alt_record_ids(mets_hdr, metadata, mets_ns)
        
        # Add metsDocumentID
        doc_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}metsDocumentID")
        doc_id.text = "info.xml"
    
    def _add_agents(self, mets_hdr, metadata, mets_ns):
        """Add all agent elements to metsHdr."""
        # ARCHIVIST - Organization
        if metadata.get('archivist_organization'):
            self._add_agent(mets_hdr, mets_ns, "ORGANIZATION", "ARCHIVIST", 
                          metadata['archivist_organization'])
        
        # ARCHIVIST - Software (system name)
        if metadata.get('system_name'):
            self._add_agent(mets_hdr, mets_ns, "OTHER", "ARCHIVIST", 
                          metadata['system_name'], othertype="SOFTWARE")
        
        # ARCHIVIST - Software (version)
        if metadata.get('system_version'):
            self._add_agent(mets_hdr, mets_ns, "OTHER", "ARCHIVIST", 
                          metadata['system_version'], othertype="SOFTWARE")
        
        # ARCHIVIST - Software (format)
        if metadata.get('system_format'):
            self._add_agent(mets_hdr, mets_ns, "OTHER", "ARCHIVIST", 
                          metadata['system_format'], othertype="SOFTWARE")
        
        # CREATOR - Organization (IKA)
        if metadata.get('creator_organization'):
            self._add_agent(mets_hdr, mets_ns, "ORGANIZATION", "CREATOR", 
                          metadata['creator_organization'])
        
        # PRODUCER - Organization
        if metadata.get('producer_organization'):
            self._add_agent(mets_hdr, mets_ns, "ORGANIZATION", "OTHER", 
                          metadata['producer_organization'], otherrole="PRODUCER")
        
        # PRODUCER - Individual
        if metadata.get('producer_individual'):
            self._add_agent(mets_hdr, mets_ns, "INDIVIDUAL", "OTHER", 
                          metadata['producer_individual'], otherrole="PRODUCER")
        
        # PRODUCER - Software
        if metadata.get('producer_software'):
            self._add_agent(mets_hdr, mets_ns, "OTHER", "OTHER", 
                          metadata['producer_software'], othertype="SOFTWARE", otherrole="PRODUCER")
        
        # SUBMITTER - Organization
        if metadata.get('submitter_organization'):
            self._add_agent(mets_hdr, mets_ns, "ORGANIZATION", "OTHER", 
                          metadata['submitter_organization'], otherrole="SUBMITTER")
        
        # SUBMITTER - Individual
        if metadata.get('submitter_individual'):
            self._add_agent(mets_hdr, mets_ns, "INDIVIDUAL", "OTHER", 
                          metadata['submitter_individual'], otherrole="SUBMITTER")
        
        # IPOWNER - Organization
        if metadata.get('ipowner_organization'):
            self._add_agent(mets_hdr, mets_ns, "ORGANIZATION", "IPOWNER", 
                          metadata['ipowner_organization'])
        
        # PRESERVATION - Organization
        if metadata.get('preservation_organization'):
            self._add_agent(mets_hdr, mets_ns, "ORGANIZATION", "PRESERVATION", 
                          metadata['preservation_organization'])
    
    def _add_agent(self, parent, mets_ns, agent_type, role, name, othertype=None, otherrole=None):
        """Add a single agent element."""
        agent = ET.SubElement(parent, f"{{{mets_ns}}}agent")
        agent.set("TYPE", agent_type)
        if othertype:
            agent.set("OTHERTYPE", othertype)
        agent.set("ROLE", role)
        if otherrole:
            agent.set("OTHERROLE", otherrole)
        
        name_elem = ET.SubElement(agent, f"{{{mets_ns}}}name")
        name_elem.text = name
    
    def _add_alt_record_ids(self, mets_hdr, metadata, mets_ns):
        """Add altRecordID elements."""
        # SUBMISSIONAGREEMENT
        if metadata.get('submission_agreement'):
            alt_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}altRecordID")
            alt_id.set("TYPE", "SUBMISSIONAGREEMENT")
            alt_id.text = metadata['submission_agreement']
        
        # STARTDATE
        if metadata.get('start_date'):
            alt_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}altRecordID")
            alt_id.set("TYPE", "STARTDATE")
            alt_id.text = metadata['start_date']
        
        # ENDDATE
        if metadata.get('end_date'):
            alt_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}altRecordID")
            alt_id.set("TYPE", "ENDDATE")
            alt_id.text = metadata['end_date']

        record_status = str(metadata.get('record_status', 'NEW')).strip().upper()
        if record_status in {'SUPPLEMENT', 'REPLACEMENT'}:
            if metadata.get('related_aic_id'):
                alt_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}altRecordID")
                alt_id.set("TYPE", "RELATEDAIC")
                alt_id.text = metadata['related_aic_id']

            if metadata.get('related_package_id'):
                alt_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}altRecordID")
                alt_id.set("TYPE", "RELATEDPACKAGE")
                alt_id.text = metadata['related_package_id']

            relation_type = resolve_record_relation_type(metadata)
            if relation_type:
                alt_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}altRecordID")
                alt_id.set("TYPE", "RELATIONTYPE")
                alt_id.text = relation_type
    
    def _create_file_section(self, root, tar_file_info, aip_uuid, mets_ns, xlink_ns):
        """Create fileSec with reference to tar archive."""
        file_sec = ET.SubElement(root, f"{{{mets_ns}}}fileSec")
        file_grp = ET.SubElement(file_sec, f"{{{mets_ns}}}fileGrp")
        file_grp.set("ID", "fgrp001")
        file_grp.set("USE", "FILES")
        
        file_elem = ET.SubElement(file_grp, f"{{{mets_ns}}}file")
        file_elem.set("MIMETYPE", "application/x-tar")
        file_elem.set("CHECKSUMTYPE", "SHA-256")
        file_elem.set("CREATED", tar_file_info.get('created', get_timestamp()))
        file_elem.set("CHECKSUM", tar_file_info.get('checksum', ''))
        file_elem.set("USE", "Datafile")
        file_elem.set("ID", f"ID{generate_uuid()}")
        file_elem.set("SIZE", str(tar_file_info.get('size', 0)))
        
        flocat = ET.SubElement(file_elem, f"{{{mets_ns}}}FLocat")
        flocat.set(f"{{{xlink_ns}}}href", f"file:{aip_uuid}.tar")
        flocat.set("LOCTYPE", "URL")
        flocat.set(f"{{{xlink_ns}}}type", "simple")
        
        # Store file ID for structMap
        tar_file_info['file_id'] = file_elem.get("ID")
    
    def _create_struct_map(self, root, tar_file_info, mets_ns):
        """Create structMap element."""
        struct_map = ET.SubElement(root, f"{{{mets_ns}}}structMap")
        
        div_package = ET.SubElement(struct_map, f"{{{mets_ns}}}div")
        div_package.set("LABEL", "Package")
        
        div_content = ET.SubElement(div_package, f"{{{mets_ns}}}div")
        div_content.set("LABEL", "Content Description")
        
        div_datafiles = ET.SubElement(div_package, f"{{{mets_ns}}}div")
        div_datafiles.set("LABEL", "Datafiles")
        
        if tar_file_info and tar_file_info.get('file_id'):
            fptr = ET.SubElement(div_datafiles, f"{{{mets_ns}}}fptr")
            fptr.set("FILEID", tar_file_info['file_id'])
    
    def save(self, element, output_path):
        """Save the XML to file."""
        tree = ET.ElementTree(element)
        ET.indent(tree, space="    ", level=0)
        tree.write(output_path, encoding='UTF-8', xml_declaration=True)


class DIASMetsGenerator:
    """
    Generator for mets.xml (SIP-level METS) file.
    This is the main structural map at the SIP level.
    """
    
    NAMESPACES = {
        'mets': 'http://www.loc.gov/METS/',
        'xlink': 'http://www.w3.org/1999/xlink',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    def __init__(self):
        for prefix, uri in self.NAMESPACES.items():
            ET.register_namespace(prefix, uri)
    
    def create_mets_xml(self, metadata, sip_uuid, files_info, premis_file_info=None):
        """
        Create mets.xml for SIP level.
        
        Args:
            metadata: Package metadata dictionary
            sip_uuid: UUID of the SIP package
            files_info: List of file information dictionaries
            premis_file_info: Information about the premis.xml file
        """
        mets_ns = self.NAMESPACES['mets']
        xlink_ns = self.NAMESPACES['xlink']
        xsi_ns = self.NAMESPACES['xsi']
        
        root = ET.Element(f"{{{mets_ns}}}mets")
        root.set(f"{{{xsi_ns}}}schemaLocation", config.METS_SIP_SCHEMA_LOCATION)
        root.set("PROFILE", config.METS_PROFILE)
        root.set("LABEL", metadata.get('label', ''))
        root.set("TYPE", resolve_package_type(metadata))
        root.set("ID", f"ID{generate_uuid()}")
        root.set("OBJID", f"UUID:{sip_uuid}")
        
        # Create metsHdr
        self._create_mets_header(root, metadata, mets_ns)
        
        # Create amdSec (reference to PREMIS)
        premis_id = self._create_amd_section(root, premis_file_info, mets_ns, xlink_ns)
        
        # Create fileSec
        file_ids = self._create_file_section(root, files_info, mets_ns, xlink_ns)
        
        # Create structMap
        self._create_struct_map(root, premis_id, file_ids, mets_ns)
        
        return root
    
    def _create_mets_header(self, root, metadata, mets_ns):
        """Create the metsHdr element."""
        mets_hdr = ET.SubElement(root, f"{{{mets_ns}}}metsHdr")
        mets_hdr.set("CREATEDATE", get_timestamp())
        mets_hdr.set("RECORDSTATUS", metadata.get('record_status', 'NEW'))
        
        # Add agents (same as info.xml)
        self._add_agents(mets_hdr, metadata, mets_ns)
        
        # Add altRecordID elements
        self._add_alt_record_ids(mets_hdr, metadata, mets_ns)
        
        # Add metsDocumentID
        doc_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}metsDocumentID")
        doc_id.text = "mets.xml"
    
    def _add_agents(self, mets_hdr, metadata, mets_ns):
        """Add all agent elements (reuse from DIASInfoGenerator)."""
        # ARCHIVIST - Organization
        if metadata.get('archivist_organization'):
            self._add_agent(mets_hdr, mets_ns, "ORGANIZATION", "ARCHIVIST", 
                          metadata['archivist_organization'])
        
        # ARCHIVIST - Software
        if metadata.get('system_name'):
            self._add_agent(mets_hdr, mets_ns, "OTHER", "ARCHIVIST", 
                          metadata['system_name'], othertype="SOFTWARE")
        if metadata.get('system_version'):
            self._add_agent(mets_hdr, mets_ns, "OTHER", "ARCHIVIST", 
                          metadata['system_version'], othertype="SOFTWARE")
        if metadata.get('system_format'):
            self._add_agent(mets_hdr, mets_ns, "OTHER", "ARCHIVIST", 
                          metadata['system_format'], othertype="SOFTWARE")
        
        # CREATOR
        if metadata.get('creator_organization'):
            self._add_agent(mets_hdr, mets_ns, "ORGANIZATION", "CREATOR", 
                          metadata['creator_organization'])
        
        # PRODUCER
        if metadata.get('producer_organization'):
            self._add_agent(mets_hdr, mets_ns, "ORGANIZATION", "OTHER", 
                          metadata['producer_organization'], otherrole="PRODUCER")
        if metadata.get('producer_individual'):
            self._add_agent(mets_hdr, mets_ns, "INDIVIDUAL", "OTHER", 
                          metadata['producer_individual'], otherrole="PRODUCER")
        if metadata.get('producer_software'):
            self._add_agent(mets_hdr, mets_ns, "OTHER", "OTHER", 
                          metadata['producer_software'], othertype="SOFTWARE", otherrole="PRODUCER")
        
        # SUBMITTER
        if metadata.get('submitter_organization'):
            self._add_agent(mets_hdr, mets_ns, "ORGANIZATION", "OTHER", 
                          metadata['submitter_organization'], otherrole="SUBMITTER")
        if metadata.get('submitter_individual'):
            self._add_agent(mets_hdr, mets_ns, "INDIVIDUAL", "OTHER", 
                          metadata['submitter_individual'], otherrole="SUBMITTER")
        
        # IPOWNER
        if metadata.get('ipowner_organization'):
            self._add_agent(mets_hdr, mets_ns, "ORGANIZATION", "IPOWNER", 
                          metadata['ipowner_organization'])
        
        # PRESERVATION
        if metadata.get('preservation_organization'):
            self._add_agent(mets_hdr, mets_ns, "ORGANIZATION", "PRESERVATION", 
                          metadata['preservation_organization'])
    
    def _add_agent(self, parent, mets_ns, agent_type, role, name, othertype=None, otherrole=None):
        """Add a single agent element."""
        agent = ET.SubElement(parent, f"{{{mets_ns}}}agent")
        agent.set("TYPE", agent_type)
        if othertype:
            agent.set("OTHERTYPE", othertype)
        agent.set("ROLE", role)
        if otherrole:
            agent.set("OTHERROLE", otherrole)
        
        name_elem = ET.SubElement(agent, f"{{{mets_ns}}}name")
        name_elem.text = name
    
    def _add_alt_record_ids(self, mets_hdr, metadata, mets_ns):
        """Add altRecordID elements."""
        if metadata.get('submission_agreement'):
            alt_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}altRecordID")
            alt_id.set("TYPE", "SUBMISSIONAGREEMENT")
            alt_id.text = metadata['submission_agreement']
        
        if metadata.get('start_date'):
            alt_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}altRecordID")
            alt_id.set("TYPE", "STARTDATE")
            alt_id.text = metadata['start_date']
        
        if metadata.get('end_date'):
            alt_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}altRecordID")
            alt_id.set("TYPE", "ENDDATE")
            alt_id.text = metadata['end_date']

        record_status = str(metadata.get('record_status', 'NEW')).strip().upper()
        if record_status in {'SUPPLEMENT', 'REPLACEMENT'}:
            if metadata.get('related_aic_id'):
                alt_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}altRecordID")
                alt_id.set("TYPE", "RELATEDAIC")
                alt_id.text = metadata['related_aic_id']

            if metadata.get('related_package_id'):
                alt_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}altRecordID")
                alt_id.set("TYPE", "RELATEDPACKAGE")
                alt_id.text = metadata['related_package_id']

            relation_type = resolve_record_relation_type(metadata)
            if relation_type:
                alt_id = ET.SubElement(mets_hdr, f"{{{mets_ns}}}altRecordID")
                alt_id.set("TYPE", "RELATIONTYPE")
                alt_id.text = relation_type
    
    def _create_amd_section(self, root, premis_file_info, mets_ns, xlink_ns):
        """Create amdSec with reference to PREMIS file."""
        amd_sec = ET.SubElement(root, f"{{{mets_ns}}}amdSec")
        amd_sec.set("ID", "amdSec001")
        
        digiprov_md = ET.SubElement(amd_sec, f"{{{mets_ns}}}digiprovMD")
        digiprov_id = f"ID{generate_uuid()}"
        digiprov_md.set("ID", "digiprovMD001")
        
        md_ref = ET.SubElement(digiprov_md, f"{{{mets_ns}}}mdRef")
        md_ref.set("MIMETYPE", "text/xml")
        md_ref.set("CHECKSUMTYPE", "SHA-256")
        if premis_file_info:
            md_ref.set("CHECKSUM", premis_file_info.get('checksum', ''))
            md_ref.set("CREATED", premis_file_info.get('created', get_timestamp()))
            md_ref.set("SIZE", str(premis_file_info.get('size', 0)))
        md_ref.set("MDTYPE", "PREMIS")
        md_ref.set(f"{{{xlink_ns}}}href", "file:administrative_metadata/premis.xml")
        md_ref.set("LOCTYPE", "URL")
        md_ref.set(f"{{{xlink_ns}}}type", "simple")
        md_ref.set("ID", digiprov_id)
        
        return digiprov_id
    
    def _create_file_section(self, root, files_info, mets_ns, xlink_ns):
        """Create fileSec with all package files."""
        file_sec = ET.SubElement(root, f"{{{mets_ns}}}fileSec")
        file_grp = ET.SubElement(file_sec, f"{{{mets_ns}}}fileGrp")
        file_grp.set("ID", "fgrp001")
        file_grp.set("USE", "FILES")
        
        file_ids = []
        
        for file_info in files_info:
            file_elem = ET.SubElement(file_grp, f"{{{mets_ns}}}file")
            file_id = f"ID{generate_uuid()}"
            
            mimetype = file_info.get('mimetype', 'application/octet-stream')
            if not mimetype:
                mimetype = mimetypes.guess_type(file_info.get('path', ''))[0] or 'application/octet-stream'
            
            file_elem.set("MIMETYPE", mimetype)
            file_elem.set("CHECKSUMTYPE", "SHA-256")
            file_elem.set("CREATED", file_info.get('created', get_timestamp()))
            file_elem.set("CHECKSUM", file_info.get('checksum', ''))
            file_elem.set("USE", "Datafile")
            file_elem.set("ID", file_id)
            file_elem.set("SIZE", str(file_info.get('size', 0)))
            
            flocat = ET.SubElement(file_elem, f"{{{mets_ns}}}FLocat")
            flocat.set(f"{{{xlink_ns}}}href", f"file:{file_info.get('path', '')}")
            flocat.set("LOCTYPE", "URL")
            flocat.set(f"{{{xlink_ns}}}type", "simple")
            
            file_ids.append(file_id)
        
        return file_ids
    
    def _create_struct_map(self, root, premis_id, file_ids, mets_ns):
        """Create structMap element."""
        struct_map = ET.SubElement(root, f"{{{mets_ns}}}structMap")
        
        div_package = ET.SubElement(struct_map, f"{{{mets_ns}}}div")
        div_package.set("LABEL", "Package")
        
        div_content = ET.SubElement(div_package, f"{{{mets_ns}}}div")
        div_content.set("ADMID", "amdSec001")
        div_content.set("LABEL", "Content Description")
        
        if premis_id:
            fptr = ET.SubElement(div_content, f"{{{mets_ns}}}fptr")
            fptr.set("FILEID", premis_id)
        
        div_datafiles = ET.SubElement(div_package, f"{{{mets_ns}}}div")
        div_datafiles.set("ADMID", "amdSec001")
        div_datafiles.set("LABEL", "Datafiles")
        
        for file_id in file_ids:
            fptr = ET.SubElement(div_datafiles, f"{{{mets_ns}}}fptr")
            fptr.set("FILEID", file_id)
    
    def save(self, element, output_path):
        """Save the XML to file."""
        tree = ET.ElementTree(element)
        ET.indent(tree, space="    ", level=0)
        tree.write(output_path, encoding='UTF-8', xml_declaration=True)


class DIASLogGenerator:
    """
    Generator for log.xml (PREMIS) files.
    Creates both SIP-level and AIP-level log/premis files.
    """
    
    NAMESPACES = {
        'premis': 'http://arkivverket.no/standarder/PREMIS',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xlink': 'http://www.w3.org/1999/xlink'
    }
    
    def __init__(self):
        for prefix, uri in self.NAMESPACES.items():
            ET.register_namespace(prefix, uri)
    
    def create_log_xml(self, metadata, object_uuid, aic_uuid=None, files_info=None, is_sip_level=True,
                       user_events=None, agents=None):
        """
        Create log.xml (PREMIS) file.
        
        Args:
            metadata: Package metadata dictionary
            object_uuid: UUID of the object (SIP or AIP)
            aic_uuid: UUID of the AIC (parent container)
            files_info: List of file information (for SIP-level premis.xml)
            is_sip_level: True for SIP-level, False for AIP-level
            user_events: Optional list of user-defined event dicts
            agents: Optional list of agent dicts
        """
        premis_ns = self.NAMESPACES['premis']
        xsi_ns = self.NAMESPACES['xsi']
        
        root = ET.Element(f"{{{premis_ns}}}premis")
        root.set(f"{{{xsi_ns}}}schemaLocation", config.PREMIS_SCHEMA_LOCATION)
        root.set("version", config.PREMIS_VERSION)
        
        # Create main object element
        self._create_object(root, metadata, object_uuid, aic_uuid, premis_ns, xsi_ns)
        
        # Create file objects if this is SIP-level premis.xml
        if is_sip_level and files_info:
            for file_info in files_info:
                self._create_file_object(root, file_info, object_uuid, premis_ns, xsi_ns)
        
        # Create automatic event (log creation)
        self._create_event(root, object_uuid, premis_ns)
        
        # Create user-defined events
        if user_events:
            for user_event in user_events:
                self._create_user_event(root, object_uuid, premis_ns, user_event)
        
        # Create agent elements
        if agents:
            for agent in agents:
                self._create_agent(root, premis_ns, agent)
        
        return root
    
    def _create_object(self, root, metadata, object_uuid, aic_uuid, premis_ns, xsi_ns):
        """Create the main PREMIS object element."""
        obj = ET.SubElement(root, f"{{{premis_ns}}}object")
        obj.set(f"{{{xsi_ns}}}type", "premis:file")
        
        # Object identifier
        obj_id = ET.SubElement(obj, f"{{{premis_ns}}}objectIdentifier")
        obj_id_type = ET.SubElement(obj_id, f"{{{premis_ns}}}objectIdentifierType")
        obj_id_type.text = "NO/RA"
        obj_id_value = ET.SubElement(obj_id, f"{{{premis_ns}}}objectIdentifierValue")
        obj_id_value.text = object_uuid
        
        # Preservation level
        pres_level = ET.SubElement(obj, f"{{{premis_ns}}}preservationLevel")
        pres_level_value = ET.SubElement(pres_level, f"{{{premis_ns}}}preservationLevelValue")
        pres_level_value.text = "full"
        
        # Significant properties
        self._add_significant_property(obj, premis_ns, "aic_object", aic_uuid or "")
        self._add_significant_property(obj, premis_ns, "createdate", get_timestamp())
        self._add_significant_property(obj, premis_ns, "archivist_organization", 
                                       metadata.get('archivist_organization', ''))
        self._add_significant_property(obj, premis_ns, "label", metadata.get('label', ''))
        self._add_significant_property(obj, premis_ns, "iptype", resolve_package_type(metadata))

        relation_type = resolve_record_relation_type(metadata)
        record_status = str(metadata.get('record_status', 'NEW')).strip().upper()
        if record_status in {'SUPPLEMENT', 'REPLACEMENT'}:
            self._add_significant_property(obj, premis_ns, "record_status", record_status)
            if relation_type:
                self._add_significant_property(obj, premis_ns, "relation_type", relation_type)
            if metadata.get('related_aic_id'):
                self._add_significant_property(obj, premis_ns, "related_aic_id", metadata['related_aic_id'])
            if metadata.get('related_package_id'):
                self._add_significant_property(obj, premis_ns, "related_package_id", metadata['related_package_id'])
        
        # Object characteristics
        obj_char = ET.SubElement(obj, f"{{{premis_ns}}}objectCharacteristics")
        comp_level = ET.SubElement(obj_char, f"{{{premis_ns}}}compositionLevel")
        comp_level.text = "0"
        
        format_elem = ET.SubElement(obj_char, f"{{{premis_ns}}}format")
        format_des = ET.SubElement(format_elem, f"{{{premis_ns}}}formatDesignation")
        format_name = ET.SubElement(format_des, f"{{{premis_ns}}}formatName")
        format_name.text = "tar"
        
        # Storage
        storage = ET.SubElement(obj, f"{{{premis_ns}}}storage")
        storage_medium = ET.SubElement(storage, f"{{{premis_ns}}}storageMedium")
        storage_medium.text = config.PRESERVATION_PLATFORM
        
        # Relationship to AIC
        if aic_uuid:
            relationship = ET.SubElement(obj, f"{{{premis_ns}}}relationship")
            rel_type = ET.SubElement(relationship, f"{{{premis_ns}}}relationshipType")
            rel_type.text = "structural"
            rel_subtype = ET.SubElement(relationship, f"{{{premis_ns}}}relationshipSubType")
            rel_subtype.text = "is part of"
            
            rel_obj_id = ET.SubElement(relationship, f"{{{premis_ns}}}relatedObjectIdentification")
            rel_obj_id_type = ET.SubElement(rel_obj_id, f"{{{premis_ns}}}relatedObjectIdentifierType")
            rel_obj_id_type.text = config.OBJECT_IDENTIFIER_TYPE
            rel_obj_id_value = ET.SubElement(rel_obj_id, f"{{{premis_ns}}}relatedObjectIdentifierValue")
            rel_obj_id_value.text = aic_uuid

        if metadata.get('related_aic_id'):
            relationship = ET.SubElement(obj, f"{{{premis_ns}}}relationship")
            rel_type = ET.SubElement(relationship, f"{{{premis_ns}}}relationshipType")
            rel_type.text = "derivation"
            rel_subtype = ET.SubElement(relationship, f"{{{premis_ns}}}relationshipSubType")
            rel_subtype.text = resolve_record_relation_type(metadata) or "related to"

            rel_obj_id = ET.SubElement(relationship, f"{{{premis_ns}}}relatedObjectIdentification")
            rel_obj_id_type = ET.SubElement(rel_obj_id, f"{{{premis_ns}}}relatedObjectIdentifierType")
            rel_obj_id_type.text = config.OBJECT_IDENTIFIER_TYPE
            rel_obj_id_value = ET.SubElement(rel_obj_id, f"{{{premis_ns}}}relatedObjectIdentifierValue")
            rel_obj_id_value.text = metadata['related_aic_id']

        if metadata.get('related_package_id'):
            relationship = ET.SubElement(obj, f"{{{premis_ns}}}relationship")
            rel_type = ET.SubElement(relationship, f"{{{premis_ns}}}relationshipType")
            rel_type.text = "derivation"
            rel_subtype = ET.SubElement(relationship, f"{{{premis_ns}}}relationshipSubType")
            rel_subtype.text = resolve_record_relation_type(metadata) or "related to"

            rel_obj_id = ET.SubElement(relationship, f"{{{premis_ns}}}relatedObjectIdentification")
            rel_obj_id_type = ET.SubElement(rel_obj_id, f"{{{premis_ns}}}relatedObjectIdentifierType")
            rel_obj_id_type.text = config.OBJECT_IDENTIFIER_TYPE
            rel_obj_id_value = ET.SubElement(rel_obj_id, f"{{{premis_ns}}}relatedObjectIdentifierValue")
            rel_obj_id_value.text = metadata['related_package_id']
    
    def _add_significant_property(self, parent, premis_ns, prop_type, prop_value):
        """Add a significant property element."""
        sig_props = ET.SubElement(parent, f"{{{premis_ns}}}significantProperties")
        sig_type = ET.SubElement(sig_props, f"{{{premis_ns}}}significantPropertiesType")
        sig_type.text = prop_type
        sig_value = ET.SubElement(sig_props, f"{{{premis_ns}}}significantPropertiesValue")
        sig_value.text = prop_value
    
    def _create_file_object(self, root, file_info, parent_uuid, premis_ns, xsi_ns):
        """Create a PREMIS file object for individual files."""
        obj = ET.SubElement(root, f"{{{premis_ns}}}object")
        obj.set(f"{{{xsi_ns}}}type", "premis:file")
        
        # Object identifier
        obj_id = ET.SubElement(obj, f"{{{premis_ns}}}objectIdentifier")
        obj_id_type = ET.SubElement(obj_id, f"{{{premis_ns}}}objectIdentifierType")
        obj_id_type.text = config.OBJECT_IDENTIFIER_TYPE
        obj_id_value = ET.SubElement(obj_id, f"{{{premis_ns}}}objectIdentifierValue")
        obj_id_value.text = f"{parent_uuid}/{file_info.get('path', '')}"
        
        # Object characteristics
        obj_char = ET.SubElement(obj, f"{{{premis_ns}}}objectCharacteristics")
        
        comp_level = ET.SubElement(obj_char, f"{{{premis_ns}}}compositionLevel")
        comp_level.text = "0"
        
        # Fixity
        fixity = ET.SubElement(obj_char, f"{{{premis_ns}}}fixity")
        msg_algo = ET.SubElement(fixity, f"{{{premis_ns}}}messageDigestAlgorithm")
        msg_algo.text = "SHA-256"
        msg_digest = ET.SubElement(fixity, f"{{{premis_ns}}}messageDigest")
        msg_digest.text = file_info.get('checksum', '')
        msg_orig = ET.SubElement(fixity, f"{{{premis_ns}}}messageDigestOriginator")
        msg_orig.text = config.CHECKSUM_ORIGINATOR
        
        # Size
        size_elem = ET.SubElement(obj_char, f"{{{premis_ns}}}size")
        size_elem.text = str(file_info.get('size', 0))
        
        # Format
        format_elem = ET.SubElement(obj_char, f"{{{premis_ns}}}format")
        format_des = ET.SubElement(format_elem, f"{{{premis_ns}}}formatDesignation")
        format_name = ET.SubElement(format_des, f"{{{premis_ns}}}formatName")
        
        # Get format from mimetype or extension
        path = file_info.get('path', '')
        ext = os.path.splitext(path)[1].lstrip('.').lower() or 'unknown'
        format_name.text = ext
        
        # Storage
        storage = ET.SubElement(obj, f"{{{premis_ns}}}storage")
        content_loc = ET.SubElement(storage, f"{{{premis_ns}}}contentLocation")
        content_loc_type = ET.SubElement(content_loc, f"{{{premis_ns}}}contentLocationType")
        content_loc_type.text = "SIP"
        content_loc_value = ET.SubElement(content_loc, f"{{{premis_ns}}}contentLocationValue")
        content_loc_value.text = parent_uuid
        
        # Relationship to parent
        relationship = ET.SubElement(obj, f"{{{premis_ns}}}relationship")
        rel_type = ET.SubElement(relationship, f"{{{premis_ns}}}relationshipType")
        rel_type.text = "structural"
        rel_subtype = ET.SubElement(relationship, f"{{{premis_ns}}}relationshipSubType")
        rel_subtype.text = "is part of"
        
        rel_obj_id = ET.SubElement(relationship, f"{{{premis_ns}}}relatedObjectIdentification")
        rel_obj_id_type = ET.SubElement(rel_obj_id, f"{{{premis_ns}}}relatedObjectIdentifierType")
        rel_obj_id_type.text = config.OBJECT_IDENTIFIER_TYPE
        rel_obj_id_value = ET.SubElement(rel_obj_id, f"{{{premis_ns}}}relatedObjectIdentifierValue")
        rel_obj_id_value.text = parent_uuid
    
    def _create_event(self, root, object_uuid, premis_ns):
        """Create a PREMIS event element."""
        event = ET.SubElement(root, f"{{{premis_ns}}}event")
        
        # Event identifier
        event_id = ET.SubElement(event, f"{{{premis_ns}}}eventIdentifier")
        event_id_type = ET.SubElement(event_id, f"{{{premis_ns}}}eventIdentifierType")
        event_id_type.text = config.OBJECT_IDENTIFIER_TYPE
        event_id_value = ET.SubElement(event_id, f"{{{premis_ns}}}eventIdentifierValue")
        event_id_value.text = generate_uuid()
        
        # Event type (using DIAS numeric codes)
        event_type = ET.SubElement(event, f"{{{premis_ns}}}eventType")
        event_type.text = config.LOG_CREATION_EVENT_TYPE  # Log creation event
        
        # Event datetime
        event_datetime = ET.SubElement(event, f"{{{premis_ns}}}eventDateTime")
        event_datetime.text = get_timestamp()
        
        # Event detail
        event_detail = ET.SubElement(event, f"{{{premis_ns}}}eventDetail")
        event_detail.text = "Log circular created"
        
        # Event outcome
        event_outcome_info = ET.SubElement(event, f"{{{premis_ns}}}eventOutcomeInformation")
        event_outcome = ET.SubElement(event_outcome_info, f"{{{premis_ns}}}eventOutcome")
        event_outcome.text = "0"  # Success
        
        event_outcome_detail = ET.SubElement(event_outcome_info, f"{{{premis_ns}}}eventOutcomeDetail")
        event_outcome_note = ET.SubElement(event_outcome_detail, f"{{{premis_ns}}}eventOutcomeDetailNote")
        event_outcome_note.text = "Success to create logfile"
        
        # Linking agent
        linking_agent = ET.SubElement(event, f"{{{premis_ns}}}linkingAgentIdentifier")
        linking_agent_type = ET.SubElement(linking_agent, f"{{{premis_ns}}}linkingAgentIdentifierType")
        linking_agent_type.text = config.OBJECT_IDENTIFIER_TYPE
        linking_agent_value = ET.SubElement(linking_agent, f"{{{premis_ns}}}linkingAgentIdentifierValue")
        linking_agent_value.text = config.LINKING_AGENT
        
        # Linking object
        linking_obj = ET.SubElement(event, f"{{{premis_ns}}}linkingObjectIdentifier")
        linking_obj_type = ET.SubElement(linking_obj, f"{{{premis_ns}}}linkingObjectIdentifierType")
        linking_obj_type.text = config.OBJECT_IDENTIFIER_TYPE
        linking_obj_value = ET.SubElement(linking_obj, f"{{{premis_ns}}}linkingObjectIdentifierValue")
        linking_obj_value.text = object_uuid
    
    def _create_user_event(self, root, object_uuid, premis_ns, event_data):
        """Create a PREMIS event element from user-provided event data."""
        event = ET.SubElement(root, f"{{{premis_ns}}}event")
        
        # Event identifier
        event_id = ET.SubElement(event, f"{{{premis_ns}}}eventIdentifier")
        event_id_type = ET.SubElement(event_id, f"{{{premis_ns}}}eventIdentifierType")
        event_id_type.text = config.OBJECT_IDENTIFIER_TYPE
        event_id_value = ET.SubElement(event_id, f"{{{premis_ns}}}eventIdentifierValue")
        event_id_value.text = generate_uuid()
        
        # Event type
        event_type = ET.SubElement(event, f"{{{premis_ns}}}eventType")
        event_type.text = event_data.get('event_type', 'Creation')
        
        # Event datetime (use user-provided date or current timestamp)
        event_datetime = ET.SubElement(event, f"{{{premis_ns}}}eventDateTime")
        user_date = event_data.get('event_date', '').strip()
        event_datetime.text = user_date if user_date else get_timestamp()
        
        # Event detail
        event_detail = ET.SubElement(event, f"{{{premis_ns}}}eventDetail")
        event_detail.text = event_data.get('event_detail', '')
        
        # Event outcome
        event_outcome_info = ET.SubElement(event, f"{{{premis_ns}}}eventOutcomeInformation")
        event_outcome = ET.SubElement(event_outcome_info, f"{{{premis_ns}}}eventOutcome")
        event_outcome.text = event_data.get('event_outcome', '0')
        
        outcome_detail_text = event_data.get('event_outcome_detail', '')
        if outcome_detail_text:
            event_outcome_detail = ET.SubElement(event_outcome_info, f"{{{premis_ns}}}eventOutcomeDetail")
            event_outcome_note = ET.SubElement(event_outcome_detail, f"{{{premis_ns}}}eventOutcomeDetailNote")
            event_outcome_note.text = outcome_detail_text
        
        # Linking object
        linking_obj = ET.SubElement(event, f"{{{premis_ns}}}linkingObjectIdentifier")
        linking_obj_type = ET.SubElement(linking_obj, f"{{{premis_ns}}}linkingObjectIdentifierType")
        linking_obj_type.text = config.OBJECT_IDENTIFIER_TYPE
        linking_obj_value = ET.SubElement(linking_obj, f"{{{premis_ns}}}linkingObjectIdentifierValue")
        linking_obj_value.text = object_uuid
    
    def _create_agent(self, root, premis_ns, agent_data):
        """Create a PREMIS agent element."""
        agent = ET.SubElement(root, f"{{{premis_ns}}}agent")
        
        # Agent identifier
        agent_id = ET.SubElement(agent, f"{{{premis_ns}}}agentIdentifier")
        agent_id_type = ET.SubElement(agent_id, f"{{{premis_ns}}}agentIdentifierType")
        agent_id_type.text = agent_data.get('agent_id_type', config.OBJECT_IDENTIFIER_TYPE)
        agent_id_value = ET.SubElement(agent_id, f"{{{premis_ns}}}agentIdentifierValue")
        agent_id_value.text = agent_data.get('agent_id_value', '')
        
        # Agent name
        agent_name = ET.SubElement(agent, f"{{{premis_ns}}}agentName")
        agent_name.text = agent_data.get('agent_name', '')
        
        # Agent type
        agent_type = ET.SubElement(agent, f"{{{premis_ns}}}agentType")
        agent_type.text = agent_data.get('agent_type', 'software')
    
    def save(self, element, output_path):
        """Save the XML to file."""
        tree = ET.ElementTree(element)
        ET.indent(tree, space="  ", level=0)
        tree.write(output_path, encoding='UTF-8', xml_declaration=True)
