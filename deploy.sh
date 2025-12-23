#!/bin/bash

# Verified Compliance Production Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="verified-compliance"
ENVIRONMENT=${1:-production}
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"

echo -e "${BLUE}🚀 Starting Verified Compliance Deployment${NC}"
echo "=================================================="
echo "Environment: $ENVIRONMENT"
echo "Docker Compose: $DOCKER_COMPOSE_FILE"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please update .env file with your production values before continuing."
        exit 1
    else
        print_error ".env.example file not found. Please create a .env file with required environment variables."
        exit 1
    fi
fi

# Load environment variables
source .env

# Validate required environment variables
required_vars=(
    "POSTGRES_PASSWORD"
    "SECRET_KEY"
    "GHL_API_KEY"
    "GOOGLE_MAPS_API_KEY"
    "SENDGRID_API_KEY"
    "FCM_SERVER_KEY"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Required environment variable $var is not set in .env file"
        exit 1
    fi
done

print_status "Environment variables validated"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p ssl
mkdir -p grafana/provisioning/datasources
mkdir -p grafana/provisioning/dashboards

# Generate SSL certificates (self-signed for development)
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    print_warning "SSL certificates not found. Generating self-signed certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    print_status "SSL certificates generated"
fi

# Create Grafana datasource configuration
cat > grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

print_status "Grafana datasource configured"

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f $DOCKER_COMPOSE_FILE down --remove-orphans

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f $DOCKER_COMPOSE_FILE up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose -f $DOCKER_COMPOSE_FILE exec -T postgres pg_isready -U ${POSTGRES_USER:-vc_user} -d ${POSTGRES_DB:-verified_compliance} > /dev/null 2>&1; then
    print_status "PostgreSQL is healthy"
else
    print_error "PostgreSQL is not healthy"
    exit 1
fi

# Check Redis
if docker-compose -f $DOCKER_COMPOSE_FILE exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_status "Redis is healthy"
else
    print_error "Redis is not healthy"
    exit 1
fi

# Check Backend API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Backend API is healthy"
else
    print_error "Backend API is not healthy"
    exit 1
fi

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose -f $DOCKER_COMPOSE_FILE exec -T backend alembic upgrade head

if [ $? -eq 0 ]; then
    print_status "Database migrations completed"
else
    print_error "Database migrations failed"
    exit 1
fi

# Run initial data setup
echo "📊 Setting up initial data..."
docker-compose -f $DOCKER_COMPOSE_FILE exec -T backend python -c "
from app.core.database import get_db
from app.models.base import Base
from app.models.contact import Contact
from app.models.meeting import Meeting
from app.models.session import Session
from app.models.session_event import SessionEvent
import asyncio

async def setup_initial_data():
    # This would create initial data if needed
    pass

asyncio.run(setup_initial_data())
"

if [ $? -eq 0 ]; then
    print_status "Initial data setup completed"
else
    print_warning "Initial data setup failed (this may be normal)"
fi

# Display service information
echo ""
echo "🎉 Deployment completed successfully!"
echo "=================================================="
echo "Services:"
echo "  • Backend API: http://localhost:8000"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Health Check: http://localhost:8000/health"
echo "  • Prometheus: http://localhost:9090"
echo "  • Grafana: http://localhost:3000"
echo "  • Nginx: http://localhost:80"
echo ""
echo "Default Grafana credentials:"
echo "  • Username: admin"
echo "  • Password: ${GRAFANA_PASSWORD:-admin}"
echo ""
echo "To view logs:"
echo "  docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose -f $DOCKER_COMPOSE_FILE down"
echo ""

# Run health check
echo "🏥 Running final health check..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "All services are healthy and ready!"
else
    print_error "Health check failed. Please check the logs."
    exit 1
fi

echo "🚀 Verified Compliance is now running in production mode!"
