#!/bin/bash

# Script tự động deploy LBG
# Usage: ./deploy.sh

set -e

echo "🚀 Starting deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Pull latest code (if in git repo)
if [ -d ".git" ]; then
    echo "📥 Pulling latest code..."
    git pull origin main || echo "⚠️  Could not pull latest code. Continuing..."
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker ps | grep -q lbg_backend; then
    echo "✅ Backend is running!"
else
    echo "❌ Backend failed to start. Check logs: docker-compose -f docker-compose.prod.yml logs backend"
fi

if docker ps | grep -q lbg_frontend; then
    echo "✅ Frontend is running!"
else
    echo "❌ Frontend failed to start. Check logs: docker-compose -f docker-compose.prod.yml logs frontend"
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📊 Services:"
echo "  - Backend: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Useful commands:"
echo "  - View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  - Stop: docker-compose -f docker-compose.prod.yml down"
echo "  - Restart: docker-compose -f docker-compose.prod.yml restart"

