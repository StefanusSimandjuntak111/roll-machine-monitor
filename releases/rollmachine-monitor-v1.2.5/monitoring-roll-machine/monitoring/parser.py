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
    """Validasi checksum paket JSK3588.
    
    Checksum = (sum of all bytes except checksum) & 0xFF
    
    Contoh dari dokumentasi JSK3588:
    - Send: 55 AA 02 00 00 01 → checksum = (55+AA+02+00+00) & 0xFF = 01 ✅
    - Receive: 55 AA 20 0C 01 00 00 23 00 00 01 50 → checksum = (sum semua kecuali 50) & 0xFF = 50 ✅
    """
    if len(packet) < 3:
        return False
    
    # Hitung checksum dari semua byte kecuali byte terakhir (checksum)
    calculated_checksum = sum(packet[:-1]) & 0xFF
    received_checksum = packet[-1]
    
    return calculated_checksum == received_checksum

def parse_packet(packet: bytes) -> Dict[str, Any]:
    """Parse paket JSK3588, validasi header, checksum, dan panjang data.
    
    Format JSK3588: 55 aa com len D6 D5 D4 D3 D2 D1 D0 checksum
    
    Dari contoh dokumentasi:
    55 AA 20 0C 01 00 00 23 00 00 01 50
    - Length 0x0C = 12 bytes, tapi data setelah length = 8 bytes
    - Kemungkinan length mencakup: data(7) + checksum(1) + padding/reserved(4) = 12
    """
    if not packet.startswith(HEADER):
        raise PacketParseError("Header tidak valid")
    if not validate_checksum(packet):
        raise PacketParseError("Checksum tidak valid")
    
    # Minimal: header(2) + com(1) + len(1) + data(1) + chk(1) = 6 bytes
    if len(packet) < 6:
        raise PacketParseError("Panjang paket kurang dari minimal (6 byte)")
    
    com = packet[2]
    length = packet[3]
    data = packet[4:-1]  # Semua data antara length dan checksum
    
    # Sesuai dokumentasi JSK3588, length field mungkin tidak langsung == len(data)
    # Contoh: 55 AA 20 0C ... → length=0x0C=12, tapi actual data=8 bytes
    # Validasi minimal data untuk field D6..D0 (7 bytes)
    if len(data) < 7:
        raise PacketParseError("Data tidak cukup untuk parsing field D6..D0 (min 7 byte)")
    
    logger.debug(f"Packet parsed - COM: 0x{com:02X}, Length: {length}, Data bytes: {len(data)}")
    
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