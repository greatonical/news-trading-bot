"""
Configuration package for News Trading Bot V1.0

Exports all configuration modules for easy importing
"""

from .settings import *
from .risk_profiles import *
from .allowed_events import *
from .instruments import *

__all__ = [
    # Settings
    "VOLATILITY_LOOKBACK_PERIOD",
    "VOLATILITY_THRESHOLD_MULTIPLIER",
    "DIRECTION_CONFIRMATION_THRESHOLD",
    "SPREAD_THRESHOLD_MULTIPLIER",
    "ABSOLUTE_SPREAD_LIMITS",
    "NEWS_WINDOW_START_OFFSET",
    "NEWS_WINDOW_END_OFFSET",
    "MAX_TRADE_DURATION_MINUTES",
    "STOP_LOSS_MULTIPLIER",
    "TAKE_PROFIT_MULTIPLIER",
    "REASON_CODES",
    
    # Risk Profiles
    "RiskMode",
    "RiskProfile",
    "LOW_RISK_PROFILE",
    "HIGH_RISK_PROFILE",
    "RISK_PROFILES",
    "DAILY_LOSS_LIMIT_PERCENT",
    "MAX_CONSECUTIVE_LOSSES",
    "MAX_OPEN_POSITIONS_TOTAL",
    "MAX_POSITIONS_PER_BASE_CURRENCY",
    "MAX_ASSETS_PER_EVENT",
    "calculate_multi_asset_risk",
    "validate_risk_limits",
    
    # Allowed Events
    "EventImpact",
    "DeviationThreshold",
    "DEVIATION_THRESHOLDS",
    "EVENT_CURRENCY_MAP",
    "EVENT_ASSET_MAP",
    "get_event_code",
    "is_event_whitelisted",
    "get_mapped_assets",
    
    # Instruments
    "AssetType",
    "AssetDefinition",
    "ASSETS",
    "get_broker_symbol",
    "get_internal_symbol",
    "get_pip_value",
    "get_base_currency",
    "get_absolute_spread_limit",
    "get_slippage_category",
]
