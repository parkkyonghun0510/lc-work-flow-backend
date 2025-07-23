#!/bin/bash

# Stop services using podman-compose
set -e

echo "===== Stopping LC Work Flow Backend with Podman ====="

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    echo "Error: podman-compose is not installed. Please run ./podman-setup.sh first."
    exit 1
fi

# Stop services
echo "Stopping services..."
podman-compose -f podman-compose.yml down

echo "\nServices stopped successfully!\n"