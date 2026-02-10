"""
Asset definitions and broker-specific mappings for News Trading Bot V1.0

All values extracted from: /docs/quantitative_thresholds.md Section 10
Last Updated: 2025-12-30
"""

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class AssetType(Enum):
    """Asset classification"""
    FOREX_MAJOR = "forex_major"
    FOREX_CROSS = "forex_cross"
    COMMODITY = "commodity"
    INDEX = "index"


@dataclass
class AssetDefinition:
    """
    Complete asset definition with broker mappings
    
    Reference: quantitative_thresholds.md Section 10
    """
    internal_symbol: str
    asset_type: AssetType
    base_currency: str
    quote_currency: str
    standard_lot_size: float
    pip_value_usd: float  # Per standard lot
    pip_size: float  # Minimum price increment
    absolute_spread_limit: float  # From Section 3
    typical_spread_range: str  # For reference
    description: str
    
    # Broker-specific symbol mappings
    broker_symbols: Dict[str, str]


# ============================================================================
# ASSET DEFINITIONS (Section 10)
# ============================================================================

ASSETS: Dict[str, AssetDefinition] = {
    # ========== FOREX MAJORS ==========
    "EURUSD": AssetDefinition(
        internal_symbol="EURUSD",
        asset_type=AssetType.FOREX_MAJOR,
        base_currency="EUR",
        quote_currency="USD",
        standard_lot_size=100000,
        pip_value_usd=10.0,
        pip_size=0.0001,
        absolute_spread_limit=5.0,  # pips
        typical_spread_range="0.5-1.5 pips",
        description="Euro vs US Dollar",
        broker_symbols={
            "default": "EURUSD",
            "oanda": "EUR_USD",
            "fxcm": "EUR/USD",
        }
    ),
    
    "GBPUSD": AssetDefinition(
        internal_symbol="GBPUSD",
        asset_type=AssetType.FOREX_MAJOR,
        base_currency="GBP",
        quote_currency="USD",
        standard_lot_size=100000,
        pip_value_usd=10.0,
        pip_size=0.0001,
        absolute_spread_limit=6.0,  # pips
        typical_spread_range="1.0-2.0 pips",
        description="British Pound vs US Dollar",
        broker_symbols={
            "default": "GBPUSD",
            "oanda": "GBP_USD",
            "fxcm": "GBP/USD",
        }
    ),
    
    "USDJPY": AssetDefinition(
        internal_symbol="USDJPY",
        asset_type=AssetType.FOREX_MAJOR,
        base_currency="USD",
        quote_currency="JPY",
        standard_lot_size=100000,
        pip_value_usd=9.17,  # Approximate, varies with JPY rate
        pip_size=0.01,
        absolute_spread_limit=5.0,  # pips
        typical_spread_range="0.5-1.5 pips",
        description="US Dollar vs Japanese Yen",
        broker_symbols={
            "default": "USDJPY",
            "oanda": "USD_JPY",
            "fxcm": "USD/JPY",
        }
    ),
    
    # ========== FOREX CROSSES ==========
    "EURGBP": AssetDefinition(
        internal_symbol="EURGBP",
        asset_type=AssetType.FOREX_CROSS,
        base_currency="EUR",
        quote_currency="GBP",
        standard_lot_size=100000,
        pip_value_usd=12.5,  # Approximate
        pip_size=0.0001,
        absolute_spread_limit=6.0,  # pips
        typical_spread_range="1.5-2.5 pips",
        description="Euro vs British Pound",
        broker_symbols={
            "default": "EURGBP",
            "oanda": "EUR_GBP",
            "fxcm": "EUR/GBP",
        }
    ),
    
    "EURJPY": AssetDefinition(
        internal_symbol="EURJPY",
        asset_type=AssetType.FOREX_CROSS,
        base_currency="EUR",
        quote_currency="JPY",
        standard_lot_size=100000,
        pip_value_usd=9.17,  # Approximate
        pip_size=0.01,
        absolute_spread_limit=6.0,  # pips
        typical_spread_range="1.5-2.5 pips",
        description="Euro vs Japanese Yen",
        broker_symbols={
            "default": "EURJPY",
            "oanda": "EUR_JPY",
            "fxcm": "EUR/JPY",
        }
    ),
    
    # ========== COMMODITIES ==========
    "XAUUSD": AssetDefinition(
        internal_symbol="XAUUSD",
        asset_type=AssetType.COMMODITY,
        base_currency="XAU",  # Gold
        quote_currency="USD",
        standard_lot_size=100,  # 100 oz
        pip_value_usd=10.0,  # Per 0.10 move
        pip_size=0.01,  # $0.01
        absolute_spread_limit=100.0,  # cents
        typical_spread_range="20-40 cents",
        description="Gold vs US Dollar",
        broker_symbols={
            "default": "XAUUSD",
            "oanda": "XAU_USD",
            "fxcm": "XAU/USD",
            "alternative": "GOLD",
        }
    ),
    
    # ========== INDICES ==========
    "NAS100": AssetDefinition(
        internal_symbol="NAS100",
        asset_type=AssetType.INDEX,
        base_currency="USD",
        quote_currency="USD",
        standard_lot_size=1,  # 1 contract
        pip_value_usd=1.0,  # Per 1.0 point
        pip_size=1.0,
        absolute_spread_limit=5.0,  # points
        typical_spread_range="1.0-2.0 points",
        description="NASDAQ 100 Index",
        broker_symbols={
            "default": "NAS100",
            "alternative1": "US100",
            "alternative2": "USTEC",
            "oanda": "NAS100_USD",
        }
    ),
    
    "US30": AssetDefinition(
        internal_symbol="US30",
        asset_type=AssetType.INDEX,
        base_currency="USD",
        quote_currency="USD",
        standard_lot_size=1,  # 1 contract
        pip_value_usd=1.0,  # Per 1.0 point
        pip_size=1.0,
        absolute_spread_limit=8.0,  # points
        typical_spread_range="2.0-4.0 points",
        description="Dow Jones Industrial Average",
        broker_symbols={
            "default": "US30",
            "alternative1": "DJ30",
            "alternative2": "DJIA",
            "oanda": "US30_USD",
        }
    ),
}


