# 🚀 Alo-Veda Deployment Guide

This guide covers multiple deployment options for your Alo-Veda AI Database Chatbot.

## 📋 Prerequisites

- Python 3.11+
- Docker (for containerized deployment)
- Git

## 🔧 Local Deployment

### Option 1: Using the Deployment Script
```bash
# Full stack (backend + frontend)
python deploy.py --mode full --env production

# Backend only
python deploy.py --mode backend --env production
```

### Option 2: Manual Deployment
```bash
# Start backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
streamlit run frontend/streamlit_app.py --server.port 8501
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop
docker-compose down
```

### Using Docker directly
```bash
# Build image
docker build -t alo-veda .

# Run container
docker run -p 8000:8000 -p 8501:8501 alo-veda
```

## ☁️ Cloud Deployment Options

### 1. Render.com (Recommended - Free Tier Available)

1. **Create Render Account**: Go to [render.com](https://render.com)

2. **Connect GitHub**: Link your repository

3. **Create Web Service**:
   - Runtime: Docker
   - Build Command: `docker build -t alo-veda .`
   - Start Command: `python deploy.py --mode full`

4. **Environment Variables**:
   ```
   ENVIRONMENT=production
   API_HOST=0.0.0.0
   API_PORT=10000
   FRONTEND_PORT=8501
   ```

### 2. Railway.app

1. **Connect Repository**: Link your GitHub repo
2. **Deploy**: Railway auto-detects Python and deploys
3. **Set Environment Variables**:
   ```
   ENVIRONMENT=production
   API_HOST=0.0.0.0
   ```

### 3. Heroku

1. **Create Heroku App**:
   ```bash
   heroku create your-alo-veda-app
   ```

2. **Add Procfile**:
   ```
   web: python deploy.py --mode full --env production
   ```

3. **Deploy**:
   ```bash
   git push heroku main
   ```

### 4. AWS/GCP/Azure

For cloud providers, use the Docker deployment with their container services:
- **AWS**: ECS or Elastic Beanstalk
- **Google Cloud**: Cloud Run or App Engine
- **Azure**: Container Instances or App Service

## 🔒 Production Configuration

### Environment Variables
Set these for production deployment:

```bash
export ENVIRONMENT=production
export API_HOST=0.0.0.0
export API_PORT=8000
export FRONTEND_PORT=8501
export LOG_LEVEL=INFO
export SECRET_KEY=your-super-secret-key
```

### Database Upgrade (Optional)
For production scale, consider upgrading from SQLite:

```bash
# PostgreSQL example
export DATABASE_URL=postgresql://user:password@host:port/database
export DATABASE_TYPE=postgresql
```

## 📊 Monitoring & Health Checks

### Health Check Endpoints
- Backend Health: `http://your-domain:8000/health`
- API Documentation: `http://your-domain:8000/docs`

### Logs
```bash
# Docker logs
docker-compose logs -f

# Local deployment logs
tail -f logs/alo-veda.log
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Kill processes using the ports
   lsof -ti:8000 | xargs kill -9
   lsof -ti:8501 | xargs kill -9
   ```

2. **Database Errors**:
   ```bash
   # Reset database
   rm -f alo_veda.db
   python -c "from database.database import init_database; init_database()"
   ```

3. **Module Import Errors**:
   ```bash
   # Ensure you're in the correct directory
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

## 🎯 Quick Start Commands

```bash
# Clone and setup
git clone <your-repo>
cd Chatbot
pip install -r requirements.txt

# Deploy locally
python deploy.py

# Deploy with Docker
docker-compose up --build

# Deploy to cloud (Render example)
# Push to GitHub, then connect to Render.com
```

## 📞 Support

Your Alo-Veda chatbot should now be running! Visit:
- **Frontend**: http://localhost:8501 (or your cloud URL)
- **API**: http://localhost:8000 (or your cloud URL)
- **Docs**: http://localhost:8000/docs

For issues, check the logs and ensure all dependencies are installed. 