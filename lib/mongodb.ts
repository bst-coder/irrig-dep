import { MongoClient, type Db } from "mongodb"

if (!process.env.MONGODB_URI) {
  throw new Error('Invalid/Missing environment variable: "MONGODB_URI"')
}

const uri = process.env.MONGODB_URI
const options = {}

let client: MongoClient
let clientPromise: Promise<MongoClient>

if (process.env.NODE_ENV === "development") {
  // In development mode, use a global variable so that the value
  // is preserved across module reloads caused by HMR (Hot Module Replacement).
  const globalWithMongo = global as typeof globalThis & {
    _mongoClientPromise?: Promise<MongoClient>
  }

  if (!globalWithMongo._mongoClientPromise) {
    client = new MongoClient(uri, options)
    globalWithMongo._mongoClientPromise = client.connect()
  }
  clientPromise = globalWithMongo._mongoClientPromise
} else {
  // In production mode, it's best to not use a global variable.
  client = new MongoClient(uri, options)
  clientPromise = client.connect()
}

// Export a module-scoped MongoClient promise. By doing this in a
// separate module, the client can be shared across functions.
export default clientPromise

// Helper function to get database
export async function getDatabase(): Promise<Db> {
  const client = await clientPromise
  return client.db()
}

// Helper functions for common operations
export async function insertSensorReading(
  deviceId: string,
  timestamp: Date,
  sensors: any,
  states: any,
  zoneStatus: any,
) {
  const db = await getDatabase()

  // Insert sensor reading
  await db.collection("sensorReadings").insertOne({
    deviceId,
    timestamp,
    sensors,
    createdAt: new Date(),
  })

  // Insert device state
  await db.collection("deviceStates").insertOne({
    deviceId,
    timestamp,
    zoneStatus,
    states,
    createdAt: new Date(),
  })
}

export async function getLatestSensorReading(deviceId: string) {
  const db = await getDatabase()

  return await db.collection("sensorReadings").findOne({ deviceId }, { sort: { timestamp: -1 } })
}

export async function getLatestDeviceState(deviceId: string) {
  const db = await getDatabase()

  return await db.collection("deviceStates").findOne({ deviceId }, { sort: { timestamp: -1 } })
}

export async function insertAICommand(deviceId: string, commandType: string, zoneId: string, action: string) {
  const db = await getDatabase()

  return await db.collection("aiCommands").insertOne({
    deviceId,
    commandType,
    zoneId,
    action,
    status: "pending",
    createdAt: new Date(),
  })
}

export async function getPendingCommands(deviceId: string) {
  const db = await getDatabase()

  return await db.collection("aiCommands").find({ deviceId, status: "pending" }).toArray()
}

export async function markCommandExecuted(commandId: string) {
  const db = await getDatabase()

  return await db.collection("aiCommands").updateOne(
    { _id: commandId },
    {
      $set: {
        status: "executed",
        executedAt: new Date(),
      },
    },
  )
}

export async function insertSystemLog(deviceId: string, logLevel: string, message: string, metadata?: any) {
  const db = await getDatabase()

  return await db.collection("systemLogs").insertOne({
    deviceId,
    logLevel,
    message,
    metadata: metadata || {},
    createdAt: new Date(),
  })
}

export async function getDevice(deviceId: string) {
  const db = await getDatabase()

  return await db.collection("devices").findOne({ deviceId })
}

export async function getAllDevices() {
  const db = await getDatabase()

  return await db.collection("devices").find({ isActive: true }).toArray()
}
