# macOS Setup - Quick Reference

## ✅ Corrected Setup (siliconmetatrader5)

### 1. Run Automated Setup

```bash
cd /Users/admin/Documents/Projects/BotsProjects/news-trading-bot

# Run setup script (creates venv + installs everything)
./setup.sh
```

### 2. Manual Setup (Alternative)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Activate venv first
source venv/bin/activate

# Test MT5 connection
python3 test_mt5_connection.py
```

---

## 🔧 Key Differences from Windows Version

| Aspect         | Windows                              | macOS (siliconmetatrader5)                       |
| -------------- | ------------------------------------ | ------------------------------------------------ |
| **Package**    | `MetaTrader5`                        | `siliconmetatrader5`                             |
| **Connection** | Direct terminal                      | Bridge (localhost:8001)                          |
| **Import**     | `import MetaTrader5 as mt5`          | `from siliconmetatrader5 import MetaTrader5`     |
| **Initialize** | `mt5.initialize()`                   | `mt5 = MetaTrader5(host="localhost", port=8001)` |
| **Login**      | `mt5.login(login, password, server)` | Not supported (use bridge)                       |

---

## 📝 Updated Code Example

```python
# macOS version (siliconmetatrader5)
from siliconmetatrader5 import MetaTrader5

# Connect via bridge
mt5 = MetaTrader5(host="localhost", port=8001)

# Fetch data
rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M15, 0, 100)

# Get account info
account = mt5.account_info()
print(f"Balance: ${account.balance:.2f}")

# Close when done
mt5.shutdown()
```

---

## 🚀 Quick Start Commands

```bash
# 1. Setup (one-time)
./setup.sh

# 2. Activate venv (every session)
source venv/bin/activate

# 3. Test connection
python3 test_mt5_connection.py

# 4. Run bot (dev mode)
python3 main.py --mode dev

# 5. Deactivate when done
deactivate
```

---

## ⚠️ Important Notes

1. **MT5 Bridge Required**:

   - `siliconmetatrader5` requires a bridge server on `localhost:8001`
   - See: https://github.com/bahadirumutiscimen/silicon-metatrader5

2. **No Direct Login**:

   - Cannot use `login(user, password, server)`
   - Must connect via bridge to already-logged-in MT5

3. **Virtual Environment**:

   - Always activate: `source venv/bin/activate`
   - Prompt shows `(venv)` when active

4. **Python Command**:
   - Use `python3` not `python`
   - Use `pip` (not `pip3`) when venv is active

---

## 🐛 Troubleshooting

### "command not found: pip"

```bash
# Use python3 -m pip instead
python3 -m pip install siliconmetatrader5
```

### "ModuleNotFoundError: No module named 'siliconmetatrader5'"

```bash
# Make sure venv is activated
source venv/bin/activate

# Then install
pip install siliconmetatrader5
```

### "Connection refused" or "Bridge not running"

```bash
# MT5 bridge must be running on localhost:8001
# See docs/MT5_SETUP.md for bridge setup
```

---

## 📚 Documentation Files

- `docs/VENV_SETUP.md` - Virtual environment guide
- `docs/MT5_SETUP.md` - MT5 bridge setup
- `QUICKSTART.md` - General quick start
- `README.md` - Full documentation

---

## ✅ Files Updated for macOS

1. ✅ `src/market/data.py` - Uses `siliconmetatrader5` API
2. ✅ `test_mt5_connection.py` - Tests bridge connection
3. ✅ `requirements.txt` - Correct package name
4. ✅ `setup.sh` - Automated setup script
5. ✅ `docs/VENV_SETUP.md` - Virtual environment guide

---

**You're all set!** Run `./setup.sh` to get started.
