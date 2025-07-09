#!/usr/bin/env python3
"""
Test Streamlit App
Quick test to verify the Streamlit app can run
"""

def test_imports():
    """Test that all required imports work"""
    print("🧪 Testing Streamlit App Imports")
    print("-" * 40)
    
    try:
        import streamlit as st
        print("✅ streamlit")
    except ImportError as e:
        print(f"❌ streamlit: {e}")
        return False
    
    try:
        import requests
        print("✅ requests")
    except ImportError as e:
        print(f"❌ requests: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas")
    except ImportError as e:
        print(f"❌ pandas: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ plotly")
    except ImportError as e:
        print(f"⚠️ plotly: {e} (will use fallback charts)")
    
    try:
        import pymongo
        print("✅ pymongo")
    except ImportError as e:
        print(f"⚠️ pymongo: {e} (not needed for Streamlit app)")
    
    return True

def test_app_structure():
    """Test that the app structure is correct"""
    print("\n🧪 Testing App Structure")
    print("-" * 40)
    
    try:
        # Try to import the main app components
        import streamlit_app
        print("✅ streamlit_app.py imports successfully")
        
        # Check if main classes exist
        if hasattr(streamlit_app, 'ESP32Dashboard'):
            print("✅ ESP32Dashboard class found")
        else:
            print("❌ ESP32Dashboard class not found")
            return False
        
        if hasattr(streamlit_app, 'main'):
            print("✅ main function found")
        else:
            print("❌ main function not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ App structure error: {e}")
        return False

def main():
    print("🚀 Streamlit App Test")
    print("=" * 50)
    
    if not test_imports():
        print("\n❌ Import test failed")
        return
    
    if not test_app_structure():
        print("\n❌ App structure test failed")
        return
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Streamlit app is ready for deployment")
    print("\n🚀 To run locally:")
    print("   streamlit run streamlit_app.py")
    print("\n☁️ To deploy on Streamlit Cloud:")
    print("   Repository: https://github.com/yourusername/your-repo")
    print("   Branch: main")
    print("   Main file path: streamlit_app.py")

if __name__ == "__main__":
    main()