#!/usr/bin/env python3
"""
Connect to Deployed ESP32 Irrigation System
This script connects your local ESP32 simulator to the deployed Streamlit dashboard
"""

import requests
import json
import time
import os
from datetime import datetime, timezone

class DeploymentConnector:
    def __init__(self, streamlit_url=None, api_url=None):
        # Default URLs - update these with your actual deployment URLs
        self.streamlit_url = streamlit_url or "https://irrig-dep.streamlit.app"
        self.api_url = api_url or "https://your-api.herokuapp.com"  # Update this when you deploy the API
        
    def test_streamlit_dashboard(self):
        """Test connection to Streamlit dashboard"""
        print("🌐 Testing Streamlit Dashboard Connection")
        print("-" * 50)
        
        try:
            response = requests.get(self.streamlit_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Streamlit dashboard is accessible")
                print(f"🔗 URL: {self.streamlit_url}")
                return True
            else:
                print(f"❌ Dashboard returned status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Dashboard connection failed: {e}")
            return False
    
    def test_api_backend(self):
        """Test connection to API backend"""
        print("\n🔧 Testing API Backend Connection")
        print("-" * 50)
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ API backend is accessible")
                print(f"🔗 URL: {self.api_url}")
                return True
            else:
                print(f"❌ API returned status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            print(f"💡 This is expected if you haven't deployed the API backend yet")
            return False
    
    def simulate_esp32_connection(self):
        """Simulate ESP32 connecting to deployed system"""
        print("\n🤖 Simulating ESP32 Connection")
        print("-" * 50)
        
        if not self.test_api_backend():
            print("⚠️ Cannot simulate ESP32 without API backend")
            print("📋 To deploy the API backend:")
            print("   1. Deploy api_server.py on Heroku/Railway")
            print("   2. Update the API_URL in this script")
            print("   3. Run this script again")
            return False
        
        # Try to authenticate
        try:
            auth_payload = {"deviceId": "esp32-remote"}
            response = requests.post(
                f"{self.api_url}/api/devices/authenticate",
                json=auth_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                print(f"✅ ESP32 authentication successful")
                print(f"🔑 Token received: {token[:20]}...")
                
                # Try to send sensor data
                self.send_test_data(token)
                return True
            else:
                print(f"❌ ESP32 authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ESP32 simulation failed: {e}")
            return False
    
    def send_test_data(self, token):
        """Send test sensor data"""
        try:
            sync_payload = {
                "deviceId": "esp32-remote",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "zoneStatus": {"zone1": "idle", "zone2": "idle"},
                "sensors": {"humidity": 30.0, "temperature": 25.0, "pressure": 1013.0},
                "states": {"pump": "off", "valve": "closed"}
            }
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.api_url}/api/devices/sync",
                json=sync_payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Test sensor data sent successfully")
                print(f"📊 Data: Humidity 30%, Temperature 25°C, Pressure 1013 hPa")
            else:
                print(f"❌ Data sync failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Data sending failed: {e}")
    
    def run_esp32_simulator_with_deployment(self):
        """Run ESP32 simulator connected to deployment"""
        print("\n🚀 Starting ESP32 Simulator (Connected to Deployment)")
        print("-" * 50)
        
        if not self.test_api_backend():
            print("❌ Cannot start simulator without API backend")
            return
        
        # Set environment variable for the simulator
        os.environ["API_BASE_URL"] = self.api_url
        
        print(f"🔗 Simulator will connect to: {self.api_url}")
        print(f"📱 Dashboard available at: {self.streamlit_url}")
        print("\n💡 Run this command to start the simulator:")
        print(f"   export API_BASE_URL={self.api_url}")
        print(f"   python scripts/esp32-simulator.py")
        
    def show_deployment_status(self):
        """Show overall deployment status"""
        print("\n📊 Deployment Status Summary")
        print("=" * 60)
        
        streamlit_ok = self.test_streamlit_dashboard()
        api_ok = self.test_api_backend()
        
        print(f"\n📱 Streamlit Dashboard: {'✅ Working' if streamlit_ok else '❌ Not accessible'}")
        print(f"🔧 API Backend: {'✅ Working' if api_ok else '❌ Not deployed'}")
        
        if streamlit_ok and api_ok:
            print(f"\n🎉 Full system is operational!")
            print(f"��� Dashboard: {self.streamlit_url}")
            print(f"🔧 API: {self.api_url}")
        elif streamlit_ok and not api_ok:
            print(f"\n⚠️ Dashboard is working in demo mode")
            print(f"📋 Next step: Deploy the API backend")
        else:
            print(f"\n❌ System not fully deployed")

def main():
    print("🌱 ESP32 Irrigation System - Deployment Connector")
    print("=" * 60)
    
    # Update these URLs with your actual deployment URLs
    STREAMLIT_URL = "https://irrig-dep.streamlit.app"  # Your actual Streamlit URL
    API_URL = "https://your-api.herokuapp.com"  # Update this when you deploy the API
    
    connector = DeploymentConnector(STREAMLIT_URL, API_URL)
    
    # Show deployment status
    connector.show_deployment_status()
    
    # Test ESP32 simulation if API is available
    connector.simulate_esp32_connection()
    
    # Show how to run simulator with deployment
    connector.run_esp32_simulator_with_deployment()
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS:")
    print("1. ✅ Streamlit dashboard is deployed")
    print("2. 🔄 Deploy API backend (api_server.py) on Heroku/Railway")
    print("3. 🔧 Update API_URL in this script")
    print("4. 🤖 Run ESP32 simulator with: export API_BASE_URL=your_api_url")
    print("5. 🌐 Monitor real-time data on your Streamlit dashboard")

if __name__ == "__main__":
    main()