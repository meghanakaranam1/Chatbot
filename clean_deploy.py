#!/usr/bin/env python3
"""
Clean deployment script - stops existing processes and starts fresh
"""

import os
import subprocess
import time
from deploy import AloVedaDeployer

def kill_processes_on_ports(ports):
    """Kill any processes running on specified ports"""
    killed = []
    
    for port in ports:
        try:
            # Use lsof to find processes using the port
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        print(f"🔄 Killing process PID {pid} on port {port}")
                        subprocess.run(['kill', '-9', pid], check=False)
                        killed.append(port)
        except Exception as e:
            print(f"⚠️  Could not check port {port}: {e}")
    
    if killed:
        print(f"✅ Cleaned up processes on ports: {killed}")
        time.sleep(2)  # Wait for processes to fully terminate
    else:
        print("✅ No existing processes found on target ports")

def clean_database():
    """Remove existing database to start fresh"""
    db_files = ["alo_veda.db", "database.db", "chatbot.db"]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"🗑️  Removed existing database: {db_file}")
    
    print("✅ Database cleanup completed")

def main():
    print("🧹 Alo-Veda Clean Deployment")
    print("=" * 40)
    
    # Clean up existing processes
    print("1️⃣ Stopping existing processes...")
    kill_processes_on_ports([8000, 8501, 8502, 8503])
    
    # Optional: Clean database (uncomment if you want fresh data)
    # print("2️⃣ Cleaning database...")
    # clean_database()
    
    print("3️⃣ Starting fresh deployment...")
    print()
    
    # Start deployment
    deployer = AloVedaDeployer()
    success = deployer.deploy_full_stack()
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 