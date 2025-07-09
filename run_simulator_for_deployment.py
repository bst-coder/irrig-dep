#!/usr/bin/env python3
"""
Run ESP32 Simulator for Streamlit Deployment
This script runs the ESP32 simulator configured to work with your deployed dashboard
"""

import os
import sys
import subprocess

def main():
    print("🚀 ESP32 Simulator for Streamlit Deployment")
    print("=" * 50)
    
    # Your Streamlit deployment URL
    streamlit_url = "https://irrig-dep.streamlit.app"
    
    # API URL (update this when you deploy the backend)
    api_url = "https://your-api.herokuapp.com"  # Update this!
    
    print(f"🌐 Dashboard URL: {streamlit_url}")
    print(f"🔧 API URL: {api_url}")
    
    # Check if API URL has been updated
    if "your-api" in api_url:
        print("\n⚠️ WARNING: API URL not configured!")
        print("📋 To use with real backend:")
        print("1. Deploy api_server.py on Heroku/Railway")
        print("2. Update the api_url variable in this script")
        print("3. Run this script again")
        print("\n💡 For now, the simulator will run in demo mode")
        api_url = "http://localhost:8000"  # Fallback to demo
    
    # Set environment variable for the simulator
    os.environ["API_BASE_URL"] = api_url
    
    print(f"\n🤖 Starting ESP32 simulator...")
    print(f"🔗 Connecting to: {api_url}")
    print(f"📱 Monitor at: {streamlit_url}")
    print("\n" + "=" * 50)
    
    try:
        # Run the ESP32 simulator
        subprocess.run([sys.executable, "scripts/esp32-simulator.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Simulator stopped by user")
    except FileNotFoundError:
        print("❌ ESP32 simulator not found!")
        print("💡 Make sure you're in the project directory")
        print("📁 Expected file: scripts/esp32-simulator.py")
    except Exception as e:
        print(f"❌ Error running simulator: {e}")

if __name__ == "__main__":
    main()