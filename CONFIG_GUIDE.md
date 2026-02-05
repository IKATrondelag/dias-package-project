# DIAS Package Creator - Configuration File Support

## Overview
The application now supports loading default metadata values and dropdown options from a YAML configuration file. This makes it easy to pre-populate the form with commonly used values and customize dropdown lists with your organization's specific options.

## Features
- **Optional**: If no config file exists, the application automatically falls back to the example config file
- **Auto-loading**: Configuration is loaded automatically on startup
- **Fallback**: If `dias_config.yml` doesn't exist, `dias_config.example.yml` is used
- **Easy to edit**: Human-readable YAML format
- **Custom dropdowns**: Define your own dropdown options for organizations, systems, etc.
- **Save current values**: Save your current form values as defaults via the Tools menu

## Configuration File Locations
The application looks for configuration files in the following locations (in order):

1. Current working directory:
   - `dias_config.yml`
   - `dias_config.yaml`
   - `.dias_config.yml`
   - `.dias_config.yaml`

2. User's home directory (same filenames)

3. Application directory (same filenames)

4. **If none found**: Falls back to `dias_config.example.yml` in the application directory

## Usage

### Creating a Configuration File

1. **From the GUI**: 
   - Fill in your desired default values in the form
   - Go to Help → "Save Current as Defaults"
   - Choose where to save the file (recommend `dias_config.yml` in the app directory)

2. **Manual Creation**:
   - Copy `dias_config.example.yml` to `dias_config.yml`
   - Edit the values as needed

### Example Configuration File

```yaml
version: '1.0'
description: 'Default metadata configuration for DIAS packages'

metadata:
  # Package Information
  package_type: 'SIP'
  record_status: 'NEW'
  
  # Archivist Information
  archivist_organization: '5014 Frøya Kommune'
  system_name: 'Visma Familia'
  system_version: '1.0'
  system_format: 'SIARD'
  
  # Creator Information
  creator_organization: 'IKA Trøndelag'
  
  # Producer Information
  producer_organization: 'Fosen IKT'
  producer_individual: ''
  producer_software: 'Full Convert Pro'
  
  # Submitter Information
  submitter_organization: '5011 Hemne Kommune'
  submitter_individual: ''
  
  # IP Owner & Preservation
  ipowner_organization: '5045 Grong Kommune'
  preservation_organization: 'KDRS'
  
  # Agreement & Date Range
  submission_agreement: ''
  start_date: '2000-01-01'
  end_date: '2024-12-31'

# Dropdown Options
# Define custom options for dropdown fields
options:
  # Organizations - customize with your common municipalities
  archivist_organization:
    - '5000 Trøndelag fylkeskommune'
    - '5001 Trondheim kommune'
    - '5014 Frøya kommune'
    # ... add your organizations here
  
  creator_organization:
    - '5000 Trøndelag fylkeskommune'
    - '5001 Trondheim kommune'
    # ... add your IKA organizations here
  
  system_name:
    - 'Visma Familia'
    - 'Acos'
    - 'ESA'
    # ... add your systems here
  
  producer_organization:
    - 'Fosen IKT'
    - 'KommIT'
    - 'Evry'
    - 'Visma'
```

## Available Configuration Fields

### Metadata Fields
All fields in the metadata form can be configured with default values:

- `package_type` - Type of package (SIP, AIP, etc.)
- `label` - Package label/title
- `record_status` - Record status (NEW, SUPPLEMENT, etc.)
- `archivist_organization` - Archivist organization name
- `system_name` - System/software name
- `system_version` - System version
- `system_format` - Content format (e.g., SIARD)
- `creator_organization` - Creator organization (IKA)
- `producer_organization` - Producer organization
- `producer_individual` - Producer individual name
- `producer_software` - Producer software
- `submitter_organization` - Submitter organization
- `submitter_individual` - Submitter individual name
- `ipowner_organization` - IP owner organization
- `preservation_organization` - Preservation organization
- `submission_agreement` - Submission agreement ID
- `start_date` - Content start date (YYYY-MM-DD)
- `end_date` - Content end date (YYYY-MM-DD)

### Dropdown Options
You can customize the dropdown lists for the following fields:

- `archivist_organization` - List of archivist organizations
- `submitter_organization` - List of submitter organizations  
- `ipowner_organization` - List of IP owner organizations
- `creator_organization` - List of creator (IKA) organizations
- `producer_organization` - List of producer organizations
- `system_name` - List of system/software names
- `system_version` - List of system versions
- `system_format` - List of content formats
- `producer_software` - List of producer software options
- `preservation_organization` - List of preservation organizations

**Note**: Options defined in the config file will replace the default options in the application.

## Installation

The configuration feature requires PyYAML:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install PyYAML
```

If PyYAML is not installed, the application will still work but configuration files will be ignored silently.

## Behavior

- When the application starts, it checks for a configuration file
- If found and valid, the form is pre-populated with the default values
- User can still modify any field - defaults are just starting values
- Clicking "Reset" will reload the defaults from the config file
- Invalid or missing config files don't cause errors

## Tips

1. Use organization-wide configuration files stored in a network location
2. Each user can override with their own local config file
3. Leave fields empty (`''`) in the config if you don't want a default value
4. Comments in YAML start with `#`
