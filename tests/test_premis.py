"""
Tests for PREMIS preservation features.
Covers DIASLogGenerator user events/agents, ConfigLoader PREMIS section,
and PremisForm widget data round-trip.
"""

import unittest
import tempfile
import os
import xml.etree.ElementTree as ET

from src.dias_package_creator.dias_xml_generators import DIASLogGenerator
from src.utils.config_loader import ConfigLoader


class TestDIASLogGeneratorUserEvents(unittest.TestCase):
    """Tests for user-defined PREMIS events in log.xml generation."""

    def setUp(self):
        self.generator = DIASLogGenerator()
        self.metadata = {
            'label': 'Test Package',
            'archivist_organization': 'Test Archive',
            'package_type': 'SIP',
        }
        self.premis_ns = 'http://arkivverket.no/standarder/PREMIS'

    def _find_elements(self, root, local_name):
        """Find all elements with a given local name."""
        return [el for el in root.iter() if el.tag.split('}')[-1] == local_name]

    def test_no_user_events_backward_compat(self):
        """create_log_xml without user_events still produces one auto-event."""
        root = self.generator.create_log_xml(
            metadata=self.metadata,
            object_uuid='uuid-123',
        )
        events = self._find_elements(root, 'event')
        self.assertEqual(len(events), 1)  # Only the auto event

    def test_user_events_added(self):
        """User events appear after the automatic event."""
        user_events = [
            {
                'event_type': 'Migration',
                'event_detail': 'Migrated from NOARK-4 to NOARK-5',
                'event_outcome': '0',
                'event_outcome_detail': 'Migration successful',
                'event_date': '2024-06-01',
            },
            {
                'event_type': 'Ingestion',
                'event_detail': 'Ingested into archive',
                'event_outcome': '0',
                'event_outcome_detail': '',
                'event_date': '',
            },
        ]
        root = self.generator.create_log_xml(
            metadata=self.metadata,
            object_uuid='uuid-123',
            user_events=user_events,
        )
        events = self._find_elements(root, 'event')
        # 1 auto + 2 user = 3
        self.assertEqual(len(events), 3)

    def test_user_event_type_correct(self):
        """User event type is written correctly."""
        user_events = [{'event_type': 'Disposal', 'event_detail': '', 'event_outcome': '0',
                        'event_outcome_detail': '', 'event_date': ''}]
        root = self.generator.create_log_xml(
            metadata=self.metadata, object_uuid='uuid-123',
            user_events=user_events,
        )
        events = self._find_elements(root, 'event')
        # Second event is the user event
        user_event = events[1]
        event_type = [el for el in user_event if el.tag.split('}')[-1] == 'eventType'][0]
        self.assertEqual(event_type.text, 'Disposal')

    def test_user_event_date_used(self):
        """User-provided event date is used when present."""
        user_events = [{'event_type': 'Creation', 'event_detail': 'test',
                        'event_outcome': '0', 'event_outcome_detail': '',
                        'event_date': '2024-03-15'}]
        root = self.generator.create_log_xml(
            metadata=self.metadata, object_uuid='uuid-123',
            user_events=user_events,
        )
        events = self._find_elements(root, 'event')
        user_event = events[1]
        event_datetime = [el for el in user_event if el.tag.split('}')[-1] == 'eventDateTime'][0]
        self.assertEqual(event_datetime.text, '2024-03-15')

    def test_user_event_date_auto_when_empty(self):
        """When user event date is empty, a timestamp is auto-generated."""
        user_events = [{'event_type': 'Creation', 'event_detail': 'test',
                        'event_outcome': '0', 'event_outcome_detail': '',
                        'event_date': ''}]
        root = self.generator.create_log_xml(
            metadata=self.metadata, object_uuid='uuid-123',
            user_events=user_events,
        )
        events = self._find_elements(root, 'event')
        user_event = events[1]
        event_datetime = [el for el in user_event if el.tag.split('}')[-1] == 'eventDateTime'][0]
        # Should have a timestamp, not be empty
        self.assertTrue(len(event_datetime.text) > 0)

    def test_user_event_outcome_detail_omitted_when_empty(self):
        """eventOutcomeDetailNote is omitted when outcome detail is empty."""
        user_events = [{'event_type': 'Creation', 'event_detail': 'test',
                        'event_outcome': '0', 'event_outcome_detail': '',
                        'event_date': ''}]
        root = self.generator.create_log_xml(
            metadata=self.metadata, object_uuid='uuid-123',
            user_events=user_events,
        )
        events = self._find_elements(root, 'event')
        user_event = events[1]
        outcome_details = [el for el in user_event.iter()
                          if el.tag.split('}')[-1] == 'eventOutcomeDetailNote']
        self.assertEqual(len(outcome_details), 0)


