#!/bin/bash
# Startup script for the PharmaQuery backend server

echo "Starting PharmaQuery Backend Server..."
echo "Make sure you have:"
echo "1. Installed dependencies: pip install -r requirements.txt"
echo "2. Configured Firebase in .env file"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Using default configuration."
    echo "Create .env file from .env.example for production use."
fi

# Run the server
python main.py




