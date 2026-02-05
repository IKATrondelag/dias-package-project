"""
Custom widgets for DIAS Package Creator GUI.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import re
from pathlib import Path

from ..utils.env_config import config
from ..utils.config_loader import ConfigLoader
from .labels import labels


class ProgressFrame(ttk.Frame):
    """Widget for displaying progress bar and status."""
    
    def __init__(self, parent):
        """Initialize the progress frame."""
        super().__init__(parent)
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the progress bar and status label."""
        self.columnconfigure(0, weight=1)
        
        # Status label
        self.status_var = tk.StringVar(value=labels.STATUS_READY)
        self.status_label = ttk.Label(self, textvariable=self.status_var)
        self.status_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self, 
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=400
        )
        self.progress_bar.grid(row=1, column=0, sticky="ew")
        
        # Percentage label
        self.percent_var = tk.StringVar(value="0%")
        self.percent_label = ttk.Label(self, textvariable=self.percent_var, width=6)
        self.percent_label.grid(row=1, column=1, padx=(10, 0))
        
    def update_progress(self, value, status=None):
        """
        Update the progress bar and status.
        
        Args:
            value: Progress value (0-100).
            status: Optional status message.
        """
        self.progress_var.set(value)
        self.percent_var.set(f"{int(value)}%")
        
        if status:
            self.status_var.set(status)
            
        # Update UI
        self.update_idletasks()
        
    def reset(self):
        """Reset the progress bar to initial state."""
        self.progress_var.set(0)
        self.percent_var.set("0%")
        self.status_var.set(labels.STATUS_READY)


