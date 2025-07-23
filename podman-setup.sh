#!/bin/bash

# Podman Setup Script for LC Work Flow Backend
set -e

echo "===== LC Work Flow Backend - Podman Setup ====="

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    echo "Error: Podman is not installed. Please install Podman first."
    echo "Ubuntu/Debian: sudo apt-get install podman"
    echo "Fedora: sudo dnf install podman"
    echo "RHEL/CentOS: sudo yum install podman"
    exit 1
fi

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    echo "Warning: podman-compose is not installed."
    echo "Installing podman-compose using pip..."
    pip install podman-compose
fi

echo "Podman version: $(podman --version)"
echo "Podman-compose version: $(podman-compose --version)"

# Create podman network if it doesn't exist
if ! podman network exists lc-network; then
    echo "Creating podman network: lc-network"
    podman network create lc-network
fi

# Create directories for volumes if they don't exist
mkdir -p ./uploads

echo "\nSetup complete! You can now run the application using podman-compose:"
echo "\npodman-compose -f podman-compose.yml up -d\n"
echo "Or use the helper scripts:\n"
echo "./podman-start.sh    # Start all services"
echo "./podman-stop.sh     # Stop all services"
echo "./podman-logs.sh     # View logs"
echo "\nAccess the API at: http://localhost:8080\n"