class TestDIASLogGeneratorAgents(unittest.TestCase):
    """Tests for PREMIS agent generation."""

    def setUp(self):
        self.generator = DIASLogGenerator()
        self.metadata = {
            'label': 'Test Package',
            'archivist_organization': 'Test Archive',
            'package_type': 'SIP',
        }
        self.premis_ns = 'http://arkivverket.no/standarder/PREMIS'

    def _find_elements(self, root, local_name):
        return [el for el in root.iter() if el.tag.split('}')[-1] == local_name]

    def test_no_agents_backward_compat(self):
        """No agent elements when agents param is None."""
        root = self.generator.create_log_xml(
            metadata=self.metadata, object_uuid='uuid-123',
        )
        agents = self._find_elements(root, 'agent')
        self.assertEqual(len(agents), 0)

    def test_agents_added(self):
        """Agent elements are created when agents list is provided."""
        agents_data = [
            {
                'agent_name': 'DIAS Package Creator',
                'agent_type': 'software',
                'agent_id_type': 'NO/RA',
                'agent_id_value': 'DIAS-PC',
            },
            {
                'agent_name': 'Test User',
                'agent_type': 'person',
                'agent_id_type': 'NO/RA',
                'agent_id_value': 'user-001',
            },
        ]
        root = self.generator.create_log_xml(
            metadata=self.metadata, object_uuid='uuid-123',
            agents=agents_data,
        )
        agents = self._find_elements(root, 'agent')
        self.assertEqual(len(agents), 2)

    def test_agent_contents(self):
        """Agent element contains correct name, type, and identifier."""
        agents_data = [{
            'agent_name': 'Test Organization',
            'agent_type': 'organization',
            'agent_id_type': 'NO/RA',
            'agent_id_value': 'org-001',
        }]
        root = self.generator.create_log_xml(
            metadata=self.metadata, object_uuid='uuid-123',
            agents=agents_data,
        )
        agents = self._find_elements(root, 'agent')
        agent = agents[0]

        name = [el for el in agent if el.tag.split('}')[-1] == 'agentName'][0]
        self.assertEqual(name.text, 'Test Organization')

        agent_type = [el for el in agent if el.tag.split('}')[-1] == 'agentType'][0]
        self.assertEqual(agent_type.text, 'organization')

        id_value = [el for el in agent.iter()
                    if el.tag.split('}')[-1] == 'agentIdentifierValue'][0]
        self.assertEqual(id_value.text, 'org-001')


class TestDIASLogGeneratorEventAndAgentsCombined(unittest.TestCase):
    """Test user events and agents together in log.xml."""

    def setUp(self):
        self.generator = DIASLogGenerator()
        self.metadata = {
            'label': 'Combined Test',
            'archivist_organization': 'Test Archive',
            'package_type': 'SIP',
        }

    def _find_elements(self, root, local_name):
        return [el for el in root.iter() if el.tag.split('}')[-1] == local_name]

    def test_combined_events_and_agents(self):
        """Both user events and agents appear in the same document."""
        user_events = [{'event_type': 'Migration', 'event_detail': 'test',
                        'event_outcome': '0', 'event_outcome_detail': '',
                        'event_date': ''}]
        agents = [{'agent_name': 'Agent X', 'agent_type': 'software',
                   'agent_id_type': 'NO/RA', 'agent_id_value': 'X'}]
        root = self.generator.create_log_xml(
            metadata=self.metadata, object_uuid='uuid-123',
            user_events=user_events, agents=agents,
        )
        events = self._find_elements(root, 'event')
        agent_elems = self._find_elements(root, 'agent')
        self.assertEqual(len(events), 2)  # 1 auto + 1 user
        self.assertEqual(len(agent_elems), 1)

    def test_auto_event_type_is_creation(self):
        """Auto-generated event type should use DIAS integer code for Creation."""
        root = self.generator.create_log_xml(
            metadata=self.metadata, object_uuid='uuid-123',
        )
        events = self._find_elements(root, 'event')
        auto_event = events[0]
        event_type = [el for el in auto_event if el.tag.split('}')[-1] == 'eventType'][0]
        self.assertEqual(event_type.text, '10000')


