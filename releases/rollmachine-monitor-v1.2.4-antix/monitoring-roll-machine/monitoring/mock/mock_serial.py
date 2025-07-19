"""
Mock serial device untuk testing protokol JSK3588.
"""
import random
import time
from typing import Optional, List, Tuple
from serial import SerialException

class MockJSK3588Device:
    """Mock device yang mensimulasikan protokol JSK3588."""
    
    def __init__(self, simulate_errors: bool = False) -> None:
        self.connected = True
        self.simulate_errors = simulate_errors
        self._current_count = 0
        self._current_speed = 0
        self._shift = 1
        self._unit = 0  # 0=meter, 1=yard
        self._decimal = 0  # 0=1, 1=0.1

    def disconnect(self) -> None:
        """Simulasi device disconnect."""
        self.connected = False

    def connect(self) -> None:
        """Simulasi device connect."""
        self.connected = True

    def process_command(self, data: bytes) -> Optional[bytes]:
        """Proses command dari PC dan generate response sesuai protokol."""
        if not self.connected:
            raise SerialException("Device disconnected")

        if self.simulate_errors and random.random() < 0.1:
            # 10% chance untuk error
            return None

        if not data.startswith(bytes([0x55, 0xAA])):
            return None

        command = data[2]  # COM byte
        if command == 0x02:  # Query status
            return self._generate_status_response()
        elif command == 0x01:  # Reset
            self._current_count = 0
            return self._generate_status_response()
        elif command == 0x04:  # Reset akumulasi
            self._current_count = 0
            return self._generate_status_response()
        elif command in [0x10, 0x11, 0x12, 0x13]:  # Set panjang/koefisien
            return self._generate_status_response()
        
        return None

    def _generate_status_response(self) -> bytes:
        """Generate response packet dengan status device."""
        # Update simulasi
        self._simulate_movement()

        # Format response: 55 AA 20 07 D6 D5 D4 D3 D2 D1 D0 CHK
        # D6: Unit & decimal
        # D5D4D3: Current count (3 bytes)
        # D2D1: Speed (2 bytes)
        # D0: Shift
        d6 = (self._unit << 4) | self._decimal
        d5d4d3 = self._current_count.to_bytes(3, 'big')
        d2d1 = self._current_speed.to_bytes(2, 'big')
        d0 = self._shift

        data = bytes([d6]) + d5d4d3 + d2d1 + bytes([d0])
        length = len(data)  # Should be 7 bytes

        packet = bytes([
            0x55, 0xAA,  # Header
            0x20,        # COM (reversed from query)
            length,      # Length of data
        ]) + data
        
        # Add checksum
        chk = sum(packet) & 0xFF
        return packet + bytes([chk])

    def _simulate_movement(self) -> None:
        """Simulasi pergerakan mesin roll."""
        if not self.connected:
            return

        # Simulasi kecepatan random
        if random.random() < 0.1:  # 10% chance untuk ubah kecepatan
            self._current_speed = random.randint(0, 100)

        # Update count berdasarkan kecepatan
        if self._current_speed > 0:
            # Konversi kecepatan (m/min) ke increment per detik
            increment = self._current_speed / 60
            self._current_count += int(increment)

        # Random shift change setiap 1000 count
        if self._current_count % 1000 == 0:
            self._shift = random.randint(1, 3)

class MockSerial:
    """Mock Serial port untuk testing."""
    def __init__(
        self, 
        port: str = "COM1", 
        baudrate: int = 19200, 
        timeout: float = 1,
        simulate_errors: bool = False
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_open = False
        self._device = MockJSK3588Device(simulate_errors)
        self._read_buffer: List[int] = []

    def open(self) -> None:
        """Open port."""
        if self.is_open:
            raise SerialException("Port already open")
        self.is_open = True
        self._device.connect()

    def close(self) -> None:
        """Close port."""
        self.is_open = False
        self._device.disconnect()

    def write(self, data: bytes) -> int:
        """Write data ke device."""
        if not self.is_open:
            raise SerialException("Port not open")
        
        response = self._device.process_command(data)
        if response:
            self._read_buffer.extend(response)
        return len(data)

    def read(self, size: int = 1) -> bytes:
        """Read data dari buffer."""
        if not self.is_open:
            raise SerialException("Port not open")

        # Simulasi timeout
        if not self._read_buffer and self.timeout:
            time.sleep(self.timeout)

        result = []
        for _ in range(min(size, len(self._read_buffer))):
            result.append(self._read_buffer.pop(0))
        return bytes(result)

    def reset_input_buffer(self) -> None:
        """Clear input buffer."""
        self._read_buffer = []

    def reset_output_buffer(self) -> None:
        """Clear output buffer."""
        pass  # No output buffer in mock 