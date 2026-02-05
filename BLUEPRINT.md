# DIAS Package Creator Blueprint

## Project Overview
A standalone desktop application to create DIAS-compliant submission packages. The application allows users to select input files, provide metadata via a form, and generates a structured output package containing the files and necessary XML documentation (`mets.xml`, `premis.xml`, `info.xml`).

## Design Philosophy
- **Standalone**: Distributed as a single executable file (using PyInstaller).
- **Non-Docker**: Native Python application utilizing system resources directly.
- **Production Grade**: Error handling, logging, validation, and test coverage.
- **User Friendly**: Simple GUI for data entry and process monitoring.

## Technical Stack
- **Language**: Python 3.x
- **GUI Framework**: `tkinter` + `tkinter.ttk` (Standard Python library, robust and native look). 
- **XML Processing**: `xml.etree.ElementTree` (Existing implementation).
- **Build Tool**: `PyInstaller` (To create the .exe/binary).
- **Testing**: `unittest` (Standard library).

## Architecture

### 1. User Interface (GUI)
* Module: `src/gui/`
* **Main Window**: processing status logs, progress bar.
* **Input Form**:
    * **Source Selection**: File/Folder picker.
    * **Destination Selection**: Output folder picker.
    * **Package Metadata**:
        * Package Type (SIP, AIP, etc.)
        * Producer/Agent Name
        * Submission Agreement ID
        * Description/Label
* **Action Buttons**: "Validate", "Create Package".

### 2. Core Logic (Controller)
* Module: `src/core/`
* **PackageController**: Bridges GUI events to backend logic.
* **JobManager**: Runs long-running tasks (file copying, checksumming) in a background thread to keep GUI responsive.

### 3. File Processing
* Module: `src/utils/file_processor.py`
* **Capabilities**:
    * Recursive directory scanning.
    * Secure file copying (`shutil`).
    * Checksum calculation (MD5/SHA256) for PREMIS.
    * Mime-type detection.

### 4. XML Generation (Existing/Refined)
* Module: `src/dias_package_creator/xml_generators.py` & `submission_description_generator.py`
* **MetsGenerator**: Creates `mets.xml`.
* **PremisGenerator**: Creates `premis.xml`.
* **InfoGenerator**: Adapts `SubmissionDescriptionMetsGenerator` to create `info.xml`.

## Workflow
1. **Startup**: User launches the exe.
2. **Input**: User selects a folder containing data (e.g., `data/input/test_aip`).
3. **Configuration**: User fills in required metadata fields.
4. **Execution**:
    * App verifies input validity.
    * App creates output directory structure.
    * App copies files to `content/` or similar structure (flattened or preserved).
    * App calculates checksums during copy.
    * App generates XMLs based on file list and metadata.
    * App ensures XSD validation (programmatic check).
5. **Completion**: Success message and log file generation.

## Package Output Specification

### Actual DIAS Package Structure (Based on Real Example)

The DIAS package has a **nested structure** with multiple levels:

#### Level 1: AIC (Archival Information Collection) Wrapper
```
[AIC_UUID]/                          # e.g., 241bd137-ed4b-11f0-8ff6-f4a80da967fe
├── info.xml                         # AIC-level METS (submission description)
└── [AIP_UUID]/                      # e.g., 1a29a39c-ed4b-11f0-8056-f4a80da967fe
    ├── log.xml                      # AIP-level PREMIS (preservation events)
    ├── administrative_metadata/
    │   └── repository_operations/   # (empty, for future operations)
    ├── descriptive_metadata/        # (empty at AIP level)
    └── content/
        └── [SIP_UUID].tar           # Packaged SIP (or expanded as below)
```

#### Level 2: AIP (Archival Information Package)
When the SIP tar is expanded, the AIP contains:
```
[AIP_UUID]/
├── log.xml                          # PREMIS preservation events
├── administrative_metadata/
│   └── repository_operations/
├── descriptive_metadata/
└── content/
    └── [SIP_UUID]/                  # Nested SIP folder
        └── [SIP_UUID]/              # Double-nested SIP structure
            ├── mets.xml             # SIP-level METS (main structural map)
            ├── log.xml              # SIP-level log
            ├── mets.xsd             # METS schema
            ├── administrative/      # SIP administrative metadata
            │   ├── premis.xml       # File-level preservation metadata
            │   └── DIAS_PREMIS.xsd  # PREMIS schema
            ├── content/             # Actual payload files
            │   ├── ika-info.txt
            │   └── content/         # Sometimes double-nested
            │       ├── file1.siard
            │       └── file2.zip
            └── descriptive/         # Descriptive metadata files
                ├── doc1.pdf
                └── doc2.pdf
```

