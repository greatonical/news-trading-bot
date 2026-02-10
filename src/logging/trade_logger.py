"""
Structured logging system for News Trading Bot V1.0

All logging requirements from: /docs/quantitative_thresholds.md Section 11
Last Updated: 2025-12-30
"""

import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TradeLogger:
    """
    Structured logging for all trading decisions and actions
    
    Reference: quantitative_thresholds.md Section 11
    
    Every decision must be explainable and reproducible through logs.
    """
    
    def __init__(
        self,
        log_dir: str = "logs",
        log_level: str = "INFO",
        console_output: bool = True,
        file_output: bool = True,
    ):
        """
        Initialize trade logger
        
        Args:
            log_dir: Directory for log files
            log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            console_output: Enable console logging
            file_output: Enable file logging
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("NewsTrading Bot")
        self.logger.setLevel(getattr(logging, log_level))
        self.logger.handlers = []  # Clear any existing handlers
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, log_level))
            console_formatter = logging.Formatter(
                '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # File handler (JSON lines format)
        if file_output:
            log_file = self.log_dir / f"trading_{datetime.now().strftime('%Y%m%d')}.jsonl"
            file_handler = logging.FileHandler(log_file, mode='a')
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file
            self.logger.addHandler(file_handler)
            
            self.json_log_file = log_file
        else:
            self.json_log_file = None
    
    def _log_json(self, data: Dict[str, Any]) -> None:
        """
        Log structured data as JSON line
        
        Args:
            data: Dictionary to log
        """
        if self.json_log_file:
            with open(self.json_log_file, 'a') as f:
                json.dump(data, f)
                f.write('\n')
    
    def log_decision(
        self,
        event_name: str,
        scheduled_time: datetime,
        risk_mode: str,
        assets_evaluated: list[str],
        volatility_measurement: Dict[str, float],
        direction_confirmed: bool,
        deviation_from_forecast: Optional[float],
        risk_calculations: Dict[str, float],
        entry_price: Optional[float],
        exit_prices: Optional[Dict[str, float]],
        spread_at_execution: Optional[float],
        position_size: Optional[float],
        reason_code: str,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a trading decision with all mandatory fields
        
        Reference: quantitative_thresholds.md Section 11
        
        Args:
            event_name: Name of news event
            scheduled_time: Scheduled event time
            risk_mode: LOW_RISK or HIGH_RISK
            assets_evaluated: List of assets considered
            volatility_measurement: Dict with current_range, avg_range, multiplier
            direction_confirmed: True if direction confirmation passed
            deviation_from_forecast: Deviation value (HIGH_RISK mode only)
            risk_calculations: Dict with account_balance, risk_percent, position_size
            entry_price: Entry price if trade executed
            exit_prices: Dict with stop_loss and take_profit prices
            spread_at_execution: Spread in pips/points at execution time
            position_size: Position size in lots
            reason_code: Reason code (TRADE_001, NO_TRADE_003, etc.)
            additional_context: Any additional context to log
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "timestamp_ms": datetime.now().timestamp() * 1000,  # Millisecond precision
            "event_name": event_name,
            "scheduled_time": scheduled_time.isoformat(),
            "risk_mode": risk_mode,
            "assets_evaluated": assets_evaluated,
            "volatility": {
                "current_range": volatility_measurement.get("current_range"),
                "avg_range": volatility_measurement.get("avg_range"),
                "multiplier": volatility_measurement.get("multiplier"),
                "threshold_met": volatility_measurement.get("threshold_met", False),
            },
            "direction_confirmed": direction_confirmed,
            "deviation_from_forecast": deviation_from_forecast,
            "risk_calculations": risk_calculations,
            "execution": {
                "entry_price": entry_price,
                "stop_loss": exit_prices.get("stop_loss") if exit_prices else None,
                "take_profit": exit_prices.get("take_profit") if exit_prices else None,
                "spread": spread_at_execution,
                "position_size": position_size,
            },
            "reason_code": reason_code,
            "reason_description": self._get_reason_description(reason_code),
        }
        
        if additional_context:
            log_entry["additional_context"] = additional_context
        
        # Log to JSON file
        self._log_json(log_entry)
        
        # Log to console
        if reason_code.startswith("TRADE_"):
            self.logger.info(
                f"TRADE EXECUTED | {event_name} | {reason_code} | "
                f"Entry: {entry_price} | Size: {position_size} lots"
            )
        else:
            self.logger.info(
                f"TRADE REJECTED | {event_name} | {reason_code} | "
                f"{self._get_reason_description(reason_code)}"
            )
    
    def log_event_detected(
        self,
        event_name: str,
        scheduled_time: datetime,
        currency: str,
        impact: str,
        forecast: Optional[float],
        previous: Optional[float],
    ) -> None:
        """
        Log when a high-impact event is detected
        
        Args:
            event_name: Name of event
            scheduled_time: Scheduled time
            currency: Affected currency
            impact: Impact level (high/medium/low)
            forecast: Forecasted value
            previous: Previous value
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "EVENT_DETECTED",
            "event_name": event_name,
            "scheduled_time": scheduled_time.isoformat(),
            "currency": currency,
            "impact": impact,
            "forecast": forecast,
            "previous": previous,
        }
        
        self._log_json(log_entry)
        self.logger.info(
            f"EVENT DETECTED | {event_name} | {scheduled_time.strftime('%Y-%m-%d %H:%M')} | "
            f"{currency} | Impact: {impact}"
        )
    
    def log_data_source_error(
        self,
        source: str,
        error_type: str,
        error_message: str,
        retry_attempt: Optional[int] = None,
    ) -> None:
        """
        Log data source failures
        
        Args:
            source: Data source name (ForexFactory, BLS, MT5, etc.)
            error_type: Type of error (connection, parsing, timeout, etc.)
            error_message: Detailed error message
            retry_attempt: Current retry attempt number
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "DATA_SOURCE_ERROR",
            "source": source,
            "error_type": error_type,
            "error_message": error_message,
            "retry_attempt": retry_attempt,
        }
        
        self._log_json(log_entry)
        
        if retry_attempt:
            self.logger.warning(
                f"DATA SOURCE ERROR | {source} | {error_type} | "
                f"Retry {retry_attempt} | {error_message}"
            )
        else:
            self.logger.error(
                f"DATA SOURCE ERROR | {source} | {error_type} | {error_message}"
            )
    
    def log_system_state_change(
        self,
        old_state: str,
        new_state: str,
        reason: str,
    ) -> None:
        """
        Log system state changes
        
        Args:
            old_state: Previous state (ACTIVE, PAUSED, EMERGENCY_STOP)
            new_state: New state
            reason: Reason for state change
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "STATE_CHANGE",
            "old_state": old_state,
            "new_state": new_state,
            "reason": reason,
        }
        
        self._log_json(log_entry)
        self.logger.warning(
            f"STATE CHANGE | {old_state} → {new_state} | {reason}"
        )
    
    def log_position_update(
        self,
        action: str,
        symbol: str,
        position_id: Optional[str] = None,
        entry_price: Optional[float] = None,
        exit_price: Optional[float] = None,
        pnl: Optional[float] = None,
        exit_reason: Optional[str] = None,
    ) -> None:
        """
        Log position lifecycle events
        
        Args:
            action: OPEN, CLOSE, UPDATE
            symbol: Asset symbol
            position_id: MT5 position ID
            entry_price: Entry price
            exit_price: Exit price (for CLOSE)
            pnl: Realized P&L (for CLOSE)
            exit_reason: Reason for exit (SL, TP, TIME, MANUAL)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "POSITION_UPDATE",
            "action": action,
            "symbol": symbol,
            "position_id": position_id,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "pnl": pnl,
            "exit_reason": exit_reason,
        }
        
        self._log_json(log_entry)
        
        if action == "OPEN":
            self.logger.info(f"POSITION OPENED | {symbol} | Entry: {entry_price}")
        elif action == "CLOSE":
            self.logger.info(
                f"POSITION CLOSED | {symbol} | Exit: {exit_price} | "
                f"P&L: {pnl:.2f} | Reason: {exit_reason}"
            )
    
    def _get_reason_description(self, reason_code: str) -> str:
        """
        Get human-readable description for reason code
        
        Args:
            reason_code: Reason code (e.g., TRADE_001)
        
        Returns:
            Description string
        """
        # Try to import REASON_CODES
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from config.settings import REASON_CODES
        except ImportError:
            # Fallback reason codes if config not available
            REASON_CODES = {
                "TRADE_001": "Volatility + direction confirmed (LOW_RISK)",
                "TRADE_002": "Deviation threshold met (HIGH_RISK)",
                "NO_TRADE_001": "Insufficient volatility",
                "NO_TRADE_002": "Direction not confirmed",
                "NO_TRADE_003": "Spread too wide",
                "NO_TRADE_004": "Daily loss limit reached",
                "NO_TRADE_005": "Consecutive loss limit reached",
                "NO_TRADE_006": "Deviation below threshold (HIGH_RISK abort)",
                "NO_TRADE_007": "Position limit reached",
                "NO_TRADE_008": "System paused",
                "NO_TRADE_009": "MT5 connection failed",
                "NO_TRADE_010": "Data source unavailable",
            }
        return REASON_CODES.get(reason_code, "Unknown reason code")
    
    def info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(message)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        self.logger.debug(message)


# Global logger instance
_global_logger: Optional[TradeLogger] = None


def get_logger() -> TradeLogger:
    """
    Get global logger instance
    
    Returns:
        TradeLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = TradeLogger()
    return _global_logger


