# 🐳 Docker Deployment Guide

This guide explains how to run the **AI Nutritional Health Assistant** using Docker.

## 📋 Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** v2.0+
- **Git** (for cloning the project)

### Install Docker
- **Windows/Mac**: [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux**: Follow [official Docker Engine installation](https://docs.docker.com/engine/install/)

---

## 🏗️ Architecture

The application runs with **3 Docker containers**:

```
┌─────────────────┐
│  Frontend       │  Port 3000
│  (Next.js)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backend        │  Port 8000
│  (FastAPI)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Database       │  Port 5432
│  (PostgreSQL)   │
└─────────────────┘
```

All containers are connected via a custom Docker network: `nutrify-network`

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/theankitdash/AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets.git
cd AI-Nutritional-Health-Assistant-Personalized-Guidance-for-Indian-Diets
```

### 2. Configure Environment Variables

Ensure `.env` file exists in the project root with the following:

```env
# Database Configuration
DB_NAME=nutrify_db
DB_PASSWORD=your_secure_password_here

# API Keys (add your own)
NVIDIA_API_KEY=your_nvidia_api_key
# Add other required environment variables
```

### 3. Start All Services

```bash
docker-compose up --build
```

**What this does:**
- Builds Docker images for frontend and backend
- Pulls PostgreSQL 17 image
- Creates containers and starts all services
- Sets up networking between containers

### 4. Access the Application

- **Frontend (Next.js)**: [http://localhost:3000](http://localhost:3000)
- **Backend API (FastAPI)**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Database**: `localhost:5432` (accessible via pgAdmin or other DB clients)

---

## 📦 Docker Commands Reference

### Start Services (Detached Mode)
```bash
docker-compose up -d
```
Runs containers in the background.

### Stop Services
```bash
docker-compose down
```
Stops and removes containers (but preserves volumes/data).

### Stop Services + Remove Volumes
```bash
docker-compose down -v
```
⚠️ **Warning**: This deletes all database data!

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f fastapi
docker-compose logs -f postgres-db
```

### Rebuild Images
```bash
docker-compose up --build
```
Use this after code changes.

### View Running Containers
```bash
docker ps
```

### Execute Commands Inside Container
```bash
# Backend container
docker exec -it nutrify-health bash

# Frontend container
docker exec -it nutrify-frontend sh

# Database container
docker exec -it postgres-db psql -U postgres -d nutrify_db
```

### Restart a Single Service
```bash
docker-compose restart frontend
docker-compose restart fastapi
docker-compose restart postgres-db
```

---

## 🔧 Development Workflow

### Making Code Changes

#### Frontend Changes
1. Edit files in `frontend/` directory
2. Rebuild frontend:
   ```bash
   docker-compose up --build frontend
   ```
3. Or restart:
   ```bash
   docker-compose restart frontend
   ```

#### Backend Changes
1. Edit files in `app/` directory
2. Rebuild backend:
   ```bash
   docker-compose up --build fastapi
   ```

#### Hot Reload (Development Mode)
For development with hot reload, you can mount volumes:
```yaml
# Add to docker-compose.yml under frontend service
volumes:
  - ./frontend:/app
  - /app/node_modules
  - /app/.next
```

---

## 🐛 Troubleshooting

### Port Already in Use
If ports 3000, 8000, or 5432 are already in use:

**Option 1**: Stop conflicting services
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

**Option 2**: Change ports in `docker-compose.yml`
```yaml
ports:
  - "3001:3000"  # Use port 3001 instead
```

### Database Connection Failed
1. Check if PostgreSQL container is running:
   ```bash
   docker ps | grep postgres-db
   ```
2. Verify environment variables in `.env`
3. Check database logs:
   ```bash
   docker-compose logs postgres-db
   ```

### Build Errors
1. Clear Docker cache:
   ```bash
   docker system prune -a
   ```
2. Rebuild from scratch:
   ```bash
   docker-compose down -v
   docker-compose build --no-cache
   docker-compose up
   ```

### Permission Errors (Linux)
If getting permission errors:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

## 📊 Database Management

### Access PostgreSQL CLI
```bash
docker exec -it postgres-db psql -U postgres -d nutrify_db
```

### Backup Database
```bash
docker exec postgres-db pg_dump -U postgres nutrify_db > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker exec -i postgres-db psql -U postgres -d nutrify_db
```

### Connect via pgAdmin
- **Host**: localhost
- **Port**: 5432
- **Database**: nutrify_db (from .env)
- **Username**: postgres
- **Password**: (from .env DB_PASSWORD)

---

## 🌐 Production Deployment

### Building for Production

1. **Update environment variables** for production:
   ```env
   NODE_ENV=production
   DB_PASSWORD=strong_production_password
   ```

2. **Build production images**:
   ```bash
   docker-compose -f docker-compose.yml build
   ```

3. **Push to Docker Hub** (optional):
   ```bash
   docker-compose push
   ```

### Deployment Platforms

#### Option 1: Traditional VPS (DigitalOcean, AWS EC2, etc.)
1. Install Docker on server
2. Clone repository
3. Configure `.env`
4. Run `docker-compose up -d`

#### Option 2: AWS ECS
Use your existing Docker images with Amazon ECS.

#### Option 3: Google Cloud Run
Deploy containerized apps without managing infrastructure.

#### Option 4: Azure Container Instances
Quick deployment with Azure's container service.

---

## 🔐 Security Best Practices

1. **Never commit `.env` files** to Git
2. **Use strong passwords** for production databases
3. **Limit exposed ports** in production (don't expose 5432 publicly)
4. **Use Docker secrets** for sensitive data in production
5. **Regular updates**: Keep base images updated
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

---

## 📈 Performance Optimization

### Multi-Stage Builds
Both Dockerfiles use multi-stage builds to minimize image size.

### Cache Optimization
Dependencies are installed before copying source code for better layer caching.

### Health Checks (Advanced)
Add health checks to `docker-compose.yml`:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Next.js Docker Deployment](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)

---

## ❓ FAQ

**Q: Do I need Kubernetes?**  
A: No! Docker Compose is sufficient for this project unless you need auto-scaling across multiple servers or 99.99% uptime requirements.

**Q: Can I run this in development mode?**  
A: Yes! The current setup works for both development and production. For faster dev iteration, you can run services individually outside Docker.

**Q: How do I update dependencies?**  
A: Update `requirements.txt` (backend) or `package.json` (frontend), then rebuild:
```bash
docker-compose up --build
```

**Q: How much memory do I need?**  
A: Minimum **4GB RAM** recommended. 8GB+ for optimal performance.

---

Made with ❤️ for healthier Indian diets
