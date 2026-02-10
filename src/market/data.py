"""
MT5 data handler for News Trading Bot V1.0 - Cross-Platform

Reference: /docs/quantitative_thresholds.md Section 15
Last Updated: 2025-12-31

Purpose: Real-time price data, historical candles, account info from MetaTrader 5

Cross-Platform Support:
- macOS: Uses siliconmetatrader5 (requires bridge on localhost:8001)
- Windows/Linux: Uses MetaTrader5 (official library, direct connection)
- Auto-detection via DEVICE config in settings.py
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import sys
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.logging.trade_logger import get_logger
from config.settings import DEVICE, MT5_BRIDGE_HOST, MT5_BRIDGE_PORT

# Import appropriate MT5 library based on device
MT5_AVAILABLE = False
MT5_TYPE = None

if DEVICE == "mac":
    # macOS: Use siliconmetatrader5
    try:
        from siliconmetatrader5 import MetaTrader5
        MT5_AVAILABLE = True
        MT5_TYPE = "siliconmetatrader5"
    except ImportError:
        print("WARNING: siliconmetatrader5 library not available for macOS")
        print("Install with: pip install siliconmetatrader5")
        print("See docs/MT5_SETUP.md for macOS setup instructions")

elif DEVICE == "windows":
    # Windows/Linux: Use official MetaTrader5
    try:
        import MetaTrader5 as mt5
        MT5_AVAILABLE = True
        MT5_TYPE = "MetaTrader5"
    except ImportError:
        print("WARNING: MetaTrader5 library not available")
        print("Install with: pip install MetaTrader5")

else:
    print(f"WARNING: Unknown DEVICE type: {DEVICE}")


class MT5DataHandler:
    """
    MetaTrader 5 data handler - Cross-Platform
    
    Reference: quantitative_thresholds.md Section 15
    
    Features:
    - Auto-detects OS and uses appropriate MT5 library
    - macOS: Bridge connection (localhost:8001)
    - Windows/Linux: Direct terminal connection
    - Historical candle retrieval (60 × 1-min)
    - Real-time price polling
    - Spread monitoring
    - Position reconciliation
    - Account information
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        timeout_seconds: int = 10,
        max_reconnection_attempts: int = 3,
        reconnection_delay_seconds: int = 5,
    ):
        """
        Initialize MT5 data handler
        
        Args:
            host: MT5 bridge host (macOS only, default from config)
            port: MT5 bridge port (macOS only, default from config)
            timeout_seconds: Timeout for MT5 operations
            max_reconnection_attempts: Max reconnection attempts
            reconnection_delay_seconds: Delay between reconnection attempts
        """
        self.device = DEVICE
        self.mt5_type = MT5_TYPE
        
        # macOS bridge settings
        self.host = host or MT5_BRIDGE_HOST
        self.port = port or MT5_BRIDGE_PORT
        
        self.timeout_seconds = timeout_seconds
        self.max_reconnection_attempts = max_reconnection_attempts
        self.reconnection_delay_seconds = reconnection_delay_seconds
        
        self.logger = get_logger()
        self.connected = False
        self.mt5 = None
        
        if not MT5_AVAILABLE:
            self.logger.error(f"MT5 library not available for device: {DEVICE}")
        else:
            self.logger.info(f"MT5 handler initialized for {DEVICE} using {MT5_TYPE}")
    
    def connect(
        self,
        login: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
    ) -> bool:
        """
        Connect to MT5
        
        Args:
            login: MT5 account login (Windows only, optional if already logged in)
            password: MT5 account password (Windows only)
            server: MT5 server name (Windows only)
        
        Returns:
            True if connected, False otherwise
        
        Reference:
            quantitative_thresholds.md Section 15
        
        Note:
            - macOS: Connects via bridge, ignores login credentials
            - Windows: Can login programmatically or use already-logged-in terminal
        """
        if not MT5_AVAILABLE:
            self.logger.error(f"Cannot connect: MT5 library not available for {DEVICE}")
            return False
        
        try:
            if DEVICE == "mac":
                return self._connect_mac()
            elif DEVICE == "windows":
                return self._connect_windows(login, password, server)
            else:
                self.logger.error(f"Unknown device type: {DEVICE}")
                return False
        
        except Exception as e:
            self.logger.error(f"MT5 connection error: {e}")
            return False
    
    def _connect_mac(self) -> bool:
        """Connect to MT5 via bridge (macOS)"""
        self.logger.info(f"Connecting to MT5 bridge at {self.host}:{self.port}...")
        
        # Connect to MT5 bridge
        self.mt5 = MetaTrader5(host=self.host, port=self.port)
        
        # Test connection by getting account info
        account_info = self.mt5.account_info()
        if account_info is None:
            self.logger.error("MT5 bridge connection failed")
            self.logger.error(f"Make sure MT5 bridge is running on {self.host}:{self.port}")
            return False
        
        self.connected = True
        self.logger.info(f"MT5 connected via bridge ({self.host}:{self.port})")
        
        # Log account info
        self.logger.info(
            f"Account: {account_info.login} | "
            f"Balance: ${account_info.balance:.2f} | "
            f"Server: {account_info.server}"
        )
        
        return True
    
    def _connect_windows(
        self,
        login: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
    ) -> bool:
        """Connect to MT5 terminal (Windows/Linux)"""
        self.logger.info("Connecting to MT5 terminal...")
        
        # Initialize MT5
        if not mt5.initialize():
            error = mt5.last_error()
            self.logger.error(f"MT5 initialization failed: {error}")
            return False
        
        # Login if credentials provided
        if login and password and server:
            self.logger.info(f"Logging in to MT5 account {login}...")
            if not mt5.login(login, password, server):
                error = mt5.last_error()
                self.logger.error(f"MT5 login failed: {error}")
                mt5.shutdown()
                return False
        
        self.connected = True
        self.mt5 = mt5  # Store reference for consistency
        self.logger.info("MT5 connected successfully")
        
        # Log account info
        account_info = mt5.account_info()
        if account_info:
            self.logger.info(
                f"Account: {account_info.login} | "
                f"Balance: ${account_info.balance:.2f} | "
                f"Server: {account_info.server}"
            )
        
        return True
    
    def disconnect(self) -> None:
        """Disconnect from MT5"""
        if MT5_AVAILABLE and self.connected:
            if DEVICE == "mac":
                if self.mt5:
                    self.mt5.shutdown()
            elif DEVICE == "windows":
                mt5.shutdown()
            
            self.connected = False
            self.mt5 = None
            self.logger.info("MT5 disconnected")
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to MT5
        
        Returns:
            True if reconnected, False otherwise
        """
        self.logger.warning("Attempting MT5 reconnection...")
        
        for attempt in range(1, self.max_reconnection_attempts + 1):
            self.logger.info(f"Reconnection attempt {attempt}/{self.max_reconnection_attempts}")
            
            # Disconnect first
            self.disconnect()
            time.sleep(self.reconnection_delay_seconds)
            
            # Try to reconnect
            if self.connect():
                self.logger.info("MT5 reconnection successful")
                return True
        
        self.logger.error("MT5 reconnection failed after all attempts")
        return False
    
    def verify_connection(self) -> bool:
        """
        Verify MT5 connection is active
        
        Returns:
            True if connected and responsive, False otherwise
        """
        if not MT5_AVAILABLE or not self.connected:
            return False
        
        try:
            # Test connection by getting terminal info
            if DEVICE == "mac":
                terminal_info = self.mt5.terminal_info()
            elif DEVICE == "windows":
                terminal_info = mt5.terminal_info()
            else:
                return False
            
            return terminal_info is not None
        
        except Exception as e:
            self.logger.error(f"MT5 connection verification failed: {e}")
            return False
    
    def get_historical_candles(
        self,
        symbol: str,
        timeframe: str = "1min",
        count: int = 60,
    ) -> Optional[List[Dict]]:
        """
        Get historical OHLC candles
        
        Args:
            symbol: Symbol name (broker-specific)
            timeframe: Timeframe (default: 1min)
            count: Number of candles (default: 60)
        
        Returns:
            List of candle dictionaries or None if failed
        """
        if not self.verify_connection():
            self.logger.error("MT5 not connected")
            return None
        
        try:
            # Map timeframe string to MT5 constant
            if DEVICE == "mac":
                timeframe_map = {
                    "1min": self.mt5.TIMEFRAME_M1,
                    "5min": self.mt5.TIMEFRAME_M5,
                    "15min": self.mt5.TIMEFRAME_M15,
                    "1hour": self.mt5.TIMEFRAME_H1,
                }
            elif DEVICE == "windows":
                timeframe_map = {
                    "1min": mt5.TIMEFRAME_M1,
                    "5min": mt5.TIMEFRAME_M5,
                    "15min": mt5.TIMEFRAME_M15,
                    "1hour": mt5.TIMEFRAME_H1,
                }
            else:
                return None
            
            mt5_timeframe = timeframe_map.get(timeframe)
            if mt5_timeframe is None:
                self.logger.error(f"Invalid timeframe: {timeframe}")
                return None
            
            # Get candles
            if DEVICE == "mac":
                rates = self.mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            elif DEVICE == "windows":
                rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            else:
                return None
            
            if rates is None or len(rates) == 0:
                self.logger.error(f"Failed to get candles for {symbol}")
                return None
            
            # Convert to list of dicts
            candles = []
            for rate in rates:
                candles.append({
                    "time": datetime.fromtimestamp(rate['time']),
                    "open": float(rate['open']),
                    "high": float(rate['high']),
                    "low": float(rate['low']),
                    "close": float(rate['close']),
                    "volume": int(rate['tick_volume']),
                })
            
            self.logger.debug(f"Retrieved {len(candles)} candles for {symbol}")
            return candles
        
        except Exception as e:
            self.logger.error(f"Error getting historical candles: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Get current bid/ask prices
        
        Args:
            symbol: Symbol name (broker-specific)
        
        Returns:
            Dict with bid, ask, spread or None if failed
        """
        if not self.verify_connection():
            self.logger.error("MT5 not connected")
            return None
        
        try:
            if DEVICE == "mac":
                tick = self.mt5.symbol_info_tick(symbol)
            elif DEVICE == "windows":
                tick = mt5.symbol_info_tick(symbol)
            else:
                return None
            
            if tick is None:
                self.logger.error(f"Failed to get tick for {symbol}")
                return None
            
            return {
                "bid": float(tick.bid),
                "ask": float(tick.ask),
                "spread": float(tick.ask - tick.bid),
                "time": datetime.fromtimestamp(tick.time),
            }
        
        except Exception as e:
            self.logger.error(f"Error getting current price: {e}")
            return None
    
    def get_account_info(self) -> Optional[Dict]:
        """
        Get account information
        
        Returns:
            Dict with balance, equity, margin, etc. or None if failed
        """
        if not self.verify_connection():
            self.logger.error("MT5 not connected")
            return None
        
        try:
            if DEVICE == "mac":
                account = self.mt5.account_info()
            elif DEVICE == "windows":
                account = mt5.account_info()
            else:
                return None
            
            if account is None:
                self.logger.error("Failed to get account info")
                return None
            
            return {
                "login": account.login,
                "balance": float(account.balance),
                "equity": float(account.equity),
                "margin": float(account.margin),
                "free_margin": float(account.margin_free),
                "profit": float(account.profit),
                "currency": account.currency,
                "server": account.server,
            }
        
        except Exception as e:
            self.logger.error(f"Error getting account info: {e}")
            return None
    
    def get_open_positions(self) -> List[Dict]:
        """
        Get all open positions
        
        Returns:
            List of position dictionaries
        """
        if not self.verify_connection():
            self.logger.error("MT5 not connected")
            return []
        
        try:
            if DEVICE == "mac":
                positions = self.mt5.positions_get()
            elif DEVICE == "windows":
                positions = mt5.positions_get()
            else:
                return []
            
            if positions is None:
                return []
            
            position_list = []
            for pos in positions:
                # Determine position type
                if DEVICE == "mac":
                    pos_type = "BUY" if pos.type == 0 else "SELL"
                elif DEVICE == "windows":
                    pos_type = "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL"
                else:
                    pos_type = "UNKNOWN"
                
                position_list.append({
                    "ticket": pos.ticket,
                    "symbol": pos.symbol,
                    "type": pos_type,
                    "volume": float(pos.volume),
                    "price_open": float(pos.price_open),
                    "price_current": float(pos.price_current),
                    "sl": float(pos.sl) if pos.sl > 0 else None,
                    "tp": float(pos.tp) if pos.tp > 0 else None,
                    "profit": float(pos.profit),
                    "time": datetime.fromtimestamp(pos.time),
                })
            
            return position_list
        
        except Exception as e:
            self.logger.error(f"Error getting open positions: {e}")
            return []


