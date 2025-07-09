
import { NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';
import { insertSensorReading, insertSystemLog } from '@/lib/mongodb';

const JWT_SECRET = process.env.JWT_SECRET || 'your_jwt_secret_change_this_in_production';

export async function POST(request: Request) {
  try {
    // Verify the JWT token from the request headers
    const authHeader = request.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, JWT_SECRET) as { deviceId: string };

    const data = await request.json();

    // Verify that the deviceId from the token matches the one in the request body
    if (decoded.deviceId !== data.deviceId) {
      return NextResponse.json({ message: 'Device ID mismatch' }, { status: 403 });
    }

    console.log('Received sync data from ESP32:', {
      deviceId: data.deviceId,
      timestamp: data.timestamp,
      sensors: data.sensors,
      zoneStatus: data.zoneStatus,
      states: data.states
    });

    // Save sensor data to MongoDB
    try {
      await insertSensorReading(
        data.deviceId,
        new Date(data.timestamp),
        data.sensors,
        data.states,
        data.zoneStatus
      );

      // Log successful data reception
      await insertSystemLog(
        data.deviceId,
        'info',
        'Sensor data received and stored successfully',
        { sensors: data.sensors, states: data.states }
      );

      console.log('Data successfully saved to MongoDB');
    } catch (dbError) {
      console.error('Database error:', dbError);
      await insertSystemLog(
        data.deviceId,
        'error',
        'Failed to store sensor data',
        { error: dbError }
      );
    }

    // Handle buffered data if present
    if (data.bufferedData && Array.isArray(data.bufferedData)) {
      console.log(`Processing ${data.bufferedData.length} buffered records`);
      for (const bufferedItem of data.bufferedData) {
        try {
          await insertSensorReading(
            bufferedItem.deviceId,
            new Date(bufferedItem.timestamp),
            bufferedItem.sensors,
            bufferedItem.states,
            bufferedItem.zoneStatus
          );
        } catch (bufferError) {
          console.error('Error processing buffered data:', bufferError);
        }
      }
    }

    // Generate AI-driven commands based on sensor data
    const commands: Record<string, string> = {};
    
    // Simple AI logic: irrigate if humidity is low
    if (data.sensors && data.sensors.humidity < 40) {
      commands.zone1 = 'start';
      console.log('AI Decision: Starting irrigation for zone1 due to low humidity');
    } else if (data.sensors && data.sensors.humidity > 65) {
      commands.zone1 = 'stop';
      console.log('AI Decision: Stopping irrigation for zone1 due to high humidity');
    }

    // Zone 2 logic - different threshold
    if (data.sensors && data.sensors.humidity < 35) {
      commands.zone2 = 'start';
      console.log('AI Decision: Starting irrigation for zone2 due to very low humidity');
    } else if (data.sensors && data.sensors.humidity > 70) {
      commands.zone2 = 'stop';
      console.log('AI Decision: Stopping irrigation for zone2 due to high humidity');
    }

    return NextResponse.json({
      commands,
      message: 'Data received and processed successfully',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    if (error instanceof jwt.JsonWebTokenError) {
      return NextResponse.json({ message: 'Invalid token' }, { status: 401 });
    }
    console.error('Sync error:', error);
    return NextResponse.json({ message: 'Internal server error' }, { status: 500 });
  }
}
