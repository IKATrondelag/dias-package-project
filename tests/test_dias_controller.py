"""
Tests for DIAS Package Controller.
Tests validate_inputs, callback wiring, cancellation, and file processing utilities.
"""

import os
import shutil
import tempfile
import unittest

from src.core.dias_controller import PackageController
from src.utils.validation import ValidationResult


class TestControllerInit(unittest.TestCase):
    """Tests for controller initialization."""
    
    def test_init_creates_controller(self):
        """Constructor should succeed and set up components."""
        controller = PackageController()
        self.assertIsNotNone(controller.job_manager)
        self.assertIsNotNone(controller.file_processor)
        self.assertIsNotNone(controller.info_generator)
        self.assertIsNotNone(controller.mets_generator)
        self.assertIsNotNone(controller.log_generator)
    
    def test_callbacks_initially_none(self):
        """Callbacks should be None before being set."""
        controller = PackageController()
        self.assertIsNone(controller._progress_callback)
        self.assertIsNone(controller._log_callback)
        self.assertIsNone(controller._completion_callback)


class TestControllerCallbacks(unittest.TestCase):
    """Tests for callback registration."""
    
    def setUp(self):
        self.controller = PackageController()
    
    def test_set_progress_callback(self):
        """Setting progress callback should register it."""
        cb = lambda v, s: None
        self.controller.set_progress_callback(cb)
        self.assertEqual(self.controller._progress_callback, cb)
    
    def test_set_log_callback(self):
        """Setting log callback should register it."""
        cb = lambda m, l: None
        self.controller.set_log_callback(cb)
        self.assertEqual(self.controller._log_callback, cb)
    
    def test_set_completion_callback(self):
        """Setting completion callback should register it."""
        cb = lambda s, m: None
        self.controller.set_completion_callback(cb)
        self.assertEqual(self.controller._completion_callback, cb)
    
    def test_log_with_callback(self):
        """_log should invoke the log callback."""
        messages = []
        self.controller.set_log_callback(lambda msg, level: messages.append((msg, level)))
        self.controller._log("test message", "DEBUG")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], ("test message", "DEBUG"))
    
    def test_log_without_callback(self):
        """_log should not fail when no callback is set."""
        self.controller._log("no callback")  # Should not raise
    
    def test_update_progress_with_callback(self):
        """_update_progress should invoke the progress callback."""
        updates = []
        self.controller.set_progress_callback(lambda v, s: updates.append((v, s)))
        self.controller._update_progress(50.0, "Half done")
        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0], (50.0, "Half done"))
    
    def test_update_progress_without_callback(self):
        """_update_progress should not fail when no callback is set."""
        self.controller._update_progress(50.0, "Half done")  # Should not raise


class TestControllerValidation(unittest.TestCase):
    """Tests for input validation through the controller."""
    
    def setUp(self):
        self.controller = PackageController()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test source file
        self.test_file = os.path.join(self.temp_dir, 'source.txt')
        with open(self.test_file, 'w') as f:
            f.write('test content')
        
        self.output_dir = os.path.join(self.temp_dir, 'output')
        os.makedirs(self.output_dir)
        
        self.valid_metadata = {
            'package_type': 'SIP',
            'label': 'Test Package',
            'system_name': 'TestSystem',
            'system_type': 'Fagsystem',
            'archivist_organization': 'Test Archive',
            'creator_organization': 'Test Creator',
            'submission_agreement': 'AGR-001',
            'agreement_id': 'AGR-001',
            'start_date': '2020-01-01',
            'end_date': '2023-12-31',
        }
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_validate_valid_inputs(self):
        """Valid inputs should pass validation."""
        result = self.controller.validate_inputs(
            self.test_file, self.output_dir, "TestPackage", self.valid_metadata
        )
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid())
    
    def test_validate_invalid_source(self):
        """Missing source path should fail validation."""
        result = self.controller.validate_inputs(
            "/nonexistent/path", self.output_dir, "TestPackage", self.valid_metadata
        )
        self.assertFalse(result.is_valid())
    
    def test_validate_empty_package_name(self):
        """Empty package name should fail validation."""
        result = self.controller.validate_inputs(
            self.test_file, self.output_dir, "", self.valid_metadata
        )
        self.assertFalse(result.is_valid())


class TestControllerCancellation(unittest.TestCase):
    """Tests for cancellation checking."""
    
    def setUp(self):
        self.controller = PackageController()
    
    def test_check_cancelled_not_cancelled(self):
        """_check_cancelled should not raise when job is not cancelled."""
        self.controller._check_cancelled()  # Should not raise
    
    def test_check_cancelled_when_cancelled(self):
        """_check_cancelled should raise InterruptedError when job is cancelled."""
        self.controller.job_manager.cancel_job()
        with self.assertRaises(InterruptedError):
            self.controller._check_cancelled()