# ============================================================================
# BROKER CONFIGURATIONS
# ============================================================================

# Supported brokers
SUPPORTED_BROKERS = ["default", "oanda", "fxcm"]

# Current broker (set via environment variable or config)
import os
CURRENT_BROKER = os.getenv("MT5_BROKER", "default")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_broker_symbol(internal_symbol: str, broker: Optional[str] = None) -> str:
    """
    Get broker-specific symbol name
    
    Args:
        internal_symbol: Internal symbol (e.g., "EURUSD")
        broker: Broker name (default: use CURRENT_BROKER)
    
    Returns:
        Broker-specific symbol name
    
    Raises:
        KeyError: If symbol not found
        ValueError: If broker not supported
    
    Example:
        >>> get_broker_symbol("EURUSD", "oanda")
        "EUR_USD"
    """
    if broker is None:
        broker = CURRENT_BROKER
    
    if internal_symbol not in ASSETS:
        raise KeyError(f"Unknown asset: {internal_symbol}")
    
    asset = ASSETS[internal_symbol]
    
    # Try exact broker match
    if broker in asset.broker_symbols:
        return asset.broker_symbols[broker]
    
    # Fallback to default
    return asset.broker_symbols.get("default", internal_symbol)


def get_internal_symbol(broker_symbol: str, broker: Optional[str] = None) -> Optional[str]:
    """
    Reverse lookup: broker symbol → internal symbol
    
    Args:
        broker_symbol: Broker-specific symbol
        broker: Broker name (default: use CURRENT_BROKER)
    
    Returns:
        Internal symbol or None if not found
    
    Example:
        >>> get_internal_symbol("EUR_USD", "oanda")
        "EURUSD"
    """
    if broker is None:
        broker = CURRENT_BROKER
    
    for internal_symbol, asset in ASSETS.items():
        if broker in asset.broker_symbols:
            if asset.broker_symbols[broker] == broker_symbol:
                return internal_symbol
        # Also check default
        if asset.broker_symbols.get("default") == broker_symbol:
            return internal_symbol
    
    return None


def get_pip_value(internal_symbol: str) -> float:
    """
    Get pip value in USD for position sizing
    
    Args:
        internal_symbol: Internal symbol
    
    Returns:
        Pip value in USD per standard lot
    
    Reference:
        quantitative_thresholds.md Section 10
    """
    if internal_symbol not in ASSETS:
        raise KeyError(f"Unknown asset: {internal_symbol}")
    
    return ASSETS[internal_symbol].pip_value_usd


