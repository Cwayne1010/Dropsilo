#!/bin/bash
# ClickUp MCP Server Setup Script

set -e

echo "🚀 Setting up ClickUp MCP Server..."

# Check for Python 3.11
if command -v python3.11 &> /dev/null; then
    PYTHON=python3.11
    PIP=pip3.11
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ $(echo "$PYTHON_VERSION >= 3.10" | bc -l) -eq 1 ]]; then
        PYTHON=python3
        PIP=pip3
    else
        echo "❌ Python 3.10+ is required. Found Python $PYTHON_VERSION"
        echo "Install Python 3.11: brew install python@3.11"
        exit 1
    fi
else
    echo "❌ Python 3 is required but not found"
    exit 1
fi

echo "✓ Found $($PYTHON --version)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
$PYTHON -m pip install mcp httpx python-dotenv --quiet

echo "✓ Dependencies installed"

# Check for .env file
echo ""
if [ ! -f "../../.env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp ../../.env.template ../../.env
    echo "⚠️  Please edit .env and add your CLICKUP_API_KEY"
else
    echo "✓ .env file exists"
fi

# Check for ClickUp API key
if ! grep -q "CLICKUP_API_KEY=pk_" ../../.env 2>/dev/null; then
    echo ""
    echo "⚠️  CLICKUP_API_KEY not configured in .env"
    echo ""
    echo "To get your API key:"
    echo "1. Go to ClickUp → Settings → Apps"
    echo "2. Generate an API token"
    echo "3. Add to .env: CLICKUP_API_KEY=pk_YOUR_KEY_HERE"
fi

# Provide next steps
echo ""
echo "✅ MCP Server setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your ClickUp API key to .env"
echo "2. Configure Claude Desktop (see README.md)"
echo "3. Restart Claude Desktop"
echo ""
echo "Configuration file location:"
echo "macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "Windows: %APPDATA%\\Claude\\claude_desktop_config.json"
echo ""
echo "Add this to mcpServers section:"
echo '{'
echo '  "clickup": {'
echo '    "command": "python",'
echo '    "args": ["'$(pwd)'/server.py"],'
echo '    "env": {'
echo '      "CLICKUP_API_KEY": "pk_your_key_here",'
echo '      "CLICKUP_WORKSPACE_NAME": "Rhizome"'
echo '    }'
echo '  }'
echo '}'
echo ""
