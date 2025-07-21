"""
Enhanced Parser dan validator protokol JSK3588 untuk monitoring mesin roll kain.
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
        
        # Enhanced result with detailed information
        result = {
            "com": com,
            "length": length,
            "fields": fields,
            # Add direct access to key values for cards
            "length_meters": fields["length_meters"],
            "speed_mps": fields["speed_mps"],
            "shift": fields["shift"],
            "unit": fields["unit"],
            "factor": fields["factor"],
            "status": "Valid",
            # Raw hex for debugging
            "raw_hex": packet.hex().upper(),
            "raw_bytes": [f"{b:02X}" for b in packet]
        }
        
        return result
    except Exception as e:
        raise PacketParseError(f"Error parsing fields: {str(e)}")

def parse_fields(data: bytes) -> Dict[str, Any]:
    """Parse field D6..D0 dari data payload JSK3588 dengan interpretasi yang lebih detail."""
    if len(data) < 7:
        raise PacketParseError("Data field kurang dari 7 byte")
    
    try:
        d6 = data[0]
        
        # Parse D6 flags according to JSK3588 documentation
        # OLD IMPLEMENTATION (WRONG):
        # factor_code = d6 & 0x0F  # Lower 4 bits determine factor
        # unit_bit = (d6 & 0x10) >> 4  # bit 4: unit (0=meter, 1=yard)
        # unit = "yard" if unit_bit else "meter"
        # 
        # # Determine factor based on factor_code (01&0F)
        # if factor_code == 0x00:
        #     factor = 1.0
        #     factor_text = "×1.0"
        # elif factor_code == 0x01:
        #     factor = 0.1
        #     factor_text = "×0.1"
        # elif factor_code == 0x02:
        #     factor = 0.01
        #     factor_text = "×0.01"
        # else:
        #     # Default fallback
        #     factor = 0.01
        #     factor_text = f"×{factor_code:02X}"
        
        # NEW IMPLEMENTATION (CORRECT according to JSK3588.md):
        # D6.bit0 保留小数点1位 0.1 (reserve 1 decimal place 0.1)
        # D6.bit4 码制 (0=米制/meter, 1=码制/yard)
        factor_bit = d6 & 0x01  # Only bit 0 determines factor
        unit_bit = (d6 & 0x10) >> 4  # bit 4: unit (0=meter, 1=yard)
        unit = "yard" if unit_bit else "meter"
        
        # Determine factor based on bit 0 only
        if factor_bit == 0x00:
            factor = 1.0
            factor_text = "×1.0"
        elif factor_bit == 0x01:
            factor = 0.1
            factor_text = "×0.1"
        else:
            # Fallback for any other value
            factor = 1.0
            factor_text = "×1.0"
        
        # MACHINE-SPECIFIC PARSER FOR ROLL MACHINE
        # Based on user's machine: 0001.00m → 100.00m
        # This suggests the machine uses a different factor or format
        # Let's try to detect and handle this specific case
        
        # Current count (3 bytes: D5 D4 D3)
        current_count_raw = int.from_bytes(data[1:4], 'big')
        
        # MACHINE-SPECIFIC PARSER FOR ROLL MACHINE
        # Based on user's machine pattern: all values are multiplied by 100
        # 0001.11m → 111.00m (111 = 1.11 × 100)
        # 0001.21 yard → 121.00 yard (121 = 1.21 × 100)
        
        # Check if this is the user's machine format (all values need /100)
        if factor == 1.0:
            # This is the user's machine format - all values are multiplied by 100
            current_count = current_count_raw / 100.0  # Convert any value → actual value
            factor_text = "×0.01 (machine-specific)"
            logger.info(f"Applied machine-specific correction: {current_count_raw} → {current_count}")
        else:
            # Use standard JSK3588 parsing for factor 0.1
        current_count = current_count_raw * factor
        
        # Speed (2 bytes: D2 D1)
        current_speed_raw = int.from_bytes(data[4:6], 'big')
        # Speed uses standard factor (no machine-specific correction needed)
        current_speed = current_speed_raw * factor
        
        # Shift (1 byte: D0)
        shift = data[6]
        shift_text = "Aktif" if shift == 1 else f"Shift {shift}"
        
        # Convert to appropriate units for display
        if unit == "meter":
            length_meters = current_count
            speed_mps = current_speed / 60.0  # Convert from m/min to m/s
            speed_text = f"{current_speed:.2f} m/min"
        else:  # yard
            length_meters = current_count * 0.9144  # Convert yard to meter
            speed_mps = (current_speed * 0.9144) / 60.0  # Convert from yd/min to m/s
            speed_text = f"{current_speed:.2f} yd/min"
        
        return {
            # Raw values
            "factor_bit": factor_bit,  # Changed from factor_code to factor_bit
            "unit": unit,
            "current_count": current_count,
            "current_speed": current_speed,
            "shift": shift,
            
            # Processed values for cards
            "length_meters": length_meters,
            "speed_mps": speed_mps,
            "speed_text": speed_text,
            "shift_text": shift_text,
            "factor": factor_text,
            
            # Raw hex values for debugging
            "d6_hex": f"{d6:02X}",
            "d5_d4_d3_hex": f"{data[1]:02X} {data[2]:02X} {data[3]:02X}",
            "d2_d1_hex": f"{data[4]:02X} {data[5]:02X}",
            "d0_hex": f"{data[6]:02X}",
            
            # Detailed interpretation
            "interpretation": {
                "d6": {
                    "value": f"{d6:02X}",
                    "factor_bit": factor_bit,  # Changed from factor_code to factor_bit
                    "unit": unit,
                    "description": f"Factor: {factor_text}, Unit: {unit}"
                },
                "length": {
                    "raw": f"{data[1]:02X} {data[2]:02X} {data[3]:02X}",
                    "value": current_count_raw,
                    "calculated": f"{current_count:.2f} {unit}",
                    "description": f"Length = {current_count_raw} × {factor} = {current_count:.2f} {unit}"
                },
                "speed": {
                    "raw": f"{data[4]:02X} {data[5]:02X}",
                    "value": current_speed_raw,
                    "calculated": f"{current_speed:.2f} {unit}/min",
                    "description": f"Speed = {current_speed_raw} × {factor} = {current_speed:.2f} {unit}/min"
                },
                "shift": {
                    "value": f"{data[6]:02X}",
                    "text": shift_text,
                    "description": f"Shift: {shift_text}"
                }
            }
        }
    except Exception as e:
        raise PacketParseError(f"Error parsing field values: {str(e)}")

def format_packet_table(packet: bytes) -> str:
    """Format packet data sebagai tabel untuk display."""
    if len(packet) < 6:
        return "Invalid packet"
    
    try:
        parsed = parse_packet(packet)
        fields = parsed["fields"]
        
        table = f"""