class LogFrame(ttk.Frame):
    """Widget for displaying log messages."""
    
    def __init__(self, parent):
        """Initialize the log frame."""
        super().__init__(parent)
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the log text area with scrollbar."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        ttk.Label(header_frame, text=labels.HEADING_PROCESSING_LOG, font=('Helvetica', 10, 'bold')).pack(side="left")
        ttk.Button(header_frame, text=labels.BTN_CLEAR, command=self.clear, width=6).pack(side="right")
        
        # Text area with scrollbar
        text_frame = ttk.Frame(self)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.text = tk.Text(
            text_frame,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        self.text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scrollbar.set)
        
        # Configure tags for different log levels
        self.text.tag_configure('INFO', foreground='#d4d4d4')
        self.text.tag_configure('WARNING', foreground='#dcdcaa')
        self.text.tag_configure('ERROR', foreground='#f14c4c')
        self.text.tag_configure('SUCCESS', foreground='#4ec9b0')
        self.text.tag_configure('DEBUG', foreground='#808080')
        self.text.tag_configure('TIMESTAMP', foreground='#569cd6')
        
    def log(self, message, level="INFO"):
        """
        Add a log message.
        
        Args:
            message: The message to log.
            level: Log level (INFO, WARNING, ERROR, SUCCESS, DEBUG).
        """
        self.text.configure(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text.insert(tk.END, f"[{timestamp}] ", 'TIMESTAMP')
        
        # Add level tag
        self.text.insert(tk.END, f"[{level}] ", level)
        
        # Add message
        self.text.insert(tk.END, f"{message}\n", level)
        
        # Auto-scroll to bottom
        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)
        
        # Update UI
        self.update_idletasks()
        
    def clear(self):
        """Clear all log messages."""
        self.text.configure(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.configure(state=tk.DISABLED)


class MetadataForm(ttk.Frame):
    """Widget for entering package metadata."""
    
    # Valid values from schema
    PACKAGE_TYPES = ["SIP", "AIP", "DIP", "AIU", "AIC"]
    RECORD_STATUSES = ["NEW", "SUPPLEMENT", "REPLACEMENT", "TEST", "VERSION", "OTHER"]
    
    def __init__(self, parent):
        """Initialize the metadata form."""
        super().__init__(parent, padding="10")
        self.fields = {}
        self.config_loader = ConfigLoader()
        self.config_defaults = self._load_config_defaults()
        self._create_widgets()
        
    def _load_config_defaults(self):
        """Load default values from config file, falling back to example file."""
        # Try to load from dias_config.yml
        defaults = self.config_loader.load_defaults()
        
        if defaults:
            return defaults
        
        # If not found, try to load from example file
        try:
            app_dir = Path(__file__).parent.parent.parent
            example_file = app_dir / 'dias_config.example.yml'
            
            if example_file.exists():
                example_loader = ConfigLoader(str(example_file))
                defaults = example_loader.load_defaults()
                if defaults:
                    return defaults
        except Exception as e:
            print(f"Warning: Could not load example config: {e}")
        
        return {}
    
    def _create_widgets(self):
        """Create the metadata form fields."""
        self.columnconfigure(1, weight=1)
        
        # Create scrollable frame
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Bind mousewheel scrolling only when cursor is over the canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        # Configure inner frame columns
        self.scrollable_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Package Information Section
        row = self._add_section_header(row, labels.SECTION_PACKAGE_INFO)
        row = self._add_combobox(row, "package_type", labels.LABEL_PACKAGE_TYPE, self.PACKAGE_TYPES, "SIP", readonly=True)
        row = self._add_entry(row, "label", labels.LABEL_LABEL_TITLE, "")
        row = self._add_combobox(row, "record_status", labels.LABEL_RECORD_STATUS, self.RECORD_STATUSES, "NEW", readonly=True)
        
        # Archivist Information Section (from example: ORGANIZATION + SOFTWARE agents)
        row = self._add_section_header(row, labels.SECTION_ARCHIVIST_INFO)
        row = self._add_editable_combo(row, "archivist_organization", labels.LABEL_ARCHIVIST_ORG, 
                                       self.config_defaults.get('archivist_organization_options', config.DEFAULT_ARCHIVIST_ORGANIZATIONS))
        row = self._add_editable_combo(row, "system_name", labels.LABEL_SYSTEM_NAME, 
                                       self.config_defaults.get('system_name_options', config.DEFAULT_SYSTEM_NAMES))
        row = self._add_editable_combo(row, "system_version", labels.LABEL_SYSTEM_VERSION, 
                                       self.config_defaults.get('system_version_options', ["1.0", "2.0", "3.0"]), "1.0")
        row = self._add_editable_combo(row, "system_format", labels.LABEL_SYSTEM_FORMAT, 
                                       self.config_defaults.get('system_format_options', config.DEFAULT_CONTENT_FORMATS), "SIARD")
        
        # Creator Information (IKA organization)
        row = self._add_section_header(row, labels.SECTION_CREATOR_INFO)
        row = self._add_editable_combo(row, "creator_organization", labels.LABEL_CREATOR_ORG, 
                                       self.config_defaults.get('creator_organization_options', config.DEFAULT_CREATOR_ORGANIZATIONS))
        
        # Producer Information Section
        row = self._add_section_header(row, labels.SECTION_PRODUCER_INFO)
        row = self._add_editable_combo(row, "producer_organization", labels.LABEL_PRODUCER_ORG, 
                                       self.config_defaults.get('producer_organization_options', ["Fosen IKT", "KommIT", "Evry", "Visma"]))
        row = self._add_entry(row, "producer_individual", labels.LABEL_PRODUCER_INDIVIDUAL, "")
        row = self._add_editable_combo(row, "producer_software", labels.LABEL_PRODUCER_SOFTWARE, 
                                       self.config_defaults.get('producer_software_options', ["Full Convert Pro", "Noark 5 Standard", "Custom Export"]))
        
        # Submitter Information Section
        row = self._add_section_header(row, labels.SECTION_SUBMITTER_INFO)
        row = self._add_editable_combo(row, "submitter_organization", labels.LABEL_SUBMITTER_ORG, 
                                       self.config_defaults.get('submitter_organization_options', config.DEFAULT_ARCHIVIST_ORGANIZATIONS))
        row = self._add_entry(row, "submitter_individual", labels.LABEL_SUBMITTER_INDIVIDUAL, "")
        
        # IP Owner Information
        row = self._add_section_header(row, labels.SECTION_IP_OWNER)
        row = self._add_editable_combo(row, "ipowner_organization", labels.LABEL_IPOWNER_ORG, 
                                       self.config_defaults.get('ipowner_organization_options', config.DEFAULT_ARCHIVIST_ORGANIZATIONS))
        row = self._add_editable_combo(row, "preservation_organization", labels.LABEL_PRESERVATION_ORG, 
                                       self.config_defaults.get('preservation_organization_options', ["KDRS", "Arkivverket"]), 
                                       config.DEFAULT_PRESERVATION_ORGANIZATION)
        
        # Agreement and Date Information
        row = self._add_section_header(row, labels.SECTION_AGREEMENT_DATE)
        row = self._add_entry(row, "submission_agreement", labels.LABEL_SUBMISSION_AGREEMENT, "")
        row = self._add_date_field(row, "start_date", labels.LABEL_START_DATE)
        row = self._add_date_field(row, "end_date", labels.LABEL_END_DATE)
        
    def _add_section_header(self, row, text):
        """Add a section header."""
        ttk.Separator(self.scrollable_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=(15, 5))
        row += 1
        
        ttk.Label(self.scrollable_frame, text=text, font=('Helvetica', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 10))
        return row + 1
        
    def _add_entry(self, row, field_name, label, default=""):
        """Add an entry field."""
        ttk.Label(self.scrollable_frame, text=label).grid(row=row, column=0, sticky="w", pady=2)
        
        var = tk.StringVar(value=default)
        entry = ttk.Entry(self.scrollable_frame, textvariable=var, width=50)
        entry.grid(row=row, column=1, sticky="ew", pady=2, padx=(10, 0))
        
        self.fields[field_name] = {'var': var, 'widget': entry, 'type': 'entry'}
        return row + 1
        
    def _add_combobox(self, row, field_name, label, values, default="", readonly=False):
        """Add a combobox field."""
        ttk.Label(self.scrollable_frame, text=label).grid(row=row, column=0, sticky="w", pady=2)
        
        var = tk.StringVar(value=default)
        state = "readonly" if readonly else "normal"
        combo = ttk.Combobox(self.scrollable_frame, textvariable=var, values=values, width=47, state=state)
        combo.grid(row=row, column=1, sticky="ew", pady=2, padx=(10, 0))
        
        self.fields[field_name] = {'var': var, 'widget': combo, 'type': 'combobox'}
        return row + 1
    
    def _add_editable_combo(self, row, field_name, label, values=None, default=""):
        """Add an editable combobox field (dropdown with ability to type new values)."""
        ttk.Label(self.scrollable_frame, text=label).grid(row=row, column=0, sticky="w", pady=2)
        
        var = tk.StringVar(value=default)
        combo = ttk.Combobox(self.scrollable_frame, textvariable=var, values=values or [], width=47)
        combo.grid(row=row, column=1, sticky="ew", pady=2, padx=(10, 0))
        
        self.fields[field_name] = {'var': var, 'widget': combo, 'type': 'combobox', 'editable': True}
        return row + 1
    
    def _add_date_field(self, row, field_name, label):
        """Add a date entry field with validation and formatting."""
        ttk.Label(self.scrollable_frame, text=label).grid(row=row, column=0, sticky="w", pady=2)
        
        var = tk.StringVar(value="")
        
        # Create a frame to hold entry and helper button
        date_frame = ttk.Frame(self.scrollable_frame)
        date_frame.grid(row=row, column=1, sticky="ew", pady=2, padx=(10, 0))
        date_frame.columnconfigure(0, weight=1)
        
        # Entry field with validation
        entry = ttk.Entry(date_frame, textvariable=var, width=50)
        entry.grid(row=0, column=0, sticky="ew")
        
        # Helper button to insert today's date
        def insert_today():
            var.set(datetime.now().strftime("%Y-%m-%d"))
        
        today_btn = ttk.Button(date_frame, text=labels.BTN_TODAY, command=insert_today, width=8)
        today_btn.grid(row=0, column=1, padx=(5, 0))
        
        # Add validation on focus out
        def validate_date(event=None):
            value = var.get().strip()
            if not value:
                return
            
            # Try to parse and reformat the date
            # Accept formats: YYYY-MM-DD, YYYYMMDD, DD.MM.YYYY, DD/MM/YYYY, etc.
            patterns = [
                (r'(\d{4})-(\d{1,2})-(\d{1,2})', lambda m: f"{m[0]}-{m[1]:0>2}-{m[2]:0>2}"),  # YYYY-MM-DD
                (r'(\d{4})(\d{2})(\d{2})', lambda m: f"{m[0]}-{m[1]}-{m[2]}"),  # YYYYMMDD
                (r'(\d{1,2})\.(\d{1,2})\.(\d{4})', lambda m: f"{m[2]}-{m[1]:0>2}-{m[0]:0>2}"),  # DD.MM.YYYY
                (r'(\d{1,2})/(\d{1,2})/(\d{4})', lambda m: f"{m[2]}-{m[1]:0>2}-{m[0]:0>2}"),  # DD/MM/YYYY
            ]
            
            for pattern, formatter in patterns:
                match = re.match(pattern, value)
                if match:
                    try:
                        formatted = formatter(match.groups())
                        # Validate it's a real date
                        datetime.strptime(formatted, "%Y-%m-%d")
                        var.set(formatted)
                        entry.config(foreground='black')
                        return
                    except ValueError:
                        pass
            
            # If no pattern matched or invalid date, show in red
            if value:
                entry.config(foreground='red')
        
        entry.bind('<FocusOut>', validate_date)
        entry.bind('<Return>', validate_date)
        
        self.fields[field_name] = {'var': var, 'widget': entry, 'type': 'entry'}
        return row + 1
        
    def _add_text(self, row, field_name, label, height=3):
        """Add a text area field."""
        ttk.Label(self.scrollable_frame, text=label).grid(row=row, column=0, sticky="nw", pady=2)
        
        text = tk.Text(self.scrollable_frame, height=height, width=50, wrap=tk.WORD)
        text.grid(row=row, column=1, sticky="ew", pady=2, padx=(10, 0))
        
        self.fields[field_name] = {'widget': text, 'type': 'text'}
        return row + 1
        
    def validate(self):
        """
        Validate the form fields.
        
        Returns:
            List of error messages. Empty if valid.
        """
        errors = []
        
        # Required fields based on DIAS package requirements
        required = {
            'label': labels.FIELD_LABEL_TITLE,
            'archivist_organization': labels.FIELD_ARCHIVIST_ORG,
            'system_name': labels.FIELD_SYSTEM_NAME,
            'creator_organization': labels.FIELD_CREATOR_ORG,
            'submission_agreement': labels.FIELD_SUBMISSION_AGREEMENT
        }
        
        for field, name in required.items():
            value = self._get_field_value(field)
            if not value or not value.strip():
                errors.append(f"{name} is required")
                
        return errors
        
    def _get_field_value(self, field_name):
        """Get the value of a field."""
        field = self.fields.get(field_name)
        if not field:
            return ""
            
        if field['type'] == 'text':
            return field['widget'].get("1.0", tk.END).strip()
        else:
            return field['var'].get()
            
    def get_metadata(self):
        """
        Get all metadata values.
        
        Returns:
            Dictionary of metadata values.
        """
        metadata = {}
        
        for field_name in self.fields:
            metadata[field_name] = self._get_field_value(field_name)
            
        return metadata
        
    def set_metadata(self, metadata):
        """
        Set metadata values from a dictionary.
        Can also update dropdown options if provided.
        
        Args:
            metadata: Dictionary of metadata values.
                     Can include special '_options' keys for dropdown values.
        """
        for field_name, value in metadata.items():
            # Skip special option keys
            if field_name.endswith('_options'):
                continue
                
            if field_name in self.fields:
                field = self.fields[field_name]
                
                if field['type'] == 'text':
                    field['widget'].delete("1.0", tk.END)
                    field['widget'].insert("1.0", value or "")
                else:
                    # Update dropdown options if provided
                    options_key = f"{field_name}_options"
                    if options_key in metadata and field['type'] == 'combobox':
                        options = metadata[options_key]
                        if options and isinstance(options, list):
                            field['widget']['values'] = options
                    
                    field['var'].set(value or "")
                    
    def reset(self):
        """Reset all fields to default values from config or hardcoded defaults."""
        # Load config defaults
        config_defaults = self.config_defaults
        
        # Hardcoded fallback defaults
        hardcoded_defaults = {
            'package_type': 'SIP',
            'record_status': 'NEW',
            'system_version': '1.0',
            'system_format': 'SIARD',
            'preservation_organization': config.DEFAULT_PRESERVATION_ORGANIZATION
        }
        
        # Merge: config defaults take precedence over hardcoded
        defaults = {**hardcoded_defaults, **config_defaults}
        
        for field_name, field in self.fields.items():
            # Skip option fields
            if field_name.endswith('_options'):
                continue
                
            default = defaults.get(field_name, "")
            
            if field['type'] == 'text':
                field['widget'].delete("1.0", tk.END)
                if default:
                    field['widget'].insert("1.0", default)
            else:
                field['var'].set(default)