def get_base_currency(internal_symbol: str) -> str:
    """
    Get base currency for position limit tracking
    
    Args:
        internal_symbol: Internal symbol
    
    Returns:
        Base currency code (e.g., "EUR", "USD", "GBP")
    
    Example:
        >>> get_base_currency("EURUSD")
        "EUR"
    """
    if internal_symbol not in ASSETS:
        raise KeyError(f"Unknown asset: {internal_symbol}")
    
    return ASSETS[internal_symbol].base_currency


def get_absolute_spread_limit(internal_symbol: str) -> float:
    """
    Get absolute spread limit for this asset
    
    Args:
        internal_symbol: Internal symbol
    
    Returns:
        Absolute spread limit (pips/points/cents)
    
    Reference:
        quantitative_thresholds.md Section 3
    """
    if internal_symbol not in ASSETS:
        raise KeyError(f"Unknown asset: {internal_symbol}")
    
    return ASSETS[internal_symbol].absolute_spread_limit


def get_slippage_category(internal_symbol: str) -> str:
    """
    Get slippage category for this asset
    
    Args:
        internal_symbol: Internal symbol
    
    Returns:
        Slippage category: "majors", "crosses", "gold", or "indices"
    
    Reference:
        quantitative_thresholds.md Section 12
    """
    if internal_symbol not in ASSETS:
        raise KeyError(f"Unknown asset: {internal_symbol}")
    
    asset = ASSETS[internal_symbol]
    
    if asset.asset_type == AssetType.FOREX_MAJOR:
        return "majors"
    elif asset.asset_type == AssetType.FOREX_CROSS:
        return "crosses"
    elif asset.asset_type == AssetType.COMMODITY:
        return "gold"
    elif asset.asset_type == AssetType.INDEX:
        return "indices"
    
    return "majors"  # Default fallback


# ============================================================================
# VALIDATION
# ============================================================================

def validate_instruments() -> bool:
    """
    Validate instrument configurations
    
    Returns:
        True if all configurations are valid
    
    Raises:
        AssertionError: If any configuration is invalid
    """
    # Check all assets have required fields
    for symbol, asset in ASSETS.items():
        assert asset.internal_symbol == symbol, \
            f"Internal symbol mismatch for {symbol}"
        assert asset.standard_lot_size > 0, \
            f"Invalid lot size for {symbol}"
        assert asset.pip_value_usd > 0, \
            f"Invalid pip value for {symbol}"
        assert asset.absolute_spread_limit > 0, \
            f"Invalid spread limit for {symbol}"
        assert "default" in asset.broker_symbols, \
            f"Missing default broker symbol for {symbol}"
    
    # Verify pip values match Section 10
    assert ASSETS["EURUSD"].pip_value_usd == 10.0
    assert ASSETS["GBPUSD"].pip_value_usd == 10.0
    assert ASSETS["XAUUSD"].pip_value_usd == 10.0
    assert ASSETS["NAS100"].pip_value_usd == 1.0
    assert ASSETS["US30"].pip_value_usd == 1.0
    
    # Verify spread limits match Section 3
    assert ASSETS["EURUSD"].absolute_spread_limit == 5.0
    assert ASSETS["GBPUSD"].absolute_spread_limit == 6.0
    assert ASSETS["USDJPY"].absolute_spread_limit == 5.0
    assert ASSETS["XAUUSD"].absolute_spread_limit == 100.0
    assert ASSETS["NAS100"].absolute_spread_limit == 5.0
    assert ASSETS["US30"].absolute_spread_limit == 8.0
    
    return True


if __name__ == "__main__":
    # Run validation
    validate_instruments()
    print("✓ All instrument configurations validated")
    
    # Show summary
    print(f"\nConfigured assets: {len(ASSETS)}")
    print(f"Current broker: {CURRENT_BROKER}")
    
    # Test broker mapping
    print("\nBroker symbol mappings (OANDA):")
    for symbol in ["EURUSD", "GBPUSD", "XAUUSD"]:
        broker_sym = get_broker_symbol(symbol, "oanda")
        print(f"  {symbol} → {broker_sym}")
