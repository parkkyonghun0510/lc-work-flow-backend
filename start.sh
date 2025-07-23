#!/bin/bash

# This script starts the FastAPI application with proper PORT handling
# It can be used for local testing before Railway deployment

# Set default port if not provided
PORT=${PORT:-8000}

# Start the application
echo "Starting application on port $PORT..."
uvicorn main:app --host 0.0.0.0 --port $PORT