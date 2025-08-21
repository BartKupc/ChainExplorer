#!/bin/bash

# Crono Explorer Restart Script
# This script stops and then starts all Crono Explorer services

echo "🔄 Restarting Crono Explorer..."


# Clean database first for a fresh start
echo "🧹 Cleaning database for fresh start..."
./clean_db.sh

echo "🧹 Stopping services..."
./stop.sh

# Start services
echo "🚀 Starting services..."
python app.py -port