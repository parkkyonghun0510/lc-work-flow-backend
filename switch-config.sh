#!/bin/bash

# Script to switch between local and Podman configurations
set -e

echo "===== LC Work Flow Backend - Configuration Switcher ====="

if [ "$1" = "local" ]; then
    echo "Switching to local configuration..."
    # Update DATABASE_URL
    sed -i 's/^DATABASE_URL=.*/DATABASE_URL=postgresql:\/\/postgres:123456@localhost:5432\/le-db/' .env
    # Update REDIS_URL
    sed -i 's/^REDIS_URL=.*/REDIS_URL=redis:\/\/localhost:6379\/0/' .env
    echo "Configuration switched to local mode."
    echo "- PostgreSQL: localhost:5432"
    echo "- Redis: localhost:6379"
    
    echo "\nTo start the application locally, run:"
    echo "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    
elif [ "$1" = "podman" ]; then
    echo "Switching to Podman configuration..."
    # Update DATABASE_URL
    sed -i 's/^DATABASE_URL=.*/DATABASE_URL=postgresql:\/\/postgres:123456@localhost:5433\/le-db/' .env
    # Update REDIS_URL
    sed -i 's/^REDIS_URL=.*/REDIS_URL=redis:\/\/localhost:6380\/0/' .env
    echo "Configuration switched to Podman mode."
    echo "- PostgreSQL: localhost:5433"
    echo "- Redis: localhost:6380"
    
    echo "\nTo start the application with Podman, run:"
    echo "./podman-start.sh"
    
else
    echo "Error: Invalid configuration mode."
    echo "Usage: ./switch-config.sh [local|podman]"
    echo "  local  - Switch to local configuration"
    echo "  podman - Switch to Podman configuration"
    exit 1
fi

echo "\nDone!"