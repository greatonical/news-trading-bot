#!/usr/bin/env python3
"""
Quick MT5 connection test - Cross-Platform

This script tests MT5 connection for both macOS and Windows/Linux.
Auto-detects your OS and uses the appropriate library.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import DEVICE

print("=" * 60)
print(f"MT5 Connection Test ({DEVICE.upper()})")
print("=" * 60)

# Test 1: Check device detection
print(f"\n[1/5] Device Detection...")
print(f"✓ Detected OS: {DEVICE}")

if DEVICE == "mac":
    print("  Using: siliconmetatrader5 (bridge connection)")
elif DEVICE == "windows":
    print("  Using: MetaTrader5 (direct connection)")
else:
    print(f"  ✗ Unknown device: {DEVICE}")
    sys.exit(1)

# Test 2: Check if MT5 library is installed
print(f"\n[2/5] Checking MT5 library installation...")

if DEVICE == "mac":
    try:
        from siliconmetatrader5 import MetaTrader5
        print("✓ siliconmetatrader5 library found")
    except ImportError:
        print("✗ siliconmetatrader5 library NOT found")
        print("\nInstall with:")
        print("  pip install siliconmetatrader5")
        sys.exit(1)

elif DEVICE == "windows":
    try:
        import MetaTrader5 as mt5
        print("✓ MetaTrader5 library found")
    except ImportError:
        print("✗ MetaTrader5 library NOT found")
        print("\nInstall with:")
        print("  pip install MetaTrader5")
        sys.exit(1)

# Test 3: Import MT5 data handler
print(f"\n[3/5] Importing MT5 data handler...")
try:
    from src.market.data import MT5DataHandler
    print("✓ MT5DataHandler imported successfully")
except Exception as e:
    print(f"✗ Failed to import MT5DataHandler: {e}")
    sys.exit(1)

# Test 4: Try to connect to MT5
print(f"\n[4/5] Attempting to connect to MT5...")

try:
    handler = MT5DataHandler()
    
    if handler.connect():
        print("✓ MT5 connection successful")
    else:
        print("✗ MT5 connection failed")
        if DEVICE == "mac":
            print("\nPossible reasons:")
            print("  1. MT5 bridge is not running on localhost:8001")
            print("  2. MT5 terminal is not open")
            print("  3. MT5 terminal is not logged in")
            print("\nSolution:")
            print("  See docs/MT5_SETUP.md for bridge setup instructions")
        elif DEVICE == "windows":
            print("\nPossible reasons:")
            print("  1. MT5 terminal is not running")
            print("  2. MT5 terminal is not logged in")
            print("\nSolution:")
            print("  1. Open MT5 terminal")
            print("  2. Login to your account")
            print("  3. Run this test again")
        sys.exit(1)

except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Test 5: Get account info
print(f"\n[5/5] Retrieving account information...")

try:
    account = handler.get_account_info()
    
    if account is None:
        print("✗ Failed to get account info")
        print("Make sure MT5 is logged in to an account")
        handler.disconnect()
        sys.exit(1)
    
    print("✓ Account info retrieved")
    print("\n" + "=" * 60)
    print("MT5 Account Details")
    print("=" * 60)
    print(f"Account Number: {account['login']}")
    print(f"Server: {account['server']}")
    print(f"Balance: ${account['balance']:,.2f}")
    print(f"Equity: ${account['equity']:,.2f}")
    print(f"Currency: {account['currency']}")
    print(f"Margin Free: ${account['free_margin']:,.2f}")

except Exception as e:
    print(f"✗ Error: {e}")
    handler.disconnect()
    sys.exit(1)

# Test 6: Check available symbols
print("\n" + "=" * 60)
print("Checking Symbol Availability")
print("=" * 60)

test_symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
available = []
unavailable = []

for symbol in test_symbols:
    try:
        price = handler.get_current_price(symbol)
        if price is not None:
            available.append(symbol)
            print(f"✓ {symbol} - Available (Bid: {price['bid']:.5f})")
        else:
            unavailable.append(symbol)
            print(f"✗ {symbol} - Not available")
    except Exception as e:
        unavailable.append(symbol)
        print(f"✗ {symbol} - Error: {e}")

if unavailable:
    print(f"\nNote: {len(unavailable)} symbols not available")
    print("You may need to update config/instruments.py with your broker's symbol names")

# Test 7: Fetch sample data
print("\n" + "=" * 60)
print("Fetching Sample Data (EURUSD M1)")
print("=" * 60)

try:
    candles = handler.get_historical_candles("EURUSD", timeframe="1min", count=10)
    if candles is not None and len(candles) > 0:
        print(f"✓ Retrieved {len(candles)} candles")
        print(f"Latest close: {candles[-1]['close']:.5f}")
        print(f"Latest time: {candles[-1]['time']}")
    else:
        print("✗ Failed to retrieve candles")
except Exception as e:
    print(f"✗ Error fetching data: {e}")

# Cleanup
handler.disconnect()

print("\n" + "=" * 60)
print("✅ MT5 Connection Test PASSED")
print("=" * 60)
print(f"\nYour {DEVICE.upper()} system is ready to run the trading bot!")
print("\nNext steps:")
print("  1. Review config files in config/ directory")
print("  2. Run bot in dev mode: python3 main.py --mode dev")
print("  3. Monitor logs in logs/ directory")

if DEVICE == "mac":
    print("\nIMPORTANT (macOS):")
    print("  - Keep MT5 bridge running on localhost:8001")
    print("  - Keep MT5 terminal open and logged in")
elif DEVICE == "windows":
    print("\nIMPORTANT (Windows):")
    print("  - Keep MT5 terminal open and logged in")
