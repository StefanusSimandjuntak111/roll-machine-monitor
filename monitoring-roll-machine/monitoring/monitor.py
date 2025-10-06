"""
Enhanced Monitor untuk mesin roll kain dengan auto-send dan real-time display.
"""
from typing import Optional, Dict, Any, Callable
import logging
import threading
import time

from .serial_handler import JSKSerialPort
from .parser import PacketParseError

logger = logging.getLogger(__name__)

class Monitor:
    """Enhanced Monitor untuk mesin roll kain dengan auto-send."""
    def __init__(
        self,
        serial_port: JSKSerialPort,
        on_data: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_serial_data: Optional[Callable[[str], None]] = None,
        poll_interval: float = 1.0,
        auto_send_enabled: bool = True,
        auto_send_command: str = "55 AA 02 00 00",
        auto_send_interval: int = 1200  # Changed from 100ms to 1200ms
    ) -> None:
        self.serial_port = serial_port
        self.on_data = on_data
        self.on_error = on_error
        self.on_serial_data = on_serial_data
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.is_running = False
        self.product_info: Dict[str, Any] = {}
        
        # Auto-send configuration
        self.auto_send_enabled = auto_send_enabled
        self.auto_send_command = auto_send_command
        self.auto_send_interval = auto_send_interval
        
        # FIX: Add watchdog timer for idle detection
        self.last_activity = time.time()
        self.watchdog_interval = 300  # 5 minutes
        self._watchdog_thread: Optional[threading.Thread] = None
        
        # Setup serial callbacks for real-time display
        self._setup_serial_callbacks()

    def _setup_serial_callbacks(self):
        """Setup callbacks untuk real-time serial data display."""
        if self.serial_port:
            self.serial_port.on_data_received = self._on_serial_data_received
            self.serial_port.on_packet_parsed = self._on_packet_parsed
            self.serial_port.on_error = self._on_serial_error

    def _on_serial_data_received(self, data: str):
        """Handle received serial data for real-time display."""
        if self.on_serial_data:
            self.on_serial_data(data)
        logger.debug(f"Serial data: {data}")

    def _on_packet_parsed(self, data: dict):
        """Handle parsed packet data."""
        # FIX: Update activity timestamp to prevent false idle detection
        self.last_activity = time.time()
        
        if self.on_data:
            self.on_data(data)
        logger.debug(f"Packet parsed: {data}")

    def _on_serial_error(self, error: str):
        """Handle serial error."""
        # FIX: Update activity timestamp even on errors
        self.last_activity = time.time()
        
        logger.error(f"Serial error: {error}")
        if self.on_error:
            # Create exception object for error callback
            class SerialError(Exception):
                pass
            self.on_error(SerialError(error))

    def start(self) -> None:
        """Mulai monitoring dengan auto-send."""
        if self._thread and self._thread.is_alive():
            return

        # Start auto-send if enabled
        if self.auto_send_enabled:
            self.start_auto_send()

        # FIX: Start watchdog thread
        self._start_watchdog()

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._monitor_loop)
        self._thread.daemon = True
        self._thread.start()
        self.is_running = True
        logger.info("Monitor started with auto-send and watchdog")

    def stop(self) -> None:
        """Stop monitoring thread dan auto-send."""
        self._stop_event.set()
        
        # Stop auto-send
        self.stop_auto_send()
        
        # FIX: Stop watchdog thread
        self._stop_watchdog()
        
        if self._thread:
            self._thread.join()
        self.is_running = False
        logger.info("Monitor stopped")

    def start_auto_send(self, command: Optional[str] = None, interval: Optional[int] = None) -> None:
        """Start auto-send functionality."""
        if command:
            self.auto_send_command = command
        if interval:
            self.auto_send_interval = interval
            
        if self.serial_port:
            self.serial_port.start_auto_send(self.auto_send_command, self.auto_send_interval)
            logger.info(f"Auto-send started: {self.auto_send_command} every {self.auto_send_interval}ms")

    def stop_auto_send(self) -> None:
        """Stop auto-send functionality."""
        if self.serial_port:
            self.serial_port.stop_auto_send()
            logger.info("Auto-send stopped")

    def is_auto_send_active(self) -> bool:
        """Check if auto-send is active."""
        if self.serial_port:
            return self.serial_port.is_auto_send_active()
        return False

    def send_manual_command(self, hex_command: str) -> None:
        """Send manual command to device."""
        try:
            if self.serial_port:
                self.serial_port.send_hex(hex_command)
                logger.info(f"Manual command sent: {hex_command}")
        except Exception as e:
            logger.error(f"Error sending manual command: {e}")
            if self.on_error:
                self.on_error(e)

    def _monitor_loop(self) -> None:
        """Loop utama monitoring (simplified karena auto-send menangani polling)."""
        while not self._stop_event.is_set():
            try:
                # With auto-send, we don't need manual polling
                # The serial reader thread handles data reception
                # Just keep the thread alive
                time.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                if self.on_error:
                    self.on_error(e)

    def get_status(self) -> Optional[Dict[str, Any]]:
        """Get status terkini dari mesin."""
        try:
            return self.serial_port.query_status()
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return None

    def update_product_info(self, product_info: Dict[str, Any]) -> None:
        """Update product information."""
        self.product_info = product_info
        logger.info(f"Product info updated: {product_info}")

    def clear_current_data(self) -> Optional[Dict[str, Any]]:
        """Clear current data dan return data."""
        try:
            return self.serial_port.clear_current_data()
        except Exception as e:
            logger.error(f"Error clearing current data: {e}")
            return None

    def clear_accumulated_data(self) -> Optional[Dict[str, Any]]:
        """Clear accumulated data dan return data."""
        try:
            return self.serial_port.clear_accumulated_data()
        except Exception as e:
            logger.error(f"Error clearing accumulated data: {e}")
            return None

    def set_length(self, length_value: int) -> bool:
        """Set length value."""
        try:
            return self.serial_port.set_length(length_value)
        except Exception as e:
            logger.error(f"Error setting length: {e}")
            return False

    def set_coefficient(self, coeff_value: int) -> bool:
        """Set coefficient value."""
        try:
            return self.serial_port.set_coefficient(coeff_value)
        except Exception as e:
            logger.error(f"Error setting coefficient: {e}")
            return False 

    def _start_watchdog(self) -> None:
        """Start watchdog thread untuk mencegah hang setelah idle."""
        if self._watchdog_thread and self._watchdog_thread.is_alive():
            return
            
        self._watchdog_thread = threading.Thread(target=self._watchdog_loop)
        self._watchdog_thread.daemon = True
        self._watchdog_thread.start()
        logger.info("Watchdog thread started")

    def _stop_watchdog(self) -> None:
        """Stop watchdog thread."""
        if self._watchdog_thread:
            self._watchdog_thread.join(timeout=1.0)
            self._watchdog_thread = None
        logger.info("Watchdog thread stopped")

    def _watchdog_loop(self) -> None:
        """Watchdog loop untuk mendeteksi idle dan restart jika perlu."""
        while not self._stop_event.is_set():
            try:
                current_time = time.time()
                
                # Check if serial communication is idle
                if current_time - self.last_activity > self.watchdog_interval:
                    logger.warning("Watchdog: Serial communication idle for too long, restarting...")
                    
                    # Try to restart serial communication
                    if self.serial_port:
                        try:
                            self.serial_port.restart_if_needed()
                            self.last_activity = current_time
                            logger.info("Watchdog: Serial communication restarted successfully")
                        except Exception as e:
                            logger.error(f"Watchdog: Failed to restart serial communication: {e}")
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Watchdog error: {e}")
                time.sleep(60)  # Wait before retrying 