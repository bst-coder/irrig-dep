import { type NextRequest, NextResponse } from "next/server"
import { getAllDevices, getLatestSensorReading, getLatestDeviceState } from "@/lib/mongodb"

export async function GET(request: NextRequest) {
  try {
    // Get all devices from MongoDB
    const devices = await getAllDevices()

    // Enrich devices with latest sensor data and states
    const enrichedDevices = await Promise.all(
      devices.map(async (device: any) => {
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
        }
      }),
    )

    return NextResponse.json({
      success: true,
      devices: enrichedDevices,
    })
  } catch (error) {
    console.error("Error fetching devices:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
