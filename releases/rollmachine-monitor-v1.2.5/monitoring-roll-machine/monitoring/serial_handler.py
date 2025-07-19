"""
Handler untuk komunikasi serial dengan mesin JSK3588.
"""
from typing import Optional, Dict, Any, Union, Callable, List
import logging
import time
import threading
import platform
import os
import serial
import serial.tools.list_ports
from serial.serialutil import SerialException

from .parser import parse_packet, PacketParseError
from .mock.mock_serial import MockSerial

logger = logging.getLogger(__name__)

def auto_detect_serial_ports() -> List[str]:
    """Auto-detect available serial ports for JSK3588."""
    ports = []
    
    try:
        # Use pyserial port detection
        available_ports = serial.tools.list_ports.comports()
        
        for port in available_ports:
            port_name = port.device
            
            # For CH340 devices, prioritize them
            if ('CH340' in str(port.description) or 
                'USB-SERIAL' in str(port.description) or
                '1a86' in str(port.hwid)):
                ports.insert(0, port_name)  # Add to beginning
                logger.info(f"CH340 device found: {port_name} - {port.description}")
            else:
                ports.append(port_name)
                logger.debug(f"Serial port found: {port_name} - {port.description}")
        
        # Platform-specific fallbacks
        system = platform.system()
        if system == "Linux":
            # Check common Linux serial devices
            linux_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
            for lport in linux_ports:
                if os.path.exists(lport) and lport not in ports:
                    ports.append(lport)
        elif system == "Windows":
            # Check common Windows COM ports
            win_ports = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6']
            for wport in win_ports:
                if wport not in ports:
                    ports.append(wport)
    
    except Exception as e:
        logger.warning(f"Error during port detection: {e}")
        # Fallback to common ports
        if platform.system() == "Linux":
            ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0']
        else:
            ports = ['COM1', 'COM2', 'COM3', 'COM4']
    
    logger.info(f"Detected serial ports: {ports}")
    return ports

