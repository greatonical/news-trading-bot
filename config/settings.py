"""
Configuration settings for News Trading Bot V1.0

Reference: /docs/quantitative_thresholds.md All Sections
Last Updated: 2025-12-31

Purpose: System-wide constants and thresholds
"""

import platform
from typing import Dict
import os

# ============================================================================
# DEVICE CONFIGURATION
# ============================================================================
# Auto-detect operating system for MT5 library selection
# Reference: Cross-platform compatibility
#
# Options:
#   "mac" - Use siliconmetatrader5 (requires bridge on localhost:8001)
#   "windows" - Use MetaTrader5 (official library, direct connection)
#
# Auto-detection based on platform.system():
#   - Darwin (macOS) → "mac"
#   - Windows → "windows"
#   - Linux → "windows" (uses official MT5 library)

_system = platform.system()
if _system == "Darwin":
    DEVICE = "mac"
elif _system == "Windows":
    DEVICE = "windows"
else:
    # Linux and others use official MT5 library
    DEVICE = "windows"

# MT5 Bridge Configuration (for macOS only)
MT5_BRIDGE_HOST = "localhost"
MT5_BRIDGE_PORT = 8001

# ============================================================================
# VOLATILITY DETECTION (Section 1)
# ============================================================================

# Purpose: Detect abnormal market reaction to news events
# Reference: quantitative_thresholds.md Section 1

VOLATILITY_LOOKBACK_PERIOD: int = 60  # minutes (60 candles on 1-min chart)
VOLATILITY_THRESHOLD_MULTIPLIER: float = 2.0  # Current range must be >= 2.0× average
VOLATILITY_TIMEFRAME: str = "1min"  # 1-minute candles exclusively

# ============================================================================
# DIRECTION CONFIRMATION (Section 2)
# ============================================================================

# Purpose: Avoid first-candle fakeouts
# Reference: quantitative_thresholds.md Section 2

DIRECTION_CONFIRMATION_THRESHOLD: float = 0.5  # 50% of reaction candle range
# Next candle must close in upper/lower 50% of reaction range

# ============================================================================
# SPREAD GUARDS (Section 3)
# ============================================================================

# Purpose: Avoid execution during abnormal liquidity conditions
# Reference: quantitative_thresholds.md Section 3

SPREAD_AVERAGING_PERIOD: int = 60  # minutes
SPREAD_THRESHOLD_MULTIPLIER: float = 3.0  # Current spread must be <= 3.0× average

# Absolute spread limits per asset (pips/points/cents)
# Emergency override - if exceeded, NO TRADE regardless of average
ABSOLUTE_SPREAD_LIMITS: Dict[str, float] = {
    "EURUSD": 5.0,   # pips, typical: 0.5-1.5
    "GBPUSD": 6.0,   # pips, typical: 1.0-2.0
    "USDJPY": 5.0,   # pips, typical: 0.5-1.5
    "XAUUSD": 100.0, # cents, typical: 20-40
    "NAS100": 5.0,   # points, typical: 1.0-2.0
    "US30": 8.0,     # points, typical: 2.0-4.0
}

# ============================================================================
# TIME-BASED RULES (Section 9)
# ============================================================================

# News window: Period during which LOW_RISK mode monitors for reactions
NEWS_WINDOW_START_OFFSET: int = -1  # minutes before scheduled release
NEWS_WINDOW_END_OFFSET: int = 15    # minutes after scheduled release

# Maximum trade duration
MAX_TRADE_DURATION_MINUTES: int = 15  # Force close if still open after 15 min

# High-Risk mode auto-revert
HIGH_RISK_AUTO_REVERT_MINUTES: int = 5  # Auto-revert 5 min after news release

# ============================================================================
# POSITION SIZE CALCULATION (Section 6)
# ============================================================================

# Stop Loss and Take Profit multipliers
STOP_LOSS_MULTIPLIER: float = 1.5   # SL = 1.5× reaction candle range
TAKE_PROFIT_MULTIPLIER: float = 2.0  # TP = 2.0× SL distance (1:2 R:R minimum)

# ============================================================================
# RECOVERY & EDGE CASES (Section 12)
# ============================================================================

# Connection loss handling
MAX_RECONNECTION_ATTEMPTS: int = 3
RECONNECTION_DELAY_SECONDS: int = 5

# Slippage thresholds (warning only, trade already executed)
MAX_ACCEPTABLE_SLIPPAGE: Dict[str, float] = {
    "majors": 3.0,   # pips (EURUSD, GBPUSD, USDJPY)
    "crosses": 5.0,  # pips (EURGBP, EURJPY, etc.)
    "gold": 50.0,    # cents (XAUUSD)
    "indices": 5.0,  # points (NAS100, US30)
}

