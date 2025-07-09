"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Droplets, Thermometer, Gauge, Zap, Settings } from "lucide-react"

interface SensorData {
  humidity: number
  temperature: number
  pressure: number
}

interface DeviceStatus {
  deviceId: string
  timestamp: string
  zoneStatus: Record<string, string>
  sensors: SensorData
  states: {
    pump: string
    valve: string
  }
  isOnline: boolean
}

export default function IrrigationDashboard() {
  const [devices, setDevices] = useState<DeviceStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [controlLoading, setControlLoading] = useState<string | null>(null)

  const fetchDevices = async () => {
    try {
      const response = await fetch('/api/devices')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      
      // Handle both old and new API response formats
      if (data.success && data.devices) {
        setDevices(data.devices)
        setError(null)
      } else if (Array.isArray(data)) {
        // Convert to expected format
        const convertedDevices = data.map(device => ({
          deviceId: device.deviceId,
          timestamp: device.lastSeen,
          zoneStatus: device.zoneStatus || {},
          sensors: device.sensors || { humidity: 0, temperature: 0, pressure: 0 },
          states: device.states || { pump: 'off', valve: 'closed' },
          isOnline: device.status === 'online'
        }))
        setDevices(convertedDevices)
        setError(null)
      } else {
        throw new Error('Invalid response format')
      }
    } catch (err) {
      console.error('Error fetching devices:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch device data')
      
      // Fallback to show that no ESP32 data is available
      setDevices([])
    } finally {
      setLoading(false)
    }
  }

  const sendCommand = async (deviceId: string, command: string, zone?: string) => {
    const commandKey = `${deviceId}-${command}-${zone || ''}`
    setControlLoading(commandKey)
    
    try {
      let action = 'command'
      let commandPayload = zone ? `${zone} ${command}` : command
      
      // Handle specific actions
      if (command === 'restart' && !zone) {
        action = 'restart'
        commandPayload = undefined
      } else if (command === 'sync' && !zone) {
        action = 'sync'
        commandPayload = undefined
      }
      
      const payload: any = {
        deviceId,
        action
      }
      
      if (commandPayload) {
        payload.command = commandPayload
      }
      
      console.log('Sending command:', payload)
      
      const response = await fetch('/api/esp32', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP ${response.status}: Failed to send command`)
      }

      const result = await response.json()
      console.log('Command result:', result)

      // Refresh devices after command
      setTimeout(fetchDevices, 500)
    } catch (err) {
      console.error('Command failed:', err)
      setError(err instanceof Error ? err.message : 'Failed to send command')
      // Clear error after 3 seconds
      setTimeout(() => setError(null), 3000)
    } finally {
      setControlLoading(null)
    }
  }

  useEffect(() => {
    // Initial fetch
    fetchDevices()

    // Set up real-time updates every 1 second for immediate offline detection
    const interval = setInterval(fetchDevices, 1000)

    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case "irrigating":
        return "bg-blue-500"
      case "on":
        return "bg-green-500"
      case "open":
        return "bg-green-500"
      case "idle":
        return "bg-gray-500"
      case "off":
        return "bg-red-500"
      case "closed":
        return "bg-red-500"
      default:
        return "bg-gray-500"
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading irrigation system...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-red-800 mb-2">Connection Error</h2>
              <p className="text-red-600 mb-4">{error}</p>
              <Button onClick={fetchDevices} className="bg-red-600 hover:bg-red-700">
                Retry Connection
              </Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Show devices even if empty, with better messaging

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Smart Irrigation System</h1>
          <p className="text-gray-600">Monitor and control your irrigation zones in real-time</p>
        </div>

        {/* Status Banner */}
        <div className="mb-6">
          <div className="bg-white rounded-lg shadow-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">System Status</h2>
                <p className="text-gray-600">
                  {devices.length > 0
                    ? `${devices.filter(d => d.isOnline).length} of ${devices.length} devices online`
                    : "No devices connected"
                  }
                </p>
              </div>
              <div className="flex space-x-2">
                <Button onClick={fetchDevices} variant="outline" size="sm">
                  Refresh
                </Button>
                <Badge variant={devices.some(d => d.isOnline) ? "default" : "destructive"}>
                  {devices.some(d => d.isOnline) ? "System Online" : "System Offline"}
                </Badge>
              </div>
            </div>
          </div>
        </div>

        {/* Device Cards */}
        <div className="grid gap-6">
          {devices.length === 0 ? (
            <Card className="shadow-lg">
              <CardContent className="p-8 text-center">
                <Settings className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-700 mb-2">No Devices Found</h3>
                <p className="text-gray-500 mb-4">
                  Run the interactive ESP32 simulator to connect a device:
                </p>
                <code className="bg-gray-100 px-3 py-1 rounded text-sm">
                  python scripts/interactive-esp32-simulator.py
                </code>
              </CardContent>
            </Card>
          ) : (
            devices.map((device) => (
            <Card key={device.deviceId} className="shadow-lg">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Settings className="h-5 w-5" />
                      Device: {device.deviceId}
                    </CardTitle>
                    <CardDescription>Last update: {new Date(device.timestamp).toLocaleString()}</CardDescription>
                  </div>
                  <Badge variant={device.isOnline ? "default" : "destructive"}>
                    {device.isOnline ? "Online" : "Offline"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-6">
                  {/* Sensor Readings */}
                  <div className="space-y-4">
                    <h3 className="font-semibold text-lg mb-3">Sensor Readings</h3>

                    <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                      <Droplets className="h-6 w-6 text-blue-600" />
                      <div>
                        <p className="font-medium">Humidity</p>
                        <p className="text-2xl font-bold text-blue-600">{device.sensors.humidity}%</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg">
                      <Thermometer className="h-6 w-6 text-orange-600" />
                      <div>
                        <p className="font-medium">Temperature</p>
                        <p className="text-2xl font-bold text-orange-600">{device.sensors.temperature}°C</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
                      <Gauge className="h-6 w-6 text-purple-600" />
                      <div>
                        <p className="font-medium">Pressure</p>
                        <p className="text-2xl font-bold text-purple-600">{device.sensors.pressure} hPa</p>
                      </div>
                    </div>
                  </div>

                  {/* Zone Status */}
                  <div className="space-y-4">
                    <h3 className="font-semibold text-lg mb-3">Zone Control</h3>

                    {Object.entries(device.zoneStatus).map(([zone, status]) => (
                      <div key={zone} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center">
                          <span className="font-medium capitalize">{zone}:</span>
                          <Badge className={`ml-2 ${getStatusColor(status)}`}>{status}</Badge>
                        </div>
                        {device.isOnline && (
                          <div className="flex space-x-1">
                            <Button
                              onClick={() => sendCommand(device.deviceId, 'start', zone)}
                              disabled={controlLoading === `${device.deviceId}-start-${zone}`}
                              size="sm"
                              className="bg-green-500 hover:bg-green-600 text-white px-2 py-1 text-xs"
                            >
                              {controlLoading === `${device.deviceId}-start-${zone}` ? '...' : 'Start'}
                            </Button>
                            <Button
                              onClick={() => sendCommand(device.deviceId, 'stop', zone)}
                              disabled={controlLoading === `${device.deviceId}-stop-${zone}`}
                              size="sm"
                              className="bg-red-500 hover:bg-red-600 text-white px-2 py-1 text-xs"
                            >
                              {controlLoading === `${device.deviceId}-stop-${zone}` ? '...' : 'Stop'}
                            </Button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* System States */}
                  <div className="space-y-4">
                    <h3 className="font-semibold text-lg mb-3">System States</h3>

                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Zap className="h-5 w-5" />
                        <span className="font-medium">Pump</span>
                      </div>
                      <Badge className={getStatusColor(device.states.pump)}>{device.states.pump}</Badge>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Settings className="h-5 w-5" />
                        <span className="font-medium">Valve</span>
                      </div>
                      <Badge className={getStatusColor(device.states.valve)}>{device.states.valve}</Badge>
                    </div>

                    {device.isOnline && (
                      <div className="pt-4 space-y-2">
                        <h4 className="font-medium text-gray-900 text-sm">Manual Controls</h4>
                        <div className="flex space-x-2">
                          <Button
                            onClick={() => sendCommand(device.deviceId, 'restart')}
                            disabled={controlLoading === `${device.deviceId}-restart-`}
                            size="sm"
                            className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 text-xs"
                          >
                            {controlLoading === `${device.deviceId}-restart-` ? '...' : 'Restart'}
                          </Button>
                          <Button
                            onClick={() => sendCommand(device.deviceId, 'sync')}
                            disabled={controlLoading === `${device.deviceId}-sync-`}
                            size="sm"
                            className="bg-purple-500 hover:bg-purple-600 text-white px-3 py-1 text-xs"
                          >
                            {controlLoading === `${device.deviceId}-sync-` ? '...' : 'Sync'}
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
            ))
          )}
        </div>

        {/* System Overview */}
        <Card className="mt-6 shadow-lg">
          <CardHeader>
            <CardTitle>System Overview</CardTitle>
            <CardDescription>Real-time monitoring and AI-driven irrigation control</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-4 text-center">
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{devices.filter(d => d.isOnline).length}</p>
                <p className="text-sm text-gray-600">Online Devices</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">{devices.length}</p>
                <p className="text-sm text-gray-600">Total Devices</p>
              </div>
              <div className="p-4 bg-orange-50 rounded-lg">
                <p className="text-2xl font-bold text-orange-600">
                  {devices.reduce((total, device) => total + Object.keys(device.zoneStatus || {}).length, 0)}
                </p>
                <p className="text-sm text-gray-600">Irrigation Zones</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <p className="text-2xl font-bold text-purple-600">
                  {devices.filter(d => Object.values(d.zoneStatus || {}).some(status => status === 'irrigating')).length}
                </p>
                <p className="text-sm text-gray-600">Active Zones</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
