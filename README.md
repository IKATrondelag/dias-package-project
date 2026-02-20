# DIAS Package Creator

[![CI/CD Pipeline](https://github.com/IKATrondelag/dias-package-project/actions/workflows/ci.yml/badge.svg)](https://github.com/IKATrondelag/dias-package-project/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/IKATrondelag/dias-package-project/branch/main/graph/badge.svg)](https://codecov.io/gh/IKATrondelag/dias-package-project)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

The DIAS Package Creator is a **standalone desktop application** for creating DIAS-compliant submission packages (SIP/AIP). It provides a user-friendly GUI interface built with Python's tkinter library, enabling users to:

- Select source files or folders
- Enter package metadata via an intuitive form
- Generate structured output packages with proper XML documentation

## Features

- **GUI Interface**: Native tkinter-based interface with progress tracking
- **SIP/AIP Support**: Create both Submission Information Packages and Archival Information Packages
- **XML Generation**: Automatically generates `mets.xml`, `premis.xml`, and `info.xml`
- **Checksum Calculation**: SHA-256 checksums for package files and archives
- **Metadata Templates**: Load and save metadata templates for reuse
- **Configuration File Support**: Auto-load default values from YAML config files (optional)
- **Background Processing**: Non-blocking file operations with progress feedback
- **Comprehensive Validation**: 
  - Input validation (source/output paths, package names, metadata)
  - Disk space checking for large packages (500GB+)
  - Automatic size estimation with safety margins
- **Cross-Platform**: Works on Linux, Windows, and macOS
- **Standalone Executable**: Can be packaged as a single executable file

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd dias-package-project

# Install dependencies (minimal - mostly standard library)
pip install -r requirements.txt

# Run the application
python app.py
```

### Building Executable

The application can be built as a standalone executable for Windows, macOS, or Linux:

```bash
# Install build dependency
pip install .[build]

# Build single-file executable (recommended, works even if pyinstaller is not on PATH)
python -m PyInstaller --clean --noconfirm build_exe.spec

# The executable will be in dist/dias-package-creator
# On Windows: dist/dias-package-creator.exe
# On macOS: dist/DIAS Package Creator.app (or dias-package-creator)
# On Linux: dist/dias-package-creator
```

#### Build Troubleshooting

- If you get `pyinstaller is not recognized`, use `python -m PyInstaller ...` as shown above.
- If `python -m PyInstaller` fails, install dependency explicitly: `python -m pip install pyinstaller`.
- Use the same Python interpreter for install and build commands.

#### Windows-specific Notes

- The executable is completely standalone and doesn't require Python installed
- Configuration files (`.env`, `dias_config.yml`) can be placed next to the executable
- Log files are stored in `%APPDATA%\dias_package_creator\logs`

#### macOS-specific Notes

- Creates an app bundle that can be moved to Applications folder
- Configuration is stored in `~/Library/Preferences/dias_package_creator`
- Logs are in `~/Library/Logs/dias_package_creator`

#### Linux-specific Notes

- Configuration follows XDG spec: `~/.config/dias_package_creator`
- Legacy location `~/.dias_package_creator` is also supported
- Logs are in `~/.dias_package_creator/logs` or `~/.local/share/dias_package_creator/logs`

### CI/CD: Optional Windows EXE Build

The repository includes an optional GitHub Actions workflow for Windows executable builds:

- Workflow: `.github/workflows/windows-exe.yml`
- Manual run: **Actions → "Windows EXE Build" → Run workflow**
- Automatic run: when a GitHub **Release** is published
- Output: artifact `dias-package-creator-windows` (zip file)

For release publishing:

- On `release: published`, the EXE zip is uploaded automatically to that release.
- On manual runs, you can optionally upload to an existing release by setting:
  - `upload_to_release = true`
  - `release_tag = vX.Y.Z`

Note about Docker:

- GitHub-hosted runners cannot produce a Windows EXE inside a Linux Docker container.
- This project uses a native `windows-latest` runner for Windows builds.
- If you need Windows-container builds, use a self-hosted Windows runner with Docker.

For a concise operational handoff (CI/CD, release flow, and what to keep minimal), see [HANDOFF.md](docs/HANDOFF.md).

## Cross-Platform Support

The application is designed to run on all major platforms:

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| GUI Application | ✅ | ✅ | ✅ |
| Standalone Executable | ✅ | ✅ | ✅ |
| Configuration Files | ✅ | ✅ | ✅ |
| Platform-native paths | ✅ | ✅ | ✅ |

## Environment Configuration

The application supports environment-based configuration via `.env` files:

1. Copy `.env.example` to `.env`
2. Customize values for your environment
3. Place the file either:
   - Next to the executable
   - In the user config directory (platform-specific)

Key configurable values:
- Application version and metadata
- DIAS/PREMIS schema locations
- Default organizations and system names
- Logging settings

## Usage

### GUI Mode (Default)

```bash
python app.py
```

This launches the graphical interface where you can:

1. **Source & Destination Tab**: Select source files/folders and output location
2. **Package Metadata Tab**: Fill in package type, producer info, and Dublin Core metadata
3. Click **"Create Package"** to generate the DIAS package

The current application entrypoint is GUI mode (`app.py`).

## Package Output Structure

The generated output follows the nested DIAS structure used by the controller:

```
[AIC_UUID]/
├── info.xml
└── [AIP_UUID]/
  ├── log.xml
  ├── administrative_metadata/
  │   └── repository_operations/
  ├── descriptive_metadata/
  └── content/
    └── [SIP_UUID].tar
```

The `.tar` archive contains:

```
[SIP_UUID]/
├── mets.xml
├── mets.xsd
├── log.xml
├── administrative_metadata/
│   ├── premis.xml
│   └── DIAS_PREMIS.xsd
├── descriptive_metadata/
└── content/
  └── [source files]
```

## Project Structure

```
dias-package-creator/
├── app.py                   # Main application entry point
├── dias_config.example.yml  # Example configuration file
├── CONFIG_GUIDE.md          # Configuration documentation
├── src/
│   ├── gui/                 # GUI components (tkinter)
│   │   ├── main_window.py
│   │   └── widgets.py
│   ├── core/                # Business logic
│   │   ├── dias_controller.py  # PackageController
│   │   └── job_manager.py      # Background task handling
│   ├── utils/               # Utilities
│   │   ├── file_processor.py
│   │   ├── config_loader.py    # YAML config support
│   │   ├── env_config.py       # Environment configuration
│   │   └── platform_utils.py   # Cross-platform utilities
│   └── dias_package_creator/  # XML generation/validation
│       ├── dias_xml_generators.py
│       ├── package_validator.py
│       ├── package_inspector.py
│       └── metadata_handler.py
├── tests/                   # Unit tests
├── data/                    # Sample data
├── *.xsd                    # XML Schema files
├── build_exe.spec           # PyInstaller configuration
├── pyproject.toml           # Project configuration
├── .env.example             # Environment template
└── requirements.txt
```

## Configuration

The application supports optional configuration files to pre-populate form fields with default values. 

**Quick Start:**
1. Copy `dias_config.example.yml` to `dias_config.yml`
2. Copy `.env.example` to `.env` (optional, for advanced settings)
3. Edit the values to match your organization's defaults
4. Start the application - fields will be pre-filled

See [CONFIG_GUIDE.md](docs/CONFIG_GUIDE.md) for detailed documentation.

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run with verbose output
pytest tests/ -v
```

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run linting
flake8 src/ tests/

# Run type checking
mypy src/
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.