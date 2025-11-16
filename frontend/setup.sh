#!/bin/bash

# Setup script for frontend

echo "=================================="
echo "🚀 Setting up Frontend"
echo "=================================="

# Check Node.js version
echo "📦 Checking Node.js version..."
node_version=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$node_version" -lt 18 ]; then
    echo "❌ Error: Node.js version must be >= 18.0.0"
    echo "Current version: $(node -v)"
    exit 1
fi
echo "✅ Node.js version: $(node -v)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ Setup completed successfully!"
    echo "=================================="
    echo ""
    echo "📝 Next steps:"
    echo "  1. Make sure backend is running on http://localhost:8000"
    echo "  2. Run 'npm run dev' to start development server"
    echo "  3. Open http://localhost:3000 in your browser"
    echo ""
else
    echo ""
    echo "❌ Installation failed. Please check the errors above."
    exit 1
fi