# ============================================================================
# DATA SOURCES (Section 15)
# ============================================================================

# ForexFactory scraping
FOREXFACTORY_URL: str = "https://www.forexfactory.com/calendar"
FOREXFACTORY_RATE_LIMIT_SECONDS: int = 60  # Max 1 request per minute
FOREXFACTORY_CACHE_MINUTES: int = 30
FOREXFACTORY_CACHE_INVALIDATE_BEFORE_EVENT_MINUTES: int = 5

# Government sites scraping
GOVERNMENT_SITES_RATE_LIMIT_SECONDS: int = 30  # Max 1 request per 30 seconds
GOVERNMENT_SITES_CACHE_HOURS: int = 24

# Government site URLs
GOVERNMENT_SITES: Dict[str, str] = {
    "BLS": "https://www.bls.gov",  # US: CPI, NFP, Unemployment
    "FED": "https://www.federalreserve.gov",  # US: Interest rates
    "ONS": "https://www.ons.gov.uk",  # UK: CPI, GDP, Employment
    "EUROSTAT": "https://ec.europa.eu/eurostat",  # EU: CPI, GDP
}

# Network settings
HTTP_TIMEOUT_SECONDS: int = 10
HTTP_MAX_RETRIES: int = 3
HTTP_RETRY_DELAY_SECONDS: int = 5

# User-Agent for web scraping
USER_AGENT: str = "NewsBot/1.0 (Educational Automated Trading System)"

# ============================================================================
# MT5 SETTINGS
# ============================================================================

# MT5 connection settings
MT5_TIMEOUT_SECONDS: int = 10
MT5_POLL_INTERVAL_SECONDS: int = 1  # Poll prices every 1 second during news window

# Historical data
MT5_HISTORICAL_CANDLES: int = 60  # Fetch last 60 × 1-min candles

# ============================================================================
# LOGGING (Section 11)
# ============================================================================

# Log levels
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Log file settings
LOG_DIR: str = "logs"
LOG_FILE_PREFIX: str = "news_trading_bot"
LOG_ROTATION: str = "daily"  # Rotate logs daily
LOG_TIMESTAMP_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"  # Millisecond precision

# Reason codes for logging
REASON_CODES: Dict[str, str] = {
    # Trade executed
    "TRADE_001": "Volatility + direction confirmed (LOW_RISK)",
    "TRADE_002": "Deviation threshold met (HIGH_RISK)",
    
    # Trade rejected
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

# ============================================================================
# SYSTEM STATE
# ============================================================================

# State persistence
STATE_FILE: str = "state/system_state.json"
STATE_SAVE_AFTER_TRADE: bool = True

# System modes
SYSTEM_MODES = ["ACTIVE", "PAUSED", "EMERGENCY_STOP"]

# ============================================================================
# DEVELOPMENT / PRODUCTION
# ============================================================================

# Execution mode
EXECUTION_MODE: str = os.getenv("EXECUTION_MODE", "dev")  # "dev" or "prod"

# Development mode settings
DEV_MODE_PAPER_TRADING: bool = True
DEV_MODE_LOG_ALL_DECISIONS: bool = True

# Production mode settings
PROD_MODE_REQUIRE_CONFIRMATION: bool = True  # Require explicit user confirmation

# ============================================================================
# VALIDATION
# ============================================================================

def validate_settings() -> bool:
    """
    Validate all settings against quantitative_thresholds.md
    
    Returns:
        True if all settings are valid, False otherwise
    
    Raises:
        ValueError: If any critical setting is invalid
    """
    # Volatility checks
    assert VOLATILITY_THRESHOLD_MULTIPLIER == 2.0, "Volatility multiplier must be 2.0"
    assert VOLATILITY_LOOKBACK_PERIOD == 60, "Lookback period must be 60 minutes"
    
    # Direction checks
    assert DIRECTION_CONFIRMATION_THRESHOLD == 0.5, "Direction threshold must be 50%"
    
    # Spread checks
    assert SPREAD_THRESHOLD_MULTIPLIER == 3.0, "Spread multiplier must be 3.0"
    
    # Exit checks
    assert STOP_LOSS_MULTIPLIER == 1.5, "SL multiplier must be 1.5"
    assert TAKE_PROFIT_MULTIPLIER == 2.0, "TP multiplier must be 2.0"
    
    # Time checks
    assert MAX_TRADE_DURATION_MINUTES == 15, "Max trade duration must be 15 minutes"
    
    return True


if __name__ == "__main__":
    # Run validation on import
    validate_settings()
    print("✓ All settings validated against quantitative_thresholds.md")
