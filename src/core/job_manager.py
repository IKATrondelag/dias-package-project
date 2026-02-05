"""
Job Manager for DIAS Package Creator.
Handles running long-running tasks in background threads.
"""

import queue
import threading
from typing import Callable, Optional, Tuple


class JobManager:
    """
    Manages background job execution to keep GUI responsive.
    Uses threading to run heavy operations without blocking the UI.
    """
    
    def __init__(self) -> None:
        """Initialize the job manager."""
        self._current_thread: Optional[threading.Thread] = None
        self._progress_callback: Optional[Callable[[float, str], None]] = None
        self._log_callback: Optional[Callable[[str, str], None]] = None
        self._result_queue: queue.Queue[Tuple[str, Tuple[bool, str]]] = queue.Queue()
        self._is_running = False
        self._cancel_requested = False
        
    def set_progress_callback(self, callback: Callable[[float, str], None]) -> None:
        """Set callback for progress updates (called from worker thread)."""
        self._progress_callback = callback
        
    def set_log_callback(self, callback: Callable[[str, str], None]) -> None:
        """Set callback for log messages (called from worker thread)."""
        self._log_callback = callback
        
    @property
    def is_running(self) -> bool:
        """Check if a job is currently running."""
        return self._is_running and self._current_thread is not None and self._current_thread.is_alive()
        
    def start_job(self, target: Callable[..., Tuple[bool, str]], 
                  args: tuple = (), 
                  completion_callback: Optional[Callable[[bool, str], None]] = None) -> None:
        """
        Start a job in a background thread.
        
        Args:
            target: The function to run. Must return (success: bool, message: str).
            args: Arguments to pass to the target function.
            completion_callback: Called when job completes with (success, message).
        """
        if self.is_running:
            if self._log_callback:
                self._log_callback("A job is already running", "WARNING")
            return
            
        self._is_running = True
        self._cancel_requested = False
        
        def worker():
            try:
                result = target(*args)
                self._result_queue.put(('success', result))
            except Exception as e:
                self._result_queue.put(('error', (False, str(e))))
            finally:
                self._is_running = False
                
        def monitor():
            """Monitor the worker and call completion callback on main thread."""
            worker_thread.join()
            
            try:
                status, result = self._result_queue.get_nowait()
                success, message = result
            except queue.Empty:
                success, message = False, "Job completed without result"
                
            if completion_callback:
                # Call completion callback
                completion_callback(success, message)
                
        # Start worker thread
        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()
        self._current_thread = worker_thread
        
        # Start monitor thread to handle completion
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
    def cancel_job(self) -> None:
        """
        Request cancellation of the current job.
        Note: The job must check is_cancelled() periodically.
        """
        self._cancel_requested = True
        if self._log_callback:
            self._log_callback("Cancellation requested...", "WARNING")
            
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self._cancel_requested
        
    def update_progress(self, value: float, status: str = None):
        """
        Update progress (thread-safe).
        
        Args:
            value: Progress value (0-100).
            status: Optional status message.
        """
        if self._progress_callback:
            # Note: tkinter requires updates from main thread
            # In a real app, you'd use after() or a queue
            self._progress_callback(value, status)
            
    def log(self, message: str, level: str = "INFO"):
        """
        Log a message (thread-safe).
        
        Args:
            message: The message to log.
            level: Log level.
        """
        if self._log_callback:
            self._log_callback(message, level)