| Byte Index | Hex Value  | Arti                                             |
| ---------- | ---------- | ------------------------------------------------ |
| 0–1        | `{packet[0]:02X} {packet[1]:02X}`    | Header (tetap)                                   |
| 2          | `{packet[2]:02X}`       | COM = {packet[2] >> 4}, Addr = {packet[2] & 0x0F}                                |
| 3          | `{packet[3]:02X}`       | Panjang payload = {packet[3]} byte                        |
| 4          | `{packet[4]:02X}`       | {fields['interpretation']['d6']['description']}                                   |
| 5–7        | `{fields['d5_d4_d3_hex']}` | Panjang = `0x{fields['interpretation']['length']['raw'].replace(' ', '')}` = {fields['interpretation']['length']['description']} |
| 8–9        | `{fields['d2_d1_hex']}`    | Kecepatan = {fields['interpretation']['speed']['description']}   |
| 10         | `{fields['d0_hex']}`       | Shift: {fields['shift_text']}                                 |
| 11         | `{packet[-1]:02X}`       | Checksum (valid)                                 |

| Field         | Nilai        |
| ------------- | ------------ |
| **Panjang**   | `{fields['length_meters']:.2f} m`     |
| **Kecepatan** | `{fields['speed_text']}`   |
| **Faktor**    | `{fields['factor']}`      |
| **Unit**      | {fields['unit'].title()}        |
| **Shift**     | {fields['shift_text']} |
| **Status**    | Valid        |
"""
        return table
    except Exception as e:
        return f"Error formatting table: {e}" 