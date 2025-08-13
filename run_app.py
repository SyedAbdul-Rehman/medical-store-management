#!/usr/bin/env python3
"""
Simple script to run the Medical Store Management Application
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run the medical store application"""
    app_path = Path(__file__).parent / "medical_store_app" / "main.py"
    
    if not app_path.exists():
        print(f"Error: Application file not found at {app_path}")
        return 1
    
    try:
        # Run the application
        result = subprocess.run([sys.executable, str(app_path)], check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running application: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0

if __name__ == "__main__":
    sys.exit(main())