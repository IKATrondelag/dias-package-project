#!/usr/bin/env python3
"""
DIAS Package Creator - Main Application Entry Point

A standalone desktop application to create DIAS-compliant submission packages.
"""

import sys
from pathlib import Path

# Add src directory to path for development
if __name__ == "__main__":
    src_path = Path(__file__).parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def main() -> None:
    """Main entry point for the GUI application."""
    # Set up logging before anything else
    from src.utils.logging_config import setup_logging, cleanup_old_logs, log_memory_usage
    import logging
    
    log_file = setup_logging()
    cleanup_old_logs()  # Clean up old logs on startup
    
    logger = logging.getLogger(__name__)
    logger.info("DIAS Package Creator starting...")
    log_memory_usage(logger, "Initial memory")
    
    try:
        from src.core import PackageController
        from src.gui import MainWindow
        
        # Initialize controller
        logger.info("Initializing controller...")
        controller = PackageController()
        
        # Create and run main window
        logger.info("Creating main window...")
        window = MainWindow(controller)
        
        logger.info("Application ready")
        window.run()
        
    except Exception as e:
        logger.exception("Fatal error in application")
        raise


if __name__ == "__main__":
    main()
