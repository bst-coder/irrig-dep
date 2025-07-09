#!/usr/bin/env python3
"""
ESP32 Smart Irrigation Simulator
Real-time simulator with auto-sync, exact sensor values, and complete device control
"""

import requests
import json
import time
import random
import threading
import os
from datetime import datetime, timezone
from typing import Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ESP32Simulator:
    def __init__(self, device_id: str = "esp32-main", server_url: str = None):
        self.device_id = device_id
        # Default to local development, but can be overridden for production
        if server_url is None:
            server_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.server_url = server_url.rstrip('/')
        self.jwt_token = None
        self.is_online = True
        
        # Device state
        self.zone_status = {"zone1": "idle", "zone2": "idle"}
        self.pump_state = "off"
        self.valve_state = "closed"
        
        # Sensor simulation
        self.base_humidity = 45.0
        self.base_temperature = 25.0
        self.base_pressure = 1013.25
        
        # Data buffering for offline mode
        self.buffered_data = []
        self.last_sync = None
        
        # Configuration from server
        self.zones = ["zone1", "zone2"]
        self.sensors = ["humidity", "temperature", "pressure"]
        
        # Auto sync settings
        self.auto_sync = True
        self.auto_sync_interval = 5  # seconds
        self.sync_thread = None
        self.stop_auto_sync = False
        
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with JWT authentication"""
        if not self.jwt_token:
            return {'Content-Type': 'application/json'}
        return {
            'Authorization': f'Bearer {self.jwt_token}',
            'Content-Type': 'application/json'
        }
    
    def simulate_sensor_readings(self) -> Dict[str, float]:
        """Simulate sensor readings with minimal variation to preserve exact values"""
        # Very small random variation to preserve manual settings
        humidity = self.base_humidity + random.uniform(-0.05, 0.05)
        temperature = self.base_temperature + random.uniform(-0.05, 0.05)
        pressure = self.base_pressure + random.uniform(-0.1, 0.1)
        
        # Simulate irrigation effects
        if self.pump_state == "on":
            humidity += random.uniform(0.1, 0.3)
        
        return {
            "humidity": round(max(0, humidity), 1),
            "temperature": round(temperature, 1),
            "pressure": round(pressure, 1)
        }
    
    def create_data_payload(self) -> Dict:
        """Create data payload to send to server"""
        return {
            "deviceId": self.device_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "zoneStatus": self.zone_status.copy(),
            "sensors": self.simulate_sensor_readings(),
            "states": {
                "pump": self.pump_state,
                "valve": self.valve_state
            }
        }
    
    def authenticate(self) -> bool:
        """Authenticate with server"""
        try:
            url = f"{self.server_url}/api/devices/authenticate"
            payload = {"deviceId": self.device_id}
            
            print(f"🔐 Authenticating device {self.device_id}...")
            response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Authentication successful")
                
                if 'token' in data:
                    self.jwt_token = data['token']
                    print(f"🔑 JWT token received")
                
                if 'config' in data:
                    config = data['config']
                    self.zones = config.get('zones', self.zones)
                    self.sensors = config.get('sensors', self.sensors)
                    print(f"📋 Configuration: zones={self.zones}")
                
                if 'commands' in data:
                    print(f"📨 Initial commands: {data['commands']}")
                    self.process_commands(data['commands'])
                
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Authentication error: {e}")
            self.is_online = False
            return False
    
    def sync_with_server(self, silent: bool = False) -> bool:
        """Sync with server"""
        if not self.is_online:
            if not silent:
                print(f"❌ Device OFFLINE - buffering data")
            self.buffer_current_data()
            return False
        
        try:
            url = f"{self.server_url}/api/devices/sync"
            payload = self.create_data_payload()
            
            if self.buffered_data:
                payload['bufferedData'] = self.buffered_data.copy()
                if not silent:
                    print(f"📦 Sending {len(self.buffered_data)} buffered records")
            
            if not silent:
                sensors = payload['sensors']
                print(f"🔄 Syncing: H:{sensors['humidity']}% T:{sensors['temperature']}°C P:{sensors['pressure']}hPa")
            
            response = requests.post(url, json=payload, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if not silent:
                    print(f"✅ Sync successful")
                
                if self.buffered_data:
                    self.buffered_data.clear()
                    if not silent:
                        print("🗑️ Buffered data cleared")
                
                if 'commands' in data:
                    if not silent:
                        print(f"📨 Server commands: {data['commands']}")
                    self.process_commands(data['commands'])
                
                self.last_sync = datetime.now(timezone.utc)
                self.is_online = True
                return True
            else:
                if not silent:
                    print(f"❌ Sync failed: {response.status_code}")
                self.is_online = False
                self.buffer_current_data()
                return False
                
        except requests.exceptions.RequestException as e:
            if not silent:
                print(f"❌ Sync error: {e}")
            self.is_online = False
            self.buffer_current_data()
            return False
    
    def auto_sync_worker(self):
        """Background auto-sync worker"""
        while not self.stop_auto_sync:
            if self.is_online and self.jwt_token:
                success = self.sync_with_server(silent=True)
                if success:
                    current_time = datetime.now().strftime("%H:%M:%S")
                    print(f"🔄 [{current_time}] Auto-sync ✓", end="\r")
            time.sleep(self.auto_sync_interval)
    
    def start_auto_sync(self):
        """Start automatic syncing"""
        if not self.sync_thread:
            self.stop_auto_sync = False
            self.sync_thread = threading.Thread(target=self.auto_sync_worker, daemon=True)
            self.sync_thread.start()
            print(f"🚀 Auto-sync started (every {self.auto_sync_interval}s)")
    
    def stop_auto_sync_worker(self):
        """Stop automatic syncing"""
        if self.sync_thread:
            self.stop_auto_sync = True
            self.sync_thread = None
            print(f"🛑 Auto-sync stopped")
    
    def process_commands(self, commands: Dict):
        """Process commands from server"""
        for zone, action in commands.items():
            if zone in self.zones:
                if action == "start":
                    self.zone_status[zone] = "irrigating"
                    self.pump_state = "on"
                    self.valve_state = "open"
                    print(f"💧 Started irrigation: {zone}")
                elif action == "stop":
                    self.zone_status[zone] = "idle"
                    if all(status == "idle" for status in self.zone_status.values()):
                        self.pump_state = "off"
                        self.valve_state = "closed"
                    print(f"🛑 Stopped irrigation: {zone}")
    
    def buffer_current_data(self):
        """Buffer data when offline"""
        data = self.create_data_payload()
        self.buffered_data.append(data)
        if len(self.buffered_data) > 100:
            self.buffered_data.pop(0)
    
    def set_sensor_value(self, sensor: str, value: float):
        """Set exact sensor value"""
        if sensor == "humidity":
            self.base_humidity = value
            print(f"🌡️ Humidity set to {value}%")
        elif sensor == "temperature":
            self.base_temperature = value
            print(f"🌡️ Temperature set to {value}°C")
        elif sensor == "pressure":
            self.base_pressure = value
            print(f"🌡️ Pressure set to {value} hPa")
        else:
            print(f"❌ Unknown sensor: {sensor}")
            return
        
        # Immediate sync for sensor changes
        self.sync_with_server()
    
    def control_pump(self, action: str):
        """Control pump"""
        if action == "on":
            self.pump_state = "on"
            print(f"💧 Pump ON")
        elif action == "off":
            self.pump_state = "off"
            print(f"🛑 Pump OFF")
        else:
            print(f"❌ Invalid pump action: {action}")
            return
        self.sync_with_server()
    
    def control_valve(self, action: str):
        """Control valve"""
        if action == "open":
            self.valve_state = "open"
            print(f"🚰 Valve OPEN")
        elif action == "close":
            self.valve_state = "closed"
            print(f"🔒 Valve CLOSED")
        else:
            print(f"❌ Invalid valve action: {action}")
            return
        self.sync_with_server()
    
    def control_zone(self, zone: str, action: str):
        """Control irrigation zone"""
        if zone not in self.zones:
            print(f"❌ Invalid zone: {zone}")
            return
        if action not in ["start", "stop"]:
            print(f"❌ Invalid action: {action}")
            return
        
        self.process_commands({zone: action})
        self.sync_with_server()
    
    def go_offline(self):
        """Simulate going offline"""
        self.is_online = False
        print("📴 Device OFFLINE")
        print("💡 Dashboard will show offline within 10 seconds")
    
    def go_online(self):
        """Simulate going online"""
        self.is_online = True
        print("📶 Device ONLINE")
        self.sync_with_server()
    
    def show_status(self):
        """Show current status"""
        print(f"\n📊 DEVICE STATUS")
        print(f"🆔 ID: {self.device_id}")
        print(f"🌐 Online: {'✅' if self.is_online else '❌'}")
        print(f"🔄 Auto-sync: {'✅' if self.auto_sync and self.sync_thread else '❌'}")
        print(f"🏗️ Zones: {self.zone_status}")
        print(f"💧 Pump: {self.pump_state}")
        print(f"🚰 Valve: {self.valve_state}")
        print(f"📊 Sensors: {self.simulate_sensor_readings()}")
        print(f"💾 Buffer: {len(self.buffered_data)} records")
        print(f"🕐 Last sync: {self.last_sync}")
    
    def show_help(self):
        """Show available commands"""
        print(f"\n📖 COMMANDS:")
        print(f"  status                    - Show device status")
        print(f"  sensor <type> <value>     - Set sensor value")
        print(f"    Examples: sensor humidity 1, sensor temperature 35")
        print(f"  pump <on|off>            - Control pump")
        print(f"  valve <open|close>       - Control valve")
        print(f"  zone <zone> <start|stop> - Control irrigation zone")
        print(f"  offline                  - Go offline")
        print(f"  online                   - Go online")
        print(f"  sync                     - Manual sync")
        print(f"  help                     - Show this help")
        print(f"  quit                     - Exit")
        print(f"\n💡 Auto-sync every {self.auto_sync_interval}s - Dashboard updates in real-time!")

def main():
    print("🚀 ESP32 Smart Irrigation Simulator")
    print("=" * 50)
    print("🔄 Real-time auto-sync enabled")
    print("💡 Dashboard: http://localhost:3000")
    print("=" * 50)
    
    simulator = ESP32Simulator()
    
    # Auto-connect and start auto-sync
    if simulator.authenticate():
        simulator.start_auto_sync()
        print("✅ System ready! Try these commands:")
        print("  'sensor humidity 15' - Trigger irrigation")
        print("  'offline' - Test offline detection")
        print("  'help' - Show all commands")
    else:
        print("�� Connection failed. Check server status.")
        return
    
    # Interactive command loop
    while True:
        try:
            command = input("\n💻 Command: ").strip().lower()
            
            if command in ["quit", "exit"]:
                simulator.stop_auto_sync_worker()
                print("👋 Goodbye!")
                break
            elif command == "help":
                simulator.show_help()
            elif command == "status":
                simulator.show_status()
            elif command == "sync":
                simulator.sync_with_server()
            elif command == "offline":
                simulator.go_offline()
            elif command == "online":
                simulator.go_online()
            elif command.startswith("sensor "):
                parts = command.split()
                if len(parts) == 3:
                    try:
                        sensor_type = parts[1]
                        value = float(parts[2])
                        simulator.set_sensor_value(sensor_type, value)
                    except ValueError:
                        print("❌ Invalid value. Use: sensor <type> <number>")
                else:
                    print("❌ Usage: sensor <type> <value>")
            elif command.startswith("pump "):
                parts = command.split()
                if len(parts) == 2:
                    simulator.control_pump(parts[1])
                else:
                    print("❌ Usage: pump <on|off>")
            elif command.startswith("valve "):
                parts = command.split()
                if len(parts) == 2:
                    simulator.control_valve(parts[1])
                else:
                    print("❌ Usage: valve <open|close>")
            elif command.startswith("zone "):
                parts = command.split()
                if len(parts) == 3:
                    simulator.control_zone(parts[1], parts[2])
                else:
                    print("❌ Usage: zone <zone> <start|stop>")
            elif command == "":
                continue
            else:
                print(f"❌ Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            simulator.stop_auto_sync_worker()
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()