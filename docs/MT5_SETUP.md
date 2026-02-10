# MT5 Configuration Guide

## Installation

### For macOS (Your System)

```bash
# Install unofficial MT5 fork for macOS
pip install silicon-metatrader5
```

### For Windows/Linux

```bash
# Install official MT5 library
pip install MetaTrader5
```

## MT5 Terminal Setup

1. **Download and Install MT5**:

   - macOS: Download from your broker or use Wine/CrossOver
   - Windows: Download from MetaQuotes or your broker

2. **Login to MT5 Terminal**:

   - Open MT5 application
   - File → Login to Trade Account
   - Enter your credentials:
     - Login (account number)
     - Password
     - Server (e.g., "ICMarkets-Demo", "OANDA-v20 Live")

3. **Keep MT5 Running**:
   - The bot connects to the already-logged-in MT5 terminal
   - MT5 must remain open while the bot is running

## Configuration Methods

### Method 1: Use Already Logged-In Terminal (Recommended)

The bot will automatically connect to your already-logged-in MT5 terminal:

```bash
# Just run the bot - no credentials needed
python main.py --mode dev
```

This is the **safest and easiest** method.

### Method 2: Programmatic Login (Optional)

Create a `.env` file in the project root:

```bash
# .env file
MT5_LOGIN=12345678
MT5_PASSWORD=your_password_here
MT5_SERVER=YourBroker-Demo
```

Then the bot can login programmatically (see updated `main.py`).

## Broker Server Names

Common broker server formats:

- **Demo Accounts**:

  - `ICMarkets-Demo`
  - `OANDA-v20 Demo`
  - `FXCM-Demo`
  - `Pepperstone-Demo`

- **Live Accounts**:
  - `ICMarkets-Live01`
  - `OANDA-v20 Live`
  - `FXCM-USDDemo01`

**How to Find Your Server**:

1. Open MT5 terminal
2. Tools → Options → Server tab
3. Your server name is displayed there

## Testing MT5 Connection

```bash
# Test MT5 connection
python -c "
try:
    import MetaTrader5 as mt5
    if mt5.initialize():
        account = mt5.account_info()
        print(f'✓ Connected: Account {account.login}')
        print(f'  Balance: ${account.balance:.2f}')
        print(f'  Server: {account.server}')
        mt5.shutdown()
    else:
        print('✗ MT5 initialization failed')
        print('  Make sure MT5 terminal is running and logged in')
except ImportError:
    print('✗ MT5 library not installed')
    print('  Run: pip install silicon-metatrader5  # for macOS')
    print('  Or:  pip install MetaTrader5          # for Windows/Linux')
"
```

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use demo account** for testing
3. **Start with paper trading** (`--mode dev`)
4. **Verify all settings** before live trading

## Troubleshooting

### "MT5 library not available"

- Install the correct library for your OS
- macOS: `pip install silicon-metatrader5`
- Windows/Linux: `pip install MetaTrader5`

### "MT5 initialization failed"

- Ensure MT5 terminal is running
- Ensure you're logged in to an account
- Try restarting MT5 terminal

### "Failed to connect to MT5"

- Check MT5 terminal is not frozen
- Verify account is active
- Check internet connection

### Symbol not found (e.g., "EURUSD")

- Different brokers use different symbol names
- Update `config/instruments.py` with your broker's symbols
- Common variations:
  - `EURUSD` vs `EUR/USD` vs `EURUSD.a`
  - Check Tools → Symbols in MT5 terminal

## Example: Complete Setup

```bash
# 1. Install MT5 library (macOS)
pip install silicon-metatrader5

# 2. Install other dependencies
pip install -r requirements.txt

# 3. Open MT5 terminal and login
# (Use your broker's credentials)

# 4. Test connection
python src/market/data.py

# 5. Run bot in dev mode
python main.py --mode dev

# 6. (Optional) For programmatic login, create .env:
echo "MT5_LOGIN=your_account_number" > .env
echo "MT5_PASSWORD=your_password" >> .env
echo "MT5_SERVER=YourBroker-Demo" >> .env
```

## Next Steps

1. ✅ Install `silicon-metatrader5`
2. ✅ Open and login to MT5 terminal
3. ✅ Test connection with test script above
4. ✅ Run bot in dev mode
5. ✅ Monitor logs for any issues
