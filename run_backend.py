#!/usr/bin/env python3
"""
Script to run the FastAPI backend server
"""

import uvicorn
from config import FASTAPI_HOST, FASTAPI_PORT

def main():
    print("🚀 Starting FastAPI backend server...")
    print(f"📍 Running on http://{FASTAPI_HOST}:{FASTAPI_PORT}")
    print("📚 API docs available at http://localhost:8000/docs")
    print("🔧 Health check at http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(
        "backend.main:app",
        host=FASTAPI_HOST,
        port=FASTAPI_PORT,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 