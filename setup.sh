#!/bin/bash

set -e

echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

echo "📦 Activating virtualenv and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "⚠️  Warning: No requirements.txt file found."
fi

echo "✅ Environment setup complete."
