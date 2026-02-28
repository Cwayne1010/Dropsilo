# ClickUp MCP Server - Installation Notes

## Python Version Requirement

⚠️ **IMPORTANT**: MCP SDK requires **Python 3.10 or higher**

Your current system has: **Python 3.9.6**

## Installation Options

### Option 1: Upgrade Python (Recommended)

Install Python 3.10+ using one of these methods:

**Using Homebrew (macOS)**:
```bash
brew install python@3.11
# Then use python3.11 instead of python3
```

**Using pyenv**:
```bash
brew install pyenv
pyenv install 3.11
pyenv global 3.11
```

**Download from python.org**:
Visit https://www.python.org/downloads/ and install Python 3.11+

### Option 2: Use Virtual Environment with Python 3.10+

If you have Python 3.10+ installed alongside 3.9:

```bash
# Find Python 3.10+
which python3.10 || which python3.11 || which python3.12

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install mcp httpx python-dotenv
```

## Once Python 3.10+ is Available

Run the setup script:

```bash
cd execution/clickup_mcp
./setup.sh
```

Or install manually:

```bash
pip install mcp httpx python-dotenv
```

## Verify Installation

```bash
python3 --version  # Should show 3.10+
python3 -c "import mcp; print(mcp.__version__)"  # Should print version number
```

## Next Steps

Once Python 3.10+ is installed:

1. Follow [CLICKUP_QUICKSTART.md](../../CLICKUP_QUICKSTART.md)
2. Get your ClickUp API key
3. Configure Claude Desktop
4. Start using the MCP server!

## Current Status

✅ MCP Server code complete and ready to use
✅ Directive and documentation created
✅ Setup scripts prepared
⚠️ Waiting for Python 3.10+ to install dependencies

## Alternative: Use Without Local Installation

If you can't upgrade Python locally, you can:

1. **Deploy to Modal**: Run the MCP server in Modal's cloud environment
2. **Use Docker**: Package the MCP server in a Docker container with Python 3.11
3. **Remote Server**: Install on a remote server with Python 3.10+

Would you like help with any of these alternatives?
