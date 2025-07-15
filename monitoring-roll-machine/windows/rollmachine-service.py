#!/usr/bin/env python3
"""
Roll Machine Monitor Windows Service
====================================

This module provides Windows service functionality for the Roll Machine Monitor application.
It allows the application to run as a Windows service with automatic start/stop capabilities.

Requirements:
- pywin32 (for Windows service functionality)
- The main application modules

Usage:
    python rollmachine-service.py install    # Install the service
    python rollmachine-service.py start      # Start the service
    python rollmachine-service.py stop       # Stop the service
    python rollmachine-service.py remove     # Remove the service
    python rollmachine-service.py debug      # Run in debug mode
"""

import os
import sys
import time
import logging
import threading
from pathlib import Path

# Add the parent directory to the path to import the main application
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    import socket
except ImportError:
    print("ERROR: pywin32 not installed!")
    print("Please install pywin32: pip install pywin32")
    sys.exit(1)

try:
    from monitoring.monitor import RollMachineMonitor
    from monitoring.logging_utils import setup_logging
except ImportError as e:
    print(f"ERROR: Failed to import application modules: {e}")
    print("Please ensure the application is properly installed.")
    sys.exit(1)


class RollMachineService(win32serviceutil.ServiceFramework):
    """
    Windows service class for Roll Machine Monitor.
    
    This service runs the main monitoring application in the background
    and handles Windows service lifecycle events.
    """
    
    _svc_name_ = "RollMachineMonitor"
    _svc_display_name_ = "Roll Machine Monitor"
    _svc_description_ = "Industrial monitoring application for JSK3588 roll machines"
    
    def __init__(self, args):
        """Initialize the service."""
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.monitor = None
        self.monitor_thread = None
        self.is_running = False
        
        # Setup logging
        self.setup_service_logging()
        
    def setup_service_logging(self):
        """Setup logging for the service."""
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "service.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("RollMachineService")
        self.logger.info("Service logging initialized")
    
    def SvcStop(self):
        """Stop the service."""
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_running = False
        
        if self.monitor:
            self.logger.info("Stopping monitor...")
            self.monitor.stop()
    
    def SvcDoRun(self):
        """Run the service."""
        self.logger.info("Service starting...")
        self.is_running = True
        
        try:
            # Change to application directory
            app_dir = Path(__file__).parent.parent
            os.chdir(app_dir)
            self.logger.info(f"Changed to application directory: {app_dir}")
            
            # Initialize and start the monitor
            self.monitor = RollMachineMonitor()
            self.logger.info("Monitor initialized")
            
            # Start monitor in a separate thread
            self.monitor_thread = threading.Thread(target=self.run_monitor)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            self.logger.info("Service started successfully")
            
            # Wait for stop event
            while self.is_running:
                # Check if stop event is signaled
                if win32event.WaitForSingleObject(self.stop_event, 1000) == win32event.WAIT_OBJECT_0:
                    break
                    
                # Check if monitor thread is still alive
                if not self.monitor_thread.is_alive():
                    self.logger.error("Monitor thread died unexpectedly")
                    break
                    
        except Exception as e:
            self.logger.error(f"Service error: {e}", exc_info=True)
            self.is_running = False
        finally:
            self.logger.info("Service stopped")
    
    def run_monitor(self):
        """Run the monitor in a separate thread."""
        try:
            self.logger.info("Starting monitor...")
            self.monitor.start()
        except Exception as e:
            self.logger.error(f"Monitor error: {e}", exc_info=True)
            self.is_running = False


def main():
    """Main entry point for the service."""
    if len(sys.argv) == 1:
        # Running as service
        try:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(RollMachineService)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error as e:
            logging.error(f"Service error: {e}")
    else:
        # Command line arguments
        win32serviceutil.HandleCommandLine(RollMachineService)


if __name__ == '__main__':
    main()
