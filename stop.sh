#!/bin/bash

# Crono Explorer Stop Script
# This script stops all Crono Explorer services

echo "🛑 Stopping Crono Explorer..."

# Stop Flask application on port 5001
# echo "   Stopping Flask application on port 5001..."
# pkill -f "python.*app.py" 2>/dev/null
# pkill -f "flask" 2>/dev/null

# Force kill any process on port 5001
PORT=5001
PID=$(lsof -ti:$PORT 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "   Force killing process on port $PORT (PID: $PID)"
    kill -9 $PID 2>/dev/null
fi

# Wait a moment for processes to stop
sleep 3

# Check if processes are still running on port 5001
FLASK_RUNNING=$(lsof -ti:$PORT 2>/dev/null | wc -l)

if [ $FLASK_RUNNING -eq 0 ]; then
    echo "✅ Crono Explorer stopped successfully on port $PORT"
else
    echo "⚠️  Some processes may still be running on port $PORT:"
    if [ $FLASK_RUNNING -gt 0 ]; then
        echo "   - Flask app: $FLASK_RUNNING process(es)"
        echo "   PIDs: $(lsof -ti:$PORT)"
    fi
    echo "   You can force kill with: lsof -ti:$PORT | xargs kill -9"
fi

echo ""
echo "�� Port Status:"
echo "   Port $PORT (Flask): $(netstat -tlnp 2>/dev/null | grep :$PORT | wc -l | tr -d ' ') listener(s)"