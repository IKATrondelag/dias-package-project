"""
Unit tests for DIAS Package Creator.
Tests cover XML generators, file processor, and controller components.
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
from datetime import datetime

# Import from refactored modules
from src.dias_package_creator.dias_xml_generators import (
    DIASMetsGenerator, 
    DIASLogGenerator,
    DIASInfoGenerator
)
from src.dias_package_creator.metadata_handler import MetadataHandler
from src.utils.file_processor import FileProcessor


class TestDIASMetsGenerator(unittest.TestCase):
    """Tests for METS XML generation."""
    
    def setUp(self):
        self.generator = DIASMetsGenerator()
        self.sample_metadata = {
            'package_type': 'SIP',
            'label': 'Test DIAS Package',
            'archivist_organization': 'Test Archive',
            'system_name': 'Test System',
            'creator_organization': 'Test Creator'
        }
        self.sample_files = [
            {
                'path': 'content/test.txt',
                'checksum': 'abc123',
                'size': 1024,
                'mimetype': 'text/plain',
                'name': 'test.txt'
            }
        ]
        
    def test_create_mets_xml(self):
        """Test METS XML creation."""
        sip_uuid = 'test-uuid-123'
        mets = self.generator.create_mets_xml(
            metadata=self.sample_metadata,
            sip_uuid=sip_uuid,
            files_info=self.sample_files
        )
        self.assertIsNotNone(mets)
        # Check root element
        self.assertTrue(mets.tag.endswith('mets'))
        
    def test_mets_has_required_sections(self):
        """Test that METS has all required sections."""
        sip_uuid = 'test-uuid-123'
        mets = self.generator.create_mets_xml(
            metadata=self.sample_metadata,
            sip_uuid=sip_uuid,
            files_info=self.sample_files
        )
        
        # Find sections (accounting for namespace)
        sections = [child.tag.split('}')[-1] for child in mets]
        
        self.assertIn('metsHdr', sections)
        self.assertIn('fileSec', sections)
        self.assertIn('structMap', sections)
        
    def test_save_mets_xml(self):
        """Test saving METS XML to file."""
        sip_uuid = 'test-uuid-123'
        mets = self.generator.create_mets_xml(
            metadata=self.sample_metadata,
            sip_uuid=sip_uuid,
            files_info=self.sample_files
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            temp_path = f.name
            
        try:
            self.generator.save(mets, temp_path)
            self.assertTrue(os.path.exists(temp_path))
            
            # Verify XML content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('<?xml', content)
                self.assertIn('mets', content)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_mets_type_uses_package_type(self):
        """METS TYPE should reflect selected package type."""
        metadata = {**self.sample_metadata, 'package_type': 'AIP'}
        mets = self.generator.create_mets_xml(
            metadata=metadata,
            sip_uuid='test-uuid-123',
            files_info=self.sample_files
        )
        self.assertEqual(mets.get('TYPE'), 'AIP')

    def test_mets_supplement_includes_relation_alt_record_ids(self):
        """Supplement/replacement metadata should be reflected as relation altRecordIDs."""
        metadata = {
            **self.sample_metadata,
            'record_status': 'SUPPLEMENT',
            'related_aic_id': 'aic-abc',
            'related_package_id': 'pkg-def'
        }
        mets = self.generator.create_mets_xml(
            metadata=metadata,
            sip_uuid='test-uuid-123',
            files_info=self.sample_files
        )
        alt_record_ids = [
            elem for elem in mets.iter()
            if elem.tag.split('}')[-1] == 'altRecordID'
        ]
        alt_map = {elem.get('TYPE'): elem.text for elem in alt_record_ids}

        self.assertEqual(alt_map.get('RELATEDAIC'), 'aic-abc')
        self.assertEqual(alt_map.get('RELATEDPACKAGE'), 'pkg-def')
        self.assertEqual(alt_map.get('RELATIONTYPE'), 'supplements')


class TestDIASLogGenerator(unittest.TestCase):
    """Tests for Log (PREMIS) XML generation."""
    
    def setUp(self):
        self.generator = DIASLogGenerator()
        self.sample_metadata = {
            'label': 'Test Package',
            'archivist_organization': 'Test Archive'
        }
        
    def test_create_log_xml(self):
        """Test log XML creation."""
        object_uuid = 'test-uuid-123'
        log = self.generator.create_log_xml(
            metadata=self.sample_metadata,
            object_uuid=object_uuid
        )
        self.assertIsNotNone(log)
        self.assertTrue(log.tag.endswith('premis'))
        
    def test_log_has_object(self):
        """Test log has object element."""
        object_uuid = 'test-uuid-123'
        log = self.generator.create_log_xml(
            metadata=self.sample_metadata,
            object_uuid=object_uuid
        )
        
        # Find object element
        objects = [child for child in log if child.tag.split('}')[-1] == 'object']
        self.assertGreater(len(objects), 0)

    def test_log_replacement_includes_related_reference_properties(self):
        """PREMIS should include relation properties for replacement/supplement records."""
        metadata = {
            **self.sample_metadata,
            'record_status': 'REPLACEMENT',
            'related_aic_id': 'aic-old',
            'related_package_id': 'pkg-old'
        }
        log = self.generator.create_log_xml(
            metadata=metadata,
            object_uuid='uuid-123',
            aic_uuid='aic-current'
        )

        sig_props = [
            elem for elem in log.iter()
            if elem.tag.split('}')[-1] == 'significantProperties'
        ]
        sig_map = {}
        for sig in sig_props:
            prop_type = None
            prop_value = None
            for child in sig:
                local = child.tag.split('}')[-1]
                if local == 'significantPropertiesType':
                    prop_type = child.text
                elif local == 'significantPropertiesValue':
                    prop_value = child.text
            if prop_type:
                sig_map[prop_type] = prop_value

        self.assertEqual(sig_map.get('record_status'), 'REPLACEMENT')
        self.assertEqual(sig_map.get('relation_type'), 'replaces')
        self.assertEqual(sig_map.get('related_aic_id'), 'aic-old')
        self.assertEqual(sig_map.get('related_package_id'), 'pkg-old')


class TestDIASInfoGenerator(unittest.TestCase):
    """Tests for Info XML generation."""
    
    def setUp(self):
        self.generator = DIASInfoGenerator()
        self.sample_metadata = {
            'package_type': 'SIP',
            'label': 'Test Package',
            'archivist_organization': 'Test Archive',
            'system_name': 'Test System'
        }
        
    def test_create_info_xml(self):
        """Test info XML creation."""
        aip_uuid = 'aip-uuid-123'
        aic_uuid = 'aic-uuid-123'
        info = self.generator.create_info_xml(
            metadata=self.sample_metadata,
            aip_uuid=aip_uuid,
            aic_uuid=aic_uuid
        )
        self.assertIsNotNone(info)
        self.assertTrue(info.tag.endswith('mets'))
        
    def test_info_has_required_sections(self):
        """Test that info has required sections."""
        aip_uuid = 'aip-uuid-123'
        aic_uuid = 'aic-uuid-123'
        info = self.generator.create_info_xml(
            metadata=self.sample_metadata,
            aip_uuid=aip_uuid,
            aic_uuid=aic_uuid
        )
        
        sections = [child.tag.split('}')[-1] for child in info]
        self.assertIn('metsHdr', sections)

    def test_info_type_uses_package_type(self):
        """info.xml TYPE should reflect selected package type."""
        metadata = {**self.sample_metadata, 'package_type': 'DIP'}
        info = self.generator.create_info_xml(
            metadata=metadata,
            aip_uuid='aip-uuid-123',
            aic_uuid='aic-uuid-123'
        )
        self.assertEqual(info.get('TYPE'), 'DIP')


class TestFileProcessor(unittest.TestCase):
    """Tests for file processing utilities."""
    
    def setUp(self):
        self.processor = FileProcessor()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test file
        self.test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(self.test_file, 'w') as f:
            f.write('Test content for file processing.')
            
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        
    def test_analyze_file(self):
        """Test file analysis."""
        info = self.processor.analyze_file(self.test_file)
        
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'test.txt')
        self.assertIn('size', info)
        self.assertIn('mimetype', info)
        
    def test_calculate_checksum(self):
        """Test checksum calculation."""
        checksum = self.processor.calculate_checksum(self.test_file, 'SHA256')
        
        self.assertIsNotNone(checksum)
        self.assertEqual(len(checksum), 64)
        
    def test_copy_with_checksum(self):
        """Test file copy with checksum."""
        dest = os.path.join(self.temp_dir, 'copy.txt')
        
        info = self.processor.copy_with_checksum(self.test_file, dest)
        
        self.assertIsNotNone(info)
        self.assertTrue(os.path.exists(dest))
        self.assertIn('checksum', info)
        self.assertIn('checksumtype', info)
        
    def test_get_mimetype(self):
        """Test MIME type detection."""
        mimetype = self.processor.get_mimetype(self.test_file)
        self.assertEqual(mimetype, 'text/plain')
        
    def test_verify_checksum(self):
        """Test checksum verification."""
        checksum = self.processor.calculate_checksum(self.test_file, 'SHA256')
        
        # Should pass with correct checksum
        self.assertTrue(self.processor.verify_checksum(self.test_file, checksum, 'SHA256'))
        
        # Should fail with wrong checksum
        self.assertFalse(self.processor.verify_checksum(self.test_file, 'wrong', 'SHA256'))
        
    def test_get_directory_size(self):
        """Test directory size calculation."""
        # Create additional files
        with open(os.path.join(self.temp_dir, 'file2.txt'), 'w') as f:
            f.write('More content')
            
        size = self.processor.get_directory_size(self.temp_dir)
        self.assertGreater(size, 0)


class TestMetadataHandler(unittest.TestCase):
    """Tests for metadata handling."""
    
    def setUp(self):
        self.handler = MetadataHandler()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        
    def test_validate_metadata_success(self):
        """Test metadata validation with valid data."""
        metadata = {
            'objid': 'TEST-001',
            'type': 'SIP',
            'agents': [
                {'role': 'CREATOR', 'name': 'Test'},
                {'role': 'ARCHIVIST', 'name': 'Archive'},
                {'role': 'OTHER', 'name': 'User'}
            ],
            'alt_record_ids': [
                {'type': 'SUBMISSIONAGREEMENT', 'value': 'AGR-001'}
            ],
            'descriptive_metadata': {
                'title': 'Test Package',
                'creator': 'Creator',
                'identifier': 'ID-001'
            }
        }
        
        self.assertTrue(self.handler.validate_metadata(metadata))
        
    def test_validate_metadata_missing_fields(self):
        """Test metadata validation with missing fields."""
        metadata = {
            'objid': 'TEST-001',
            'type': 'INVALID_TYPE',  # Invalid
            'agents': [],  # Not enough
            'alt_record_ids': [],  # Missing
            'descriptive_metadata': {}  # Missing required
        }
        
        self.assertFalse(self.handler.validate_metadata(metadata))
        
    @unittest.skip("save_metadata_template needs to be updated to use new generators")
    def test_save_metadata_template(self):
        """Test metadata template saving."""
        template_path = os.path.join(self.temp_dir, 'template.xml')
        
        self.handler.save_metadata_template(template_path)
        
        self.assertTrue(os.path.exists(template_path))
        
        with open(template_path, 'r') as f:
            content = f.read()
            self.assertIn('mets', content)
            
    def test_convert_gui_metadata(self):
        """Test GUI metadata conversion."""
        gui_metadata = {
            'package_type': 'SIP',
            'label': 'Test Package',
            'archivist_organization': 'Test Archive',
            'system_name': 'Test System',
            'creator_organization': 'Test Creator',
            'submission_agreement': 'AGR-001'
        }
        
        full_metadata = self.handler._convert_gui_metadata(gui_metadata)
        
        self.assertIn('agents', full_metadata)
        self.assertEqual(full_metadata['package_type'], 'SIP')
        self.assertEqual(full_metadata['type'], 'SIP')
        # Metadata conversion creates agents from GUI fields
        self.assertGreater(len(full_metadata['agents']), 0)

    def test_convert_gui_metadata_preserves_relation_fields(self):
        """GUI relation fields should be mapped into metadata and altRecordIDs."""
        gui_metadata = {
            'package_type': 'SIP',
            'label': 'Test Package',
            'record_status': 'SUPPLEMENT',
            'archivist_organization': 'Test Archive',
            'system_name': 'Test System',
            'creator_organization': 'Test Creator',
            'submission_agreement': 'AGR-001',
            'related_aic_id': 'aic-prev',
            'related_package_id': 'pkg-prev'
        }

        full_metadata = self.handler._convert_gui_metadata(gui_metadata)

        self.assertEqual(full_metadata['related_aic_id'], 'aic-prev')
        self.assertEqual(full_metadata['related_package_id'], 'pkg-prev')
        self.assertEqual(full_metadata['relation_type'], 'supplements')
        alt_types = {entry['type'] for entry in full_metadata['alt_record_ids']}
        self.assertIn('RELATEDAIC', alt_types)
        self.assertIn('RELATEDPACKAGE', alt_types)
        self.assertIn('RELATIONTYPE', alt_types)


if __name__ == '__main__':
    unittest.main()