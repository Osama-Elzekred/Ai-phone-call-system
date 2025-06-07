#!/bin/bash
set -e

echo "🚀 Starting AI Hotline Backend..."

# Function to validate environment
validate_environment() {
    echo "🔍 Validating environment..."
    
    required_vars=("DATABASE_URL" "SECRET_KEY")
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo "❌ Error: Required environment variable $var is not set"
            exit 1
        fi
    done
    
    echo "✅ Environment validation passed!"
}

# Function to setup file system
setup_filesystem() {
    echo "📝 Setting up filesystem..."
    
    # Create necessary directories
    mkdir -p uploads logs
    
    # Try to set permissions (don't fail if we can't)
    chmod 755 uploads logs 2>/dev/null || echo "⚠️  Could not set permissions (using mounted volumes)"
    
    echo "✅ Filesystem setup complete!"
}

# Function to wait for external services (Docker networking only)
wait_for_docker_services() {
    # Only wait for services that are part of the Docker Compose stack
    if [ "$WAIT_FOR_DB" = "true" ] && [ -n "$DATABASE_HOST" ]; then
        echo "⏳ Waiting for Docker database service..."
        while ! nc -z "$DATABASE_HOST" "${DATABASE_PORT:-5432}" 2>/dev/null; do
            echo "Database service unavailable - sleeping"
            sleep 2
        done
        echo "✅ Database service is reachable!"
    fi
    
    if [ "$WAIT_FOR_REDIS" = "true" ] && [ -n "$REDIS_HOST" ]; then
        echo "⏳ Waiting for Docker Redis service..."
        while ! nc -z "$REDIS_HOST" "${REDIS_PORT:-6379}" 2>/dev/null; do
            echo "Redis service unavailable - sleeping"
            sleep 2
        done
        echo "✅ Redis service is reachable!"
    fi
}

# Main execution flow - INFRASTRUCTURE ONLY
main() {
    echo "🔧 AI Hotline Backend Infrastructure Setup"
    echo "=========================================="
    
    validate_environment
    setup_filesystem
    wait_for_docker_services
    
    echo "🎉 Infrastructure setup completed!"
    echo "🚀 Starting application: $*"
    echo "=========================================="
    
    # Let the application handle its own initialization
    exec "$@"
}

# Handle signals for graceful shutdown
trap 'echo "🛑 Received termination signal"; exit 0' SIGTERM SIGINT

# Run main function
main "$@"