class JSKSerialPort:
    """Handler untuk komunikasi serial dengan mesin JSK3588."""
    def __init__(
        self,
        port: str = "AUTO",
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
        self._detected_port: Optional[str] = None

        if simulation_mode:
            self._serial_class = lambda p: MockSerial(
                port=p,
                baudrate=baudrate,
                timeout=timeout,
                simulate_errors=simulate_errors
            )
        else:
            self._serial_class = lambda p: serial.Serial(
                port=p,
                baudrate=baudrate,
                timeout=timeout
            )

    def open(self) -> None:
        """Buka koneksi serial dengan auto-detection jika diperlukan."""
        try:
            # Determine which port to use
            target_port = self._determine_port()
            
            if not self._serial or not self._serial.is_open:
                self._serial = self._serial_class(target_port)
                
                # For mock serial, we need to explicitly call open()
                if self.simulation_mode:
                    self._serial.open()
                
                self._detected_port = target_port
                logger.info(f"Port {target_port} opened successfully")
        except Exception as e:
            error_msg = f"Error opening port {self.port}: {e}"
            logger.error(error_msg)
            raise SerialException(error_msg)

    def _determine_port(self) -> str:
        """Determine which port to use - handle AUTO detection."""
        if self.port == "AUTO":
            # Auto-detect port
            available_ports = auto_detect_serial_ports()
            
            if not available_ports:
                raise SerialException("No serial ports detected. Please check USB connection.")
            
            # Use first available port
            selected_port = available_ports[0]
            logger.info(f"Auto-detected port: {selected_port}")
            return selected_port
        else:
            # Use specified port
            return self.port

    def get_active_port(self) -> Optional[str]:
        """Get the currently active/detected port."""
        return self._detected_port or self.port

    def close(self) -> None:
        """Tutup koneksi serial."""
        if self._serial and self._serial.is_open:
            self._serial.close()
            port_name = self._detected_port or self.port
            logger.info(f"Port {port_name} closed")

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

    def clear_current_data(self) -> Optional[Dict[str, Any]]:
        """Clear current collected data dan return data (command 0x01)."""
        try:
            query = bytes([0x55, 0xAA, 0x01, 0x00, 0x00, 0x00])
            self.send(query)
            resp = self.receive(16)
            if resp:
                return parse_packet(resp)
            else:
                logger.warning("No response from machine")
                return None
        except Exception as e:
            logger.error(f"Error clearing current data: {e}")
            raise

    def clear_accumulated_data(self) -> Optional[Dict[str, Any]]:
        """Clear accumulated data dan return data (command 0x04)."""
        try:
            query = bytes([0x55, 0xAA, 0x04, 0x00, 0x00, 0x03])
            self.send(query)
            resp = self.receive(16)
            if resp:
                return parse_packet(resp)
            else:
                logger.warning("No response from machine")
                return None
        except Exception as e:
            logger.error(f"Error clearing accumulated data: {e}")
            raise

    def set_length(self, length_value: int) -> bool:
        """Set length menggunakan command 0x10 dan 0x11.
        
        Sesuai dokumentasi: dua command harus dikirim dalam 1 detik.
        Command 0x10 untuk D3D2, command 0x11 untuk D1D0.
        """
        try:
            # Split 32-bit value ke D3D2 dan D1D0
            d3d2 = (length_value >> 16) & 0xFFFF
            d1d0 = length_value & 0xFFFF
            
            # Command 1: Set D3D2
            checksum1 = (0x55 + 0xAA + 0x10 + 0x00 + 0x00) & 0xFF
            cmd1 = bytes([0x55, 0xAA, 0x10, 0x00, 0x00, checksum1])
            self.send(cmd1)
            resp1 = self.receive(16)
            
            if not resp1:
                logger.error("No response to set length command 1")
                return False
            
            # Command 2: Set D1D0 (harus dalam 1 detik)
            d1_byte = (d1d0 >> 8) & 0xFF
            d0_byte = d1d0 & 0xFF
            checksum2 = (0x55 + 0xAA + 0x11 + 0x00 + d1_byte + d0_byte) & 0xFF
            cmd2 = bytes([0x55, 0xAA, 0x11, 0x00, d1_byte, d0_byte, checksum2])
            self.send(cmd2)
            resp2 = self.receive(16)
            
            if not resp2:
                logger.error("No response to set length command 2")
                return False
                
            # Parse response untuk validasi success
            parsed_resp = parse_packet(resp2)
            return parsed_resp is not None
            
        except Exception as e:
            logger.error(f"Error setting length: {e}")
            return False

    def set_coefficient(self, coeff_value: int) -> bool:
        """Set coefficient menggunakan command 0x12 dan 0x13.
        
        Sesuai dokumentasi: dua command harus dikirim dalam 1 detik.
        Command 0x12 untuk D3D2, command 0x13 untuk D1D0.
        """
        try:
            # Split 32-bit value ke D3D2 dan D1D0
            d3d2 = (coeff_value >> 16) & 0xFFFF
            d1d0 = coeff_value & 0xFFFF
            
            # Command 1: Set D3D2
            checksum1 = (0x55 + 0xAA + 0x12 + 0x00 + 0x00) & 0xFF
            cmd1 = bytes([0x55, 0xAA, 0x12, 0x00, 0x00, checksum1])
            self.send(cmd1)
            resp1 = self.receive(16)
            
            if not resp1:
                logger.error("No response to set coefficient command 1")
                return False
            
            # Command 2: Set D1D0 (harus dalam 1 detik)
            d1_byte = (d1d0 >> 8) & 0xFF
            d0_byte = d1d0 & 0xFF
            checksum2 = (0x55 + 0xAA + 0x13 + 0x00 + d1_byte + d0_byte) & 0xFF
            cmd2 = bytes([0x55, 0xAA, 0x13, 0x00, d1_byte, d0_byte, checksum2])
            self.send(cmd2)
            resp2 = self.receive(16)
            
            if not resp2:
                logger.error("No response to set coefficient command 2")
                return False
                
            # Parse response untuk validasi success
            parsed_resp = parse_packet(resp2)
            return parsed_resp is not None
            
        except Exception as e:
            logger.error(f"Error setting coefficient: {e}")
            return False

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