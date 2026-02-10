"""
Base MT5 executor for News Trading Bot V1.0

Reference: /docs/quantitative_thresholds.md Sections 6, 12
Last Updated: 2025-12-30

Purpose: Order placement, position monitoring, exit execution
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.logging.trade_logger import get_logger
from src.market.data import MT5DataHandler
from config.settings import MAX_TRADE_DURATION_MINUTES

# Try to import MT5
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False


class MT5Executor:
    """
    Base MT5 order executor
    
    Reference: quantitative_thresholds.md Sections 6, 12
    
    Features:
    - Market order placement with SL/TP
    - Position monitoring
    - Exit execution (SL, TP, time-based)
    - Slippage tracking
    - Partial fill handling
    """
    
    def __init__(self, mt5_handler: MT5DataHandler):
        """
        Initialize MT5 executor
        
        Args:
            mt5_handler: MT5 data handler instance
        """
        self.mt5 = mt5_handler
        self.logger = get_logger()
    
    def place_order(
        self,
        symbol: str,
        direction: str,
        volume: float,
        stop_loss: float,
        take_profit: float,
        comment: str = "",
    ) -> Optional[str]:
        """
        Place market order with SL and TP
        
        Args:
            symbol: Broker-specific symbol
            direction: "LONG" or "SHORT"
            volume: Position size in lots
            stop_loss: SL price
            take_profit: TP price
            comment: Order comment
        
        Returns:
            Position ticket ID or None if failed
        
        Reference:
            quantitative_thresholds.md Section 6
        """
        if not MT5_AVAILABLE:
            self.logger.error("MT5 not available")
            return None
        
        if not self.mt5.verify_connection():
            self.logger.error("MT5 not connected")
            return None
        
        # Determine order type
        if direction == "LONG":
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
        elif direction == "SHORT":
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
        else:
            self.logger.error(f"Invalid direction: {direction}")
            return None
        
        # Prepare request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 10,  # Max slippage in points
            "magic": 234000,  # Magic number for this bot
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send order
        result = mt5.order_send(request)
        
        if result is None:
            self.logger.error("Order send failed: result is None")
            return None
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.logger.error(f"Order failed: {result.retcode} - {result.comment}")
            return None
        
        # Log success
        self.logger.info(
            f"Order placed: {direction} {volume} lots {symbol} @ {result.price} "
            f"(SL: {stop_loss}, TP: {take_profit})"
        )
        
        # Check slippage
        requested_price = price
        actual_price = result.price
        slippage = abs(actual_price - requested_price)
        
        if slippage > 0:
            from src.core.risk_engine import RiskEngine
            risk_engine = RiskEngine()
            from config.instruments import get_internal_symbol
            internal_symbol = get_internal_symbol(symbol)
            if internal_symbol:
                risk_engine.check_slippage(internal_symbol, requested_price, actual_price)
        
        return str(result.order)
    
    def close_position(
        self,
        ticket: str,
        symbol: str,
        volume: float,
        direction: str,
    ) -> Optional[float]:
        """
        Close position at market price
        
        Args:
            ticket: Position ticket ID
            symbol: Broker-specific symbol
            volume: Position size
            direction: Original direction ("LONG" or "SHORT")
        
        Returns:
            Exit price or None if failed
        """
        if not MT5_AVAILABLE:
            self.logger.error("MT5 not available")
            return None
        
        if not self.mt5.verify_connection():
            self.logger.error("MT5 not connected")
            return None
        
        # Determine close order type (opposite of original)
        if direction == "LONG":
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
        elif direction == "SHORT":
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
        else:
            self.logger.error(f"Invalid direction: {direction}")
            return None
        
        # Prepare close request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "position": int(ticket),
            "price": price,
            "deviation": 10,
            "magic": 234000,
            "comment": "Close by bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send close order
        result = mt5.order_send(request)
        
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            self.logger.error(f"Position close failed: {result.comment if result else 'None'}")
            return None
        
        self.logger.info(f"Position {ticket} closed @ {result.price}")
        
        return result.price
    
    def monitor_position(
        self,
        ticket: str,
        entry_time: datetime,
    ) -> Optional[str]:
        """
        Monitor position for exit conditions
        
        Args:
            ticket: Position ticket ID
            entry_time: Position entry time
        
        Returns:
            Exit reason if position should be closed, None otherwise
        
        Reference:
            quantitative_thresholds.md Section 9 (Time Exit)
        """
        # Check if position still exists
        positions = self.mt5.get_open_positions()
        position_exists = any(p['ticket'] == int(ticket) for p in positions)
        
        if not position_exists:
            # Position already closed (SL or TP hit)
            return "SL_OR_TP"
        
        # Check time-based exit (15 minutes)
        time_elapsed = datetime.now() - entry_time
        if time_elapsed > timedelta(minutes=MAX_TRADE_DURATION_MINUTES):
            self.logger.info(
                f"Position {ticket} exceeded max duration ({MAX_TRADE_DURATION_MINUTES} min)"
            )
            return "TIME"
        
        return None


if __name__ == "__main__":
    print("MT5 Executor base class created")
    print("\nNOTE: This is a base class for order execution.")
    print("See dev.py and prod.py for development and production modes.")
