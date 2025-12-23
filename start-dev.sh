#!/bin/bash

# Verified Compliance Development Startup Script

echo "🚀 Starting Verified Compliance Development Environment"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Start the development environment
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U vc_user -d verified_compliance > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
    exit 1
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis is not ready"
    exit 1
fi

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📋 Available services:"
echo "  • Backend API: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • Frontend: http://localhost:3000"
echo "  • PostgreSQL: localhost:5432"
echo "  • Redis: localhost:6379"
echo ""
echo "🔧 Next steps:"
echo "  1. Run database migrations: cd backend && poetry run alembic upgrade head"
echo "  2. Start backend development: cd backend && poetry run uvicorn app.main:app --reload"
echo "  3. Start frontend development: cd frontend && flutter run"
echo ""
echo "🛑 To stop the environment: docker-compose down"
