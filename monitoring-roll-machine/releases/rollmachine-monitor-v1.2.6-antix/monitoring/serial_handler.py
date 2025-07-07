"""
Enhanced Serial Handler untuk komunikasi serial dengan mesin JSK3588.
Mengintegrasikan fitur dari serial_tool.py dengan sistem monitoring.
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
from datetime import datetime
from PySide6.QtCore import QThread, Signal, QTimer

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

class SerialReader(QThread):
    """Thread untuk membaca data serial secara kontinu dengan real-time display."""
    data_received = Signal(str)  # Hex data with timestamp
    error_occurred = Signal(str)
    packet_parsed = Signal(dict)  # Parsed packet data
    
    def __init__(self, serial_port, parser_callback=None):
        super().__init__()
        self.serial_port = serial_port
        self.parser_callback = parser_callback
        self.running = False
        
    def run(self):
        """Run the serial reading loop."""
        self.running = True
        while self.running and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    if data:
                        hex_data = ' '.join([f'{b:02X}' for b in data])
                        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                        self.data_received.emit(f"[{timestamp}] RX: {hex_data}")
                        
                        # Try to parse packet if parser callback available
                        if self.parser_callback:
                            try:
                                parsed_data = self.parser_callback(data)
                                if parsed_data:
                                    self.packet_parsed.emit(parsed_data)
                            except Exception as e:
                                logger.debug(f"Parse error: {e}")
                                
                time.sleep(0.01)  # Small delay to prevent high CPU usage
            except Exception as e:
                self.error_occurred.emit(f"Read error: {e}")
                break
                
    def stop(self):
        """Stop the reading thread."""
        self.running = False

class JSKSerialPort:
    """Enhanced handler untuk komunikasi serial dengan mesin JSK3588."""
    
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
        
        # Enhanced features from serial_tool.py
        self.reader_thread: Optional[SerialReader] = None
        self.auto_send_timer: Optional[QTimer] = None
        self.auto_send_interval = 100  # ms
        self.auto_send_command = "55 AA 02 00 00"  # Query Status
        self.auto_send_active = False
        
        # Callbacks for real-time display
        self.on_data_received: Optional[Callable[[str], None]] = None
        self.on_packet_parsed: Optional[Callable[[dict], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

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

    def calculate_checksum(self, hex_data: str) -> int:
        """Calculate checksum for JSK3588 protocol."""
        hex_clean = hex_data.replace(' ', '').upper()
        
        if len(hex_clean) % 2 != 0:
            raise ValueError("Invalid hex data length")
        
        bytes_data = []
        for i in range(0, len(hex_clean), 2):
            byte_val = int(hex_clean[i:i+2], 16)
            bytes_data.append(byte_val)
        
        checksum = sum(bytes_data) % 256
        return checksum

    def add_checksum(self, hex_data: str) -> str:
        """Add checksum to hex data."""
        checksum = self.calculate_checksum(hex_data)
        hex_clean = hex_data.replace(' ', '').upper()
        
        # Add checksum
        result = hex_clean + f"{checksum:02X}"
        
        # Format with spaces
        formatted = ' '.join([result[i:i+2] for i in range(0, len(result), 2)])
        return formatted

    def verify_checksum(self, hex_data: str) -> bool:
        """Verify if the last byte is correct checksum."""
        hex_clean = hex_data.replace(' ', '').upper()
        
        if len(hex_clean) < 4:  # At least 2 bytes
            return False
        
        # Split data and checksum
        data_part = hex_clean[:-2]
        checksum_part = hex_clean[-2:]
        
        # Calculate expected checksum
        expected = self.calculate_checksum(data_part)
        actual = int(checksum_part, 16)
        
        return expected == actual

    def open(self) -> None:
        """Buka koneksi serial dengan auto-detection dan start reader thread."""
        max_retries = 3
        retry_delay = 2.0
        
        for attempt in range(max_retries):
            try:
                # Determine which port to use
                target_port = self._determine_port()
                
                if not self._serial or not self._serial.is_open:
                    logger.info(f"Attempting to open port {target_port} (attempt {attempt + 1}/{max_retries})")
                    
                    # Add small delay before opening to avoid timing issues
                    time.sleep(0.5)
                    
                    self._serial = self._serial_class(target_port)
                    
                    # For mock serial, we need to explicitly call open()
                    if self.simulation_mode:
                        self._serial.open()
                    
                    self._detected_port = target_port
                    logger.info(f"Port {target_port} opened successfully")
                    
                    # Start reader thread
                    self._start_reader_thread()
                    
                    return  # Success, exit retry loop
                    
            except PermissionError as e:
                logger.warning(f"Permission error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    # Try to close any existing connection
                    if self._serial:
                        try:
                            self._serial.close()
                        except:
                            pass
                        self._serial = None
                else:
                    error_msg = f"Permission denied after {max_retries} attempts. Port {self.port} may be in use by another application."
                    logger.error(error_msg)
                    raise SerialException(error_msg)
                    
            except Exception as e:
                error_msg = f"Error opening port {self.port} on attempt {attempt + 1}: {e}"
                logger.error(error_msg)
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise SerialException(error_msg)

    def _start_reader_thread(self):
        """Start the serial reader thread."""
        if self._serial and self._serial.is_open:
            self.reader_thread = SerialReader(self._serial, parse_packet)
            self.reader_thread.data_received.connect(self._on_data_received)
            self.reader_thread.packet_parsed.connect(self._on_packet_parsed)
            self.reader_thread.error_occurred.connect(self._on_error)
            self.reader_thread.start()
            logger.info("Serial reader thread started")

    def _on_data_received(self, data: str):
        """Handle received data for real-time display."""
        if self.on_data_received:
            self.on_data_received(data)
        logger.debug(f"Data received: {data}")

    def _on_packet_parsed(self, data: dict):
        """Handle parsed packet data."""
        if self.on_packet_parsed:
            self.on_packet_parsed(data)
        logger.debug(f"Packet parsed: {data}")

    def _on_error(self, error: str):
        """Handle error from reader thread."""
        if self.on_error:
            self.on_error(error)
        logger.error(f"Serial error: {error}")

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
        """Tutup koneksi serial dan stop threads."""
        # Stop auto send
        self.stop_auto_send()
        
        # Stop reader thread
        if self.reader_thread:
            self.reader_thread.stop()
            self.reader_thread.wait()
            self.reader_thread = None
        
        # Close serial port
        if self._serial and self._serial.is_open:
            self._serial.close()
            port_name = self._detected_port or self.port
            logger.info(f"Port {port_name} closed")

    def send(self, data: bytes) -> None:
        """Kirim data ke port serial dengan real-time display."""
        if not self._serial:
            raise SerialException("Port not open")
        
        try:
            self._serial.write(data)
            hex_data = ' '.join([f'{b:02X}' for b in data])
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            
            # Log for real-time display
            if self.on_data_received:
                self.on_data_received(f"[{timestamp}] TX: {hex_data}")
            
            logger.debug(f"[Kirim] {hex_data}")
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            raise

    def send_hex(self, hex_data: str) -> None:
        """Send hex string data (with optional checksum)."""
        try:
            # Check if data already has checksum
            if len(hex_data.replace(' ', '')) % 2 == 0 and len(hex_data.split()) >= 3:
                # Assume it has checksum, verify
                if not self.verify_checksum(hex_data):
                    # Add checksum if invalid
                    hex_data = self.add_checksum(hex_data)
            else:
                # Add checksum
                hex_data = self.add_checksum(hex_data)
            
            # Convert to bytes and send
            hex_clean = hex_data.replace(' ', '')
            data = bytes.fromhex(hex_clean)
            self.send(data)
            
        except Exception as e:
            logger.error(f"Error sending hex data: {e}")
            raise

    def receive(self, size: int = 1) -> Optional[bytes]:
        """Terima data dari port serial dengan improved handling untuk JSK3588."""
        if not self._serial:
            raise SerialException("Port not open")
        
        try:
            # Clear input buffer first
            self._serial.reset_input_buffer()
            
            # Read with timeout
            data = b""
            start_time = time.time()
            timeout = 3.0  # 3 second timeout
            
            while time.time() - start_time < timeout:
                if self._serial.in_waiting > 0:
                    chunk = self._serial.read(self._serial.in_waiting)
                    data += chunk
                    logger.debug(f"[Terima chunk] {chunk.hex()}")
                    
                    # Check if we have complete JSK3588 response
                    if len(data) >= 6 and data.startswith(b'\x55\xaa'):
                        # Try to determine complete packet length
                        if len(data) >= 4:
                            expected_length = data[3] + 5  # length + header(2) + com(1) + len(1) + checksum(1)
                            if len(data) >= expected_length:
                                logger.debug(f"[Terima lengkap] {data.hex()}")
                                return data
                
                time.sleep(0.1)
            
            # Return whatever we got if timeout
            if data:
                logger.debug(f"[Terima timeout] {data.hex()}")
                return data
            else:
                logger.warning("No data received within timeout")
                return None
                
        except Exception as e:
            logger.error(f"Error receiving data: {e}")
            raise

    # Auto-send functionality
    def start_auto_send(self, command: Optional[str] = None, interval: Optional[int] = None) -> None:
        """Start auto-send functionality."""
        if command is not None:
            self.auto_send_command = command
        if interval is not None:
            self.auto_send_interval = interval
            
        if not self.auto_send_timer:
            self.auto_send_timer = QTimer()
            self.auto_send_timer.timeout.connect(self._auto_send_data)
            
        self.auto_send_timer.start(self.auto_send_interval)
        self.auto_send_active = True
        logger.info(f"Auto-send started: {self.auto_send_command} every {self.auto_send_interval}ms")

    def stop_auto_send(self) -> None:
        """Stop auto-send functionality."""
        if self.auto_send_timer:
            self.auto_send_timer.stop()
        self.auto_send_active = False
        logger.info("Auto-send stopped")

    def _auto_send_data(self) -> None:
        """Send data automatically."""
        try:
            if self._serial and self._serial.is_open:
                self.send_hex(self.auto_send_command)
        except Exception as e:
            logger.error(f"Auto-send error: {e}")

    def is_auto_send_active(self) -> bool:
        """Check if auto-send is active."""
        return self.auto_send_active

    # Enhanced query methods with checksum support
    def query_status(self) -> Optional[Dict[str, Any]]:
        """Query status mesin dan parse hasilnya."""
        try:
            # Use enhanced send with checksum
            self.send_hex("55 AA 02 00 00")
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
            self.send_hex("55 AA 01 00 00")
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
            self.send_hex("55 AA 04 00 00")
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
        """Set length menggunakan command 0x10 dan 0x11 dengan checksum."""
        try:
            # Split 32-bit value ke D3D2 dan D1D0
            d3d2 = (length_value >> 16) & 0xFFFF
            d1d0 = length_value & 0xFFFF
            
            # Command 1: Set D3D2
            cmd1 = f"55 AA 10 00 00"
            self.send_hex(cmd1)
            resp1 = self.receive(16)
            
            if not resp1:
                logger.error("No response to set length command 1")
                return False
            
            # Command 2: Set D1D0 (harus dalam 1 detik)
            d1_byte = (d1d0 >> 8) & 0xFF
            d0_byte = d1d0 & 0xFF
            cmd2 = f"55 AA 11 00 {d1_byte:02X} {d0_byte:02X}"
            self.send_hex(cmd2)
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
        """Set coefficient menggunakan command 0x12 dan 0x13 dengan checksum."""
        try:
            # Split 32-bit value ke D3D2 dan D1D0
            d3d2 = (coeff_value >> 16) & 0xFFFF
            d1d0 = coeff_value & 0xFFFF
            
            # Command 1: Set D3D2
            cmd1 = f"55 AA 12 00 00"
            self.send_hex(cmd1)
            resp1 = self.receive(16)
            
            if not resp1:
                logger.error("No response to set coefficient command 1")
                return False
            
            # Command 2: Set D1D0 (harus dalam 1 detik)
            d1_byte = (d1d0 >> 8) & 0xFF
            d0_byte = d1d0 & 0xFF
            cmd2 = f"55 AA 13 00 {d1_byte:02X} {d0_byte:02X}"
            self.send_hex(cmd2)
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

    # Legacy methods for backward compatibility
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
        """Set stop event untuk auto-recover dan stop auto-send."""
        self._auto_recover = False
        self.stop_auto_send()
        self.close()

    def set_on_disconnect(self, callback: Callable[[], None]) -> None:
        """Set callback jika disconnect."""
        self._on_disconnect = callback

    def _handle_disconnect(self) -> None:
        self.close()
        if hasattr(self, '_on_disconnect') and self._on_disconnect:
            self._on_disconnect() 