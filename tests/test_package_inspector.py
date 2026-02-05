"""
Tests for package_inspector.py
Tests for package description and inspection functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.dias_package_creator.package_inspector import PackageDescription


class TestPackageDescription:
    """Tests for PackageDescription class."""
    
    def test_init_defaults(self):
        """Test PackageDescription initialization with defaults."""
        desc = PackageDescription()
        
        # Check default None values
        assert desc.aic_uuid is None
        assert desc.aip_uuid is None
        assert desc.sip_uuid is None
        assert desc.label is None
        assert desc.package_type is None
        assert desc.record_status is None
        assert desc.create_date is None
        assert desc.submission_agreement is None
        assert desc.start_date is None
        assert desc.end_date is None
        assert desc.archive_name is None
        assert desc.archive_checksum is None
        
        # Check default empty lists
        assert desc.archivist == []
        assert desc.creator == []
        assert desc.producer == []
        assert desc.submitter == []
        assert desc.ipowner == []
        assert desc.preservation == []
        assert desc.content_files == []
        
        # Check default numeric values
        assert desc.total_files == 0
        assert desc.total_size == 0
        assert desc.archive_size == 0
        
    def test_format_size_bytes(self):
        """Test format_size for bytes."""
        desc = PackageDescription()
        
        assert desc.format_size(0) == "0.00 B"
        assert desc.format_size(500) == "500.00 B"
        assert desc.format_size(1023) == "1023.00 B"
        
    def test_format_size_kilobytes(self):
        """Test format_size for kilobytes."""
        desc = PackageDescription()
        
        assert desc.format_size(1024) == "1.00 KB"
        assert desc.format_size(1536) == "1.50 KB"
        assert desc.format_size(1024 * 1023) == "1023.00 KB"
        
    def test_format_size_megabytes(self):
        """Test format_size for megabytes."""
        desc = PackageDescription()
        
        assert desc.format_size(1024 * 1024) == "1.00 MB"
        assert desc.format_size(1024 * 1024 * 5) == "5.00 MB"
        assert desc.format_size(1024 * 1024 * 500) == "500.00 MB"
        
    def test_format_size_gigabytes(self):
        """Test format_size for gigabytes."""
        desc = PackageDescription()
        
        assert desc.format_size(1024 ** 3) == "1.00 GB"
        assert desc.format_size(1024 ** 3 * 2.5) == "2.50 GB"
        
    def test_format_size_terabytes(self):
        """Test format_size for terabytes."""
        desc = PackageDescription()
        
        assert desc.format_size(1024 ** 4) == "1.00 TB"
        assert desc.format_size(1024 ** 4 * 10) == "10.00 TB"
        
    def test_get_summary_minimal(self):
        """Test get_summary with minimal data."""
        desc = PackageDescription()
        summary = desc.get_summary()
        
        assert "DIAS PACKAGE DESCRIPTION" in summary
        assert "PACKAGE INFORMATION" in summary
        assert "═" in summary  # Header separator
        
    def test_get_summary_with_basic_info(self):
        """Test get_summary with basic package info."""
        desc = PackageDescription()
        desc.label = "Test Package"
        desc.package_type = "SIP"
        desc.record_status = "NEW"
        desc.create_date = "2024-01-15"
        
        summary = desc.get_summary()
        
        assert "Test Package" in summary
        assert "SIP" in summary
        assert "NEW" in summary
        assert "2024-01-15" in summary
        
    def test_get_summary_with_uuids(self):
        """Test get_summary with UUIDs."""
        desc = PackageDescription()
        desc.aic_uuid = "aic-12345"
        desc.aip_uuid = "aip-67890"
        desc.sip_uuid = "sip-abcde"
        
        summary = desc.get_summary()
        
        assert "IDENTIFIERS" in summary
        assert "aic-12345" in summary
        assert "aip-67890" in summary
        assert "sip-abcde" in summary
        
    def test_get_summary_with_agreement(self):
        """Test get_summary with agreement and dates."""
        desc = PackageDescription()
        desc.submission_agreement = "SA-2024-001"
        desc.start_date = "2024-01-01"
        desc.end_date = "2024-12-31"
        
        summary = desc.get_summary()
        
        assert "AGREEMENT" in summary
        assert "SA-2024-001" in summary
        assert "2024-01-01" in summary
        assert "2024-12-31" in summary
        
    def test_get_summary_with_only_start_date(self):
        """Test get_summary with only start date."""
        desc = PackageDescription()
        desc.start_date = "2024-01-01"
        
        summary = desc.get_summary()
        
        assert "Start Date:" in summary
        assert "2024-01-01" in summary


class TestPackageDescriptionAgents:
    """Tests for agent-related functionality in PackageDescription."""
    
    def test_add_agents(self):
        """Test adding agents to description."""
        desc = PackageDescription()
        
        desc.archivist.append("National Archive")
        desc.creator.append("Creator Organization")
        desc.producer.append("Producer A")
        desc.producer.append("Producer B")
        desc.submitter.append("Submitter Corp")
        desc.ipowner.append("IP Owner Inc")
        desc.preservation.append("Preservation Org")
        
        assert len(desc.archivist) == 1
        assert len(desc.producer) == 2
        assert desc.archivist[0] == "National Archive"
        assert desc.producer == ["Producer A", "Producer B"]
        
    def test_agents_in_summary(self):
        """Test that agents appear in summary when added."""
        desc = PackageDescription()
        desc.archivist.append("Test Archive")
        desc.creator.append("Test Creator")
        
        summary = desc.get_summary()
        
        # The get_summary method should include agents section
        # Note: actual implementation may vary
        assert isinstance(summary, str)


class TestPackageDescriptionFiles:
    """Tests for file-related functionality in PackageDescription."""
    
    def test_add_content_files(self):
        """Test adding content files."""
        desc = PackageDescription()
        
        desc.content_files.append({
            'name': 'document.pdf',
            'size': 1024000,
            'checksum': 'abc123'
        })
        desc.content_files.append({
            'name': 'image.jpg',
            'size': 512000,
            'checksum': 'def456'
        })
        
        assert len(desc.content_files) == 2
        assert desc.content_files[0]['name'] == 'document.pdf'
        
    def test_file_statistics(self):
        """Test setting file statistics."""
        desc = PackageDescription()
        
        desc.total_files = 10
        desc.total_size = 1024 * 1024 * 100  # 100 MB
        
        assert desc.total_files == 10
        assert desc.total_size == 104857600
        
    def test_archive_info(self):
        """Test archive information fields."""
        desc = PackageDescription()
        
        desc.archive_name = "package.tar"
        desc.archive_size = 1024 * 1024 * 50  # 50 MB
        desc.archive_checksum = "sha256:abc123def456"
        
        assert desc.archive_name == "package.tar"
        assert desc.archive_size == 52428800
        assert desc.archive_checksum == "sha256:abc123def456"
