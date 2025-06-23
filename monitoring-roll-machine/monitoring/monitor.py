"""
Monitor untuk mesin roll kain.
"""
from typing import Optional, Dict, Any, Callable
import logging
import threading
import time

from .serial_handler import JSKSerialPort
from .parser import PacketParseError

logger = logging.getLogger(__name__)

class Monitor:
    """Monitor untuk mesin roll kain."""
    def __init__(
        self,
        serial_port: JSKSerialPort,
        on_data: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        poll_interval: float = 1.0
    ) -> None:
        self.serial_port = serial_port
        self.on_data = on_data
        self.on_error = on_error
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.is_running = False

    def start(self) -> None:
        """Mulai monitoring dalam thread terpisah."""
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._monitor_loop)
        self._thread.daemon = True
        self._thread.start()
        self.is_running = True
        logger.info("Monitor started")

    def stop(self) -> None:
        """Stop monitoring thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self.is_running = False
        logger.info("Monitor stopped")

    def _monitor_loop(self) -> None:
        """Loop utama monitoring."""
        while not self._stop_event.is_set():
            try:
                # Query status mesin
                data = self.serial_port.query_status()
                if data and self.on_data:
                    self.on_data(data)
            except PacketParseError as e:
                logger.warning(f"Packet parse error: {e}")
                if self.on_error:
                    self.on_error(e)
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                if self.on_error:
                    self.on_error(e)
            finally:
                # Tunggu interval sebelum query berikutnya
                time.sleep(self.poll_interval)

    def get_status(self) -> Optional[Dict[str, Any]]:
        """Get status terkini dari mesin."""
        try:
            return self.serial_port.query_status()
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return None 