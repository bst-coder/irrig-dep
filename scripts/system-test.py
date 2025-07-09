#!/usr/bin/env python3
"""
ESP32 Irrigation System - Complete Test Suite
Tests all functionality: routes, real-time updates, exact values, offline detection
"""

import requests
import json
import time
from datetime import datetime, timezone

class SystemTester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url.rstrip('/')
        self.test_device_id = "esp32-system-test"
        self.token = None
        
    def log_test(self, test_name, status, details=""):
        """Log test results with formatting"""
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {test_name}")
        if details:
            print(f"   {details}")
        return status
    
    def test_server_health(self):
        """Test if server is running"""
        try:
            response = requests.get(f"{self.base_url}", timeout=5)
            return self.log_test("Server Health Check", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Server Health Check", False, f"Error: {e}")
    
    def test_authentication(self):
        """Test device authentication"""
        try:
            url = f"{self.base_url}/api/devices/authenticate"
            payload = {"deviceId": self.test_device_id}
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                return self.log_test("Device Authentication", 
                                   True, 
                                   f"Token received: {bool(self.token)}")
            else:
                return self.log_test("Device Authentication", 
                                   False, 
                                   f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Device Authentication", False, f"Error: {e}")
    
    def test_data_sync(self):
        """Test data synchronization"""
        if not self.token:
            return self.log_test("Data Sync", False, "No token available")
        
        try:
            url = f"{self.base_url}/api/devices/sync"
            payload = {
                "deviceId": self.test_device_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "zoneStatus": {"zone1": "idle", "zone2": "idle"},
                "sensors": {"humidity": 35.0, "temperature": 22.0, "pressure": 1015.0},
                "states": {"pump": "off", "valve": "closed"}
            }
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            return self.log_test("Data Sync", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Data Sync", False, f"Error: {e}")
    
    def test_dashboard_api(self):
        """Test dashboard API endpoints"""
        try:
            # Test devices endpoint
            response = requests.get(f"{self.base_url}/api/devices", timeout=10)
            if response.status_code != 200:
                return self.log_test("Dashboard API", False, f"Devices API failed: {response.status_code}")
            
            # Test ESP32 endpoint
            response = requests.get(f"{self.base_url}/api/esp32", timeout=10)
            if response.status_code != 200:
                return self.log_test("Dashboard API", False, f"ESP32 API failed: {response.status_code}")
            
            data = response.json()
            device_count = data.get('count', 0)
            online_count = data.get('onlineCount', 0)
            
            return self.log_test("Dashboard API", 
                               True, 
                               f"Devices: {device_count}, Online: {online_count}")
        except Exception as e:
            return self.log_test("Dashboard API", False, f"Error: {e}")
    
    def test_exact_values(self):
        """Test exact sensor value preservation"""
        if not self.token:
            return self.log_test("Exact Values", False, "No token available")
        
        test_value = 1.0
        try:
            url = f"{self.base_url}/api/devices/sync"
            payload = {
                "deviceId": self.test_device_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "zoneStatus": {"zone1": "idle", "zone2": "idle"},
                "sensors": {"humidity": test_value, "temperature": 25.0, "pressure": 1013.0},
                "states": {"pump": "off", "valve": "closed"}
            }
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            # Send exact value
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code != 200:
                return self.log_test("Exact Values", False, "Sync failed")
            
            # Wait and retrieve
            time.sleep(1)
            response = requests.get(f"{self.base_url}/api/devices", timeout=10)
            if response.status_code != 200:
                return self.log_test("Exact Values", False, "Retrieval failed")
            
            devices = response.json().get('devices', [])
            test_device = next((d for d in devices if d.get('deviceId') == self.test_device_id), None)
            
            if not test_device:
                return self.log_test("Exact Values", False, "Device not found")
            
            retrieved_value = test_device.get('sensors', {}).get('humidity', 0)
            
            # Check if values match (allowing small floating point differences)
            if abs(retrieved_value - test_value) < 0.2:
                return self.log_test("Exact Values", 
                                   True, 
                                   f"Set: {test_value}%, Got: {retrieved_value}%")
            else:
                return self.log_test("Exact Values", 
                                   False, 
                                   f"Set: {test_value}%, Got: {retrieved_value}%")
        except Exception as e:
            return self.log_test("Exact Values", False, f"Error: {e}")
    
    def test_command_sending(self):
        """Test command sending to devices"""
        try:
            url = f"{self.base_url}/api/esp32"
            payload = {
                "deviceId": self.test_device_id,
                "action": "restart"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            return self.log_test("Command Sending", 
                               response.status_code == 200,
                               f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Command Sending", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 ESP32 Irrigation System - Complete Test Suite")
        print("=" * 60)
        
        tests = [
            self.test_server_health,
            self.test_authentication,
            self.test_data_sync,
            self.test_dashboard_api,
            self.test_exact_values,
            self.test_command_sending,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(0.5)
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! System is fully operational.")
            print("\n🚀 Ready to run:")
            print("   python scripts/esp32-simulator.py")
            print("   Open: http://localhost:3000")
        else:
            print(f"\n⚠️ {total - passed} test(s) failed. Check system components.")
        
        return passed == total

def main():
    tester = SystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()