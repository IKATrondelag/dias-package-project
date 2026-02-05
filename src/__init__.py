# DIAS Package Creator
"""
A standalone desktop application to create DIAS-compliant submission packages.

Modules:
- gui: GUI components using tkinter
- core: Business logic and controllers
- utils: File processing utilities  
- dias_package_creator: XML generation (METS, PREMIS, Submission Description)
"""

from .utils.env_config import config

__version__ = config.APP_VERSION
__author__ = config.APP_AUTHOR