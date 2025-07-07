#!/usr/bin/env python3
"""
Simple script to run the Roll Machine Monitor application.
This script handles the Python path correctly for Windows.
"""
import sys
import os

def main():
    """Run the monitoring application."""
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    print("Starting Roll Machine Monitor...")
    print(f"Working directory: {current_dir}")
    print(f"Python path: {sys.path[0]}")
    print()
    
    try:
        # Import and run the main application
        from monitoring.ui.main_window import main as app_main
        app_main()
    except ImportError as e:
        print(f"ERROR: Could not import monitoring module: {e}")
        print("Make sure you're running this script from the correct directory.")
        input("Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Application failed to start: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main() 