#!/usr/bin/env python3
"""
Roll Machine Monitor Windows Service
Runs the monitoring application as a Windows service
"""

import sys
import os
import time
import logging
from pathlib import Path

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
except ImportError:
    print("Error: pywin32 is required for Windows service functionality")
    print("Install with: pip install pywin32")
    sys.exit(1)


class RollMachineMonitorService(win32serviceutil.ServiceFramework):
    """Windows service for Roll Machine Monitor"""
    
    _svc_name_ = "RollMachineMonitor"
    _svc_display_name_ = "Roll Machine Monitor Service"
    _svc_description_ = "Industrial monitoring application for JSK3588 roll machines"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        
        # Get application directory
        self.app_dir = Path(__file__).parent.parent
        self.venv_python = self.app_dir / "venv" / "Scripts" / "python.exe"
        self.log_file = self.app_dir / "logs" / "service.log"
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [SERVICE] %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def SvcStop(self):
        """Stop the service"""
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        """Main service entry point"""
        try:
            self.logger.info("Roll Machine Monitor Service starting...")
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            
            self.main_loop()
            
        except Exception as e:
            self.logger.error(f"Service error: {e}", exc_info=True)
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_ERROR_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, str(e))
            )
        finally:
            self.logger.info("Roll Machine Monitor Service stopped")
            
    def main_loop(self):
        """Main service loop"""
        self.logger.info("Service main loop started")
        
        # Verify application exists
        if not self.venv_python.exists():
            self.logger.error(f"Python executable not found: {self.venv_python}")
            return
            
        monitoring_dir = self.app_dir / "monitoring"
        if not monitoring_dir.exists():
            self.logger.error(f"Monitoring application not found: {monitoring_dir}")
            return
            
        self.logger.info(f"Using Python: {self.venv_python}")
        self.logger.info(f"Application directory: {self.app_dir}")
        
        # Change to application directory
        os.chdir(str(self.app_dir))
        
        # Start monitoring process
        process = None
        restart_count = 0
        max_restarts = 10
        
        while self.is_running:
            try:
                if process is None or process.poll() is not None:
                    # Process not running, start it
                    if restart_count >= max_restarts:
                        self.logger.error(f"Maximum restart attempts ({max_restarts}) reached")
                        break
                        
                    self.logger.info(f"Starting monitoring application (attempt {restart_count + 1})")
                    
                    import subprocess
                    process = subprocess.Popen(
                        [str(self.venv_python), "-m", "monitoring"],
                        cwd=str(self.app_dir),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    restart_count += 1
                    self.logger.info(f"Monitoring application started with PID {process.pid}")
                
                # Wait for stop event or process to exit
                result = win32event.WaitForSingleObject(self.hWaitStop, 5000)  # 5 second timeout
                
                if result == win32event.WAIT_OBJECT_0:
                    # Stop event signaled
                    self.logger.info("Stop event received")
                    break
                    
                # Check if process is still running
                if process and process.poll() is not None:
                    # Process has exited
                    returncode = process.returncode
                    self.logger.warning(f"Monitoring application exited with code {returncode}")
                    
                    if returncode != 0:
                        # Non-zero exit, wait before restart
                        self.logger.info("Waiting 10 seconds before restart...")
                        time.sleep(10)
                    
                    process = None
                    
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(5)
                
        # Clean up
        if process and process.poll() is None:
            self.logger.info("Terminating monitoring application...")
            try:
                process.terminate()
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.logger.warning("Process did not terminate gracefully, killing...")
                process.kill()
                
        self.logger.info("Service main loop ended")


def install_service():
    """Install the Windows service"""
    try:
        # Add current directory to Python path
        script_path = os.path.abspath(__file__)
        
        win32serviceutil.InstallService(
            RollMachineMonitorService,
            RollMachineMonitorService._svc_name_,
            RollMachineMonitorService._svc_display_name_,
            startType=win32service.SERVICE_AUTO_START,
            description=RollMachineMonitorService._svc_description_
        )
        
        print(f"✅ Service '{RollMachineMonitorService._svc_display_name_}' installed successfully")
        print(f"   Service will start automatically with Windows")
        return True
        
    except Exception as e:
        print(f"❌ Failed to install service: {e}")
        return False


def remove_service():
    """Remove the Windows service"""
    try:
        # Stop service if running
        try:
            win32serviceutil.StopService(RollMachineMonitorService._svc_name_)
            print("🛑 Service stopped")
        except:
            pass
            
        # Remove service
        win32serviceutil.RemoveService(RollMachineMonitorService._svc_name_)
        print(f"✅ Service '{RollMachineMonitorService._svc_display_name_}' removed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to remove service: {e}")
        return False


def start_service():
    """Start the Windows service"""
    try:
        win32serviceutil.StartService(RollMachineMonitorService._svc_name_)
        print(f"✅ Service '{RollMachineMonitorService._svc_display_name_}' started")
        return True
    except Exception as e:
        print(f"❌ Failed to start service: {e}")
        return False


def stop_service():
    """Stop the Windows service"""
    try:
        win32serviceutil.StopService(RollMachineMonitorService._svc_name_)
        print(f"🛑 Service '{RollMachineMonitorService._svc_display_name_}' stopped")
        return True
    except Exception as e:
        print(f"❌ Failed to stop service: {e}")
        return False


def service_status():
    """Check service status"""
    try:
        import win32api
        scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE)
        try:
            service = win32service.OpenService(scm, RollMachineMonitorService._svc_name_, win32service.SERVICE_QUERY_STATUS)
            try:
                status = win32service.QueryServiceStatus(service)
                state = status[1]
                
                state_names = {
                    win32service.SERVICE_STOPPED: "STOPPED",
                    win32service.SERVICE_START_PENDING: "START_PENDING", 
                    win32service.SERVICE_STOP_PENDING: "STOP_PENDING",
                    win32service.SERVICE_RUNNING: "RUNNING",
                    win32service.SERVICE_CONTINUE_PENDING: "CONTINUE_PENDING",
                    win32service.SERVICE_PAUSE_PENDING: "PAUSE_PENDING",
                    win32service.SERVICE_PAUSED: "PAUSED"
                }
                
                state_name = state_names.get(state, f"UNKNOWN({state})")
                print(f"Service Status: {state_name}")
                
                if state == win32service.SERVICE_RUNNING:
                    print("✅ Service is running")
                else:
                    print("❌ Service is not running")
                    
                return state == win32service.SERVICE_RUNNING
                
            finally:
                win32service.CloseServiceHandle(service)
        finally:
            win32service.CloseServiceHandle(scm)
            
    except Exception as e:
        print(f"❌ Failed to check service status: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Run as service
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(RollMachineMonitorService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Handle command line arguments
        command = sys.argv[1].lower()
        
        if command == 'install':
            install_service()
        elif command == 'remove':
            remove_service()
        elif command == 'start':
            start_service()
        elif command == 'stop':
            stop_service()
        elif command == 'status':
            service_status()
        elif command == 'restart':
            stop_service()
            time.sleep(2)
            start_service()
        else:
            print("Usage: rollmachine-service.py [install|remove|start|stop|restart|status]")
            sys.exit(1) 