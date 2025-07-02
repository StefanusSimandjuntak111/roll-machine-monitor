"""
Handler untuk komunikasi serial dengan mesin JSK3588.
"""
from typing import Optional, Dict, Any, Union, Callable
import logging
import time
import threading
import serial
from serial.serialutil import SerialException

from .parser import parse_packet, PacketParseError
from .mock.mock_serial import MockSerial

logger = logging.getLogger(__name__)

class JSKSerialPort:
    """Handler untuk komunikasi serial dengan mesin JSK3588."""
    def __init__(
        self,
        port: str = "COM1",
        baudrate: int = 19200,
        timeout: float = 1.0,
        simulation_mode: bool = False,
        simulate_errors: bool = False
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.simulation_mode = simulation_mode
        self._serial: Optional[Union[serial.Serial, MockSerial]] = None
        self._auto_recover = False
        self._simulate_errors = simulate_errors

        if simulation_mode:
            self._serial_class = lambda: MockSerial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                simulate_errors=simulate_errors
            )
        else:
            self._serial_class = lambda: serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout
            )

    def open(self) -> None:
        """Buka koneksi serial."""
        try:
            if not self._serial or not self._serial.is_open:
                self._serial = self._serial_class()
                logger.info(f"Port {self.port} opened successfully")
        except Exception as e:
            logger.error(f"Error opening port {self.port}: {e}")
            raise

    def close(self) -> None:
        """Tutup koneksi serial."""
        if self._serial and self._serial.is_open:
            self._serial.close()
            logger.info(f"Port {self.port} closed")

    def send(self, data: bytes) -> None:
        """Kirim data ke port serial."""
        if not self._serial:
            raise SerialException("Port not open")
        
        try:
            self._serial.write(data)
            logger.debug(f"[Kirim       ] {data.hex()}")
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            raise

    def receive(self, size: int = 1) -> Optional[bytes]:
        """Terima data dari port serial."""
        if not self._serial:
            raise SerialException("Port not open")
        
        try:
            data = self._serial.read(size)
            if data:
                logger.debug(f"[Terima      ] {data.hex()}")
            return data if data else None
        except Exception as e:
            logger.error(f"Error receiving data: {e}")
            raise

    def query_status(self) -> Optional[Dict[str, Any]]:
        """Query status mesin dan parse hasilnya."""
        try:
            # Kirim query status (command 0x02)
            query = bytes([0x55, 0xAA, 0x02, 0x00, 0x00, 0x01])
            self.send(query)
            resp = self.receive(16)
            if resp:
                return parse_packet(resp)
            else:
                logger.warning("No response from machine")
                return None
        except Exception as e:
            logger.error(f"Error querying status: {e}")
            raise

    def enable_auto_recover(self) -> None:
        """Enable auto recovery jika koneksi terputus."""
        self._auto_recover = True

    def disable_auto_recover(self) -> None:
        """Disable auto recovery."""
        self._auto_recover = False

    def _try_recover(self) -> bool:
        """Coba recover koneksi yang terputus."""
        try:
            self.close()
            time.sleep(1)  # Tunggu sebentar sebelum reconnect
            self.open()
            return True
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
            return False

    def auto_recover(self) -> None:
        """Loop auto-recover koneksi serial jika terputus."""
        while self._auto_recover:
            if not self._serial or not self._serial.is_open:
                logger.warning("Serial port terputus. Mencoba reconnect...")
                self._try_recover()
            time.sleep(5)

    def start_auto_recover(self) -> None:
        """Jalankan thread auto-recover."""
        threading.Thread(target=self.auto_recover, daemon=True).start()

    def stop(self) -> None:
        """Set stop event untuk auto-recover."""
        self._auto_recover = False
        self.close()

    def set_on_disconnect(self, callback: Callable[[], None]) -> None:
        """Set callback jika disconnect."""
        self._on_disconnect = callback

    def _handle_disconnect(self) -> None:
        self.close()
        if self._on_disconnect:
            self._on_disconnect() 