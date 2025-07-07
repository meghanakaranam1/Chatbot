#!/usr/bin/env python3
"""
Test script to verify Alo-Veda deployment is working correctly
"""

import requests
import time
import sys
from deployment_config import config

def test_backend_health():
    """Test if backend is healthy"""
    try:
        response = requests.get(f"http://localhost:{config.API_PORT}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_api_endpoints():
    """Test key API endpoints"""
    base_url = f"http://localhost:{config.API_PORT}"
    
    tests = [
        ("/health", "Health endpoint"),
        ("/docs", "API documentation"),
        ("/chat/examples/", "Chat examples"),
    ]
    
    passed = 0
    for endpoint, description in tests:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {description}: OK")
                passed += 1
            else:
                print(f"❌ {description}: Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
    
    return passed == len(tests)

def test_chat_functionality():
    """Test the chat functionality"""
    try:
        response = requests.post(
            f"http://localhost:{config.API_PORT}/chat/",
            json={"message": "How many users do we have?"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "response" in data and "data" in data:
                print("✅ Chat functionality: Working")
                print(f"   Sample response: {data['response'][:100]}...")
                return True
            else:
                print("❌ Chat functionality: Invalid response format")
                return False
        else:
            print(f"❌ Chat functionality: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Chat functionality: Error - {e}")
        return False

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    try:
        response = requests.get(f"http://localhost:{config.FRONTEND_PORT}", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend accessibility: OK")
            return True
        else:
            print(f"❌ Frontend accessibility: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Frontend accessibility: Error - {e}")
        return False

def main():
    print("🧪 Testing Alo-Veda Deployment")
    print("=" * 40)
    print(f"Backend URL: http://localhost:{config.API_PORT}")
    print(f"Frontend URL: http://localhost:{config.FRONTEND_PORT}")
    print(f"Environment: {config.ENVIRONMENT}")
    print()
    
    # Wait a bit for services to start
    print("⏳ Waiting for services to initialize...")
    time.sleep(5)
    
    tests = [
        test_backend_health,
        test_api_endpoints,
        test_chat_functionality,
        test_frontend_accessibility
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        if test():
            passed_tests += 1
        print()
    
    print("📊 Test Results")
    print("=" * 20)
    print(f"Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Deployment is successful.")
        print("\n🔗 URLs:")
        print(f"   Frontend: http://localhost:{config.FRONTEND_PORT}")
        print(f"   Backend API: http://localhost:{config.API_PORT}")
        print(f"   API Docs: http://localhost:{config.API_PORT}/docs")
        return True
    else:
        print("❌ Some tests failed. Please check the deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 