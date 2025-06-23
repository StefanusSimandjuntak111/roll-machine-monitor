"""
Parser dan validator protokol JSK3588 untuk monitoring mesin roll kain.
"""
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

HEADER = bytes([0x55, 0xAA])

class PacketParseError(Exception):
    """Exception untuk error parsing paket JSK3588."""
    pass

def validate_checksum(packet: bytes) -> bool:
    """Validasi checksum paket JSK3588."""
    if len(packet) < 3:
        return False
    chk = sum(packet[:-1]) & 0xFF
    return chk == packet[-1]

def parse_packet(packet: bytes) -> Dict[str, Any]:
    """Parse paket JSK3588, validasi header, checksum, dan panjang data."""
    if not packet.startswith(HEADER):
        raise PacketParseError("Header tidak valid")
    if not validate_checksum(packet):
        raise PacketParseError("Checksum tidak valid")
    
    # Minimal: header(2) + com(1) + len(1) + data(1) + chk(1) = 6 bytes
    if len(packet) < 6:
        raise PacketParseError("Panjang paket kurang dari minimal (6 byte)")
    
    com = packet[2]
    length = packet[3]
    data = packet[4:-1]
    
    # Validasi panjang data
    if len(data) != length:
        logger.warning(f"Panjang data ({len(data)}) tidak sesuai field LEN ({length})")
        # Tetap coba parse jika data cukup untuk field yang diperlukan
        if len(data) < 7:  # Minimal 7 byte untuk D6..D0
            raise PacketParseError("Data tidak cukup untuk parsing (min 7 byte)")
    
    try:
        fields = parse_fields(data)
        return {"com": com, "length": length, "fields": fields}
    except Exception as e:
        raise PacketParseError(f"Error parsing fields: {str(e)}")

def parse_fields(data: bytes) -> Dict[str, Any]:
    """Parse field D6..D0 dari data payload JSK3588."""
    if len(data) < 7:
        raise PacketParseError("Data field kurang dari 7 byte")
    
    try:
        d6 = data[0]
        decimal_place = bool(d6 & 0x01)
        unit = "yard" if (d6 & 0x10) else "meter"
        
        # Current count (3 bytes)
        current_count = int.from_bytes(data[1:4], 'big')
        if decimal_place:
            current_count = current_count / 10.0
            
        # Speed (2 bytes)
        current_speed = int.from_bytes(data[4:6], 'big')
        
        # Shift (1 byte)
        shift = data[6]
        
        return {
            "decimal_place": decimal_place,
            "unit": unit,
            "current_count": current_count,
            "current_speed": current_speed,
            "shift": shift,
        }
    except Exception as e:
        raise PacketParseError(f"Error parsing field values: {str(e)}") 