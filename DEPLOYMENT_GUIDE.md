# ESP32 Irrigation System - Streamlit Deployment Guide 🚀

## 📋 Deployment Overview

This guide will help you deploy the ESP32 Irrigation System on Streamlit Cloud with a separate backend API.

### Architecture
```
Streamlit Dashboard → FastAPI Backend → MongoDB Atlas
```

## 🗄️ Database Setup (MongoDB Atlas)

### 1. Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Sign up for a free account
3. Create a new cluster (free tier is sufficient)

### 2. Configure Database Access
1. **Database Access**: Create a database user
   - Username: `irrigation_user`
   - Password: Generate a secure password
   - Database User Privileges: `Read and write to any database`

2. **Network Access**: Add IP addresses
   - Add `0.0.0.0/0` (allow access from anywhere) for development
   - For production, restrict to specific IPs

### 3. Get Connection String
1. Click "Connect" on your cluster
2. Choose "Connect your application"
3. Copy the connection string:
   ```
   mongodb+srv://irrigation_user:<password>@cluster0.xxxxx.mongodb.net/irrigation-system
   ```
4. Replace `<password>` with your actual password

## 🚀 Backend API Deployment (Heroku/Railway)

### Option A: Deploy on Heroku

1. **Create Heroku Account**: [heroku.com](https://heroku.com)

2. **Install Heroku CLI**: [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

3. **Deploy Backend**:
   ```bash
   # Login to Heroku
   heroku login
   
   # Create new app
   heroku create your-irrigation-api
   
   # Set environment variables
   heroku config:set MONGODB_URI="your_mongodb_connection_string"
   heroku config:set JWT_SECRET="your_secure_jwt_secret"
   
   # Deploy
   git add .
   git commit -m "Deploy API server"
   git push heroku main
   ```

### Option B: Deploy on Railway

1. **Create Railway Account**: [railway.app](https://railway.app)

2. **Deploy from GitHub**:
   - Connect your GitHub repository
   - Select the repository
   - Railway will auto-detect the Python app

3. **Set Environment Variables**:
   - `MONGODB_URI`: Your MongoDB connection string
   - `JWT_SECRET`: Your secure JWT secret
   - `PORT`: 8000

## 📱 Streamlit Dashboard Deployment

### 1. Prepare Repository

Make sure your repository has these files:
```
your-repo/
├── streamlit_app.py          # Main Streamlit app
├── requirements_streamlit.txt # Streamlit dependencies
├── .streamlit/
│   └── config.toml           # Streamlit configuration
└── scripts/
    └── esp32-simulator.py    # ESP32 simulator
```

### 2. Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**: [share.streamlit.io](https://share.streamlit.io)

2. **Sign in with GitHub**

3. **Deploy App** - Fill in the form:

   **Repository**: `https://github.com/yourusername/your-repo-name`
   
   **Branch**: `main`
   
   **Main file path**: `streamlit_app.py`
   
   **App URL (optional)**: `your-irrigation-dashboard` (will become `your-irrigation-dashboard.streamlit.app`)

### 3. Configure Secrets

After deployment, go to your app settings and add these secrets:

```toml
# In Streamlit Cloud App Settings > Secrets
API_BASE_URL = "https://your-irrigation-api.herokuapp.com"
MONGODB_URI = "mongodb+srv://irrigation_user:password@cluster0.xxxxx.mongodb.net/irrigation-system"
JWT_SECRET = "your_secure_jwt_secret"
```

## 🔧 Configuration Details

### Environment Variables Needed

#### For Backend API:
- `MONGODB_URI`: MongoDB Atlas connection string
- `JWT_SECRET`: Secure random string for JWT tokens
- `PORT`: Port number (usually set automatically by hosting platform)

#### For Streamlit Dashboard:
- `API_BASE_URL`: URL of your deployed backend API

### Security Notes

1. **JWT Secret**: Generate a secure random string:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **MongoDB**: Use strong passwords and restrict IP access in production

3. **CORS**: Configure CORS properly in production (currently set to allow all origins)

## 🧪 Testing Deployment

### 1. Test Backend API
```bash
# Test health endpoint
curl https://your-irrigation-api.herokuapp.com/health

# Test device authentication
curl -X POST https://your-irrigation-api.herokuapp.com/api/devices/authenticate \
  -H "Content-Type: application/json" \
  -d '{"deviceId": "esp32-test"}'
```

### 2. Test Streamlit Dashboard
1. Open your Streamlit app URL
2. Check if it loads without errors
3. Verify it can connect to your backend API

### 3. Test ESP32 Simulator
Update the simulator to use your deployed API:
```python
# In esp32-simulator.py, update the server URL
SERVER_URL = "https://your-irrigation-api.herokuapp.com"
```

## 📊 Complete Deployment Checklist

### ✅ Database Setup
- [ ] MongoDB Atlas cluster created
- [ ] Database user configured
- [ ] Network access configured
- [ ] Connection string obtained

### ✅ Backend Deployment
- [ ] Backend API deployed (Heroku/Railway)
- [ ] Environment variables set
- [ ] API health check passes
- [ ] CORS configured

### ✅ Frontend Deployment
- [ ] Streamlit app deployed
- [ ] Secrets configured
- [ ] Dashboard loads successfully
- [ ] API connection working

### ✅ Testing
- [ ] Device authentication works
- [ ] Data sync functional
- [ ] Dashboard shows real-time data
- [ ] Commands can be sent

## 🔄 ESP32 Simulator Usage

After deployment, run the simulator locally but connect to your deployed API:

```bash
# Update simulator configuration
python scripts/esp32-simulator.py

# In the simulator, it will connect to your deployed API
# Commands work the same:
sensor humidity 15    # Triggers irrigation
offline              # Test offline detection
pump on              # Control pump
```

## 🌐 Final URLs

After successful deployment, you'll have:

- **Streamlit Dashboard**: `https://your-irrigation-dashboard.streamlit.app`
- **Backend API**: `https://your-irrigation-api.herokuapp.com`
- **API Documentation**: `https://your-irrigation-api.herokuapp.com/docs`

## 🔍 Troubleshooting

### Common Issues

1. **Streamlit app won't start**:
   - Check `requirements_streamlit.txt` is present
   - Verify `streamlit_app.py` is in root directory
   - Check Streamlit Cloud logs

2. **API connection failed**:
   - Verify `API_BASE_URL` in Streamlit secrets
   - Check backend API is running
   - Test API endpoints manually

3. **Database connection issues**:
   - Verify MongoDB connection string
   - Check database user permissions
   - Ensure network access is configured

4. **CORS errors**:
   - Update CORS settings in `api_server.py`
   - Add your Streamlit domain to allowed origins

### Logs and Debugging

- **Streamlit logs**: Available in Streamlit Cloud dashboard
- **Heroku logs**: `heroku logs --tail -a your-irrigation-api`
- **Railway logs**: Available in Railway dashboard

## 🎉 Success!

Once deployed, you'll have a fully functional IoT irrigation system accessible from anywhere:

1. **Monitor**: Real-time dashboard on Streamlit Cloud
2. **Control**: ESP32 simulator connecting to cloud API
3. **Data**: Persistent storage in MongoDB Atlas
4. **Scale**: Ready for multiple devices and users

Your ESP32 Smart Irrigation System is now live in the cloud! 🌱☁️