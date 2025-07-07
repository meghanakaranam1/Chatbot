#!/usr/bin/env python3
"""
Deployment script for Alo-Veda Chatbot
Supports different deployment modes and platforms
"""

import os
import sys
import subprocess
import time
import signal
import argparse
from pathlib import Path
from deployment_config import config

class AloVedaDeployer:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        
    def setup_database(self):
        """Initialize database for production"""
        print("🔧 Setting up database...")
        try:
            from database.database import init_database
            from database.seed_data import create_sample_data
            
            # Always initialize the database structure
            init_database()
            
            # Check if data already exists before creating sample data
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
    
    def start_backend(self):
        """Start the FastAPI backend"""
        print(f"🚀 Starting backend on {config.API_HOST}:{config.API_PORT}")
        
        cmd = [
            "uvicorn", 
            "backend.main:app",
            "--host", config.API_HOST,
            "--port", str(config.API_PORT),
            "--workers", "1"
        ]
        
        if config.ENVIRONMENT == "production":
            cmd.extend(["--access-log"])
        else:
            cmd.append("--reload")
            
        try:
            self.backend_process = subprocess.Popen(cmd)
            print("✅ Backend started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the Streamlit frontend"""
        print(f"🎨 Starting frontend on port {config.FRONTEND_PORT}")
        
        cmd = [
            "streamlit", "run", 
            "frontend/streamlit_app.py",
            "--server.port", str(config.FRONTEND_PORT),
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        try:
            self.frontend_process = subprocess.Popen(cmd)
            print("✅ Frontend started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def wait_for_backend(self, timeout=30):
        """Wait for backend to be ready"""
        import requests
        
        for i in range(timeout):
            try:
                response = requests.get(f"http://localhost:{config.API_PORT}/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Backend is ready")
                    return True
            except:
                pass
            time.sleep(1)
            print(f"⏳ Waiting for backend... ({i+1}/{timeout})")
        
        print("❌ Backend failed to start within timeout")
        return False
    
    def deploy_full_stack(self):
        """Deploy both backend and frontend"""
        print("🚀 Starting Alo-Veda Full Stack Deployment")
        print("=" * 50)
        
        # Setup database
        if not self.setup_database():
            return False
        
        # Start backend
        if not self.start_backend():
            return False
        
        # Wait for backend to be ready
        if not self.wait_for_backend():
            self.cleanup()
            return False
        
        # Start frontend
        if not self.start_frontend():
            self.cleanup()
            return False
        
        print("\n🎉 Alo-Veda is now running!")
        print(f"🔗 Backend API: http://localhost:{config.API_PORT}")
        print(f"🔗 Frontend UI: http://localhost:{config.FRONTEND_PORT}")
        print(f"📚 API Docs: http://localhost:{config.API_PORT}/docs")
        print("\nPress Ctrl+C to stop all services")
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Shutting down...")
            self.cleanup()
        
        return True
    
    def deploy_backend_only(self):
        """Deploy only the backend API"""
        print("🚀 Starting Alo-Veda Backend Only")
        print("=" * 40)
        
        if not self.setup_database():
            return False
        
        if not self.start_backend():
            return False
        
        print(f"\n✅ Backend is running on http://localhost:{config.API_PORT}")
        print(f"📚 API Documentation: http://localhost:{config.API_PORT}/docs")
        
        try:
            self.backend_process.wait()
        except KeyboardInterrupt:
            print("\n⏹️  Shutting down backend...")
            self.cleanup()
        
        return True
    
    def cleanup(self):
        """Clean up running processes"""
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()

def main():
    parser = argparse.ArgumentParser(description="Deploy Alo-Veda Chatbot")
    parser.add_argument(
        "--mode", 
        choices=["full", "backend", "frontend"], 
        default="full",
        help="Deployment mode (default: full)"
    )
    parser.add_argument(
        "--env", 
        choices=["development", "production"], 
        default="production",
        help="Environment (default: production)"
    )
    
    args = parser.parse_args()
    
    # Set environment
    os.environ["ENVIRONMENT"] = args.env
    
    deployer = AloVedaDeployer()
    
    if args.mode == "full":
        success = deployer.deploy_full_stack()
    elif args.mode == "backend":
        success = deployer.deploy_backend_only()
    else:
        print("Frontend-only deployment not implemented yet")
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 