### Key Observations from Real Package:

1. **info.xml** at AIC root is a METS file (TYPE="SIP", PROFILE="http://xml.ra.se/METS/RA_METS_eARD.xml")
2. **log.xml** files contain PREMIS preservation events
3. **Content is tar-archived** at AIP level, then expanded to show SIP
4. **Double-nesting** pattern: content/[UUID]/[UUID]/ for the actual SIP
5. **Separate folders** for administrative, descriptive, and content
6. **Schemas included** in the package (mets.xsd, DIAS_PREMIS.xsd)
7. **Multiple agents** with specific roles: ARCHIVIST, CREATOR, PRODUCER, SUBMITTER, IPOWNER, PRESERVATION
8. **altRecordID fields**: SUBMISSIONAGREEMENT, STARTDATE, ENDDATE are standard
9. **File references** use "file:" prefix in xlink:href attributes
10. **Checksums** are SHA-256 with file sizes and creation dates

## Deliverables
1. **Source Code**: Python scripts.
2. **Executable**: One-file binary (Linux/Windows compatible depending on build env).
3. **Tests**: Unit tests for generators and processor.

## Implementation Notes (Based on Real DIAS Packages)

### File Organization
- **Use double-nesting**: content/[UUID]/[UUID]/ pattern for SIP
- **Include XSD schemas**: Bundle mets.xsd and DIAS_PREMIS.xsd in the package
- **File references**: Use "file:" prefix in xlink:href (e.g., "file:mets.xml")

### METS Generation (mets.xml)
- **Profile**: Use "http://xml.ra.se/METS/RA_METS_eARD.xml"
- **Schema location**: "http://schema.arkivverket.no/METS/mets.xsd"
- **Agents**: Include at least ARCHIVIST, CREATOR, PRODUCER, SUBMITTER, PRESERVATION roles
- **Agent types**: ORGANIZATION, INDIVIDUAL, OTHER (with OTHERTYPE="SOFTWARE")
- **altRecordID**: Minimum SUBMISSIONAGREEMENT, optionally STARTDATE, ENDDATE
- **metsDocumentID**: Self-reference to "mets.xml"
- **amdSec**: Reference PREMIS file with mdRef (not inline)
- **fileSec**: List all files with SHA-256 checksums, sizes, MIME types, creation dates
- **structMap**: Two main divs: "Content Description" and "Datafiles"

### PREMIS Generation (log.xml / premis.xml)
- **Namespace**: "http://arkivverket.no/standarder/PREMIS"
- **Schema**: "http://schema.arkivverket.no/PREMIS/v2.0/DIAS_PREMIS.xsd"
- **Object identifier**: Type "NO/RA" with UUID value
- **Preservation level**: "full"
- **Significant properties**: Include aic_object, createdate, archivist_organization, label, iptype
- **Storage medium**: "Preservation platform ESSArch" or similar
- **Relationships**: Link to parent AIC with "is part of" relationship
- **Events**: Type as numeric codes (e.g., "20000" for log creation)
- **Event outcomes**: Use "0" for success

### info.xml (AIC-level METS)
- Same structure as mets.xml but at AIC level
- **TYPE**: "SIP" (even though it's wrapping an AIP)
- **fileSec**: Reference the tar archive of the AIP
- **Simpler structure**: Fewer files, mainly the packaged AIP tar

### Required Metadata Fields
Based on real package, ensure these are collected:
- **Organization**: Archivist organization name (e.g., "5014 Frøya Kommune")
- **Software**: System name and version (e.g., "Visma Familia", "1.0")
- **Format**: Content format (e.g., "SIARD")
- **Creators**: IKA organization, Producer organization/individual
- **Submitter**: Organization and individual
- **IP Owner**: Rights holder organization
- **Preservation**: Responsible preservation organization
- **Agreement**: Submission agreement number
- **Date range**: STARTDATE and ENDDATE for content

## File Structure Plan
```
dias-package-creator/
├── src/
│   ├── gui/          # New GUI components
│   ├── core/         # Business logic
│   ├── utils/        # File helpers
│   └── dias_package_creator/ # Existing XML logic (refactored/integrated)
├── tests/            # Test suite
├── dias_mets.xsd     # Reference Schema
├── dias_premis.xsd   # Reference Schema
└── build_exe.spec    # PyInstaller spec
```
