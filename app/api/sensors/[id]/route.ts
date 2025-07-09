import { type NextRequest, NextResponse } from "next/server"
import { getLatestSensorReading } from "@/lib/mongodb"

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: deviceId } = await params
    
    if (!deviceId) {
      return NextResponse.json({ error: "Device ID is required" }, { status: 400 })
    }

    // Get latest sensor reading for the device
    const sensorReading = await getLatestSensorReading(deviceId)
    
    if (!sensorReading) {
      return NextResponse.json({ error: "No sensor data found for this device" }, { status: 404 })
    }

    return NextResponse.json({
      success: true,
      deviceId,
      timestamp: sensorReading.timestamp,
      sensors: sensorReading.sensors,
      isOnline: new Date().getTime() - new Date(sensorReading.timestamp).getTime() < 5 * 60 * 1000 // 5 minutes
    })
  } catch (error) {
    console.error("Error fetching sensor data:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}