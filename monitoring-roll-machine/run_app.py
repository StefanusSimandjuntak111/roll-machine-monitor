#!/usr/bin/env python3
"""
Main entry point for Monitoring Roll Machine application.
This file serves as the primary entry point for both development and PyInstaller builds.
"""

import sys
import os
from pathlib import Path

# Add the monitoring directory to Python path
current_dir = Path(__file__).parent
monitoring_dir = current_dir / "monitoring"
sys.path.insert(0, str(monitoring_dir))

def main():
    """Main application entry point."""
    try:
        # Import the main window after setting up the path
        from monitoring.ui.main_window import main as app_main
        app_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Trying alternative import...")
        try:
            # Alternative import path
            sys.path.insert(0, str(current_dir))
            from monitoring.ui.main_window import main as app_main
            app_main()
        except ImportError as e2:
            print(f"Alternative import also failed: {e2}")
            print("Please check that all required modules are available.")
            sys.exit(1)
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 