"""Pytest configuration for test log management."""

import glob
import os
import sys
from datetime import datetime
from pathlib import Path


class TeeOutput:
    """Tee output to both stdout/stderr and a log file."""

    def __init__(self, file_path, original_stream):
        self.file = open(file_path, "a", encoding="utf-8")
        self.original_stream = original_stream

    def write(self, data):
        self.file.write(data)
        self.file.flush()
        self.original_stream.write(data)
        self.original_stream.flush()

    def flush(self):
        self.file.flush()
        self.original_stream.flush()

    def close(self):
        self.file.close()

    def __getattr__(self, name):
        # Forward other attributes to original stream
        return getattr(self.original_stream, name)


def pytest_configure(config):
    """Configure pytest and manage test log rotation."""
    # Ensure test-logs directory exists
    test_logs_dir = Path("test-logs")
    test_logs_dir.mkdir(exist_ok=True)

    # Clean up old log files first (keep only last 3 timestamped files)
    log_files = sorted(
        glob.glob(str(test_logs_dir / "pytest-*.log")), key=os.path.getmtime, reverse=True
    )

    # Remove old log files, keeping only the last 3
    for old_log in log_files[3:]:
        try:
            os.remove(old_log)
        except OSError:
            pass  # File might have been removed already

    # Set up output capture to log file
    log_file_path = test_logs_dir / "pytest.log"
    # Clear/create the log file for this run
    log_file_path.write_text("")

    # Store tee objects on config for cleanup
    config._pytest_log_tee_stdout = TeeOutput(log_file_path, sys.stdout)
    config._pytest_log_tee_stderr = TeeOutput(log_file_path, sys.stderr)

    # Replace stdout/stderr with tee objects
    sys.stdout = config._pytest_log_tee_stdout
    sys.stderr = config._pytest_log_tee_stderr


def pytest_sessionstart(session):
    """Write session start info to log file."""
    log_file_path = Path("test-logs/pytest.log")
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"\n{'=' * 80}\n")
        f.write(f"Test session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'=' * 80}\n\n")


def pytest_runtest_logreport(report):
    """Log test results to file."""
    log_file_path = Path("test-logs/pytest.log")
    with open(log_file_path, "a", encoding="utf-8") as f:
        if report.when == "call":
            status = report.outcome.upper()
            f.write(f"{status}: {report.nodeid}\n")
            if report.outcome == "failed":
                f.write(f"  {report.longrepr}\n")


def pytest_sessionfinish(session, exitstatus):
    """Write session finish info to log file."""
    log_file_path = Path("test-logs/pytest.log")
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"\n{'=' * 80}\n")
        f.write(f"Test session finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Exit status: {exitstatus}\n")
        f.write(f"{'=' * 80}\n\n")


def pytest_unconfigure(config):
    """Clean up after pytest session."""
    # Restore original stdout/stderr first
    if hasattr(config, "_pytest_log_tee_stdout"):
        sys.stdout = config._pytest_log_tee_stdout.original_stream
        config._pytest_log_tee_stdout.close()
    if hasattr(config, "_pytest_log_tee_stderr"):
        sys.stderr = config._pytest_log_tee_stderr.original_stream
        config._pytest_log_tee_stderr.close()

    # Now rename the completed log file to timestamped version
    test_logs_dir = Path("test-logs")
    current_log = test_logs_dir / "pytest.log"
    if current_log.exists() and current_log.stat().st_size > 0:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        timestamped_log = test_logs_dir / f"pytest-{timestamp}.log"
        current_log.rename(timestamped_log)

    # Clean up old log files after renaming (keep only last 3 timestamped files)
    log_files = sorted(
        glob.glob(str(test_logs_dir / "pytest-*.log")), key=os.path.getmtime, reverse=True
    )

    # Remove old log files, keeping only the last 3
    for old_log in log_files[3:]:
        try:
            os.remove(old_log)
        except OSError:
            pass  # File might have been removed already
