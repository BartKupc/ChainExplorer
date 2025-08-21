#!/bin/bash

# Database Cleaner Script
# This script deletes the database file for a fresh start

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"
echo "SCRIPT_DIR"

echo "🗑️  Deleting database for fresh start..."

# Delete the database file if it exists (check both locations)
if [ -f "chains.db" ]; then
    rm -f chains.db
    echo "✅ Database file deleted from root directory"
elif [ -f "instance/chains.db" ]; then
    rm -f instance/chains.db
    echo "✅ Database file deleted from instance directory"
else
    echo "ℹ️  Database file not found (already clean)"
fi

echo "✅ Database cleaner completed!" 