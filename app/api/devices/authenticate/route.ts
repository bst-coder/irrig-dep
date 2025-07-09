
import { NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';
import { getDatabase } from '@/lib/mongodb';

const JWT_SECRET = process.env.JWT_SECRET || 'your_jwt_secret_change_this_in_production';

export async function POST(request: Request) {
  try {
    const { deviceId } = await request.json();

    if (!deviceId) {
      return NextResponse.json({ message: 'Device ID is required' }, { status: 400 });
    }

    // Register or update device in database
    const db = await getDatabase();
    
    // Check if device exists, if not create it
    const existingDevice = await db.collection('devices').findOne({ deviceId });
    
    if (!existingDevice) {
      // Create new device record
      await db.collection('devices').insertOne({
        deviceId,
        name: `ESP32 Device ${deviceId}`,
        isActive: true,
        createdAt: new Date(),
        lastSeen: new Date(),
        config: {
          zones: ['zone1', 'zone2'],
          sensors: ['humidity', 'temperature', 'pressure'],
        }
      });
      console.log(`New device registered: ${deviceId}`);
    } else {
      // Update last seen timestamp
      await db.collection('devices').updateOne(
        { deviceId },
        {
          $set: {
            lastSeen: new Date(),
            isActive: true
          }
        }
      );
      console.log(`Device reconnected: ${deviceId}`);
    }

    // Generate a JWT token for the device
    const token = jwt.sign({ deviceId }, JWT_SECRET, { expiresIn: '24h' });

    // Respond with the assigned configuration
    const response = {
      token,
      config: {
        zones: ['zone1', 'zone2'],
        sensors: ['humidity', 'temperature', 'pressure'],
      },
      metadata: {
        weather: 'clear',
        systemUpdate: false,
      },
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Authentication error:', error);
    return NextResponse.json({ message: 'Internal server error' }, { status: 500 });
  }
}
