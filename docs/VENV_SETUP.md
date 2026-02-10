# Virtual Environment Setup & Installation Guide

## Step 1: Create Virtual Environment

```bash
# Navigate to project directory
cd /Users/admin/Documents/Projects/BotsProjects/news-trading-bot

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
```

## Step 2: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install siliconmetatrader5 (correct package name!)
pip install siliconmetatrader5

# Install other dependencies
pip install -r requirements.txt
```

## Step 3: Verify Installation

```bash
# Check siliconmetatrader5 is installed
pip list | grep siliconmetatrader5

# Should show:
# siliconmetatrader5    x.x.x
```

## Step 4: Setup MT5 Bridge (macOS)

The `siliconmetatrader5` library works differently than the Windows MT5 library:

1. **It requires a bridge server** running on `localhost:8001`
2. **You need to run MT5 through Wine or a Windows VM**
3. **The bridge connects Python to MT5**

### Option A: Use Wine (Recommended for macOS)

```bash
# Install Wine via Homebrew
brew install --cask wine-stable

# Download MT5 installer
# Run MT5 through Wine
wine mt5setup.exe
```

### Option B: Use Windows VM

1. Install Parallels/VMware
2. Install Windows
3. Install MT5 in Windows
4. Connect from macOS Python to Windows MT5

## Step 5: Test Connection

```bash
# Make sure MT5 bridge is running on localhost:8001
python test_mt5_connection.py
```

## Deactivate Virtual Environment

```bash
# When done working
deactivate
```

## Quick Commands Reference

```bash
# Activate venv
source venv/bin/activate

# Install package
pip install package-name

# List installed packages
pip list

# Deactivate venv
deactivate

# Remove venv (if needed)
rm -rf venv
```

## Troubleshooting

### "command not found: pip"

```bash
# Use pip3 instead
pip3 install siliconmetatrader5

# Or use python3 -m pip
python3 -m pip install siliconmetatrader5
```

### "command not found: python"

```bash
# Use python3 instead
python3 test_mt5_connection.py
```

### Virtual environment not activating

```bash
# Make sure you're in the project directory
cd /Users/admin/Documents/Projects/BotsProjects/news-trading-bot

# Try with full path
source ./venv/bin/activate
```

## Next Steps

After setup:

1. ✅ Virtual environment created and activated
2. ✅ `siliconmetatrader5` installed
3. ✅ MT5 bridge running (localhost:8001)
4. ✅ Test connection successful
5. ✅ Ready to run bot!
