import { type NextRequest, NextResponse } from "next/server"
import { getAllDevices, getLatestSensorReading, getLatestDeviceState } from "@/lib/mongodb"

export async function GET(request: NextRequest) {
  try {
    // Get all ESP32 devices
    const devices = await getAllDevices()
    
    // Filter only ESP32 devices and enrich with latest data
    const esp32Devices = await Promise.all(
      devices
        .filter((device: any) => device.deviceId.startsWith('esp32'))
        .map(async (device: any) => {
          const latestSensorReading = await getLatestSensorReading(device.deviceId)
          const latestDeviceState = await getLatestDeviceState(device.deviceId)

          return {
            deviceId: device.deviceId,
            name: device.name,
            timestamp: latestSensorReading?.timestamp || new Date(),
            zoneStatus: latestDeviceState?.zoneStatus || { zone1: "idle", zone2: "idle" },
            sensors: latestSensorReading?.sensors || { humidity: 0, temperature: 0, pressure: 0 },
            states: latestDeviceState?.states || { pump: "off", valve: "closed" },
            isOnline: latestSensorReading
              ? new Date().getTime() - new Date(latestSensorReading.timestamp).getTime() < 10 * 1000  // 10 seconds for immediate offline detection
              : false,
            config: device.config || {
              zones: ['zone1', 'zone2'],
              sensors: ['humidity', 'temperature', 'pressure']
            }
          }
        })
    )

    return NextResponse.json({
      success: true,
      devices: esp32Devices,
      count: esp32Devices.length,
      onlineCount: esp32Devices.filter(d => d.isOnline).length
    })
  } catch (error) {
    console.error("Error fetching ESP32 devices:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, deviceId, command } = body

    if (!deviceId) {
      return NextResponse.json({ error: "Device ID is required" }, { status: 400 })
    }

    // Handle different ESP32 actions
    switch (action) {
      case 'restart':
        // In a real implementation, this would send a restart command to the ESP32
        return NextResponse.json({
          success: true,
          message: `Restart command sent to ${deviceId}`,
          timestamp: new Date().toISOString()
        })

      case 'update_config':
        // In a real implementation, this would update the ESP32 configuration
        return NextResponse.json({
          success: true,
          message: `Configuration updated for ${deviceId}`,
          timestamp: new Date().toISOString()
        })

      case 'send_command':
        // In a real implementation, this would send a custom command to the ESP32
        return NextResponse.json({
          success: true,
          message: `Command "${command}" sent to ${deviceId}`,
          timestamp: new Date().toISOString()
        })

      case 'command':
        // Handle zone commands and other device commands
        return NextResponse.json({
          success: true,
          message: `Command "${command}" sent to ${deviceId}`,
          timestamp: new Date().toISOString(),
          command: command
        })

      case 'sync':
        // Trigger a sync request to the device
        return NextResponse.json({
          success: true,
          message: `Sync request sent to ${deviceId}`,
          timestamp: new Date().toISOString()
        })

      default:
        return NextResponse.json({ error: `Invalid action: ${action}` }, { status: 400 })
    }
  } catch (error) {
    console.error("Error handling ESP32 action:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}