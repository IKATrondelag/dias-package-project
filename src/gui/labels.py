"""
Centralized label constants for GUI localization.
This file contains all UI labels in one place, making it easy to:
- Translate the application to different languages
- Maintain consistent terminology
- Update labels in a single location
"""


class Labels:
    """UI labels and text constants."""
    
    # Application
    APP_NAME = "DIAS Package Creator"
    
    # Menu items
    MENU_FILE = "File"
    MENU_NEW_PACKAGE = "New Package"
    MENU_LOAD_TEMPLATE = "Load Metadata Template"
    MENU_SAVE_TEMPLATE = "Save Metadata Template"
    MENU_EXIT = "Exit"
    
    MENU_TOOLS = "Tools"
    MENU_DESCRIBE_PACKAGE = "Describe Package..."
    MENU_VALIDATE_PACKAGE = "Validate Package..."
    MENU_SAVE_AS_DEFAULTS = "Save Current as Defaults"
    
    MENU_HELP = "Help"
    MENU_ABOUT = "About"
    
    # Tabs
    TAB_SOURCE_DEST = "Source & Destination"
    TAB_METADATA = "Package Metadata"
    TAB_PREMIS = "Preservation (PREMIS)"
    
    # Source & Destination Tab
    HEADING_SOURCE_SELECTION = "Source Selection"
    LABEL_SOURCE = "Source:"
    BTN_FILE = "File"
    BTN_FOLDER = "Folder"
    
    HEADING_DEST_SELECTION = "Destination Selection"
    LABEL_OUTPUT_FOLDER = "Output Folder:"
    LABEL_PACKAGE_NAME = "Package Name:"
    BTN_BROWSE = "Browse"
    
    # Action buttons
    BTN_VALIDATE = "Validate"
    BTN_CREATE_PACKAGE = "Create Package"
    BTN_RESET = "Reset"
    BTN_CLEAR = "Clear"
    BTN_TODAY = "Today"
    
    # Progress
    STATUS_READY = "Ready"
    
    # Log
    HEADING_PROCESSING_LOG = "Processing Log"
    
    # Metadata Form - Section Headers
    SECTION_PACKAGE_INFO = "Package Information"
    SECTION_ARCHIVIST_INFO = "Archivist Information"
    SECTION_CREATOR_INFO = "Creator Information"
    SECTION_PRODUCER_INFO = "Producer Information"
    SECTION_SUBMITTER_INFO = "Submitter Information"
    SECTION_IP_OWNER = "IP Owner & Preservation"
    SECTION_AGREEMENT_DATE = "Agreement & Date Range"
    
    # Metadata Form - Field Labels
    LABEL_PACKAGE_TYPE = "Package Type*:"
    LABEL_LABEL_TITLE = "Label/Title*:"
    LABEL_RECORD_STATUS = "Record Status:"
    
    LABEL_ARCHIVIST_ORG = "Archivist Organization (IKA)*:"
    LABEL_SYSTEM_NAME = "System/Software Name*:"
    LABEL_SYSTEM_VERSION = "System Version:"
    LABEL_SYSTEM_FORMAT = "Content Format:"
    
    LABEL_CREATOR_ORG = "Creator Organization*:"
    
    LABEL_PRODUCER_ORG = "Producer Organization:"
    LABEL_PRODUCER_INDIVIDUAL = "Producer Individual:"
    LABEL_PRODUCER_SOFTWARE = "Producer Software:"
    
    LABEL_SUBMITTER_ORG = "Submitter Organization:"
    LABEL_SUBMITTER_INDIVIDUAL = "Submitter Individual:"
    
    LABEL_IPOWNER_ORG = "IP Owner Organization:"
    LABEL_PRESERVATION_ORG = "Preservation Organization:"
    
    LABEL_SUBMISSION_AGREEMENT = "Submission Agreement ID*:"
    LABEL_RELATED_AIC_ID = "Related AIC UUID:"
    LABEL_RELATED_PACKAGE_ID = "Related Package UUID:"
    LABEL_START_DATE = "Content Start Date:"
    LABEL_END_DATE = "Content End Date:"
    
    # Validation messages
    VALIDATION_REQUIRED_FIELD = "{field} is required"
    VALIDATION_STARTING = "Starting validation..."
    VALIDATION_FAILED_TITLE = "Validation Failed"
    VALIDATION_FAILED_MSG = "Found {count} error(s):\n\n{errors}"
    VALIDATION_SUCCESS_TITLE = "Validation Successful"
    VALIDATION_SUCCESS_MSG = "All inputs are valid. Ready to create package."
    
    # File dialogs
    DIALOG_SELECT_SOURCE_FILE = "Select Source File"
    DIALOG_SELECT_SOURCE_FOLDER = "Select Source Folder"
    DIALOG_SELECT_OUTPUT_FOLDER = "Select Output Folder"
    DIALOG_SELECT_TEMPLATE = "Select Template File"
    DIALOG_SAVE_TEMPLATE = "Save Template"
    
    # Required field names (for validation messages)
    FIELD_LABEL_TITLE = "Label/Title"
    FIELD_ARCHIVIST_ORG = "Archivist Organization (IKA)"
    FIELD_SYSTEM_NAME = "System/Software Name"
    FIELD_CREATOR_ORG = "Creator Organization"
    FIELD_SUBMISSION_AGREEMENT = "Submission Agreement ID"
    FIELD_RELATED_REFERENCE = "Related AIC UUID or Related Package UUID"
    
    # PREMIS Form - Section Headers
    SECTION_PREMIS_EVENTS = "Preservation Events"
    SECTION_PREMIS_AGENTS = "Preservation Agents"
    
    # PREMIS Form - Event Field Labels
    LABEL_EVENT_TYPE = "Event Type:"
    LABEL_EVENT_DETAIL = "Event Detail:"
    LABEL_EVENT_OUTCOME = "Event Outcome:"
    LABEL_EVENT_OUTCOME_DETAIL = "Outcome Detail:"
    LABEL_EVENT_DATE = "Event Date:"
    LABEL_INCLUDE_SIP = "Include in SIP"
    LABEL_INCLUDE_AIP = "Include in AIP"
    
    # PREMIS Form - Agent Field Labels
    LABEL_AGENT_NAME = "Agent Name:"
    LABEL_AGENT_TYPE = "Agent Type:"
    LABEL_AGENT_ID_TYPE = "Identifier Type:"
    LABEL_AGENT_ID_VALUE = "Identifier Value:"
    LABEL_AGENT_INCLUDE_SIP = "Include in SIP"
    LABEL_AGENT_INCLUDE_AIP = "Include in AIP"
    
    # PREMIS Form - Buttons
    BTN_ADD_EVENT = "+ Add Event"
    BTN_REMOVE_EVENT = "Remove"
    BTN_ADD_AGENT = "+ Add Agent"
    BTN_REMOVE_AGENT = "Remove"
    
    # PREMIS Form - Dropdown Values (from XSD schema)
    PREMIS_EVENT_TYPES = ["Creation", "Migration", "Ingestion", "Adjustment", "Disposal", "Deletion"]
    PREMIS_EVENT_OUTCOMES = ["0", "1"]  # 0 = success, 1 = failure
    PREMIS_AGENT_TYPES = ["person", "organization", "software"]


# Create a default instance for easy importing
labels = Labels()
