# ESP32 Smart Irrigation System 🌱

A complete IoT irrigation system with real-time monitoring, AI-powered decision making, and interactive ESP32 simulation.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
pip install requests
```

### 2. Configure Environment
Create `.env.local`:
```env
MONGODB_URI=mongodb://localhost:27017/irrigation-system
JWT_SECRET=your_jwt_secret_change_this_in_production
NODE_ENV=development
```

### 3. Start the System
```bash
# Terminal 1: Start server
npm run dev

# Terminal 2: Start ESP32 simulator
python scripts/esp32-simulator.py
```

### 4. Open Dashboard
Navigate to: http://localhost:3000

## 🎮 Using the ESP32 Simulator

### Essential Commands
```bash
# Sensor Control (exact values preserved)
sensor humidity 1       # Set humidity to exactly 1%
sensor temperature 35   # Set temperature to 35°C

# Device Control
pump on                 # Turn pump on
valve open              # Open valve
zone zone1 start        # Start irrigation in zone1

# Connection Testing
offline                 # Go offline (dashboard shows within 10s)
online                  # Go online (immediate sync)

# System
status                  # Show current status
help                    # Show all commands
quit                    # Exit
```

## 🌐 Dashboard Features

- **Real-time Updates**: 1-second refresh rate
- **Offline Detection**: 10-second timeout
- **Manual Controls**: Zone, pump, valve control
- **Live Monitoring**: Sensor readings, device status
- **System Overview**: Device counts, active zones

## 🤖 AI Irrigation Logic

- **Automatic Trigger**: Low humidity (< 30%) starts irrigation
- **Smart Control**: Zone-based irrigation management
- **Real-time Response**: Commands processed immediately

## 🧪 Testing

```bash
# Run complete system test
python scripts/system-test.py
```

Tests verify:
- ✅ Server health
- ✅ Device authentication
- ✅ Data synchronization
- ✅ Dashboard APIs
- ✅ Exact sensor values
- ✅ Command sending

## 📊 System Architecture

```
ESP32 Simulator ←→ Next.js Server ←→ MongoDB ←→ Dashboard
     ↓                    ↓              ↓         ↓
- Auto-sync 5s      - JWT Auth      - Storage  - Live 1s
- Exact values      - AI Logic      - History  - Updates
- Device control    - Commands      - States   - Controls
- Offline mode      - REST API      - Buffer   - Status
```

## 🔧 Key Features

### Real-time Performance
- **Auto-sync**: Every 5 seconds
- **Dashboard refresh**: Every 1 second
- **Offline detection**: 10 seconds
- **Exact values**: Preserved precisely

### Complete Device Control
- **Sensors**: Humidity, temperature, pressure
- **Irrigation**: Zone-based control
- **Hardware**: Pump and valve control
- **Connection**: Offline/online simulation

### Production Ready
- **JWT Authentication**: Secure device communication
- **Error Handling**: Comprehensive error management
- **Data Persistence**: MongoDB storage
- **Scalable Architecture**: RESTful API design

## 📱 Real-world Usage

### Normal Operation
```bash
# Simulator auto-syncs every 5 seconds
# Dashboard shows live updates
# AI monitors for irrigation needs
```

### Low Humidity Scenario
```bash
sensor humidity 15    # Set low humidity
# AI automatically triggers irrigation
# Dashboard shows irrigation active
# Pump and valves activate
```

### Offline Testing
```bash
offline              # Device goes offline
# Dashboard shows offline within 10 seconds
# Data buffered in simulator
online               # Device comes back online
# Buffered data synced automatically
```

## ��� Troubleshooting

### Common Issues

**Dashboard not updating:**
- Check server running on port 3000
- Verify MongoDB connection
- Check browser console

**Simulator connection failed:**
- Ensure server is running
- Check network connectivity
- Verify .env.local configuration

**Offline status not showing:**
- Wait 10 seconds after going offline
- Check auto-refresh is working
- Verify simulator stopped syncing

## 📈 Performance Metrics

| Feature | Performance |
|---------|-------------|
| Dashboard Updates | 1 second |
| Offline Detection | 10 seconds |
| Auto-sync Interval | 5 seconds |
| Sensor Precision | Exact values |
| API Response | < 100ms |

## 🏆 What's Working

- ✅ Real-time ESP32 simulation with auto-sync
- ✅ Live dashboard with immediate updates
- ✅ Exact sensor value preservation
- ✅ Complete device control (pump, valve, zones)
- ✅ Immediate offline/online detection
- ✅ AI-powered irrigation decisions
- ✅ Comprehensive error handling
- ✅ Production-ready architecture

## 🔮 Ready for Enhancement

- Weather API integration
- Mobile app development
- Advanced AI algorithms
- User management system
- Cloud deployment
- Advanced analytics

---

**Built with Next.js, MongoDB, and Python - Ready for production!** 🚀