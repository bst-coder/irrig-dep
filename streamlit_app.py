import streamlit as st
import requests
import json
import time
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, List

# Try to import plotly, fallback to basic charts if not available
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly not available. Using basic charts.")

# Page configuration
st.set_page_config(
    page_title="ESP32 Smart Irrigation System",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-online {
        color: #28a745;
        font-weight: bold;
    }
    .status-offline {
        color: #dc3545;
        font-weight: bold;
    }
    .sensor-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

class ESP32Dashboard:
    def __init__(self):
        # Try to get API URL from secrets, fallback to demo mode
        try:
            self.api_base = st.secrets.get("API_BASE_URL", "http://localhost:8000")
        except:
            self.api_base = "http://localhost:8000"  # Default for demo
        
    def get_devices(self):
        """Fetch devices from API"""
        try:
            response = requests.get(f"{self.api_base}/api/devices", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('devices', [])
            else:
                st.error(f"API Error: {response.status_code}")
                return self.get_demo_devices()
        except Exception as e:
            st.warning(f"API not available: {e}")
            st.info("Showing demo data. Deploy the backend API to see real data.")
            return self.get_demo_devices()
    
    def get_demo_devices(self):
        """Return demo devices when API is not available"""
        return [
            {
                "deviceId": "esp32-demo",
                "isOnline": True,
                "sensors": {"humidity": 25.5, "temperature": 24.0, "pressure": 1013.2},
                "zoneStatus": {"zone1": "irrigating", "zone2": "idle"},
                "states": {"pump": "on", "valve": "open"},
                "timestamp": datetime.now().isoformat()
            },
            {
                "deviceId": "esp32-demo-2",
                "isOnline": False,
                "sensors": {"humidity": 45.0, "temperature": 22.0, "pressure": 1015.0},
                "zoneStatus": {"zone1": "idle", "zone2": "idle"},
                "states": {"pump": "off", "valve": "closed"},
                "timestamp": (datetime.now()).isoformat()
            }
        ]
    
    def send_command(self, device_id: str, action: str, command: str = None):
        """Send command to device"""
        try:
            payload = {
                "deviceId": device_id,
                "action": action
            }
            if command:
                payload["command"] = command
            
            response = requests.post(
                f"{self.api_base}/api/esp32",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                st.success(f"Command sent successfully: {action}")
                return True
            else:
                st.error(f"Command failed: {response.status_code}")
                return False
        except Exception as e:
            st.warning(f"Command not sent (demo mode): {action}")
            st.info("Deploy the backend API to enable real device control.")
            return False

def main():
    st.title("🌱 ESP32 Smart Irrigation System")
    st.markdown("Real-time monitoring and control dashboard")
    
    dashboard = ESP32Dashboard()
    
    # Sidebar controls
    st.sidebar.title("🎛️ Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=True)
    
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    
    # Main dashboard
    devices = dashboard.get_devices()
    
    if not devices:
        st.warning("⚠️ No devices found. Make sure the ESP32 simulator is running.")
        st.info("Run: `python scripts/esp32-simulator.py`")
        return
    
    # System overview
    st.header("📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    online_devices = len([d for d in devices if d.get('isOnline', False)])
    total_zones = sum(len(d.get('zoneStatus', {})) for d in devices)
    active_zones = len([d for d in devices for zone, status in d.get('zoneStatus', {}).items() if status == 'irrigating'])
    
    with col1:
        st.metric("Online Devices", online_devices, delta=f"of {len(devices)}")
    
    with col2:
        st.metric("Total Devices", len(devices))
    
    with col3:
        st.metric("Total Zones", total_zones)
    
    with col4:
        st.metric("Active Zones", active_zones)
    
    # Device cards
    st.header("🔌 Devices")
    
    for device in devices:
        device_id = device.get('deviceId', 'Unknown')
        is_online = device.get('isOnline', False)
        sensors = device.get('sensors', {})
        zone_status = device.get('zoneStatus', {})
        states = device.get('states', {})
        timestamp = device.get('timestamp', '')
        
        # Device container
        with st.container():
            st.subheader(f"📱 {device_id}")
            
            # Status and timestamp
            col1, col2 = st.columns([1, 2])
            with col1:
                status_class = "status-online" if is_online else "status-offline"
                status_text = "🟢 ONLINE" if is_online else "🔴 OFFLINE"
                st.markdown(f'<p class="{status_class}">{status_text}</p>', unsafe_allow_html=True)
            
            with col2:
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        st.text(f"Last update: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    except:
                        st.text(f"Last update: {timestamp}")
            
            # Three columns layout
            col1, col2, col3 = st.columns(3)
            
            # Sensor readings
            with col1:
                st.markdown("### 🌡️ Sensors")
                
                humidity = sensors.get('humidity', 0)
                temperature = sensors.get('temperature', 0)
                pressure = sensors.get('pressure', 0)
                
                st.metric("Humidity", f"{humidity}%", 
                         delta="Low" if humidity < 30 else "Normal")
                st.metric("Temperature", f"{temperature}°C")
                st.metric("Pressure", f"{pressure} hPa")
                
                # Sensor chart
                if PLOTLY_AVAILABLE:
                    sensor_data = pd.DataFrame({
                        'Sensor': ['Humidity', 'Temperature', 'Pressure'],
                        'Value': [humidity, temperature/100*50, pressure/1000*50],  # Normalized for display
                        'Actual': [f"{humidity}%", f"{temperature}°C", f"{pressure} hPa"]
                    })
                    
                    fig = px.bar(sensor_data, x='Sensor', y='Value', 
                               hover_data=['Actual'], title="Sensor Readings")
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Fallback to simple bar chart
                    chart_data = pd.DataFrame({
                        'Humidity': [humidity],
                        'Temperature': [temperature],
                        'Pressure': [pressure/10]  # Scale down for display
                    })
                    st.bar_chart(chart_data)
            
            # Zone control
            with col2:
                st.markdown("### 🏗️ Irrigation Zones")
                
                for zone, status in zone_status.items():
                    col_zone, col_btn = st.columns([2, 1])
                    
                    with col_zone:
                        status_icon = "💧" if status == "irrigating" else "⭕"
                        st.text(f"{status_icon} {zone}: {status.upper()}")
                    
                    with col_btn:
                        if is_online:
                            if status == "idle":
                                if st.button(f"▶️", key=f"start_{device_id}_{zone}"):
                                    dashboard.send_command(device_id, "command", f"{zone} start")
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                if st.button(f"⏹️", key=f"stop_{device_id}_{zone}"):
                                    dashboard.send_command(device_id, "command", f"{zone} stop")
                                    time.sleep(1)
                                    st.rerun()
                        else:
                            st.text("Offline")
            
            # System states and controls
            with col3:
                st.markdown("### ⚙️ System States")
                
                pump_state = states.get('pump', 'off')
                valve_state = states.get('valve', 'closed')
                
                pump_icon = "💧" if pump_state == "on" else "🛑"
                valve_icon = "🚰" if valve_state == "open" else "🔒"
                
                st.text(f"{pump_icon} Pump: {pump_state.upper()}")
                st.text(f"{valve_icon} Valve: {valve_state.upper()}")
                
                if is_online:
                    st.markdown("#### Manual Controls")
                    
                    col_ctrl1, col_ctrl2 = st.columns(2)
                    
                    with col_ctrl1:
                        if st.button("🔄 Restart", key=f"restart_{device_id}"):
                            dashboard.send_command(device_id, "restart")
                    
                    with col_ctrl2:
                        if st.button("🔄 Sync", key=f"sync_{device_id}"):
                            dashboard.send_command(device_id, "sync")
                else:
                    st.warning("Device offline - controls disabled")
            
            st.divider()
    
    # ESP32 Simulator section
    st.header("🤖 ESP32 Simulator")
    
    with st.expander("Simulator Commands", expanded=False):
        st.markdown("""
        **To control the ESP32 simulator, run these commands in your terminal:**
        
        ```bash
        # Start the simulator
        python scripts/esp32-simulator.py
        
        # Example commands in simulator:
        sensor humidity 15      # Set low humidity (triggers irrigation)
        sensor temperature 35   # Set temperature
        pump on                 # Turn pump on
        valve open              # Open valve
        zone zone1 start        # Start irrigation
        offline                 # Go offline
        online                  # Go online
        status                  # Show status
        ```
        """)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    main()