# DIAS Package Creator - Tests Module
"""
Unit tests for DIAS Package Creator components.
"""

import sys
import os

# Add src directory to path for imports
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_path not in sys.path:
    sys.path.insert(0, src_path)