if __name__ == "__main__":
    # Test MT5 connection
    print(f"Testing MT5 Data Handler ({DEVICE})...")
    print(f"MT5 Library: {MT5_TYPE}")
    
    if not MT5_AVAILABLE:
        print(f"\n❌ MT5 library not available for {DEVICE}")
        if DEVICE == "mac":
            print("Install with: pip install siliconmetatrader5")
            print("\nSetup guide: docs/MT5_SETUP.md")
        elif DEVICE == "windows":
            print("Install with: pip install MetaTrader5")
    else:
        handler = MT5DataHandler()
        
        # Try to connect
        if handler.connect():
            print(f"\n✓ MT5 connected ({DEVICE})")
            
            # Get account info
            account = handler.get_account_info()
            if account:
                print(f"\nAccount Balance: ${account['balance']:.2f}")
                print(f"Server: {account['server']}")
            
            # Test with EURUSD
            print("\nTesting with EURUSD...")
            
            # Get current price
            price = handler.get_current_price("EURUSD")
            if price:
                print(f"Current Price: Bid={price['bid']:.5f}, Ask={price['ask']:.5f}")
            
            # Get historical candles
            candles = handler.get_historical_candles("EURUSD", count=10)
            if candles:
                print(f"Historical Candles: {len(candles)} candles retrieved")
                print(f"Latest: Close={candles[-1]['close']:.5f}")
            
            handler.disconnect()
            print("\n✓ MT5 test completed")
        else:
            print(f"\n❌ MT5 connection failed for {DEVICE}")
            if DEVICE == "mac":
                print("Make sure:")
                print("  1. MT5 bridge is running on localhost:8001")
                print("  2. MT5 terminal is open and logged in")
                print("\nSee docs/MT5_SETUP.md for setup instructions")
            elif DEVICE == "windows":
                print("Make sure:")
                print("  1. MT5 terminal is running and logged in")
                print("  2. Or provide login credentials to connect()")
