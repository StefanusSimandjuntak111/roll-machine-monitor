"""
Modul untuk menangani konfigurasi aplikasi.
"""
import os
import json
import math
import tempfile
from typing import Dict, Any

# Try to use Program Files location for config
def get_config_file_path():
    """Get config file path with Program Files priority."""
    # Try Program Files first
    program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
    program_files_config = os.path.join(program_files, "Roll Machine Monitor", "config.json")
    
    # Create directory if it doesn't exist
    try:
        os.makedirs(os.path.dirname(program_files_config), exist_ok=True)
        return program_files_config
    except Exception:
        # Fallback to original location
        return os.path.join(os.path.dirname(__file__), "config.json")

CONFIG_FILE = get_config_file_path()

# Default configuration values
DEFAULT_CONFIG = {
    "serial_port": "",
    "baudrate": 19200,
    "length_tolerance": 3.0,
    "decimal_points": 1,  # Maps to "#.#" format
    "rounding": "UP",
    "api_url": "http://192.168.68.111:8001/api/method/frappe.utils.custom_api.get_product_detail",  # API URL for product data
    "supabase_url": "",  # Supabase project URL
    "supabase_key": "",  # Supabase API key
    "enable_supabase": False,  # Enable/disable Supabase integration
    "batch_name_format": "YYYY-MM-DD_product-code_color-code",  # Custom batch name format
    "batch_start_number": "1"  # Starting number for batch counter
}

def load_config() -> Dict[str, Any]:
    """Load konfigurasi dari file dengan multiple location support."""
    config = DEFAULT_CONFIG.copy()
    
    # Try multiple locations for config file
    config_locations = [
        CONFIG_FILE,  # Original location
        os.path.join(tempfile.gettempdir(), "rollmachine_config.json"),  # Temp directory
        os.path.join(os.path.expanduser("~"), "rollmachine_config.json")  # Home directory
    ]
    
    for config_file in config_locations:
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    saved_config = json.load(f)
                    # Update with saved values, keeping defaults for missing keys
                    config.update(saved_config)
                print(f"Config loaded from: {config_file}")
                return config
            except Exception as e:
                print(f"Error loading config from {config_file}: {e}")
                continue
    
    print("No valid config file found, using defaults")
    return config

def save_config(config: Dict[str, Any]) -> None:
    """Simpan konfigurasi ke file dengan improved error handling."""
    try:
        # Pastikan hanya data yang bisa di-serialize ke JSON yang disimpan
        serializable_config = {
            k: v for k, v in config.items()
            if isinstance(v, (str, int, float, bool, list, dict))
        }
        
        # Try to save to original location first
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(serializable_config, f, indent=4)
            print(f"Config saved successfully to: {CONFIG_FILE}")
            return
        except PermissionError as e:
            print(f"Permission denied saving to {CONFIG_FILE}: {e}")
            # Try alternative locations
            import tempfile
            import os
            
            # Try temp directory
            temp_dir = tempfile.gettempdir()
            temp_config_file = os.path.join(temp_dir, "rollmachine_config.json")
            try:
                with open(temp_config_file, "w") as f:
                    json.dump(serializable_config, f, indent=4)
                print(f"Config saved to temp location: {temp_config_file}")
                return
            except Exception as temp_e:
                print(f"Failed to save to temp location: {temp_e}")
                
            # Try user home directory
            try:
                home_dir = os.path.expanduser("~")
                home_config_file = os.path.join(home_dir, "rollmachine_config.json")
                with open(home_config_file, "w") as f:
                    json.dump(serializable_config, f, indent=4)
                print(f"Config saved to home directory: {home_config_file}")
                return
            except Exception as home_e:
                print(f"Failed to save to home directory: {home_e}")
                
        except Exception as e:
            print(f"Error saving config: {e}")
            
    except Exception as e:
        print(f"Critical error saving config: {e}") 

def get_default_config() -> Dict[str, Any]:
    """Get default configuration values."""
    return DEFAULT_CONFIG.copy() 

def calculate_print_length(target_length: float, tolerance_percent: float, decimal_points: int = 1, rounding: str = "UP") -> float:
    """
    Calculate print length using the correct tolerance formula.
    
    Formula: P_roll = P_target / (1 - T/100)
    Where:
    - P_target = target length (e.g., 100 meter)
    - T = tolerance percentage (e.g., 5%)
    - P_roll = print length for customer
    
    Example:
    - P_target = 100m, T = 5%
    - P_roll = 100 / (1 - 5/100) = 100 / 0.95 ≈ 105.26 meter
    
    Args:
        target_length: Target length in meters/yards
        tolerance_percent: Tolerance percentage (e.g., 5.0 for 5%)
        decimal_points: Number of decimal points (0, 1, or 2)
        rounding: Rounding method ("UP" or "DOWN")
    
    Returns:
        Print length with tolerance applied and rounded
    """
    if tolerance_percent <= 0:
        return target_length
    
    # Apply tolerance formula: P_roll = P_target / (1 - T/100)
    print_length = target_length / (1 - tolerance_percent / 100)
    
    # Apply rounding method
    if rounding == "UP":
        # Ceiling function
        if decimal_points == 0:
            print_length = math.ceil(print_length)
        elif decimal_points == 1:
            print_length = math.ceil(print_length * 10) / 10
        elif decimal_points == 2:
            print_length = math.ceil(print_length * 100) / 100
    else:  # DOWN
        # Floor function
        if decimal_points == 0:
            print_length = math.floor(print_length)
        elif decimal_points == 1:
            print_length = math.floor(print_length * 10) / 10
        elif decimal_points == 2:
            print_length = math.floor(print_length * 100) / 100
    
    return print_length

def get_print_length_info(target_length: float, tolerance_percent: float, decimal_points: int = 1, rounding: str = "UP") -> Dict[str, Any]:
    """
    Get detailed print length information including calculation details.
    
    Args:
        target_length: Target length in meters/yards
        tolerance_percent: Tolerance percentage
        decimal_points: Number of decimal points
        rounding: Rounding method
    
    Returns:
        Dictionary with print length details
    """
    print_length = calculate_print_length(target_length, tolerance_percent, decimal_points, rounding)
    
    return {
        "target_length": target_length,
        "tolerance_percent": tolerance_percent,
        "decimal_points": decimal_points,
        "rounding": rounding,
        "print_length": print_length,
        "formula": f"P_roll = {target_length} / (1 - {tolerance_percent}/100) = {target_length} / {1 - tolerance_percent/100:.3f}",
        "calculation": f"{target_length} / {1 - tolerance_percent/100:.3f} = {target_length / (1 - tolerance_percent/100):.6f}",
        "rounded": f"{print_length:.{decimal_points}f}"
    } 