"""
Tests for job_manager.py
Tests for background job execution functionality.
"""

import pytest
import time
import threading
from src.core.job_manager import JobManager


class TestJobManager:
    """Tests for JobManager class."""
    
    def test_init(self):
        """Test JobManager initialization."""
        manager = JobManager()
        assert manager._current_thread is None
        assert manager._progress_callback is None
        assert manager._log_callback is None
        assert not manager._is_running
        assert not manager._cancel_requested
        
    def test_set_progress_callback(self):
        """Test setting progress callback."""
        manager = JobManager()
        callback = lambda progress, msg: None
        manager.set_progress_callback(callback)
        assert manager._progress_callback is callback
        
    def test_set_log_callback(self):
        """Test setting log callback."""
        manager = JobManager()
        callback = lambda msg, level: None
        manager.set_log_callback(callback)
        assert manager._log_callback is callback
        
    def test_is_running_false_initially(self):
        """Test is_running is False when no job started."""
        manager = JobManager()
        assert not manager.is_running
        
    def test_start_job_success(self):
        """Test starting a successful job."""
        manager = JobManager()
        results = []
        completed = threading.Event()
        
        def simple_job():
            return (True, "Job completed successfully")
        
        def on_complete(success, message):
            results.append((success, message))
            completed.set()
        
        manager.start_job(simple_job, completion_callback=on_complete)
        
        # Wait for completion
        completed.wait(timeout=2.0)
        
        assert len(results) == 1
        assert results[0] == (True, "Job completed successfully")
        
    def test_start_job_failure(self):
        """Test job that returns failure."""
        manager = JobManager()
        results = []
        completed = threading.Event()
        
        def failing_job():
            return (False, "Job failed")
        
        def on_complete(success, message):
            results.append((success, message))
            completed.set()
        
        manager.start_job(failing_job, completion_callback=on_complete)
        completed.wait(timeout=2.0)
        
        assert len(results) == 1
        assert results[0] == (False, "Job failed")
        
    def test_start_job_with_exception(self):
        """Test job that raises an exception."""
        manager = JobManager()
        results = []
        completed = threading.Event()
        
        def exception_job():
            raise ValueError("Test error")
        
        def on_complete(success, message):
            results.append((success, message))
            completed.set()
        
        manager.start_job(exception_job, completion_callback=on_complete)
        completed.wait(timeout=2.0)
        
        assert len(results) == 1
        assert results[0][0] is False
        assert "Test error" in results[0][1]
        
    def test_start_job_with_args(self):
        """Test starting a job with arguments."""
        manager = JobManager()
        results = []
        completed = threading.Event()
        
        def job_with_args(a, b, c):
            return (True, f"Sum: {a + b + c}")
        
        def on_complete(success, message):
            results.append((success, message))
            completed.set()
        
        manager.start_job(job_with_args, args=(1, 2, 3), completion_callback=on_complete)
        completed.wait(timeout=2.0)
        
        assert len(results) == 1
        assert results[0] == (True, "Sum: 6")
        
    def test_cannot_start_job_when_running(self):
        """Test that starting a job while one is running logs a warning."""
        manager = JobManager()
        log_messages = []
        started = threading.Event()
        
        def long_job():
            started.set()
            time.sleep(1.0)
            return (True, "Done")
        
        manager.set_log_callback(lambda msg, level: log_messages.append((msg, level)))
        
        # Start first job
        manager.start_job(long_job)
        started.wait(timeout=1.0)
        
        # Try to start second job
        manager.start_job(long_job)
        
        assert any("already running" in msg.lower() for msg, _ in log_messages)
        
    def test_cancel_job(self):
        """Test requesting job cancellation."""
        manager = JobManager()
        log_messages = []
        
        manager.set_log_callback(lambda msg, level: log_messages.append((msg, level)))
        manager.cancel_job()
        
        assert manager._cancel_requested is True
        assert any("cancel" in msg.lower() for msg, _ in log_messages)
        
    def test_is_cancelled(self):
        """Test is_cancelled method."""
        manager = JobManager()
        
        assert not manager.is_cancelled()
        
        manager._cancel_requested = True
        assert manager.is_cancelled()


class TestJobManagerIntegration:
    """Integration tests for JobManager."""
    
    def test_job_with_progress(self):
        """Test job that reports progress."""
        manager = JobManager()
        progress_updates = []
        completed = threading.Event()
        
        def progress_job():
            for i in range(5):
                if manager._progress_callback:
                    manager._progress_callback(i * 20, f"Step {i+1}")
                time.sleep(0.01)
            return (True, "Done with progress")
        
        manager.set_progress_callback(lambda p, m: progress_updates.append((p, m)))
        manager.start_job(progress_job, completion_callback=lambda s, m: completed.set())
        completed.wait(timeout=2.0)
        
        # Should have progress updates
        assert len(progress_updates) > 0
        
    def test_job_respects_cancellation(self):
        """Test that jobs can check for cancellation."""
        manager = JobManager()
        results = []
        completed = threading.Event()
        
        def cancellable_job():
            for i in range(10):
                if manager.is_cancelled():
                    return (False, "Cancelled")
                time.sleep(0.05)
            return (True, "Completed")
        
        def on_complete(success, message):
            results.append((success, message))
            completed.set()
        
        manager.start_job(cancellable_job, completion_callback=on_complete)
        
        # Cancel after a short delay
        time.sleep(0.1)
        manager.cancel_job()
        
        completed.wait(timeout=2.0)
        
        assert len(results) == 1
        assert results[0] == (False, "Cancelled")
