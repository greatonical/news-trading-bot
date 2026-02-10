# Cross-Platform MT5 Support

## Overview

The News Trading Bot now supports **both macOS and Windows/Linux** with automatic platform detection!

### How It Works

The bot automatically detects your operating system and uses the appropriate MT5 library:

| Platform    | MT5 Library          | Connection Method          |
| ----------- | -------------------- | -------------------------- |
| **macOS**   | `siliconmetatrader5` | Bridge (localhost:8001)    |
| **Windows** | `MetaTrader5`        | Direct terminal connection |
| **Linux**   | `MetaTrader5`        | Direct terminal connection |

### DEVICE Configuration

In `config/settings.py`:

```python
import platform

_system = platform.system()
if _system == "Darwin":
    DEVICE = "mac"
elif _system == "Windows":
    DEVICE = "windows"
else:
    # Linux and others use official MT5 library
    DEVICE = "windows"
```

The `DEVICE` config is automatically set based on `platform.system()`:

- `Darwin` → `"mac"`
- `Windows` → `"windows"`
- `Linux` → `"windows"`

## Installation

### Install Both Libraries

```bash
# Install both MT5 libraries
pip install -r requirements.txt
```

The `requirements.txt` now includes **both** libraries:

```
siliconmetatrader5>=0.1.0  # For macOS
MetaTrader5>=5.0.45        # For Windows/Linux
```

The code will automatically use the correct one based on your OS!

## Usage

### macOS

```python
from src.market.data import MT5DataHandler

# Automatically uses siliconmetatrader5
handler = MT5DataHandler()

# Connects via bridge on localhost:8001
handler.connect()
```

**Requirements:**

- MT5 bridge running on `localhost:8001`
- MT5 terminal open and logged in
- See `docs/MT5_SETUP.md` for bridge setup

### Windows/Linux

```python
from src.market.data import MT5DataHandler

# Automatically uses MetaTrader5
handler = MT5DataHandler()

# Option 1: Connect to already-logged-in terminal
handler.connect()

# Option 2: Login programmatically
handler.connect(
    login=12345678,
    password="your_password",
    server="YourBroker-Demo"
)
```

**Requirements:**

- MT5 terminal running
- Either already logged in OR provide credentials

## Code Changes

### 1. `config/settings.py`

Added automatic device detection:

```python
import platform

# Auto-detect OS
_system = platform.system()
if _system == "Darwin":
    DEVICE = "mac"
elif _system == "Windows":
    DEVICE = "windows"
else:
    DEVICE = "windows"  # Linux uses official MT5

# MT5 Bridge settings (macOS only)
MT5_BRIDGE_HOST = "localhost"
MT5_BRIDGE_PORT = 8001
```

### 2. `src/market/data.py`

Complete rewrite with cross-platform support:

```python
from config.settings import DEVICE, MT5_BRIDGE_HOST, MT5_BRIDGE_PORT

# Import appropriate library
if DEVICE == "mac":
    from siliconmetatrader5 import MetaTrader5
    MT5_TYPE = "siliconmetatrader5"
elif DEVICE == "windows":
    import MetaTrader5 as mt5
    MT5_TYPE = "MetaTrader5"

class MT5DataHandler:
    def connect(self, login=None, password=None, server=None):
        if DEVICE == "mac":
            return self._connect_mac()
        elif DEVICE == "windows":
            return self._connect_windows(login, password, server)

    def _connect_mac(self):
        # Bridge connection
        self.mt5 = MetaTrader5(host=self.host, port=self.port)
        # ...

    def _connect_windows(self, login, password, server):
        # Direct connection
        mt5.initialize()
        if login and password and server:
            mt5.login(login, password, server)
        # ...
```

### 3. `requirements.txt`

Now includes both libraries:

```
# MT5 INTEGRATION - Cross-Platform Support
# Install BOTH libraries - code selects the right one

siliconmetatrader5>=0.1.0  # macOS
MetaTrader5>=5.0.45        # Windows/Linux
```

### 4. `test_mt5_connection.py`

Updated to test cross-platform:

```python
from config.settings import DEVICE

print(f"MT5 Connection Test ({DEVICE.upper()})")

if DEVICE == "mac":
    print("Using: siliconmetatrader5")
elif DEVICE == "windows":
    print("Using: MetaTrader5")
```

## Testing

### Test Your Platform

```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Run cross-platform test
python3 test_mt5_connection.py
```

**Expected Output:**

```
============================================================
MT5 Connection Test (MAC)  # or (WINDOWS)
============================================================

[1/5] Device Detection...
✓ Detected OS: mac

[2/5] Checking MT5 library installation...
✓ siliconmetatrader5 library found

[3/5] Importing MT5 data handler...
✓ MT5DataHandler imported successfully

[4/5] Attempting to connect to MT5...
✓ MT5 connection successful

[5/5] Retrieving account information...
✓ Account info retrieved

============================================================
MT5 Account Details
============================================================
Account Number: 12345678
Server: YourBroker-Demo
Balance: $10,000.00
...
```

## Benefits

### ✅ Automatic Platform Detection

- No manual configuration needed
- Works on macOS, Windows, and Linux

### ✅ Single Codebase

- Same code works on all platforms
- No platform-specific branches

### ✅ Easy Installation

- Install both libraries
- Code uses the right one automatically

### ✅ Seamless Development

- Develop on macOS
- Deploy on Windows server
- Or vice versa!

## Platform-Specific Notes

### macOS

**Connection Method:** Bridge

- Requires MT5 bridge on `localhost:8001`
- See `docs/MT5_SETUP.md` for setup

**Library:** `siliconmetatrader5`

- GitHub: https://github.com/bahadirumutiscimen/silicon-metatrader5

**Credentials:** Not supported in code

- Login manually in MT5 terminal
- Bridge connects to logged-in terminal

### Windows/Linux

**Connection Method:** Direct

- Connects directly to MT5 terminal
- No bridge required

**Library:** `MetaTrader5` (official)

- Docs: https://www.mql5.com/en/docs/python_metatrader5

**Credentials:** Optional

- Can login programmatically
- Or use already-logged-in terminal

## Troubleshooting

### "Unknown device type"

- Check `platform.system()` output
- Manually set `DEVICE` in `config/settings.py` if needed

### macOS: "Bridge connection failed"

```bash
# Make sure bridge is running
# Check localhost:8001 is accessible
```

### Windows: "MT5 initialization failed"

```bash
# Make sure MT5 terminal is running
# Try logging in manually first
```

### "Wrong MT5 library for platform"

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

## Migration Guide

### From macOS-Only Version

No changes needed! The code now works on all platforms.

### From Windows-Only Version

No changes needed! Just install `siliconmetatrader5`:

```bash
pip install siliconmetatrader5
```

## Summary

The bot is now **fully cross-platform**:

✅ Auto-detects your OS
✅ Uses appropriate MT5 library
✅ Single codebase for all platforms
✅ Easy installation and testing
✅ Seamless development workflow

**Just install both libraries and the code handles the rest!**
