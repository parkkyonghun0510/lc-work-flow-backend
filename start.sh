#!/bin/bash

# This script starts the FastAPI application with proper PORT handling
# It can be used for local testing before Railway deployment

# Start the application
echo "Starting application on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000