class TestConfigLoaderPremis(unittest.TestCase):
    """Tests for PREMIS section in ConfigLoader."""

    def test_load_premis_events(self):
        """Test loading premis events from YAML."""
        yaml_content = """
metadata:
  label: Test
premis:
  events:
    - event_type: Creation
      event_detail: Package created
      event_outcome: '0'
      event_outcome_detail: Success
      event_date: ''
      include_sip: true
      include_aip: true
    - event_type: Migration
      event_detail: Migrated data
      event_outcome: '0'
      event_outcome_detail: ''
      event_date: '2024-01-15'
      include_sip: true
      include_aip: false
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            config_path = f.name

        try:
            loader = ConfigLoader(config_path=config_path)
            defaults = loader.load_defaults()

            self.assertIn('premis_events', defaults)
            self.assertEqual(len(defaults['premis_events']), 2)
            self.assertEqual(defaults['premis_events'][0]['event_type'], 'Creation')
            self.assertEqual(defaults['premis_events'][1]['event_type'], 'Migration')
            self.assertFalse(defaults['premis_events'][1]['include_aip'])
        finally:
            os.unlink(config_path)

    def test_load_premis_agents(self):
        """Test loading premis agents from YAML."""
        yaml_content = (
            "metadata:\n"
            "  label: Test\n"
            "premis:\n"
            "  agents:\n"
            "    - agent_name: DIAS Package Creator\n"
            "      agent_type: software\n"
            "      agent_id_type: NO/RA\n"
            "      agent_id_value: DIAS-PC\n"
            "      include_sip: true\n"
            "      include_aip: false\n"
            "    - agent_name: Test User\n"
            "      agent_type: person\n"
            "      agent_id_type: NO/RA\n"
            "      agent_id_value: user-001\n"
            "      include_sip: false\n"
            "      include_aip: true\n"
        )
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            config_path = f.name

        try:
            loader = ConfigLoader(config_path=config_path)
            defaults = loader.load_defaults()

            self.assertIn('premis_agents', defaults)
            self.assertEqual(len(defaults['premis_agents']), 2)
            self.assertEqual(defaults['premis_agents'][0]['agent_name'], 'DIAS Package Creator')
            self.assertEqual(defaults['premis_agents'][1]['agent_type'], 'person')
            self.assertFalse(defaults['premis_agents'][0]['include_aip'])
            self.assertFalse(defaults['premis_agents'][1]['include_sip'])
        finally:
            os.unlink(config_path)

    def test_load_premis_options(self):
        """Test loading premis dropdown options from YAML."""
        yaml_content = """
metadata:
  label: Test
premis:
  options:
    event_type:
      - Creation
      - Migration
    agent_type:
      - person
      - organization
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            config_path = f.name

        try:
            loader = ConfigLoader(config_path=config_path)
            defaults = loader.load_defaults()

            self.assertIn('premis_event_type_options', defaults)
            self.assertEqual(defaults['premis_event_type_options'], ['Creation', 'Migration'])
            self.assertIn('premis_agent_type_options', defaults)
            self.assertEqual(defaults['premis_agent_type_options'], ['person', 'organization'])
        finally:
            os.unlink(config_path)

    def test_no_premis_section(self):
        """Config without premis section still works."""
        yaml_content = """
metadata:
  label: Test
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            config_path = f.name

        try:
            loader = ConfigLoader(config_path=config_path)
            defaults = loader.load_defaults()

            self.assertNotIn('premis_events', defaults)
            self.assertNotIn('premis_agents', defaults)
            self.assertEqual(defaults['label'], 'Test')
        finally:
            os.unlink(config_path)


class TestDIASLogGeneratorSave(unittest.TestCase):
    """Test saving PREMIS XML with user events and agents."""

    def setUp(self):
        self.generator = DIASLogGenerator()
        self.metadata = {
            'label': 'Save Test',
            'archivist_organization': 'Test Archive',
            'package_type': 'SIP',
        }

    def test_save_with_events_and_agents(self):
        """Test that XML with events and agents saves and parses correctly."""
        user_events = [{'event_type': 'Migration', 'event_detail': 'Test migration',
                        'event_outcome': '0', 'event_outcome_detail': 'OK',
                        'event_date': '2024-01-01'}]
        agents = [{'agent_name': 'Test SW', 'agent_type': 'software',
                   'agent_id_type': 'NO/RA', 'agent_id_value': 'TSW'}]

        root = self.generator.create_log_xml(
            metadata=self.metadata, object_uuid='uuid-save-test',
            user_events=user_events, agents=agents,
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            output_path = f.name

        try:
            self.generator.save(root, output_path)

            # Parse back and verify
            tree = ET.parse(output_path)
            parsed_root = tree.getroot()
            self.assertTrue(parsed_root.tag.endswith('premis'))

            # Should have events and agents
            all_tags = [el.tag.split('}')[-1] for el in parsed_root]
            self.assertIn('event', all_tags)
            self.assertIn('agent', all_tags)
        finally:
            os.unlink(output_path)


if __name__ == '__main__':
    unittest.main()
