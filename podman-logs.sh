#!/bin/bash

# View logs for services using podman-compose
set -e

echo "===== LC Work Flow Backend Logs (Podman) ====="

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    echo "Error: podman-compose is not installed. Please run ./podman-setup.sh first."
    exit 1
fi

# Check if a specific service was specified
if [ -z "$1" ]; then
    # No service specified, show options
    echo "\nUsage: ./podman-logs.sh [service]\n"
    echo "Available services:"
    echo "  backend   - FastAPI backend service"
    echo "  postgres - PostgreSQL database service"
    echo "  redis    - Redis cache service"
    echo "  all      - All services (default if no service specified)"
    echo "\nExample: ./podman-logs.sh backend\n"
    
    # Default to showing backend logs
    echo "Showing backend logs (press Ctrl+C to exit):\n"
    podman-compose -f podman-compose.yml logs -f backend
else
    # Show logs for the specified service
    if [ "$1" = "all" ]; then
        echo "Showing logs for all services (press Ctrl+C to exit):\n"
        podman-compose -f podman-compose.yml logs -f
    else
        echo "Showing logs for $1 service (press Ctrl+C to exit):\n"
        podman-compose -f podman-compose.yml logs -f "$1"
    fi
fi