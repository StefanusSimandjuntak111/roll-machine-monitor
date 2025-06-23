"""
Test untuk mock serial device JSK3588.
"""
import pytest
from monitoring.mock.mock_serial import MockSerial, MockJSK3588Device
from serial import SerialException

@pytest.fixture
def mock_serial():
    """Fixture untuk MockSerial."""
    return MockSerial(simulate_errors=False)

def test_mock_serial_open_close(mock_serial):
    """Test open dan close port."""
    assert not mock_serial.is_open
    mock_serial.open()
    assert mock_serial.is_open
    mock_serial.close()
    assert not mock_serial.is_open

def test_mock_serial_write_read(mock_serial):
    """Test write dan read data."""
    mock_serial.open()
    # Query status command
    query = bytes([0x55, 0xAA, 0x02, 0x00, 0x00, 0x01])
    mock_serial.write(query)
    response = mock_serial.read(16)
    assert response.startswith(bytes([0x55, 0xAA]))  # Check header
    assert len(response) == 12  # Check length

def test_mock_serial_invalid_command(mock_serial):
    """Test invalid command."""
    mock_serial.open()
    # Invalid command
    query = bytes([0x00, 0x00, 0x00])
    mock_serial.write(query)
    response = mock_serial.read(16)
    assert len(response) == 0  # No response for invalid command

def test_mock_serial_reset_command(mock_serial):
    """Test reset command."""
    mock_serial.open()
    # Reset command
    query = bytes([0x55, 0xAA, 0x01, 0x00, 0x00, 0x01])
    mock_serial.write(query)
    response = mock_serial.read(16)
    assert response.startswith(bytes([0x55, 0xAA]))
    
    # Parse count from response
    count = int.from_bytes(response[5:8], 'big')  # D5D4D3 bytes
    assert count == 0  # Count should be reset

def test_mock_serial_simulate_errors():
    """Test error simulation."""
    mock_serial = MockSerial(simulate_errors=True)
    mock_serial.open()
    
    # Send multiple queries to trigger error
    query = bytes([0x55, 0xAA, 0x02, 0x00, 0x00, 0x01])
    responses = []
    for _ in range(20):
        mock_serial.write(query)
        response = mock_serial.read(16)
        responses.append(len(response))
    
    # Should have some empty responses due to simulated errors
    assert 0 in responses

def test_mock_serial_movement_simulation(mock_serial):
    """Test simulasi pergerakan mesin."""
    mock_serial.open()
    query = bytes([0x55, 0xAA, 0x02, 0x00, 0x00, 0x01])
    
    # Get initial values
    mock_serial.write(query)
    response1 = mock_serial.read(16)
    count1 = int.from_bytes(response1[5:8], 'big')
    
    # Wait a bit and get new values
    import time
    time.sleep(2)
    
    mock_serial.write(query)
    response2 = mock_serial.read(16)
    count2 = int.from_bytes(response2[5:8], 'big')
    
    # Values should change due to movement simulation
    assert count1 <= count2

def test_mock_serial_not_open():
    """Test operasi saat port belum dibuka."""
    mock_serial = MockSerial()
    with pytest.raises(SerialException):
        mock_serial.write(b'test')
    with pytest.raises(SerialException):
        mock_serial.read()

def test_mock_serial_buffer_clear(mock_serial):
    """Test clear buffer."""
    mock_serial.open()
    query = bytes([0x55, 0xAA, 0x02, 0x00, 0x00, 0x01])
    mock_serial.write(query)
    mock_serial.reset_input_buffer()
    response = mock_serial.read(16)
    assert len(response) == 0  # Buffer should be empty 