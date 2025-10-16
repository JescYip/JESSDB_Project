#!/bin/bash

echo "🚀 Starting Coffee Ordering System..."
echo "=================================="

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not installed, please install Python3 first"
    exit 1
fi

# Check dependencies
echo "📦 Checking dependencies..."
python3 -c "import flask, flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing dependencies..."
    pip3 install flask flask-cors
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from database import DatabaseManager; DatabaseManager()"

echo "✅ System ready!"
echo ""
echo "🌐 Starting web server..."
echo "📱 Client access: http://localhost:5050"
echo "🔧 Admin dashboard: http://localhost:5050/admin"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

# Start Flask application
python3 app.py
