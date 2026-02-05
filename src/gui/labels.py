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
    
    LABEL_ARCHIVIST_ORG = "Archivist Organization*:"
    LABEL_SYSTEM_NAME = "System/Software Name*:"
    LABEL_SYSTEM_VERSION = "System Version:"
    LABEL_SYSTEM_FORMAT = "Content Format:"
    
    LABEL_CREATOR_ORG = "Creator Organization (IKA)*:"
    
    LABEL_PRODUCER_ORG = "Producer Organization:"
    LABEL_PRODUCER_INDIVIDUAL = "Producer Individual:"
    LABEL_PRODUCER_SOFTWARE = "Producer Software:"
    
    LABEL_SUBMITTER_ORG = "Submitter Organization:"
    LABEL_SUBMITTER_INDIVIDUAL = "Submitter Individual:"
    
    LABEL_IPOWNER_ORG = "IP Owner Organization:"
    LABEL_PRESERVATION_ORG = "Preservation Organization:"
    
    LABEL_SUBMISSION_AGREEMENT = "Submission Agreement ID*:"
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
    FIELD_ARCHIVIST_ORG = "Archivist Organization"
    FIELD_SYSTEM_NAME = "System/Software Name"
    FIELD_CREATOR_ORG = "Creator Organization (IKA)"
    FIELD_SUBMISSION_AGREEMENT = "Submission Agreement ID"


# Create a default instance for easy importing
labels = Labels()
