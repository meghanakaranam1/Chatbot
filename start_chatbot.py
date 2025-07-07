#!/usr/bin/env python3
"""
Script to start both backend and frontend services
"""

import subprocess
import sys
import time
import threading
import signal
import os
from config import FASTAPI_HOST, FASTAPI_PORT, STREAMLIT_PORT

def run_backend():
    """Run the FastAPI backend"""
    cmd = [sys.executable, "run_backend.py"]
    return subprocess.Popen(cmd)

def run_frontend():
    """Run the Streamlit frontend"""
    cmd = [sys.executable, "run_frontend.py"]
    return subprocess.Popen(cmd)

def main():
    print("🤖 Starting AI Database Chatbot...")
    print("=" * 50)
    
    # Start backend
    print("🚀 Starting backend server...")
    backend_process = run_backend()
    
    # Wait a bit for backend to start
    print("⏱️  Waiting for backend to initialize...")
    time.sleep(5)
    
    # Start frontend
    print("🎨 Starting frontend...")
    frontend_process = run_frontend()
    
    print("\n" + "=" * 50)
    print("✅ Chatbot started successfully!")
    print(f"🔗 Backend API: http://{FASTAPI_HOST}:{FASTAPI_PORT}")
    print(f"🔗 Frontend UI: http://localhost:{STREAMLIT_PORT}")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services")
    print("=" * 50)
    
    def signal_handler(signum, frame):
        print("\n🛑 Shutting down services...")
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for processes to terminate
        backend_process.wait()
        frontend_process.wait()
        
        print("✅ All services stopped")
        sys.exit(0)
    
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Wait for processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main() 