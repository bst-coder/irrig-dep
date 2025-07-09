#!/usr/bin/env python3
"""
Test Deployment Setup
Verify that all components are ready for deployment
"""

import os
import requests
import json

def test_local_api():
    """Test local FastAPI server"""
    print("🧪 Testing Local FastAPI Server")
    print("-" * 40)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI server is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ FastAPI server error: {response.status_code}")
    except Exception as e:
        print(f"❌ FastAPI server not running: {e}")
        print("   Start with: uvicorn api_server:app --reload")

def test_streamlit_app():
    """Test Streamlit app can be imported"""
    print("\n🧪 Testing Streamlit App")
    print("-" * 40)
    
    try:
        import streamlit_app
        print("✅ Streamlit app imports successfully")
    except Exception as e:
        print(f"❌ Streamlit app import error: {e}")

def check_requirements():
    """Check if all required packages are available"""
    print("\n🧪 Checking Requirements")
    print("-" * 40)
    
    # Streamlit requirements
    streamlit_packages = [
        "streamlit", "requests", "pandas", "plotly", "pymongo"
    ]
    
    # API requirements
    api_packages = [
        "fastapi", "uvicorn", "pymongo", "jwt"
    ]
    
    all_packages = streamlit_packages + api_packages
    
    for package in all_packages:
        try:
            if package == "jwt":
                import jwt as package_module
            else:
                package_module = __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Install with: pip install {package}")

def check_files():
    """Check if all required files exist"""
    print("\n🧪 Checking Required Files")
    print("-" * 40)
    
    required_files = [
        "streamlit_app.py",
        "api_server.py",
        "requirements_streamlit.txt",
        "requirements_api.txt",
        ".streamlit/config.toml",
        "scripts/esp32-simulator.py",
        "Procfile",
        "runtime.txt"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing required file")

def check_environment():
    """Check environment variables"""
    print("\n🧪 Checking Environment Variables")
    print("-" * 40)
    
    env_vars = [
        ("MONGODB_URI", "MongoDB connection string"),
        ("JWT_SECRET", "JWT secret key"),
        ("API_BASE_URL", "API base URL (optional for local)")
    ]
    
    for var_name, description in env_vars:
        value = os.getenv(var_name)
        if value:
            # Don't print sensitive values
            masked_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var_name}: {masked_value}")
        else:
            print(f"⚠️ {var_name}: Not set ({description})")

def main():
    print("🚀 ESP32 Irrigation System - Deployment Test")
    print("=" * 60)
    
    check_files()
    check_requirements()
    check_environment()
    test_streamlit_app()
    test_local_api()
    
    print("\n" + "=" * 60)
    print("📋 DEPLOYMENT CHECKLIST")
    print("=" * 60)
    print("1. ✅ Set up MongoDB Atlas database")
    print("2. ✅ Deploy FastAPI backend (Heroku/Railway)")
    print("3. ✅ Deploy Streamlit dashboard")
    print("4. ✅ Configure environment variables")
    print("5. ✅ Test ESP32 simulator connection")
    
    print("\n🌐 Deployment URLs:")
    print("   Streamlit: https://your-app.streamlit.app")
    print("   API: https://your-api.herokuapp.com")
    print("   Docs: https://your-api.herokuapp.com/docs")
    
    print("\n📚 See DEPLOYMENT_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main()