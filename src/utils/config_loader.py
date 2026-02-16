"""
Configuration loader for DIAS Package Creator.
Loads default metadata values from a YAML configuration file.
"""

import logging

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and manage configuration from YAML file."""
    
    DEFAULT_CONFIG_PATHS = [
        'dias_config.yml',
        'dias_config.yaml',
        '.dias_config.yml',
        '.dias_config.yaml',
    ]
    
    EXAMPLE_CONFIG_PATHS = [
        'dias_config.example.yml',
        'dias_config.example.yaml',
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the config loader.
        
        Args:
            config_path: Optional specific path to config file.
        """
        self.config_path = config_path
        self.config_data = {}
        
    def load_defaults(self) -> Dict[str, Any]:
        """
        Load default metadata from YAML config file.
        
        Returns:
            Dictionary of default metadata values. Empty dict if no config found.
        """
        config_file = self._find_config_file()
        
        if not config_file:
            return {}
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if not data:
                return {}
                
            # Extract metadata defaults
            metadata = data.get('metadata', {})
            
            # Flatten nested structure if needed
            defaults = {}
            
            # Direct fields
            for key in ['package_type', 'label', 'record_status', 
                       'archivist_organization', 'system_name', 'system_version', 'system_format',
                       'creator_organization', 'producer_organization', 'producer_individual', 
                       'producer_software', 'submitter_organization', 'submitter_individual',
                       'ipowner_organization', 'preservation_organization',
                       'submission_agreement', 'start_date', 'end_date']:
                if key in metadata:
                    defaults[key] = metadata[key]
            
            # Extract dropdown options if provided
            options = data.get('options', {})
            for key, values in options.items():
                if isinstance(values, list):
                    defaults[f"{key}_options"] = values
            
            # Extract PREMIS configuration
            premis = data.get('premis', {})
            if premis:
                # PREMIS events list
                premis_events = premis.get('events', [])
                if isinstance(premis_events, list):
                    defaults['premis_events'] = premis_events
                
                # PREMIS agents list
                premis_agents = premis.get('agents', [])
                if isinstance(premis_agents, list):
                    defaults['premis_agents'] = premis_agents
                
                # PREMIS dropdown options
                premis_options = premis.get('options', {})
                for key, values in premis_options.items():
                    if isinstance(values, list):
                        defaults[f"premis_{key}_options"] = values
            
            self.config_data = defaults
            return defaults
            
        except yaml.YAMLError as e:
            logger.warning(f"Error parsing YAML config: {e}")
            return {}
        except Exception as e:
            logger.warning(f"Error loading config file: {e}")
            return {}
    
    def _find_config_file(self) -> Optional[Path]:
        """
        Find the config file to use.
        Searches for dias_config.yml first, then falls back to example file.
        
        Returns:
            Path to config file, or None if not found.
        """
        # If specific path provided, use it
        if self.config_path:
            path = Path(self.config_path)
            if path.exists():
                return path
            return None
        
        # Search for default config files
        # First check in current working directory
        for filename in self.DEFAULT_CONFIG_PATHS:
            path = Path.cwd() / filename
            if path.exists():
                return path
        
        # Then check in user's home directory
        for filename in self.DEFAULT_CONFIG_PATHS:
            path = Path.home() / filename
            if path.exists():
                return path
        
        # Check in the application directory
        try:
            app_dir = Path(__file__).parent.parent.parent
            for filename in self.DEFAULT_CONFIG_PATHS:
                path = app_dir / filename
                if path.exists():
                    return path
        except Exception:
            pass
        
        # If no user config found, fall back to example files
        # Check in application directory for example config
        try:
            app_dir = Path(__file__).parent.parent.parent
            for filename in self.EXAMPLE_CONFIG_PATHS:
                path = app_dir / filename
                if path.exists():
                    logger.info(f"Using example config file: {path}")
                    return path
        except Exception:
            pass
        
        return None
    
    def save_defaults(self, metadata: Dict[str, Any], output_path: str = 'dias_config.yml'):
        """
        Save current metadata as defaults to a YAML file.
        
        Args:
            metadata: Metadata dictionary to save.
            output_path: Path to save the config file.
        """
        try:
            config_data = {
                'metadata': metadata,
                'version': '1.0',
                'description': 'DIAS Package Creator default metadata configuration'
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
            logger.info(f"Configuration saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
