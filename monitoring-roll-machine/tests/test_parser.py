import pytest
from monitoring.parser import validate_checksum, parse_packet, PacketParseError

def test_validate_checksum_valid():
    # Paket dummy: 55 AA 20 08 01 02 03 04 05 06 07 08 CHK
    packet = bytes([0x55, 0xAA, 0x20, 0x08, 1,2,3,4,5,6,7,8])
    chk = sum(packet) & 0xFF
    valid_packet = packet + bytes([chk])
    assert validate_checksum(valid_packet)

def test_validate_checksum_invalid():
    packet = bytes([0x55, 0xAA, 0x20, 0x08, 1,2,3,4,5,6,7,8,0x00])
    assert not validate_checksum(packet)

def test_parse_packet_valid():
    # Paket minimal valid (header, com, len, 8 data, chk)
    data = [0x55, 0xAA, 0x20, 0x08, 1,2,3,4,5,6,7,8]
    chk = sum(data) & 0xFF
    packet = bytes(data + [chk])
    result = parse_packet(packet)
    assert result["com"] == 0x20
    assert result["length"] == 8
    assert "fields" in result

def test_parse_packet_invalid_header():
    packet = bytes([0x00, 0xAA, 0x20, 0x08, 1,2,3,4,5,6,7,8,0x00])
    with pytest.raises(PacketParseError):
        parse_packet(packet)

def test_parse_packet_invalid_checksum():
    packet = bytes([0x55, 0xAA, 0x20, 0x08, 1,2,3,4,5,6,7,8,0x00])
    with pytest.raises(PacketParseError):
        parse_packet(packet) 