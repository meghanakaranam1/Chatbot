#!/usr/bin/env python3
"""
Script to run the Streamlit frontend
"""

import subprocess
import sys
import time
import requests
from config import STREAMLIT_PORT

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🎨 Starting Streamlit frontend...")
    
    # Check if backend is running
    if not check_backend():
        print("⚠️  Warning: Backend API is not running!")
        print("📌 Start the backend first with: python run_backend.py")
        print("⏱️  Continuing in 3 seconds...\n")
        time.sleep(3)
    else:
        print("✅ Backend API is running")
    
    print(f"📍 Frontend will be available at http://localhost:{STREAMLIT_PORT}")
    print("🔧 Make sure your backend is running on http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")
    
    # Run Streamlit
    cmd = [
        sys.executable, 
        "-m", 
        "streamlit", 
        "run", 
        "frontend/streamlit_app.py",
        "--server.port", 
        str(STREAMLIT_PORT),
        "--server.address",
        "localhost"
    ]
    
    subprocess.run(cmd)

if __name__ == "__main__":
    main() 