def initialize_logger(
    log_dir: str = "logs",
    log_level: str = "INFO",
    console_output: bool = True,
    file_output: bool = True,
) -> TradeLogger:
    """
    Initialize global logger with custom settings
    
    Args:
        log_dir: Directory for log files
        log_level: Minimum log level
        console_output: Enable console logging
        file_output: Enable file logging
    
    Returns:
        TradeLogger instance
    """
    global _global_logger
    _global_logger = TradeLogger(log_dir, log_level, console_output, file_output)
    return _global_logger


if __name__ == "__main__":
    # Test logging
    logger = initialize_logger(log_level="DEBUG")
    
    logger.info("Trade logger initialized")
    
    # Test event detection
    logger.log_event_detected(
        event_name="US CPI y/y",
        scheduled_time=datetime.now(),
        currency="USD",
        impact="high",
        forecast=3.2,
        previous=3.1,
    )
    
    # Test decision logging
    logger.log_decision(
        event_name="US CPI y/y",
        scheduled_time=datetime.now(),
        risk_mode="LOW_RISK",
        assets_evaluated=["EURUSD", "XAUUSD"],
        volatility_measurement={
            "current_range": 15.5,
            "avg_range": 7.2,
            "multiplier": 2.15,
            "threshold_met": True,
        },
        direction_confirmed=True,
        deviation_from_forecast=None,
        risk_calculations={
            "account_balance": 10000.0,
            "risk_percent": 1.0,
            "risk_amount": 100.0,
        },
        entry_price=1.0850,
        exit_prices={"stop_loss": 1.0835, "take_profit": 1.0880},
        spread_at_execution=1.2,
        position_size=0.1,
        reason_code="TRADE_001",
    )
    
    print("\n✓ Trade logger test completed")
    print(f"Log file: {logger.json_log_file}")