class TestControllerCopyFile(unittest.TestCase):
    """Tests for _copy_file_with_info utility."""
    
    def setUp(self):
        self.controller = PackageController()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create source file
        self.src_file = os.path.join(self.temp_dir, 'source', 'test.txt')
        os.makedirs(os.path.dirname(self.src_file))
        with open(self.src_file, 'w') as f:
            f.write('Hello World')
        
        # Create destination directory
        self.dest_dir = os.path.join(self.temp_dir, 'dest')
        os.makedirs(self.dest_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_copy_file_returns_info(self):
        """_copy_file_with_info should copy file and return metadata dict."""
        from pathlib import Path
        src = Path(self.src_file)
        dest = Path(self.dest_dir) / 'test.txt'
        base = Path(self.dest_dir)
        
        info = self.controller._copy_file_with_info(src, dest, base)
        
        self.assertIsNotNone(info)
        self.assertTrue(dest.exists())
        self.assertIn('path', info)
        self.assertIn('checksum', info)
        self.assertIn('size', info)
        self.assertIn('mimetype', info)
        self.assertEqual(info['name'], 'test.txt')
        self.assertGreater(info['size'], 0)
    
    def test_copy_file_checksum_is_sha256(self):
        """Checksum should be a 64-character hex string (SHA-256)."""
        from pathlib import Path
        src = Path(self.src_file)
        dest = Path(self.dest_dir) / 'test.txt'
        base = Path(self.dest_dir)
        
        info = self.controller._copy_file_with_info(src, dest, base)
        self.assertEqual(len(info['checksum']), 64)
    
    def test_copy_nonexistent_file(self):
        """Copying a nonexistent file should return None."""
        from pathlib import Path
        src = Path(self.temp_dir) / 'nonexistent.txt'
        dest = Path(self.dest_dir) / 'nonexistent.txt'
        base = Path(self.dest_dir)
        
        info = self.controller._copy_file_with_info(src, dest, base)
        self.assertIsNone(info)


class TestControllerPremisAgentFiltering(unittest.TestCase):
    """Tests for PREMIS agent inclusion filtering by SIP/AIP level."""

    def setUp(self):
        self.controller = PackageController()
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, 'source')
        self.output_dir = os.path.join(self.temp_dir, 'output')
        os.makedirs(self.source_dir)
        os.makedirs(self.output_dir)

        with open(os.path.join(self.source_dir, 'doc.txt'), 'w', encoding='utf-8') as f:
            f.write('test content')

        self.metadata = {
            'package_type': 'SIP',
            'label': 'Filter Test Package',
            'record_status': 'NEW',
            'archivist_organization': 'Test Archive',
            'system_name': 'Test System',
            'creator_organization': 'Test Creator',
            'submission_agreement': 'AGR-001',
            'start_date': '2020-01-01',
            'end_date': '2023-12-31',
            'premis_events': [],
            'premis_agents': [
                {
                    'agent_name': 'Both Agent',
                    'agent_type': 'software',
                    'agent_id_type': 'NO/RA',
                    'agent_id_value': 'both',
                    'include_sip': True,
                    'include_aip': True,
                },
                {
                    'agent_name': 'SIP Only Agent',
                    'agent_type': 'organization',
                    'agent_id_type': 'NO/RA',
                    'agent_id_value': 'sip-only',
                    'include_sip': True,
                    'include_aip': False,
                },
                {
                    'agent_name': 'AIP Only Agent',
                    'agent_type': 'person',
                    'agent_id_type': 'NO/RA',
                    'agent_id_value': 'aip-only',
                    'include_sip': False,
                    'include_aip': True,
                },
            ],
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_agents_filtered_between_sip_and_aip_logs(self):
        """SIP logs and AIP log should receive different agent sets by include flags."""
        captured_agents = []
        original_create_log_xml = self.controller.log_generator.create_log_xml

        def wrapped_create_log_xml(*args, **kwargs):
            captured_agents.append(kwargs.get('agents'))
            return original_create_log_xml(*args, **kwargs)

        self.controller.log_generator.create_log_xml = wrapped_create_log_xml

        success, _ = self.controller._create_package_task(
            source_path=self.source_dir,
            output_path=self.output_dir,
            package_name='filter-test',
            metadata=self.metadata,
        )

        self.assertTrue(success)
        self.assertEqual(len(captured_agents), 3)

        sip_premis_agents = captured_agents[0]
        sip_log_agents = captured_agents[1]
        aip_log_agents = captured_agents[2]

        self.assertEqual({a['agent_name'] for a in sip_premis_agents}, {'Both Agent', 'SIP Only Agent'})
        self.assertEqual({a['agent_name'] for a in sip_log_agents}, {'Both Agent', 'SIP Only Agent'})
        self.assertEqual({a['agent_name'] for a in aip_log_agents}, {'Both Agent', 'AIP Only Agent'})


if __name__ == '__main__':
    unittest.main()
