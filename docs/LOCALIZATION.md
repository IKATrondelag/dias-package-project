# Localization Guide

## Overview

The DIAS Package Creator GUI supports localization through a centralized labels system. All user-facing text is stored in a single file, making it easy to translate the application to different languages.

## Label Management

### Location
All UI labels are defined in:
- `src/gui/labels.py`

### Structure
Labels are organized as class constants in the `Labels` class:

```python
class Labels:
    """UI labels and text constants."""
    
    # Application
    APP_NAME = "DIAS Package Creator"
    
    # Menu items
    MENU_FILE = "File"
    MENU_NEW_PACKAGE = "New Package"
    # ... etc
```

### Usage in Code
Import and use labels in your GUI code:

```python
from .labels import labels

# Use the label
ttk.Label(frame, text=labels.LABEL_SOURCE)
ttk.Button(frame, text=labels.BTN_BROWSE, command=self._browse)
```

## Creating a Translation

To translate the application to another language:

1. Copy `src/gui/labels.py` to a new file (e.g., `labels_nb.py` for Norwegian)
2. Translate all string values while keeping the constant names unchanged
3. Import the appropriate labels file based on user preference or system locale

### Example Norwegian Translation

```python
class Labels:
    """UI-etiketter og tekstkonstanter."""
    
    # Applikasjon
    APP_NAME = "DIAS Pakkeskaper"
    
    # Menyelementer
    MENU_FILE = "Fil"
    MENU_NEW_PACKAGE = "Ny pakke"
    MENU_LOAD_TEMPLATE = "Last inn metadata-mal"
    MENU_SAVE_TEMPLATE = "Lagre metadata-mal"
    MENU_EXIT = "Avslutt"
    
    # Kildevelger
    LABEL_SOURCE = "Kilde:"
    BTN_BROWSE = "Bla gjennom"
    BTN_FILE = "Fil"
    BTN_FOLDER = "Mappe"
    # ... etc
```

## Adding New Labels

When adding new UI elements:

1. Add the label constant to `Labels` class in `labels.py`
2. Use a descriptive, uppercase name with prefix:
   - `LABEL_` for field labels
   - `BTN_` for buttons
   - `MENU_` for menu items
   - `HEADING_` for section headers
   - `SECTION_` for form sections
   - `DIALOG_` for dialog titles
   - `VALIDATION_` for validation messages
3. Use the label in your code via `labels.YOUR_CONSTANT`

## Benefits

- **Centralized Management**: All text in one place
- **Easy Translation**: Translate once, applies everywhere
- **Consistency**: Same terms used throughout the application
- **Maintainability**: Update labels without touching UI code
- **Version Control**: Track label changes separately from logic

## Future Enhancements

Potential improvements to the localization system:

1. **Dynamic Language Switching**: Allow users to switch languages at runtime
2. **Locale Detection**: Automatically select language based on system locale
3. **Plural Forms**: Handle plural forms correctly for different languages
4. **Date/Number Formatting**: Localize date and number formats
5. **RTL Support**: Support right-to-left languages
6. **Translation Files**: Use JSON/YAML files instead of Python modules
