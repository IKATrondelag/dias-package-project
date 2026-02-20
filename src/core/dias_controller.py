"""
Package Controller for DIAS Package Creator.
Creates DIAS-compliant packages with the proper nested structure.
"""

import logging
import shutil
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Any, Optional, List

from .job_manager import JobManager
from ..utils.file_processor import FileProcessor
from ..utils.validation import InputValidator, ValidationResult
from ..utils.platform_utils import get_application_path, get_resource_path
from ..dias_package_creator.dias_xml_generators import (
    DIASInfoGenerator, 
    DIASMetsGenerator, 
    DIASLogGenerator,
    calculate_sha256,
    get_timestamp,
    generate_uuid
)


class PackageController:
    """
    Controller class that bridges GUI events to backend logic.
    Handles package creation workflow and coordinates between components.
    Creates DIAS-compliant nested package structure.
    """
    
    def __init__(self) -> None:
        """Initialize the controller."""
        # Set up logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
        
        self.logger.info("Initializing DIAS Package Controller")
        
        self.job_manager = JobManager()
        self.file_processor = FileProcessor()
        
        # XML generators
        self.info_generator = DIASInfoGenerator()
        self.mets_generator = DIASMetsGenerator()
        self.log_generator = DIASLogGenerator()
        
        # Callbacks for GUI updates
        self._progress_callback: Optional[Callable[[float, str], None]] = None
        self._log_callback: Optional[Callable[[str, str], None]] = None
        self._completion_callback: Optional[Callable[[bool, str], None]] = None
        
        # Get base path for schema files (works in development and frozen exe)
        self._base_path = get_application_path()
        
        self.logger.info("Controller initialized successfully")
        
    def set_progress_callback(self, callback: Callable[[float, str], None]) -> None:
        """Set callback for progress updates."""
        self._progress_callback = callback
        self.job_manager.set_progress_callback(callback)
        
    def set_log_callback(self, callback: Callable[[str, str], None]) -> None:
        """Set callback for log messages."""
        self._log_callback = callback
        self.job_manager.set_log_callback(callback)
        
    def set_completion_callback(self, callback: Callable[[bool, str], None]) -> None:
        """Set callback for completion notification."""
        self._completion_callback = callback
        
    def validate_inputs(self, source_path: str, output_path: str, 
                       package_name: str, metadata: Dict[str, Any]) -> ValidationResult:
        """
        Validate all inputs before package creation.
        
        Args:
            source_path: Path to source file or folder.
            output_path: Path to output directory.
            package_name: Name for the package.
            metadata: Package metadata dictionary.
            
        Returns:
            ValidationResult with all validation checks.
        """
        return InputValidator.validate_all(
            source_path=source_path,
            output_path=output_path,
            package_name=package_name,
            metadata=metadata
        )
        
    def _log(self, message: str, level: str = "INFO") -> None:
        """Log a message via callback if available."""
        if self._log_callback:
            self._log_callback(message, level)
            
    def _update_progress(self, value: float, status: Optional[str] = None) -> None:
        """Update progress via callback if available."""
        if self._progress_callback:
            self._progress_callback(value, status)

    def _check_cancelled(self) -> None:
        """Raise InterruptedError if the current job has been cancelled."""
        if self.job_manager.is_cancelled():
            raise InterruptedError("Job was cancelled")
            
    def create_package(self, source_path: str, output_path: str, 
                       package_name: str, metadata: Dict[str, Any]) -> None:
        """
        Start package creation in a background thread.
        
        Args:
            source_path: Path to source file or folder.
            output_path: Path to output directory.
            package_name: Name for the package (used for label if not set).
            metadata: Package metadata dictionary.
        """
        package_type = metadata.get('package_type') or metadata.get('type')
        if package_type:
            metadata['package_type'] = package_type

        # Use package name as label if label not set
        if not metadata.get('label'):
            metadata['label'] = package_name
            
        # Start the job in background thread
        self.job_manager.start_job(
            target=self._create_package_task,
            args=(source_path, output_path, package_name, metadata),
            completion_callback=self._completion_callback
        )
        
    def _create_package_task(self, source_path: str, output_path: str,
                             package_name: str, metadata: Dict[str, Any]) -> tuple:
        """
        Task function for package creation. Runs in background thread.
        Creates the DIAS-compliant nested structure:
        
        [AIC_UUID]/                          
        ├── info.xml                         
        └── [AIP_UUID]/                      
            ├── log.xml                      
            ├── administrative_metadata/
            │   └── repository_operations/
            ├── descriptive_metadata/
            └── content/
                └── [SIP_UUID]/
                    └── [SIP_UUID]/
                        ├── mets.xml
                        ├── mets.xsd
                        ├── log.xml
                        ├── administrative_metadata/
                        │   ├── premis.xml
                        │   └── DIAS_PREMIS.xsd
                        ├── content/
                        │   └── [actual files]
                        └── descriptive_metadata/
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        aic_dir = None  # Track for cleanup on failure
        
        try:
            self.logger.info("="*60)
            self.logger.info("Starting DIAS package creation")
            self.logger.info(f"Source: {source_path}")
            self.logger.info(f"Output: {output_path}")
            self.logger.info(f"Package: {package_name}")
            
            # Validate inputs before processing
            self._log("Validating inputs...")
            validation_result = self.validate_inputs(source_path, output_path, package_name, metadata)
            
            # Log validation results
            for info in validation_result.info:
                self.logger.info(info.message)
                
            for warning in validation_result.warnings:
                self._log(warning.message, "WARNING")
                self.logger.warning(warning.message)
                
            # Check for errors
            if not validation_result.is_valid():
                error_msg = "Validation failed:\n" + "\n".join(validation_result.get_error_messages())
                self._log(error_msg, "ERROR")
                for error in validation_result.errors:
                    self.logger.error(error.message)
                return (False, error_msg)
                
            self._log("Validation passed")
            
            # Check source size
            source = Path(source_path)
            if source.exists():
                if source.is_file():
                    size_mb = source.stat().st_size / (1024*1024)
                    self.logger.info(f"Source file size: {size_mb:.2f} MB")
                else:
                    total_size = sum(f.stat().st_size for f in source.rglob('*') if f.is_file())
                    size_mb = total_size / (1024*1024)
                    self.logger.info(f"Source directory size: {size_mb:.2f} MB")
            
            self._log("Starting DIAS package creation...")
            self._update_progress(0, "Initializing...")
            
            # Generate UUIDs for the package hierarchy
            aic_uuid = generate_uuid()
            aip_uuid = generate_uuid()
            sip_uuid = aip_uuid  # In this implementation, AIP and SIP use same UUID
            
            self.logger.info(f"Generated AIC UUID: {aic_uuid}")
            self.logger.info(f"Generated AIP/SIP UUID: {aip_uuid}")
            
            self._log(f"AIC UUID: {aic_uuid}")
            self._log(f"AIP/SIP UUID: {aip_uuid}")
            
            # Create the directory structure
            aic_dir = Path(output_path) / aic_uuid
            aip_dir = aic_dir / aip_uuid
            
            # Create full structure
            self._update_progress(5, "Creating directory structure...")
            self._create_directory_structure(aic_dir, aip_dir, sip_uuid)
            
            # Get SIP content directory (double-nested)
            sip_root = aip_dir / "content" / sip_uuid / sip_uuid
            sip_content_dir = sip_root / "content"
            sip_admin_dir = sip_root / "administrative_metadata"
            sip_desc_dir = sip_root / "descriptive_metadata"
            
            # Step 1: Copy source files to SIP content (10-40%)
            self._update_progress(10, "Processing source files...")
            files_info = self._process_source_files(source_path, sip_content_dir)
            self._log(f"Processed {len(files_info)} files")
            
            # Step 2: Copy XSD schemas (40-45%)
            self._update_progress(40, "Copying schema files...")
            self._copy_schema_files(sip_root, sip_admin_dir)
            
            # Extract PREMIS events and agents from metadata
            all_premis_events = metadata.get('premis_events', [])
            all_premis_agents = metadata.get('premis_agents', [])
            sip_events = [e for e in all_premis_events if e.get('include_sip', True)]
            aip_events = [e for e in all_premis_events if e.get('include_aip', True)]
            sip_agents = [a for a in all_premis_agents if a.get('include_sip', True)]
            aip_agents = [a for a in all_premis_agents if a.get('include_aip', True)]
            
            # Step 3: Generate SIP-level premis.xml (45-55%)
            self._update_progress(45, "Generating SIP premis.xml...")
            premis_path = sip_admin_dir / "premis.xml"
            premis_xml = self.log_generator.create_log_xml(
                metadata=metadata,
                object_uuid=sip_uuid,
                aic_uuid=None,  # SIP doesn't reference AIC directly
                files_info=files_info,
                is_sip_level=True,
                user_events=sip_events,
                agents=sip_agents
            )
            self.log_generator.save(premis_xml, str(premis_path))
            self._log(f"Created: {premis_path.relative_to(aic_dir)}")
            
            # Get premis file info for mets.xml reference
            premis_file_info = {
                'checksum': calculate_sha256(str(premis_path)),
                'size': premis_path.stat().st_size,
                'created': get_timestamp()
            }
            
            # Step 4: Generate SIP-level log.xml (55-60%)
            self._update_progress(55, "Generating SIP log.xml...")
            sip_log_path = sip_root / "log.xml"
            sip_log_xml = self.log_generator.create_log_xml(
                metadata=metadata,
                object_uuid=sip_uuid,
                aic_uuid=None,
                files_info=None,
                is_sip_level=True,
                user_events=sip_events,
                agents=sip_agents
            )
            self.log_generator.save(sip_log_xml, str(sip_log_path))
            self._log(f"Created: {sip_log_path.relative_to(aic_dir)}")
            
            # Add log.xml and other SIP files to files_info for mets.xml
            sip_files_info = self._gather_sip_files_info(sip_root)
            
            # Step 5: Generate SIP mets.xml (60-70%)
            self._update_progress(60, "Generating SIP mets.xml...")
            mets_path = sip_root / "mets.xml"
            mets_xml = self.mets_generator.create_mets_xml(
                metadata=metadata,
                sip_uuid=sip_uuid,
                files_info=sip_files_info,
                premis_file_info=premis_file_info
            )
            self.mets_generator.save(mets_xml, str(mets_path))
            self._log(f"Created: {mets_path.relative_to(aic_dir)}")
            
            # Step 6: Create tar archive of SIP (70-80%)
            self._update_progress(70, "Creating SIP tar archive...")
            self.logger.info("Starting tar archive creation")
            
            tar_file_info = self._create_sip_tar_archive(sip_root, aip_dir / "content", sip_uuid)
            
            archive_size_mb = tar_file_info['size'] / (1024*1024)
            self.logger.info(f"Tar archive created: {archive_size_mb:.2f} MB")
            self._log(f"Created: {sip_uuid}.tar ({archive_size_mb:.2f} MB)")
            
            # Remove the uncompressed SIP directory after successful tar creation
            self.logger.info("Removing temporary SIP directory")
            shutil.rmtree(sip_root.parent)  # Remove the outer SIP_UUID directory
            self._log(f"Removed temporary SIP directory")
            
            # Force garbage collection to free memory
            import gc
            gc.collect()
            self.logger.debug("Performed garbage collection")
            
            # Step 7: Generate AIP-level log.xml (80-85%)
            self._update_progress(80, "Generating AIP log.xml...")
            aip_log_path = aip_dir / "log.xml"
            aip_log_xml = self.log_generator.create_log_xml(
                metadata=metadata,
                object_uuid=aip_uuid,
                aic_uuid=aic_uuid,
                files_info=None,
                is_sip_level=False,
                user_events=aip_events,
                agents=aip_agents
            )
            self.log_generator.save(aip_log_xml, str(aip_log_path))
            self._log(f"Created: {aip_log_path.relative_to(aic_dir)}")
            
            # Step 8: Generate AIC info.xml (85-95%)
            self._update_progress(85, "Generating AIC info.xml...")
            
            info_path = aic_dir / "info.xml"
            info_xml = self.info_generator.create_info_xml(
                metadata=metadata,
                aip_uuid=aip_uuid,
                aic_uuid=aic_uuid,
                tar_file_info=tar_file_info
            )
            self.info_generator.save(info_xml, str(info_path))
            self._log(f"Created: {info_path.relative_to(aic_dir)}")
            
            self._update_progress(100, "Package created successfully!")
            self._log(f"Package created at: {aic_dir}", "SUCCESS")
            total_size_mb = tar_file_info['size'] / (1024*1024)
            self._log(f"Total archive size: {total_size_mb:.2f} MB", "INFO")
            
            return (True, f"DIAS package created successfully at:\n{aic_dir}\nArchive size: {total_size_mb:.2f} MB")
            
        except Exception as e:
            self._log(f"Error creating package: {e}", "ERROR")
            import traceback
            self._log(traceback.format_exc(), "DEBUG")
            return (False, f"Package creation failed: {e}")
    
    def _create_directory_structure(self, aic_dir: Path, aip_dir: Path, sip_uuid: str) -> None:
        """Create the full DIAS directory structure."""
        # SIP root (double-nested)
        sip_root = aip_dir / "content" / sip_uuid / sip_uuid
        
        dirs = [
            # AIC level
            aic_dir,
            
            # AIP level
            aip_dir,
            aip_dir / "administrative_metadata" / "repository_operations",
            aip_dir / "descriptive_metadata",
            aip_dir / "content",
            
            # SIP level (double-nested)
            sip_root,
            sip_root / "administrative_metadata",
            sip_root / "content",
            sip_root / "descriptive_metadata",
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            self._log(f"Created directory: {d.relative_to(aic_dir.parent)}")
    
    def _process_source_files(self, source_path: str, content_dir: Path) -> List[Dict]:
        """
        Process source files: copy and calculate checksums.
        Memory-efficient processing with periodic cleanup.
        
        Args:
            source_path: Source file or directory path.
            content_dir: Destination content directory.
            
        Returns:
            List of file information dictionaries.
        """
        import gc
        
        source = Path(source_path)
        files_info = []
        
        if source.is_file():
            # Single file
            self.logger.info(f"Processing single file: {source.name} ({source.stat().st_size / (1024*1024):.2f} MB)")
            self._log(f"Processing file: {source.name}")
            dest_file = content_dir / source.name
            
            file_info = self._copy_file_with_info(source, dest_file, content_dir)
            if file_info:
                files_info.append(file_info)
        else:
            # Directory - recursive copy
            self.logger.info(f"Processing directory: {source}")
            all_items = list(source.rglob('*'))
            total_files = sum(1 for f in all_items if f.is_file())
            processed = 0
            
            self.logger.info(f"Found {total_files} files to process")
            
            for src_item in all_items:
                # Preserve relative path structure
                rel_path = src_item.relative_to(source)
                dest_item = content_dir / rel_path
                
                if src_item.is_dir():
                    # Create empty directories to preserve structure
                    dest_item.mkdir(parents=True, exist_ok=True)
                    self.logger.debug(f"Created directory: {rel_path}")
                elif src_item.is_file():
                    dest_item.parent.mkdir(parents=True, exist_ok=True)
                    
                    progress = 10 + (processed / max(total_files, 1)) * 30
                    self._update_progress(progress, f"Copying: {rel_path}")
                    
                    file_info = self._copy_file_with_info(src_item, dest_item, content_dir)
                    if file_info:
                        files_info.append(file_info)
                        
                    processed += 1
                    
                    # Perform garbage collection every 100 files to prevent memory buildup
                    if processed % 100 == 0:
                        gc.collect()
                        self.logger.debug(f"Processed {processed}/{total_files} files, performed GC")
            
            self.logger.info(f"Completed processing {processed} files")
                    
        return files_info
    
    def _create_sip_tar_archive(self, sip_root: Path, content_dir: Path, sip_uuid: str) -> Dict:
        """
        Create a tar archive of the SIP content.
        Memory-efficient streaming tar creation for large archives.
        
        Args:
            sip_root: Path to the SIP root directory.
            content_dir: Directory where tar file will be created.
            sip_uuid: UUID of the SIP.
            
        Returns:
            Dictionary with tar file information.
        """
        import gc
        import time
        
        tar_path = content_dir / f"{sip_uuid}.tar"
        
        # Count total files for progress reporting
        self.logger.info("Scanning directory structure for tar archive")
        all_files = list(sip_root.rglob('*'))
        total_files = sum(1 for f in all_files if f.is_file())
        total_size = sum(f.stat().st_size for f in all_files if f.is_file())
        
        self.logger.info(f"Creating tar archive with {total_files} files ({total_size / (1024*1024):.2f} MB)")
        self._log(f"Creating tar archive with {total_files} files...")
        
        processed = 0
        start_time = time.time()
        
        try:
            # Create tar file without compression (better for long-term preservation)
            # Using streaming mode for memory efficiency with large archives
            with tarfile.open(tar_path, 'w') as tar:
                # Add the entire SIP directory, preserving structure including empty directories
                # arcname ensures the SIP_UUID appears as the root in the tar
                for item in sip_root.rglob('*'):
                    try:
                        # Calculate relative path from SIP root's parent
                        arcname = item.relative_to(sip_root.parent)
                        
                        # Add item to tar (tarfile handles streaming internally)
                        tar.add(item, arcname=arcname, recursive=False)
                        if item.is_file():
                            processed += 1 # Progress reporting
                            if processed % 10 == 0 or processed == total_files:
                                elapsed = time.time() - start_time
                                if elapsed > 0:
                                    rate_mb = (sum(f.stat().st_size for f in all_files[:processed] if f.is_file()) / (1024*1024)) / elapsed
                                    self.logger.debug(f"Tar progress: {processed}/{total_files} files ({rate_mb:.2f} MB/s)")
                                
                                progress = 70 + (processed / max(total_files, 1)) * 10
                                self._update_progress(progress, f"Archiving: {processed}/{total_files} files")
                            
                            # Garbage collection every 50 files to prevent memory buildup
                            if processed % 50 == 0:
                                gc.collect()
                    
                    except Exception as e:
                        self.logger.error(f"Error adding {item} to tar: {e}")
                        self._log(f"Warning: Could not add {item.name} to archive", "WARNING")
            
            elapsed = time.time() - start_time
            self.logger.info(f"Tar archive creation completed in {elapsed:.2f} seconds")
            
        except Exception as e:
            self.logger.error(f"Fatal error creating tar archive: {e}")
            raise
        
        # Calculate checksum of tar file
        self.logger.info("Calculating tar archive checksum")
        checksum = calculate_sha256(str(tar_path))
        stat = tar_path.stat()
        
        return {
            'path': f"content/{tar_path.name}",
            'checksum': checksum,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(),
            'mimetype': 'application/x-tar',
            'name': tar_path.name
        }
    
    def _copy_file_with_info(self, src: Path, dest: Path, base_dir: Path) -> Optional[Dict]:
        """Copy a file and return its metadata."""
        try:
            shutil.copy2(src, dest)
            
            # Calculate checksum
            checksum = calculate_sha256(str(dest))
            
            # Get file info
            stat = dest.stat()
            
            # Determine relative path for storage in package
            rel_path = str(dest.relative_to(base_dir))
            
            # Guess mimetype
            import mimetypes
            mimetype = mimetypes.guess_type(str(dest))[0] or 'application/octet-stream'
            
            return {
                'path': f"content/{rel_path}",
                'checksum': checksum,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(),
                'mimetype': mimetype,
                'name': dest.name
            }
        except Exception as e:
            self._log(f"Error copying {src}: {e}", "ERROR")
            return None
    
    def _copy_schema_files(self, sip_root: Path, admin_dir: Path) -> None:
        """Copy XSD schema files to the package."""
        # Resolve schemas from bundled resources first (PyInstaller onefile/_MEIPASS),
        # then fall back to executable/current directory for external overrides.
        schema_files = {
            'dias_mets.xsd': sip_root / 'mets.xsd',
            'dias_premis.xsd': admin_dir / 'DIAS_PREMIS.xsd'
        }
        
        for src_name, dest_path in schema_files.items():
            candidate_paths = [
                get_resource_path(src_name),
                self._base_path / src_name,
                Path.cwd() / src_name,
            ]

            src_path = next((p for p in candidate_paths if p.exists()), None)
            if src_path is None:
                self._log(f"Schema not found: {src_name}, skipping", "WARNING")
                self.logger.warning(f"Schema not found in any expected location: {src_name}")
                continue

            shutil.copy2(src_path, dest_path)
            self._log(f"Copied schema: {dest_path.name}")
    
    def _gather_sip_files_info(self, sip_root: Path) -> List[Dict]:
        """Gather information about all files in the SIP for mets.xml."""
        files_info = []
        
        # Files to include in mets.xml fileSec
        file_patterns = [
            ('mets.xsd', 'mets.xsd'),
            ('log.xml', 'log.xml'),
            ('administrative/DIAS_PREMIS.xsd', 'administrative/DIAS_PREMIS.xsd'),
        ]
        
        for pattern, rel_path in file_patterns:
            file_path = sip_root / pattern
            if file_path.exists():
                stat = file_path.stat()
                import mimetypes
                mimetype = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
                
                files_info.append({
                    'path': rel_path,
                    'checksum': calculate_sha256(str(file_path)),
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(),
                    'mimetype': mimetype,
                    'name': file_path.name
                })
        
        # Add content files
        content_dir = sip_root / 'content'
        if content_dir.exists():
            for file_path in content_dir.rglob('*'):
                if file_path.is_file():
                    stat = file_path.stat()
                    rel_path = file_path.relative_to(sip_root)
                    import mimetypes
                    mimetype = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
                    
                    files_info.append({
                        'path': str(rel_path),
                        'checksum': calculate_sha256(str(file_path)),
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(),
                        'mimetype': mimetype,
                        'name': file_path.name
                    })
        
        # Add descriptive metadata files
        desc_dir = sip_root / 'descriptive_metadata'
        if desc_dir.exists():
            for file_path in desc_dir.rglob('*'):
                if file_path.is_file():
                    stat = file_path.stat()
                    rel_path = file_path.relative_to(sip_root)
                    import mimetypes
                    mimetype = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
                    
                    files_info.append({
                        'path': str(rel_path),
                        'checksum': calculate_sha256(str(file_path)),
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(),
                        'mimetype': mimetype,
                        'name': file_path.name
                    })
        
        return files_info
        
    def load_metadata_template(self, filepath: str) -> Dict[str, Any]:
        """
        Load metadata from an XML template file.
        
        Args:
            filepath: Path to the XML template.
            
        Returns:
            Dictionary of metadata values.
        """
        from ..dias_package_creator.metadata_handler import MetadataHandler
        handler = MetadataHandler()
        return handler.load_metadata_from_xml(filepath)
        
    def save_metadata_template(self, filepath: str, metadata: Dict[str, Any]):
        """
        Save metadata to an XML template file.
        
        Args:
            filepath: Path to save the template.
            metadata: Metadata dictionary.
        """
        from ..dias_package_creator.metadata_handler import MetadataHandler
        handler = MetadataHandler()
        handler.save_metadata_to_xml(filepath, metadata)
