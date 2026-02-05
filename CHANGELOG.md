# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Cross-platform support for Windows, macOS, and Linux
- Environment-based configuration via `.env` files
- Platform utilities for consistent behavior across operating systems
- Comprehensive GitHub Actions CI/CD pipeline with:
  - Multi-platform testing (Python 3.10, 3.11, 3.12)
  - Code quality checks (flake8, mypy)
  - Security scanning (bandit, pip-audit)
  - Test coverage reporting with Codecov integration
  - Automated releases on version tags
- Development tooling configuration in `pyproject.toml`
- Pre-commit hooks for code quality

### Changed
- Externalized hardcoded values to configuration files
- Improved test coverage and added coverage thresholds
- Enhanced logging configuration with environment variables

### Removed
- Dead CLI code that referenced non-existent modules

### Fixed
- Platform-specific path handling for Windows compatibility

## [1.0.0] - 2024-XX-XX

### Added
- Initial release
- GUI application for creating DIAS-compliant archival packages
- Support for METS and PREMIS XML generation
- Dublin Core metadata handling
- Submission description generation
- Package validation against XSD schemas
- Checksum calculation (MD5, SHA-256, SHA-512)
- TAR packaging support
- Configuration file support (YAML)
- Job management with progress tracking
- File browser integration

### Technical Features
- Python 3.10+ support
- tkinter-based GUI
- PyInstaller packaging for standalone executables
- Modular architecture with separation of concerns:
  - `src/core/` - Business logic and job management
  - `src/dias_package_creator/` - DIAS-specific functionality
  - `src/gui/` - User interface components
  - `src/utils/` - Shared utilities

---

## Release Process

To create a new release:

1. Update version in:
   - `pyproject.toml`
   - `src/utils/env_config.py` (default APP_VERSION)
   - `.env.example`

2. Update this CHANGELOG.md:
   - Move items from [Unreleased] to new version section
   - Add release date

3. Commit changes:
   ```bash
   git add -A
   git commit -m "Release v1.0.0"
   ```

4. Create and push tag:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin main --tags
   ```

5. GitHub Actions will automatically:
   - Run all tests
   - Build executables for all platforms
   - Create GitHub release with assets
