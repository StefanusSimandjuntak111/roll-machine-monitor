"""
Main entry point for the monitoring application.
This file is used when running the monitoring package directly.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to Python path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

def main():
    """Main application entry point."""
    try:
        # Import the main window
        from monitoring.ui.main_window import main as app_main
        app_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please run the application using run_app.py instead.")
        sys.exit(1)
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 