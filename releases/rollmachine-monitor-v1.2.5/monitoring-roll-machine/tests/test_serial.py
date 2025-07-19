import pytest
from unittest.mock import MagicMock, patch
from monitoring.serial_handler import JSKSerialPort

@patch('monitoring.serial_handler.serial.Serial')
def test_open_close(mock_serial):
    port = JSKSerialPort('COM1')
    port.open()
    assert port._serial is not None
    port.close()
    assert port._serial is None

@patch('monitoring.serial_handler.serial.Serial')
def test_send_receive(mock_serial):
    instance = mock_serial.return_value
    instance.is_open = True
    instance.read.return_value = b'\x01\x02'
    port = JSKSerialPort('COM1')
    port.open()
    assert port.send(b'\x01')
    assert port.receive(2) == b'\x01\x02'

@patch('monitoring.serial_handler.serial.Serial')
def test_send_fail(mock_serial):
    instance = mock_serial.return_value
    instance.is_open = False
    port = JSKSerialPort('COM1')
    port.open()
    assert not port.send(b'\x01')

@patch('monitoring.serial_handler.serial.Serial')
def test_auto_recover(mock_serial):
    port = JSKSerialPort('COM1', reconnect_interval=0.1)
    port.open = MagicMock()
    port._serial = None
    port._stop_event.set = MagicMock()
    # Jalankan auto_recover satu iterasi
    port._stop_event.is_set = MagicMock(side_effect=[False, True])
    port.auto_recover()
    port.open.assert_called() 