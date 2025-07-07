#!/usr/bin/env python3
"""
Production start script for Render deployment
Runs Streamlit on main port (10000) and API on internal port (8000)
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def setup_database():
    """Initialize database for production"""
    print("🔧 Setting up database...")
    try:
        from database.database import init_database
        from database.seed_data import create_sample_data
        
        init_database()
        
        try:
            create_sample_data()
            print("✅ Sample data created successfully")
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                print("✅ Database already has sample data, skipping creation")
            else:
                print(f"⚠️  Sample data creation warning: {e}")
        
        print("✅ Database setup completed")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False
    return True

def start_backend():
    """Start backend API on internal port 8000"""
    print("🚀 Starting backend API on internal port 8000...")
    
    def run_backend():
        cmd = [
            "uvicorn", 
            "backend.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--workers", "1"
        ]
        subprocess.run(cmd)
    
    # Start backend in background thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait for backend to be ready
    print("⏳ Waiting for backend to start...")
    time.sleep(5)
    print("✅ Backend started")

def start_frontend():
    """Start Streamlit frontend on main port 10000"""
    print("🎨 Starting Streamlit frontend on port 10000...")
    
    # Set environment variables for the frontend
    os.environ["BACKEND_URL"] = "http://localhost:8000"
    
    cmd = [
        "streamlit", "run", 
        "frontend/streamlit_app.py",
        "--server.port", "10000",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    subprocess.run(cmd)

def main():
    print("🚀 Starting Alo-Veda for Production (Render)")
    print("=" * 50)
    
    # Setup database
    if not setup_database():
        sys.exit(1)
    
    # Start backend in background
    start_backend()
    
    # Start frontend on main port (this will keep running)
    start_frontend()

if __name__ == "__main__":
    main() 