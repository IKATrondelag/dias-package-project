import logging
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MetadataHandler:
    def __init__(self) -> None:
        # Submission description specific fields
        self.submission_fields = {
            'objid': 'Object ID',
            'package_type': 'Package Type',
            'profile': 'Profile',
            'label': 'Label',
            'record_status': 'Record Status'
        }
        
        self.dublin_core_fields = [
            'title', 'creator', 'subject', 'description', 'publisher',
            'contributor', 'date', 'type', 'format', 'identifier',
            'source', 'language', 'relation', 'coverage', 'rights'
        ]
        
        # Valid values from schema
        self.valid_package_types = ["SIP", "AIP", "DIP", "AIU", "AIC"]
        self.valid_record_statuses = ["NEW", "SUPPLEMENT", "REPLACEMENT", "TEST", "VERSION", "OTHER"]
        self.valid_agent_roles = ["CREATOR", "EDITOR", "ARCHIVIST", "PRESERVATION", "DISSEMINATOR", "CUSTODIAN", "IPOWNER", "OTHER"]
        self.valid_agent_types = ["INDIVIDUAL", "ORGANIZATION", "OTHER"]
        self.valid_other_roles = ["SUBMITTER", "PRODUCER"]
        self.valid_alt_record_types = [
            "SUBMISSIONAGREEMENT", "DELIVERYTYPE", "DELIVERYSPECIFICATION", 
            "PACKAGENUMBER", "REFERENCECODE", "STARTDATE", "ENDDATE", 
            "INFORMATIONCLASS", "SYSTEMTYPE"
        ]
        
    def get_metadata_from_terminal(self):
        """Collect submission description metadata interactively from terminal"""
        print("\n=== DIAS Submission Description Metadata Collection ===")
        print("Enter metadata for the DIAS submission package:")
        
        # Get submission description metadata
        submission_metadata = self._get_submission_metadata()
        
        # Get Dublin Core descriptive metadata
        descriptive_metadata = self._get_dublin_core_metadata()
        
        # Get agents (minimum 3 required)
        agents = self._collect_agents()
        
        # Get alternative record IDs (minimum 1 required)
        alt_record_ids = self._collect_alt_record_ids()
        
        # Combine all metadata
        metadata = {
            **submission_metadata,
            'descriptive_metadata': descriptive_metadata,
            'agents': agents,
            'alt_record_ids': alt_record_ids,
            'mets_document_id': str(uuid.uuid4()),
            'mets_document_id_type': 'UUID'
        }
        
        return metadata
    
    def _get_submission_metadata(self):
        """Get core submission description metadata"""
        print("\n--- Core Submission Information ---")
        
        submission_data = {}
        
        # Object ID
        submission_data['objid'] = input("Object ID (default: auto-generated): ").strip()
        if not submission_data['objid']:
            submission_data['objid'] = f"SUBMISSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Package Type
        selected_type = self._get_choice("Package Type", self.valid_package_types, "SIP")
        submission_data['package_type'] = selected_type
        submission_data['type'] = selected_type
        
        # Profile
        submission_data['profile'] = input("Profile (default: DIAS_SUBMISSION_DESCRIPTION): ").strip()
        if not submission_data['profile']:
            submission_data['profile'] = "DIAS_SUBMISSION_DESCRIPTION"
        
        # Label (optional)
        submission_data['label'] = input("Label (optional): ").strip()
        
        # Record Status
        submission_data['record_status'] = self._get_choice("Record Status", self.valid_record_statuses, "NEW")
        
        return submission_data
    
    def _get_dublin_core_metadata(self):
        """Get Dublin Core descriptive metadata"""
        print("\n--- Descriptive Metadata (Dublin Core) ---")
        
        metadata = {}
        
        # Required fields
        metadata['title'] = input("Title* (required): ").strip()
        while not metadata['title']:
            metadata['title'] = input("Title is required. Please enter a title: ").strip()
            
        metadata['creator'] = input("Creator* (required): ").strip()
        while not metadata['creator']:
            metadata['creator'] = input("Creator is required. Please enter creator: ").strip()
            
        metadata['identifier'] = input("Identifier* (required): ").strip()
        while not metadata['identifier']:
            metadata['identifier'] = input("Identifier is required. Please enter identifier: ").strip()
            
        # Optional fields
        metadata['subject'] = input("Subject (optional): ").strip() or "Digital Archive"
        metadata['description'] = input("Description (optional): ").strip() or "DIAS Package created from AIP"
        metadata['publisher'] = input("Publisher (optional): ").strip() or "DIAS Package Creator"
        metadata['contributor'] = input("Contributor (optional): ").strip() or ""
        metadata['date'] = input(f"Date (optional, default: {datetime.now().isoformat()}): ").strip() or datetime.now().isoformat()
        metadata['type'] = input("Content Type (optional, default: Collection): ").strip() or "Collection"
        metadata['format'] = input("Format (optional, default: Digital): ").strip() or "Digital"
        metadata['source'] = input("Source (optional): ").strip() or ""
        metadata['language'] = input("Language (optional, default: en): ").strip() or "en"
        metadata['relation'] = input("Relation (optional): ").strip() or ""
        metadata['coverage'] = input("Coverage (optional): ").strip() or ""
        metadata['rights'] = input("Rights (optional): ").strip() or "All rights reserved"
        
        return metadata
    
    def load_metadata_from_xml(self, xml_file_path):
        """Load submission description metadata from XML file"""
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            metadata = {}
            
            # Handle submission description METS structure
            if root.tag.endswith('mets'):
                metadata = self._parse_submission_mets(root)
            # Handle simple Dublin Core structure
            elif root.tag.endswith('dublin_core') or root.tag.endswith('metadata'):
                metadata = self._parse_dublin_core_xml(root)
            else:
                # Try to find METS or Dublin Core elements
                mets_elem = root.find('.//{http://www.loc.gov/METS/}mets')
                if mets_elem is not None:
                    metadata = self._parse_submission_mets(mets_elem)
                else:
                    metadata = self._parse_dublin_core_xml(root)
            
            # Ensure required fields
            self._ensure_required_fields(metadata)
                
            logger.info(f"Metadata loaded from {xml_file_path}")
            return metadata
            
        except ET.ParseError as e:
            logger.error(f"Error parsing XML file: {e}")
            return None
        except FileNotFoundError:
            logger.error(f"XML file not found: {xml_file_path}")
            return None
        except Exception as e:
            logger.error(f"Error loading metadata from XML: {e}")
            return None
    
    def _parse_submission_mets(self, mets_root):
        """Parse submission description METS XML"""
        metadata = {}
        ns = {'mets': 'http://www.loc.gov/METS/'}
        
        # Get root attributes
        metadata['objid'] = mets_root.get('OBJID', f"SUBMISSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        package_type = mets_root.get('TYPE', 'SIP')
        metadata['package_type'] = package_type
        metadata['type'] = package_type
        metadata['profile'] = mets_root.get('PROFILE', 'DIAS_SUBMISSION_DESCRIPTION')
        metadata['label'] = mets_root.get('LABEL', '')
        
        # Get metsHdr information
        mets_hdr = mets_root.find('.//mets:metsHdr', ns)
        if mets_hdr is not None:
            metadata['record_status'] = mets_hdr.get('RECORDSTATUS', 'NEW')
            
            # Get agents
            agents = []
            for agent in mets_hdr.findall('.//mets:agent', ns):
                agent_data = {
                    'role': agent.get('ROLE', 'OTHER'),
                    'type': agent.get('TYPE', 'ORGANIZATION'),
                    'name': agent.find('mets:name', ns).text if agent.find('mets:name', ns) is not None else 'Unknown'
                }
                if agent.get('OTHERROLE'):
                    agent_data['otherrole'] = agent.get('OTHERROLE')
                if agent.get('OTHERTYPE'):
                    agent_data['othertype'] = agent.get('OTHERTYPE')
                note_elem = agent.find('mets:note', ns)
                if note_elem is not None:
                    agent_data['note'] = note_elem.text
                agents.append(agent_data)
            metadata['agents'] = agents
            
            # Get altRecordIDs
            alt_records = []
            for alt_record in mets_hdr.findall('.//mets:altRecordID', ns):
                alt_type = alt_record.get('TYPE', '')
                alt_value = alt_record.text or ''
                alt_records.append({'type': alt_type, 'value': alt_value})

                if alt_type == 'RELATEDAIC':
                    metadata['related_aic_id'] = alt_value
                elif alt_type == 'RELATEDPACKAGE':
                    metadata['related_package_id'] = alt_value
                elif alt_type == 'RELATIONTYPE':
                    metadata['relation_type'] = alt_value
            metadata['alt_record_ids'] = alt_records
            
            # Get metsDocumentID
            mets_doc_id = mets_hdr.find('.//mets:metsDocumentID', ns)
            if mets_doc_id is not None:
                metadata['mets_document_id'] = mets_doc_id.text
                metadata['mets_document_id_type'] = mets_doc_id.get('TYPE', 'UUID')
        
        # Get descriptive metadata
        dmd_sec = mets_root.find('.//mets:dmdSec', ns)
        if dmd_sec is not None:
            xml_data = dmd_sec.find('.//mets:xmlData', ns)
            if xml_data is not None:
                descriptive_metadata = {}
                for child in xml_data:
                    field_name = child.tag.split('}')[-1]  # Remove namespace
                    if field_name in self.dublin_core_fields:
                        descriptive_metadata[field_name] = child.text or ""
                metadata['descriptive_metadata'] = descriptive_metadata
        
        return metadata
    
    def _parse_dublin_core_xml(self, root):
        """Parse simple Dublin Core XML structure"""
        metadata = {
            'objid': f"SUBMISSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'package_type': 'SIP',
            'type': 'SIP',
            'profile': 'DIAS_SUBMISSION_DESCRIPTION',
            'record_status': 'NEW',
            'agents': [],
            'alt_record_ids': [],
            'mets_document_id': str(uuid.uuid4()),
            'mets_document_id_type': 'UUID'
        }
        
        descriptive_metadata = {}
        
        # Handle different XML structures
        if root.tag.endswith('metadata') or root.tag.endswith('dublin_core'):
            # Direct Dublin Core structure
            for child in root:
                field_name = child.tag.split('}')[-1]  # Remove namespace
                if field_name in self.dublin_core_fields:
                    descriptive_metadata[field_name] = child.text or ""
        else:
            # Look for Dublin Core elements anywhere in the XML
            for field in self.dublin_core_fields:
                elements = root.findall(f".//{field}") or root.findall(f".//dc:{field}", {'dc': 'http://purl.org/dc/elements/1.1/'})
                if elements:
                    descriptive_metadata[field] = elements[0].text or ""
                else:
                    descriptive_metadata[field] = ""
        
        metadata['descriptive_metadata'] = descriptive_metadata
        return metadata
    
    def _ensure_required_fields(self, metadata):
        """Ensure required fields have values"""
        # Ensure descriptive metadata exists
        if 'descriptive_metadata' not in metadata:
            metadata['descriptive_metadata'] = {}
        
        desc_meta = metadata['descriptive_metadata']
        
        # Ensure required Dublin Core fields
        if not desc_meta.get('title'):
            desc_meta['title'] = "DIAS Package"
        if not desc_meta.get('creator'):
            desc_meta['creator'] = "Unknown"
        if not desc_meta.get('identifier'):
            desc_meta['identifier'] = f"dias-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if not desc_meta.get('date'):
            desc_meta['date'] = datetime.now().isoformat()
        
        # Ensure submission fields
        if not metadata.get('objid'):
            metadata['objid'] = f"SUBMISSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        package_type = metadata.get('package_type') or metadata.get('type') or 'SIP'
        metadata['package_type'] = package_type
        metadata['type'] = package_type
        if not metadata.get('profile'):
            metadata['profile'] = 'DIAS_SUBMISSION_DESCRIPTION'
        if not metadata.get('agents'):
            logger.warning("No agents found in metadata — agents must be provided by user")
            metadata['agents'] = []
        if not metadata.get('alt_record_ids'):
            logger.warning("No alt_record_ids found in metadata — submission agreement must be provided by user")
            metadata['alt_record_ids'] = []

        if not metadata.get('related_aic_id'):
            metadata['related_aic_id'] = ''
        if not metadata.get('related_package_id'):
            metadata['related_package_id'] = ''
    
    def save_metadata_template(self, output_path):
        """Save a submission description metadata template XML file"""
        # Create submission description METS template
        from .submission_description_generator import SubmissionDescriptionMetsGenerator
        
        generator = SubmissionDescriptionMetsGenerator()
        
        # Sample submission data
        sample_data = {
            'objid': 'TEMPLATE_SUBMISSION_001',
            'package_type': 'SIP',
            'type': 'SIP',
            'profile': 'DIAS_SUBMISSION_DESCRIPTION',
            'label': 'Template Submission Description',
            'record_status': 'NEW',
            'agents': [
                {
                    'role': 'CREATOR',
                    'type': 'ORGANIZATION',
                    'name': 'Template Creator Organization',
                    'note': 'Organization responsible for creating this template'
                },
                {
                    'role': 'ARCHIVIST',
                    'type': 'ORGANIZATION',
                    'name': 'Template Archive Institution',
                    'note': 'Institution responsible for preservation'
                },
                {
                    'role': 'OTHER',
                    'otherrole': 'SUBMITTER',
                    'type': 'INDIVIDUAL',
                    'name': 'Template Submitter',
                    'note': 'Person submitting the package'
                }
            ],
            'alt_record_ids': [
                {'type': 'SUBMISSIONAGREEMENT', 'value': 'TEMPLATE_AGREEMENT_001'},
                {'type': 'PACKAGENUMBER', 'value': 'PKG_TEMPLATE_001'},
                {'type': 'REFERENCECODE', 'value': 'REF_TEMPLATE_001'},
                {'type': 'INFORMATIONCLASS', 'value': 'PUBLIC'}
            ],
            'mets_document_id': str(uuid.uuid4()),
            'mets_document_id_type': 'UUID',
            'descriptive_metadata': {
                'title': 'Template DIAS Package Title',
                'creator': 'Template Creator',
                'identifier': 'template-identifier-001',
                'subject': 'Template Subject',
                'description': 'Template description for DIAS package',
                'publisher': 'Template Publisher',
                'date': datetime.now().isoformat(),
                'type': 'Collection',
                'format': 'Digital',
                'language': 'en',
                'rights': 'Template rights statement'
            },
            'files': [
                {
                    'id': 'FILE_TEMPLATE_001',
                    'mimetype': 'application/pdf',
                    'size': 1048576,
                    'created': datetime.now().isoformat(),
                    'use': 'DATA',
                    'checksum': 'template_checksum_placeholder',
                    'checksumtype': 'MD5',
                    'path': 'files/template_document.pdf'
                }
            ],
            'structure': True
        }
        
        # Generate METS XML
        mets_xml = generator.create_submission_mets_xml(sample_data)
        generator.save_mets_xml(mets_xml, output_path)
        
        logger.info(f"Submission description template saved to: {output_path}")
        logger.info("Edit this file with your specific metadata values before using it.")
        
        # Also create a simple Dublin Core template
        dc_template_path = output_path.replace('.xml', '_dublin_core.xml')
        self._save_dublin_core_template(dc_template_path)
    
    def _save_dublin_core_template(self, output_path):
        """Save a simple Dublin Core template"""
        root = ET.Element("dublin_core")
        root.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")
        
        for field in self.dublin_core_fields:
            element = ET.SubElement(root, field)
            if field == 'title':
                element.text = "Sample DIAS Package Title"
            elif field == 'creator':
                element.text = "Sample Creator"
            elif field == 'identifier':
                element.text = "sample-identifier-001"
            elif field == 'date':
                element.text = datetime.now().isoformat()
            elif field == 'type':
                element.text = "Collection"
            elif field == 'format':
                element.text = "Digital"
            elif field == 'language':
                element.text = "en"
            elif field == 'rights':
                element.text = "All rights reserved"
            else:
                element.text = f"Sample {field}"
        
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        logger.info(f"Simple Dublin Core template saved to: {output_path}")
    
    def validate_metadata(self, metadata):
        """Validate submission description metadata completeness"""
        missing_required = []
        
        # Check submission description required fields
        if not metadata.get('objid') or not metadata['objid'].strip():
            missing_required.append('objid')
        
        package_type = metadata.get('package_type') or metadata.get('type')
        if not package_type or package_type not in self.valid_package_types:
            missing_required.append('package_type (must be one of: ' + ', '.join(self.valid_package_types) + ')')
        
        # Check minimum agents (3 required)
        agents = metadata.get('agents', [])
        if len(agents) < 3:
            missing_required.append('agents (minimum 3 required)')
        
        # Check minimum altRecordIDs (1 required, must include SUBMISSIONAGREEMENT)
        alt_records = metadata.get('alt_record_ids', [])
        if not alt_records:
            missing_required.append('alt_record_ids (minimum 1 required)')
        else:
            # Check for required SUBMISSIONAGREEMENT
            has_submission_agreement = any(
                record.get('type') == 'SUBMISSIONAGREEMENT' 
                for record in alt_records
            )
            if not has_submission_agreement:
                missing_required.append('alt_record_ids (must include SUBMISSIONAGREEMENT type)')
        
        # Check descriptive metadata required fields
        desc_meta = metadata.get('descriptive_metadata', {})
        desc_required = ['title', 'creator', 'identifier']
        
        for field in desc_required:
            if not desc_meta.get(field) or not desc_meta[field].strip():
                missing_required.append(f'descriptive_metadata.{field}')
        
        if missing_required:
            logger.warning(f"Missing required metadata fields: {', '.join(missing_required)}")
            return False
        
        return True
    
    def display_metadata(self, metadata):
        """Display submission description metadata for review"""
        print("\n=== Submission Description Metadata Summary ===")
        
        # Core submission info
        print("Core Submission Information:")
        print(f"  Object ID: {metadata.get('objid', 'Not set')}")
        package_type = metadata.get('package_type') or metadata.get('type', 'Not set')
        print(f"  Type: {package_type}")
        print(f"  Profile: {metadata.get('profile', 'Not set')}")
        print(f"  Label: {metadata.get('label', 'Not set')}")
        print(f"  Record Status: {metadata.get('record_status', 'Not set')}")
        
        # Agents
        agents = metadata.get('agents', [])
        print(f"\nAgents ({len(agents)}):")
        for i, agent in enumerate(agents, 1):
            role_info = agent.get('role', 'Unknown')
            if agent.get('otherrole'):
                role_info += f" ({agent['otherrole']})"
            print(f"  {i}. {agent.get('name', 'Unknown')} - {role_info} ({agent.get('type', 'Unknown')})")
        
        # Alternative Record IDs
        alt_records = metadata.get('alt_record_ids', [])
        print(f"\nAlternative Record IDs ({len(alt_records)}):")
        for record in alt_records:
            print(f"  {record.get('type', 'Unknown')}: {record.get('value', 'Not set')}")
        
        # Descriptive metadata
        desc_meta = metadata.get('descriptive_metadata', {})
        print("\nDescriptive Metadata (Dublin Core):")
        for field, value in desc_meta.items():
            if value:
                print(f"  {field.capitalize()}: {value}")
        
        print("=" * 50)
    
    def get_submission_metadata_from_terminal(self):
        """Legacy method - redirect to main method"""
        return self.get_metadata_from_terminal()

    def _get_choice(self, prompt, choices, default):
        """Helper to get choice from list"""
        print(f"\n{prompt} options: {', '.join(choices)}")
        choice = input(f"Choose {prompt} (default: {default}): ").strip()
        return choice if choice in choices else default

    def _collect_agents(self):
        """Collect agent information (minimum 3 required)"""
        agents = []
        agent_roles = ["CREATOR", "EDITOR", "ARCHIVIST", "PRESERVATION", "DISSEMINATOR", "CUSTODIAN", "IPOWNER", "OTHER"]
        agent_types = ["INDIVIDUAL", "ORGANIZATION", "OTHER"]
        
        for i in range(3):  # Minimum 3 agents
            print(f"\n--- Agent {i+1} (required) ---")
            agent = {
                'role': self._get_choice("Role", agent_roles, "CREATOR"),
                'type': self._get_choice("Type", agent_types, "ORGANIZATION"),
                'name': input("Name* (required): ").strip() or f"Agent {i+1}"
            }
            
            if agent['role'] == 'OTHER':
                agent['otherrole'] = self._get_choice("Other Role", ["SUBMITTER", "PRODUCER"], "SUBMITTER")
            if agent['type'] == 'OTHER':
                agent['othertype'] = "SOFTWARE"
                
            note = input("Note (optional): ").strip()
            if note:
                agent['note'] = note
                
            agents.append(agent)
        
        return agents

    def _collect_alt_record_ids(self):
        """Collect alternative record IDs (minimum 1 required)"""
        alt_records = []
        alt_record_types = [
            "SUBMISSIONAGREEMENT", "DELIVERYTYPE", "DELIVERYSPECIFICATION", 
            "PACKAGENUMBER", "REFERENCECODE", "STARTDATE", "ENDDATE", 
            "INFORMATIONCLASS", "SYSTEMTYPE"
        ]
        
        # Mandatory submission agreement
        print(f"\n--- Alternative Record ID 1 (Submission Agreement - required) ---")
        alt_records.append({
            'type': 'SUBMISSIONAGREEMENT',
            'value': input("Submission Agreement ID* (required): ").strip()
        })
        
        # Optional additional IDs
        add_more = input("\nAdd more alternative record IDs? (y/N): ").strip().lower() == 'y'
        while add_more:
            record_type = self._get_choice("Record Type", alt_record_types, "PACKAGENUMBER")
            value = input(f"Value for {record_type}: ").strip()
            if value:
                alt_records.append({'type': record_type, 'value': value})
            add_more = input("Add another? (y/N): ").strip().lower() == 'y'
        
        return alt_records

    def save_metadata_to_xml(self, output_path, metadata):
        """
        Save metadata dictionary to an XML file.
        
        Args:
            output_path: Path to save the XML file.
            metadata: Dictionary containing metadata (can be GUI form format or full format).
        """
        # Convert GUI form metadata to full format if needed
        full_metadata = self._convert_gui_metadata(metadata)
        
        # Create submission description METS
        from .submission_description_generator import SubmissionDescriptionMetsGenerator
        
        generator = SubmissionDescriptionMetsGenerator()
        mets_xml = generator.create_submission_mets_xml(full_metadata)
        generator.save_mets_xml(mets_xml, output_path)
        
        logger.info(f"Metadata saved to: {output_path}")
    
    def _convert_gui_metadata(self, metadata):
        """
        Convert GUI form metadata to full submission description format.
        
        Args:
            metadata: Dictionary with GUI form field names.
            
        Returns:
            Dictionary in full submission description format.
        """
        # Check if already in full format
        if 'descriptive_metadata' in metadata:
            package_type = metadata.get('package_type') or metadata.get('type')
            if package_type:
                metadata['package_type'] = package_type
                metadata['type'] = package_type
            return metadata
            
        # Build agents list based on new DIAS form fields
        agents = []
        
        # ARCHIVIST - Organization
        if metadata.get('archivist_organization'):
            agents.append({
                'role': 'ARCHIVIST',
                'type': 'ORGANIZATION',
                'name': metadata['archivist_organization']
            })
        
        # ARCHIVIST - Software (system name)
        if metadata.get('system_name'):
            agents.append({
                'role': 'ARCHIVIST',
                'type': 'OTHER',
                'othertype': 'SOFTWARE',
                'name': metadata['system_name']
            })
        
        # ARCHIVIST - Software (version)
        if metadata.get('system_version'):
            agents.append({
                'role': 'ARCHIVIST',
                'type': 'OTHER',
                'othertype': 'SOFTWARE',
                'name': metadata['system_version']
            })
        
        # ARCHIVIST - Software (format)
        if metadata.get('system_format'):
            agents.append({
                'role': 'ARCHIVIST',
                'type': 'OTHER',
                'othertype': 'SOFTWARE',
                'name': metadata['system_format']
            })
        
        # CREATOR - Organization (IKA)
        if metadata.get('creator_organization'):
            agents.append({
                'role': 'CREATOR',
                'type': 'ORGANIZATION',
                'name': metadata['creator_organization']
            })
        
        # PRODUCER - Organization
        if metadata.get('producer_organization'):
            agents.append({
                'role': 'OTHER',
                'otherrole': 'PRODUCER',
                'type': 'ORGANIZATION',
                'name': metadata['producer_organization']
            })
        
        # PRODUCER - Individual
        if metadata.get('producer_individual'):
            agents.append({
                'role': 'OTHER',
                'otherrole': 'PRODUCER',
                'type': 'INDIVIDUAL',
                'name': metadata['producer_individual']
            })
        
        # PRODUCER - Software
        if metadata.get('producer_software'):
            agents.append({
                'role': 'OTHER',
                'otherrole': 'PRODUCER',
                'type': 'OTHER',
                'othertype': 'SOFTWARE',
                'name': metadata['producer_software']
            })
        
        # SUBMITTER - Organization
        if metadata.get('submitter_organization'):
            agents.append({
                'role': 'OTHER',
                'otherrole': 'SUBMITTER',
                'type': 'ORGANIZATION',
                'name': metadata['submitter_organization']
            })
        
        # SUBMITTER - Individual
        if metadata.get('submitter_individual'):
            agents.append({
                'role': 'OTHER',
                'otherrole': 'SUBMITTER',
                'type': 'INDIVIDUAL',
                'name': metadata['submitter_individual']
            })
        
        # IPOWNER - Organization
        if metadata.get('ipowner_organization'):
            agents.append({
                'role': 'IPOWNER',
                'type': 'ORGANIZATION',
                'name': metadata['ipowner_organization']
            })
        
        # PRESERVATION - Organization
        if metadata.get('preservation_organization'):
            agents.append({
                'role': 'PRESERVATION',
                'type': 'ORGANIZATION',
                'name': metadata['preservation_organization']
            })
        
        # Build altRecordID list
        alt_record_ids = []
        
        if metadata.get('submission_agreement'):
            alt_record_ids.append({
                'type': 'SUBMISSIONAGREEMENT',
                'value': metadata['submission_agreement']
            })
        
        if metadata.get('start_date'):
            alt_record_ids.append({
                'type': 'STARTDATE',
                'value': metadata['start_date']
            })
        
        if metadata.get('end_date'):
            alt_record_ids.append({
                'type': 'ENDDATE',
                'value': metadata['end_date']
            })

        relation_type = metadata.get('relation_type', '')
        record_status = metadata.get('record_status', 'NEW')
        if not relation_type:
            relation_type = {
                'SUPPLEMENT': 'supplements',
                'REPLACEMENT': 'replaces'
            }.get(str(record_status).upper(), '')

        if metadata.get('related_aic_id'):
            alt_record_ids.append({
                'type': 'RELATEDAIC',
                'value': metadata['related_aic_id']
            })

        if metadata.get('related_package_id'):
            alt_record_ids.append({
                'type': 'RELATEDPACKAGE',
                'value': metadata['related_package_id']
            })

        if relation_type:
            alt_record_ids.append({
                'type': 'RELATIONTYPE',
                'value': relation_type
            })
        
        package_type = metadata.get('package_type') or metadata.get('type') or 'SIP'

        # Convert from GUI format
        full_metadata = {
            'objid': f"SUBMISSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'package_type': package_type,
            'type': package_type,
            'profile': 'http://xml.ra.se/METS/RA_METS_eARD.xml',
            'label': metadata.get('label', ''),
            'record_status': metadata.get('record_status', 'NEW'),
            'related_aic_id': metadata.get('related_aic_id', ''),
            'related_package_id': metadata.get('related_package_id', ''),
            'relation_type': relation_type,
            'agents': agents if agents else [
                {'role': 'CREATOR', 'type': 'OTHER', 'othertype': 'SOFTWARE', 'name': 'DIAS Package Creator'}
            ],
            'alt_record_ids': alt_record_ids if alt_record_ids else [],
            'mets_document_id': str(uuid.uuid4()),
            'mets_document_id_type': 'UUID',
            'descriptive_metadata': {
                'title': metadata.get('label', ''),
                'creator': metadata.get('creator_organization', ''),
                'identifier': f"dias-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'subject': 'Digital Archive',
                'description': '',
                'publisher': 'DIAS Package Creator',
                'date': datetime.now().isoformat(),
                'type': 'Collection',
                'format': metadata.get('system_format', 'Digital'),
                'language': 'no',
                'rights': 'All rights reserved'
            },
            'structure': True
        }
        
        return full_metadata