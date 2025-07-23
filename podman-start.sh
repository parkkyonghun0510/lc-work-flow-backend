#!/bin/bash

# Start services using podman-compose
set -e

echo "===== Starting LC Work Flow Backend with Podman ====="

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    echo "Error: podman-compose is not installed. Please run ./podman-setup.sh first."
    exit 1
fi

# Start services
echo "Starting services..."
podman-compose -f podman-compose.yml up -d

echo "\nServices started successfully!\n"
echo "Backend API is available at: http://localhost:8080"
echo "PostgreSQL is available at: localhost:5433"
echo "Redis is available at: localhost:6380"
echo "\nTo view logs, run: ./podman-logs.sh"
echo "To stop services, run: ./podman-stop.sh"