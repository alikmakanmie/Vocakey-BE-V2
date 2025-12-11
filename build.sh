#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 Creating directories..."
mkdir -p songs/original
mkdir -p songs/transposed

echo "✅ Build complete!"
