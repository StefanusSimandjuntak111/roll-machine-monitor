#!/usr/bin/env python3
"""
JSK3588 Checksum Calculator
Utility untuk menghitung dan verify checksum protokol JSK3588
"""

def calculate_checksum(hex_data: str) -> int:
    """
    Calculate checksum for JSK3588 protocol.
    
    Args:
        hex_data: Hex string (space separated or continuous)
        
    Returns:
        Checksum value (0-255)
    """
    # Remove spaces and convert to uppercase
    hex_clean = hex_data.replace(' ', '').upper()
    
    # Convert to bytes
    if len(hex_clean) % 2 != 0:
        raise ValueError("Invalid hex data length")
    
    bytes_data = []
    for i in range(0, len(hex_clean), 2):
        byte_val = int(hex_clean[i:i+2], 16)
        bytes_data.append(byte_val)
    
    # Calculate checksum (simple sum % 256)
    checksum = sum(bytes_data) % 256
    return checksum

def verify_checksum(hex_data: str) -> bool:
    """
    Verify if the last byte is correct checksum.
    
    Args:
        hex_data: Complete hex string including checksum
        
    Returns:
        True if checksum is correct
    """
    hex_clean = hex_data.replace(' ', '').upper()
    
    if len(hex_clean) < 4:  # At least 2 bytes
        return False
    
    # Split data and checksum
    data_part = hex_clean[:-2]
    checksum_part = hex_clean[-2:]
    
    # Calculate expected checksum
    expected = calculate_checksum(data_part)
    actual = int(checksum_part, 16)
    
    return expected == actual

def add_checksum(hex_data: str) -> str:
    """
    Add checksum to hex data.
    
    Args:
        hex_data: Hex data without checksum
        
    Returns:
        Hex data with checksum appended
    """
    checksum = calculate_checksum(hex_data)
    hex_clean = hex_data.replace(' ', '').upper()
    
    # Add checksum
    result = hex_clean + f"{checksum:02X}"
    
    # Format with spaces
    formatted = ' '.join([result[i:i+2] for i in range(0, len(result), 2)])
    return formatted

def parse_jsk3588_command(hex_data: str) -> dict:
    """
    Parse JSK3588 command format.
    
    Args:
        hex_data: Complete hex command
        
    Returns:
        Dictionary with parsed fields
    """
    hex_clean = hex_data.replace(' ', '').upper()
    
    if len(hex_clean) < 12:  # Minimum 6 bytes
        return {"error": "Data too short"}
    
    try:
        header1 = hex_clean[0:2]
        header2 = hex_clean[2:4]
        com = hex_clean[4:6]
        d1 = hex_clean[6:8]
        d0 = hex_clean[8:10]
        checksum = hex_clean[10:12]
        
        result = {
            "header": f"{header1} {header2}",
            "command": com,
            "data1": d1,
            "data0": d0,
            "checksum": checksum,
            "checksum_valid": verify_checksum(hex_data)
        }
        
        # Decode command
        cmd_int = int(com, 16)
        cmd_descriptions = {
            0x01: "Clear Current Data",
            0x02: "Query Status",
            0x03: "Query Data", 
            0x04: "Clear Accumulated Data",
            0x0A: "Set Length High",
            0x0B: "Set Length Low",
            0x0C: "Set Coefficient High",
            0x0D: "Set Coefficient Low"
        }
        
        result["command_description"] = cmd_descriptions.get(cmd_int, f"Unknown (0x{com})")
        
        return result
        
    except Exception as e:
        return {"error": f"Parse error: {e}"}

def main():
    """Test the checksum calculator."""
    print("JSK3588 Checksum Calculator")
    print("=" * 40)
    
    # Test cases
    test_cases = [
        "55 AA 02 00 00",  # Query Status without checksum
        "55 AA 01 00 00",  # Clear Current without checksum
        "55 AA 03 00 00",  # Query Data without checksum
        "55 AA 04 00 00",  # Clear Accumulated without checksum
    ]
    
    for test_data in test_cases:
        print(f"\nInput: {test_data}")
        
        # Add checksum
        with_checksum = add_checksum(test_data)
        print(f"With checksum: {with_checksum}")
        
        # Verify checksum
        is_valid = verify_checksum(with_checksum)
        print(f"Checksum valid: {is_valid}")
        
        # Parse command
        parsed = parse_jsk3588_command(with_checksum)
        print(f"Command: {parsed.get('command_description', 'Unknown')}")
    
    # Interactive mode
    print("\n" + "=" * 40)
    print("Interactive Mode (Enter 'quit' to exit)")
    
    while True:
        try:
            user_input = input("\nEnter hex data (without checksum): ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
                
            # Add checksum
            result = add_checksum(user_input)
            print(f"Complete command: {result}")
            
            # Parse
            parsed = parse_jsk3588_command(result)
            if "error" not in parsed:
                print(f"Command: {parsed['command_description']}")
                print(f"Checksum valid: {parsed['checksum_valid']}")
            else:
                print(f"Error: {parsed['error']}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main() 