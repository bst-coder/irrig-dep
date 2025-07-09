#!/usr/bin/env python3
"""
ESP32 Irrigation System - Standalone API Server
FastAPI backend that can be deployed independently
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, List, Optional
import jwt
import os
import pymongo
from datetime import datetime, timezone, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://bst-coder:1amine@BST@cluster0.3tcrszs.mongodb.net/")
JWT_SECRET = os.getenv("JWT_SECRET", "9ca4f51e52993c05b3c3429ab71baf1dab5d0b36a461b0000db8022010090e66")

# FastAPI app
app = FastAPI(
    title="ESP32 Irrigation System API",
    description="Backend API for ESP32 smart irrigation system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# MongoDB connection
try:
    client = pymongo.MongoClient(MONGODB_URI)
    db = client.get_default_database()
    devices_collection = db.devices
    sensor_readings_collection = db.sensor_readings
    device_states_collection = db.device_states
    logger.info("Connected to MongoDB")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")
    db = None

# Pydantic models
class DeviceAuth(BaseModel):
    deviceId: str

class SensorData(BaseModel):
    humidity: float
    temperature: float
    pressure: float

class DeviceStates(BaseModel):
    pump: str
    valve: str

class ZoneStatus(BaseModel):
    zone1: str = "idle"
    zone2: str = "idle"

class SyncData(BaseModel):
    deviceId: str
    timestamp: str
    sensors: SensorData
    states: DeviceStates
    zoneStatus: ZoneStatus
    bufferedData: Optional[List[Dict]] = None

class CommandRequest(BaseModel):
    deviceId: str
    action: str
    command: Optional[str] = None

# Helper functions
def create_jwt_token(device_id: str) -> str:
    """Create JWT token for device"""
    payload = {
        "device_id": device_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        return payload["device_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_latest_sensor_reading(device_id: str) -> Optional[Dict]:
    """Get latest sensor reading for device"""
    if not db:
        return None
    
    try:
        return sensor_readings_collection.find_one(
            {"deviceId": device_id},
            sort=[("timestamp", -1)]
        )
    except Exception as e:
        logger.error(f"Error getting sensor reading: {e}")
        return None

def get_latest_device_state(device_id: str) -> Optional[Dict]:
    """Get latest device state"""
    if not db:
        return None
    
    try:
        return device_states_collection.find_one(
            {"deviceId": device_id},
            sort=[("timestamp", -1)]
        )
    except Exception as e:
        logger.error(f"Error getting device state: {e}")
        return None

def apply_ai_irrigation_logic(sensors: SensorData) -> Dict[str, str]:
    """Apply AI logic for irrigation decisions"""
    commands = {}
    
    # Simple AI: if humidity is low, start irrigation
    if sensors.humidity < 30:
        commands["zone1"] = "start"
        commands["zone2"] = "start"
        logger.info(f"AI Decision: Low humidity ({sensors.humidity}%) - starting irrigation")
    
    return commands

# API Routes
@app.get("/")
async def root():
    return {"message": "ESP32 Irrigation System API", "status": "running"}

@app.get("/health")
async def health_check():
    db_status = "connected" if db else "disconnected"
    return {"status": "healthy", "database": db_status}

@app.post("/api/devices/authenticate")
async def authenticate_device(auth_data: DeviceAuth):
    """Authenticate ESP32 device"""
    try:
        device_id = auth_data.deviceId
        
        # Register or update device
        if db:
            devices_collection.update_one(
                {"deviceId": device_id},
                {
                    "$set": {
                        "deviceId": device_id,
                        "name": f"ESP32 Device {device_id}",
                        "lastSeen": datetime.now(timezone.utc),
                        "config": {
                            "zones": ["zone1", "zone2"],
                            "sensors": ["humidity", "temperature", "pressure"]
                        }
                    }
                },
                upsert=True
            )
        
        # Create JWT token
        token = create_jwt_token(device_id)
        
        return {
            "success": True,
            "token": token,
            "config": {
                "zones": ["zone1", "zone2"],
                "sensors": ["humidity", "temperature", "pressure"]
            },
            "commands": {}
        }
    
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@app.post("/api/devices/sync")
async def sync_device_data(sync_data: SyncData, device_id: str = Depends(verify_jwt_token)):
    """Sync device data and return commands"""
    try:
        # Verify device ID matches token
        if sync_data.deviceId != device_id:
            raise HTTPException(status_code=403, detail="Device ID mismatch")
        
        timestamp = datetime.now(timezone.utc)
        
        # Store sensor reading
        if db:
            sensor_reading = {
                "deviceId": device_id,
                "timestamp": timestamp,
                "sensors": sync_data.sensors.dict()
            }
            sensor_readings_collection.insert_one(sensor_reading)
            
            # Store device state
            device_state = {
                "deviceId": device_id,
                "timestamp": timestamp,
                "states": sync_data.states.dict(),
                "zoneStatus": sync_data.zoneStatus.dict()
            }
            device_states_collection.insert_one(device_state)
            
            # Process buffered data if any
            if sync_data.bufferedData:
                for buffered_item in sync_data.bufferedData:
                    sensor_readings_collection.insert_one({
                        "deviceId": device_id,
                        "timestamp": datetime.fromisoformat(buffered_item["timestamp"].replace('Z', '+00:00')),
                        "sensors": buffered_item["sensors"]
                    })
        
        # Apply AI irrigation logic
        commands = apply_ai_irrigation_logic(sync_data.sensors)
        
        return {
            "success": True,
            "commands": commands,
            "timestamp": timestamp.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Sync error: {e}")
        raise HTTPException(status_code=500, detail="Sync failed")

@app.get("/api/devices")
async def get_all_devices():
    """Get all devices with latest data"""
    try:
        if not db:
            return {"success": True, "devices": []}
        
        devices = list(devices_collection.find({}))
        enriched_devices = []
        
        for device in devices:
            device_id = device["deviceId"]
            latest_sensor = get_latest_sensor_reading(device_id)
            latest_state = get_latest_device_state(device_id)
            
            # Check if device is online (within 10 seconds)
            is_online = False
            if latest_sensor:
                last_update = latest_sensor["timestamp"]
                if isinstance(last_update, str):
                    last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                time_diff = datetime.now(timezone.utc) - last_update
                is_online = time_diff.total_seconds() < 10
            
            enriched_device = {
                "deviceId": device_id,
                "name": device.get("name", f"ESP32 Device {device_id}"),
                "timestamp": latest_sensor["timestamp"] if latest_sensor else datetime.now(timezone.utc),
                "sensors": latest_sensor["sensors"] if latest_sensor else {"humidity": 0, "temperature": 0, "pressure": 0},
                "states": latest_state["states"] if latest_state else {"pump": "off", "valve": "closed"},
                "zoneStatus": latest_state["zoneStatus"] if latest_state else {"zone1": "idle", "zone2": "idle"},
                "isOnline": is_online
            }
            enriched_devices.append(enriched_device)
        
        return {"success": True, "devices": enriched_devices}
    
    except Exception as e:
        logger.error(f"Get devices error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get devices")

@app.get("/api/esp32")
async def get_esp32_devices():
    """Get ESP32 specific devices"""
    devices_response = await get_all_devices()
    devices = devices_response["devices"]
    
    # Filter ESP32 devices
    esp32_devices = [d for d in devices if d["deviceId"].startswith("esp32")]
    online_count = len([d for d in esp32_devices if d["isOnline"]])
    
    return {
        "success": True,
        "devices": esp32_devices,
        "count": len(esp32_devices),
        "onlineCount": online_count
    }

@app.post("/api/esp32")
async def send_esp32_command(command_req: CommandRequest):
    """Send command to ESP32 device"""
    try:
        device_id = command_req.deviceId
        action = command_req.action
        command = command_req.command
        
        # In a real implementation, this would send commands to the actual device
        # For now, we just acknowledge the command
        
        message = f"{action.title()} command sent to {device_id}"
        if command:
            message = f"Command '{command}' sent to {device_id}"
        
        return {
            "success": True,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Command error: {e}")
        raise HTTPException(status_code=500, detail="Command failed")

@app.get("/api/sensors/{device_id}")
async def get_sensor_data(device_id: str):
    """Get sensor data for specific device"""
    try:
        latest_sensor = get_latest_sensor_reading(device_id)
        
        if not latest_sensor:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Check if device is online
        last_update = latest_sensor["timestamp"]
        if isinstance(last_update, str):
            last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
        time_diff = datetime.now(timezone.utc) - last_update
        is_online = time_diff.total_seconds() < 10
        
        return {
            "success": True,
            "deviceId": device_id,
            "timestamp": latest_sensor["timestamp"],
            "sensors": latest_sensor["sensors"],
            "isOnline": is_online
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get sensor data error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sensor data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)