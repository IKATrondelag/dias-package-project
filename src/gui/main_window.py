"""
Main Window for DIAS Package Creator GUI Application.
Handles the main application window layout and user interactions.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path

from .widgets import ProgressFrame, LogFrame, MetadataForm
from .labels import labels
from ..utils.config_loader import ConfigLoader
from ..utils.env_config import config


class MainWindow:
    """Main application window for DIAS Package Creator."""
    
    def __init__(self, controller):
        """
        Initialize the main window.
        
        Args:
            controller: PackageController instance for handling business logic.
        """
        self.controller = controller
        self.root = tk.Tk()
        self.root.title(config.APP_NAME)
        self.root.geometry("1200x700")
        self.root.minsize(1100, 600)
        
        # Load default configuration
        self.config_loader = ConfigLoader()
        
        # Configure style
        self._configure_style()
        
        # Build UI
        self._create_menu()
        self._create_main_layout()
        
        # Bind controller callbacks (wrapped with root.after for thread-safety)
        self.controller.set_progress_callback(self._thread_safe_progress)
        self.controller.set_log_callback(self._thread_safe_log)
        self.controller.set_completion_callback(self._thread_safe_completion)

    def _thread_safe_progress(self, value, status=None):
        """Thread-safe progress update via root.after()."""
        self.root.after(0, self.progress_frame.update_progress, value, status)

    def _thread_safe_log(self, message, level="INFO"):
        """Thread-safe log update via root.after()."""
        self.root.after(0, self.log_frame.log, message, level)

    def _thread_safe_completion(self, success, message):
        """Thread-safe completion callback via root.after()."""
        self.root.after(0, self._on_completion, success, message)
        
    def _configure_style(self):
        """Configure ttk styles for the application."""
        style = ttk.Style()
        style.theme_use('clam')  # Cross-platform theme
        
        # Custom styles
        style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('Heading.TLabel', font=('Helvetica', 11, 'bold'))
        style.configure('Action.TButton', font=('Helvetica', 10, 'bold'), padding=10)
        
    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=labels.MENU_FILE, menu=file_menu)
        file_menu.add_command(label=labels.MENU_NEW_PACKAGE, command=self._reset_form)
        file_menu.add_separator()
        file_menu.add_command(label=labels.MENU_LOAD_TEMPLATE, command=self._load_metadata_template)
        file_menu.add_command(label=labels.MENU_SAVE_TEMPLATE, command=self._save_metadata_template)
        file_menu.add_separator()
        file_menu.add_command(label=labels.MENU_EXIT, command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=labels.MENU_TOOLS, menu=tools_menu)
        tools_menu.add_command(label=labels.MENU_DESCRIBE_PACKAGE, command=self._describe_package)
        tools_menu.add_command(label=labels.MENU_VALIDATE_PACKAGE, command=self._validate_package)
        tools_menu.add_separator()
        tools_menu.add_command(label=labels.MENU_SAVE_AS_DEFAULTS, command=self._save_as_defaults)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=labels.MENU_HELP, menu=help_menu)
        help_menu.add_command(label=labels.MENU_ABOUT, command=self._show_about)
        
    def _create_main_layout(self):
        """Create the main window layout."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Log frame should expand
        
        # Title
        title_label = ttk.Label(main_frame, text=config.APP_NAME, style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 10), sticky="w")
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        main_frame.rowconfigure(1, weight=2)
        
        # Tab 1: Source & Destination
        source_frame = self._create_source_tab(notebook)
        notebook.add(source_frame, text=labels.TAB_SOURCE_DEST)
        
        # Tab 2: Package Metadata
        self.metadata_form = MetadataForm(notebook)
        notebook.add(self.metadata_form, text=labels.TAB_METADATA)
        
        # Load and apply default configuration
        self._load_defaults()
        
        # Progress section
        self.progress_frame = ProgressFrame(main_frame)
        self.progress_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        # Log section
        self.log_frame = LogFrame(main_frame)
        self.log_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        main_frame.rowconfigure(3, weight=3)
        
        # Action buttons
        self._create_action_buttons(main_frame)
        
    def _create_source_tab(self, parent):
        """Create the source and destination selection tab."""
        frame = ttk.Frame(parent, padding="10")
        frame.columnconfigure(1, weight=1)
        
        # Source selection
        ttk.Label(frame, text=labels.HEADING_SOURCE_SELECTION, style='Heading.TLabel').grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        ttk.Label(frame, text=labels.LABEL_SOURCE).grid(row=1, column=0, sticky="w", padx=(0, 10))
        
        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(frame, textvariable=self.source_var, width=60)
        source_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10))
        
        source_btn_frame = ttk.Frame(frame)
        source_btn_frame.grid(row=1, column=2, sticky="e")
        
        ttk.Button(source_btn_frame, text=labels.BTN_FILE, command=self._browse_source_file).pack(side="left", padx=2)
        ttk.Button(source_btn_frame, text=labels.BTN_FOLDER, command=self._browse_source_folder).pack(side="left", padx=2)
        
        # Destination selection
        ttk.Label(frame, text=labels.HEADING_DEST_SELECTION, style='Heading.TLabel').grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(20, 10))
        
        ttk.Label(frame, text=labels.LABEL_OUTPUT_FOLDER).grid(row=3, column=0, sticky="w", padx=(0, 10))
        
        self.dest_var = tk.StringVar()
        dest_entry = ttk.Entry(frame, textvariable=self.dest_var, width=60)
        dest_entry.grid(row=3, column=1, sticky="ew", padx=(0, 10))
        
        ttk.Button(frame, text=labels.BTN_BROWSE, command=self._browse_destination).grid(row=3, column=2, sticky="e")
        
        # Package name
        ttk.Label(frame, text=labels.LABEL_PACKAGE_NAME).grid(row=4, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        
        self.package_name_var = tk.StringVar()
        package_entry = ttk.Entry(frame, textvariable=self.package_name_var, width=60)
        package_entry.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=(10, 0))
        
        return frame
        
    def _create_action_buttons(self, parent):
        """Create the action buttons at the bottom of the window."""
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=4, column=0, sticky="e", pady=(0, 5))
        
        ttk.Button(btn_frame, text=labels.BTN_VALIDATE, style='Action.TButton',
                   command=self._validate).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=labels.BTN_CREATE_PACKAGE, style='Action.TButton',
                   command=self._create_package).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=labels.BTN_RESET, command=self._reset_form).pack(side="left", padx=5)
        
    def _browse_source_file(self):
        """Open file dialog for source file selection."""
        filepath = filedialog.askopenfilename(
            title=labels.DIALOG_SELECT_SOURCE_FILE,
            filetypes=[
                ("All files", "*.*"),
                ("Archive files", "*.tar *.tar.gz *.zip *.siard"),
                ("XML files", "*.xml")
            ]
        )
        if filepath:
            self.source_var.set(filepath)
            # Auto-suggest package name from filename
            if not self.package_name_var.get():
                self.package_name_var.set(Path(filepath).stem)
                
    def _browse_source_folder(self):
        """Open folder dialog for source folder selection."""
        folderpath = filedialog.askdirectory(title=labels.DIALOG_SELECT_SOURCE_FOLDER)
        if folderpath:
            self.source_var.set(folderpath)
            # Auto-suggest package name from folder name
            if not self.package_name_var.get():
                self.package_name_var.set(Path(folderpath).name)
                
    def _browse_destination(self):
        """Open folder dialog for destination selection."""
        folderpath = filedialog.askdirectory(title=labels.DIALOG_SELECT_OUTPUT_FOLDER)
        if folderpath:
            self.dest_var.set(folderpath)
            
    def _validate(self):
        """Validate the current input before package creation."""
        self.log_frame.clear()
        self.log_frame.log(labels.VALIDATION_STARTING, "INFO")
        
        # Gather all inputs
        source = self.source_var.get()
        dest = self.dest_var.get()
        package_name = self.package_name_var.get()
        metadata = self.metadata_form.get_metadata()
        
        # Use controller's comprehensive validation
        validation_result = self.controller.validate_inputs(
            source_path=source,
            output_path=dest,
            package_name=package_name,
            metadata=metadata
        )
        
        # Log all validation info messages
        for info in validation_result.info:
            self.log_frame.log(info.message, "INFO")
            
        # Log all warnings
        for warning in validation_result.warnings:
            self.log_frame.log(warning.message, "WARNING")
            
        # Log all errors
        for error in validation_result.errors:
            self.log_frame.log(error.message, "ERROR")
            
        # Report results
        if not validation_result.is_valid():
            error_messages = validation_result.get_error_messages()
            errors_text = "\n".join(error_messages[:5])  # Show first 5 errors
            if len(error_messages) > 5:
                errors_text += f"\n... and {len(error_messages) - 5} more"
            messagebox.showerror(
                labels.VALIDATION_FAILED_TITLE, 
                labels.VALIDATION_FAILED_MSG.format(count=len(error_messages), errors=errors_text)
            )
            return False
        else:
            # Validation passed
            message = labels.VALIDATION_SUCCESS_MSG
            if validation_result.has_warnings():
                warning_count = len(validation_result.warnings)
                message += f"\n\nNote: {warning_count} warning(s) found. Check the log for details."
                
            self.log_frame.log("Validation passed!", "SUCCESS")
            messagebox.showinfo(labels.VALIDATION_SUCCESS_TITLE, message)
            return True
            
    def _create_package(self):
        """Start the package creation process."""
        if not self._validate():
            return
            
        # Gather all inputs
        source = self.source_var.get()
        dest = self.dest_var.get()
        package_name = self.package_name_var.get()
        metadata = self.metadata_form.get_metadata()
        
        # Disable buttons during processing
        self._set_buttons_enabled(False)
        
        # Start package creation in background thread via controller
        self.controller.create_package(
            source_path=source,
            output_path=dest,
            package_name=package_name,
            metadata=metadata
        )
        
    def _on_completion(self, success, message):
        """Handle completion of package creation."""
        self._set_buttons_enabled(True)
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
            
    def _set_buttons_enabled(self, enabled):
        """Enable or disable action buttons."""
        state = "normal" if enabled else "disabled"
        for widget in self.root.winfo_children():
            self._set_widget_state(widget, state)
            
    def _set_widget_state(self, widget, state):
        """Recursively set widget state."""
        try:
            if isinstance(widget, (ttk.Button, tk.Button)):
                widget.configure(state=state)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._set_widget_state(child, state)
            
    def _reset_form(self):
        """Reset all form fields to default values."""
        self.source_var.set("")
        self.dest_var.set("")
        self.package_name_var.set("")
        self.metadata_form.reset()
        self.progress_frame.reset()
        self.log_frame.clear()
        self.log_frame.log("Form reset.", "INFO")
        
        # Reapply defaults from config
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default metadata from configuration file."""
        try:
            defaults = self.config_loader.load_defaults()
            if defaults:
                self.metadata_form.set_metadata(defaults)
                self.log_frame.log("Loaded default values from configuration file", "INFO")
        except Exception as e:
            # Silently fail - config is optional
            pass
        
    def _load_metadata_template(self):
        """Load metadata from an XML template file."""
        filepath = filedialog.askopenfilename(
            title=labels.DIALOG_SELECT_TEMPLATE,
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filepath:
            try:
                metadata = self.controller.load_metadata_template(filepath)
                self.metadata_form.set_metadata(metadata)
                self.log_frame.log(f"Loaded metadata from: {filepath}", "INFO")
            except Exception as e:
                self.log_frame.log(f"Failed to load metadata: {e}", "ERROR")
                messagebox.showerror("Error", f"Failed to load metadata:\n{e}")
                
    def _save_metadata_template(self):
        """Save current metadata to an XML template file."""
        filepath = filedialog.asksaveasfilename(
            title=labels.DIALOG_SAVE_TEMPLATE,
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filepath:
            try:
                metadata = self.metadata_form.get_metadata()
                self.controller.save_metadata_template(filepath, metadata)
                self.log_frame.log(f"Saved metadata to: {filepath}", "INFO")
            except Exception as e:
                self.log_frame.log(f"Failed to save metadata: {e}", "ERROR")
                messagebox.showerror("Error", f"Failed to save metadata:\n{e}")
                
    def _save_as_defaults(self):
        """Save current metadata as default configuration."""
        filepath = filedialog.asksaveasfilename(
            title="Save Default Configuration",
            defaultextension=".yml",
            initialfile="dias_config.yml",
            filetypes=[("YAML files", "*.yml *.yaml"), ("All files", "*.*")]
        )
        if filepath:
            try:
                metadata = self.metadata_form.get_metadata()
                success = self.config_loader.save_defaults(metadata, filepath)
                if success:
                    self.log_frame.log(f"Default configuration saved to: {filepath}", "SUCCESS")
                    messagebox.showinfo("Success", f"Configuration saved to:\n{filepath}")
            except Exception as e:
                self.log_frame.log(f"Failed to save configuration: {e}", "ERROR")
                messagebox.showerror("Error", f"Failed to save configuration:\n{e}")
    
    def _describe_package(self):
        """Open dialog to describe/inspect an existing DIAS package."""
        from ..dias_package_creator.package_inspector import DIASPackageInspector
        
        # Ask user to select package directory
        package_dir = filedialog.askdirectory(
            title="Select DIAS Package (AIC directory)",
            initialdir=os.path.expanduser("~")
        )
        
        if not package_dir:
            return
        
        # Create description dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Package Description")
        dialog.geometry("750x600")
        dialog.transient(self.root)
        
        # Add text widget for description
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 9))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Progress bar
        progress_frame = ttk.Frame(dialog)
        progress_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        progress_label = ttk.Label(progress_frame, text="Reading package metadata...")
        progress_label.pack(anchor=tk.W)
        
        progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        export_btn = ttk.Button(button_frame, text="Export Description", state=tk.DISABLED)
        export_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        close_btn = ttk.Button(button_frame, text="Close", command=dialog.destroy)
        close_btn.pack(side=tk.RIGHT)
        
        # Store inspector in outer scope for export function
        inspector_instance = {'obj': None}
        
        def log_callback(message, level):
            """Callback for inspector logging."""
            text.insert(tk.END, f"[{level}] {message}\n")
            text.see(tk.END)
            dialog.update()
        
        def export_description():
            """Export description to file."""
            if not hasattr(export_description, 'desc') or not inspector_instance['obj']:
                return
            
            output_path = filedialog.asksaveasfilename(
                title="Save Package Description",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if output_path:
                inspector_instance['obj'].export_description(export_description.desc, output_path)
                messagebox.showinfo("Description Saved", f"Package description saved to:\n{output_path}")
        
        export_btn.configure(command=export_description)
        
        def run_inspection():
            """Run package inspection."""
            progress_bar.start(10)
            text.insert(tk.END, f"Package: {package_dir}\n")
            text.insert(tk.END, "="*70 + "\n\n")
            
            try:
                inspector = DIASPackageInspector(log_callback=log_callback)
                inspector_instance['obj'] = inspector
                desc = inspector.inspect_package(package_dir)
                
                # Store description for export
                export_description.desc = desc
                
                # Display summary
                text.insert(tk.END, "\n")
                text.insert(tk.END, desc.get_summary())
                
                # Enable export button
                export_btn.configure(state=tk.NORMAL)
                
            except Exception as e:
                text.insert(tk.END, f"\n\nERROR: {e}\n")
                import traceback
                text.insert(tk.END, traceback.format_exc())
            finally:
                progress_bar.stop()
                progress_label.configure(text="Inspection complete")
        
        # Run inspection after dialog is shown
        dialog.after(100, run_inspection)
    
    def _validate_package(self):
        """Open dialog to validate an existing DIAS package."""
        from ..dias_package_creator.package_validator import DIASPackageValidator
        
        # Ask user to select package directory
        package_dir = filedialog.askdirectory(
            title="Select DIAS Package (AIC directory)",
            initialdir=os.path.expanduser("~")
        )
        
        if not package_dir:
            return
        
        # Create validation dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Package Validation")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        
        # Add text widget for results
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 9))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Progress bar
        progress_frame = ttk.Frame(dialog)
        progress_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        progress_label = ttk.Label(progress_frame, text="Starting validation...")
        progress_label.pack(anchor=tk.W)
        
        progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        export_btn = ttk.Button(button_frame, text="Export Report", state=tk.DISABLED)
        export_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        close_btn = ttk.Button(button_frame, text="Close", command=dialog.destroy)
        close_btn.pack(side=tk.RIGHT)
        
        # Store validator in outer scope for export function
        validator_instance = {'obj': None}
        
        def log_callback(message, level):
            """Callback for validator logging."""
            text.insert(tk.END, f"[{level}] {message}\n")
            text.see(tk.END)
            dialog.update()
        
        def export_report():
            """Export validation report to file."""
            if not hasattr(export_report, 'result') or not validator_instance['obj']:
                return
            
            output_path = filedialog.asksaveasfilename(
                title="Save Validation Report",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if output_path:
                validator_instance['obj'].export_validation_report(export_report.result, output_path)
                messagebox.showinfo("Report Saved", f"Validation report saved to:\n{output_path}")
        
        export_btn.configure(command=export_report)
        
        def run_validation():
            """Run validation in thread."""
            progress_bar.start(10)
            text.insert(tk.END, f"Validating package: {package_dir}\n")
            text.insert(tk.END, "="*70 + "\n\n")
            
            try:
                validator = DIASPackageValidator(log_callback=log_callback)
                validator_instance['obj'] = validator
                result = validator.validate_package(package_dir)
                
                # Store result for export
                export_report.result = result
                
                # Display summary
                text.insert(tk.END, "\n" + "="*70 + "\n")
                text.insert(tk.END, result.get_summary())
                
                # Enable export button
                export_btn.configure(state=tk.NORMAL)
                
            except Exception as e:
                text.insert(tk.END, f"\n\nERROR: {e}\n")
                import traceback
                text.insert(tk.END, traceback.format_exc())
            finally:
                progress_bar.stop()
                progress_label.configure(text="Validation complete")
        
        # Run validation after dialog is shown
        dialog.after(100, run_validation)
    
    def _show_about(self):
        """Show the about dialog."""
        messagebox.showinfo(
            f"About {config.APP_NAME}",
            f"{config.APP_NAME}\n\n"
            "A standalone application to create DIAS-compliant\n"
            "submission packages.\n\n"
            f"Version: {config.APP_VERSION}\n\n"
            "Tip: Place a 'dias_config.yml' file in the application\n"
            "directory to auto-load default metadata values."
        )
        
    def run(self):
        """Start the main event loop."""
        self.root.mainloop()
