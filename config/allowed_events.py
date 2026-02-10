"""
Whitelisted news events and deviation thresholds for News Trading Bot V1.0

All values extracted from: /docs/quantitative_thresholds.md Section 8
Last Updated: 2025-12-30
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class EventImpact(Enum):
    """Event impact classification"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class DeviationThreshold:
    """
    Deviation threshold for HIGH_RISK mode qualification
    
    Reference: quantitative_thresholds.md Section 8
    """
    event_name: str
    threshold_value: float
    threshold_unit: str  # "%", "K" (thousands), "bps" (basis points), "points"
    description: str
    
    def check_deviation(self, forecast: float, actual: float) -> bool:
        """
        Check if deviation meets threshold for HIGH_RISK qualification
        
        Args:
            forecast: Forecasted value
            actual: Actual released value
        
        Returns:
            True if deviation >= threshold, False otherwise
        
        Reference:
            quantitative_thresholds.md Section 8
        """
        deviation = abs(actual - forecast)
        return deviation >= self.threshold_value


# ============================================================================
# EVENT DEVIATION THRESHOLDS (Section 8)
# ============================================================================

# Purpose: Determine when news outcome is "significant enough" for HIGH_RISK execution
# These are conservative, institutional-grade significance levels

DEVIATION_THRESHOLDS: Dict[str, DeviationThreshold] = {
    # US Events
    "US_CPI_YOY": DeviationThreshold(
        event_name="US CPI (YoY)",
        threshold_value=0.3,
        threshold_unit="%",
        description="Forecast 3.2%, actual ≥3.5% or ≤2.9%"
    ),
    "US_CORE_CPI_YOY": DeviationThreshold(
        event_name="US Core CPI (YoY)",
        threshold_value=0.3,
        threshold_unit="%",
        description="Forecast 3.0%, actual ≥3.3% or ≤2.7%"
    ),
    "US_NFP": DeviationThreshold(
        event_name="US Non-Farm Payrolls",
        threshold_value=50.0,
        threshold_unit="K",
        description="Forecast 200K, actual ≥250K or ≤150K"
    ),
    "US_UNEMPLOYMENT_RATE": DeviationThreshold(
        event_name="US Unemployment Rate",
        threshold_value=0.2,
        threshold_unit="%",
        description="Forecast 4.1%, actual ≥4.3% or ≤3.9%"
    ),
    "US_FED_INTEREST_RATE": DeviationThreshold(
        event_name="US Federal Funds Rate",
        threshold_value=25.0,
        threshold_unit="bps",
        description="±25 bps OR qualitative statement shift"
    ),
    "US_GDP_QOQ": DeviationThreshold(
        event_name="US GDP (QoQ)",
        threshold_value=0.5,
        threshold_unit="%",
        description="Forecast 2.5%, actual ≥3.0% or ≤2.0%"
    ),
    "US_RETAIL_SALES": DeviationThreshold(
        event_name="US Retail Sales",
        threshold_value=0.4,
        threshold_unit="%",
        description="Forecast 0.5%, actual ≥0.9% or ≤0.1%"
    ),
    "US_PMI_MANUFACTURING": DeviationThreshold(
        event_name="US PMI Manufacturing",
        threshold_value=2.0,
        threshold_unit="points",
        description="Forecast 51.0, actual ≥53.0 or ≤49.0"
    ),
    "US_TRADE_BALANCE": DeviationThreshold(
        event_name="US Trade Balance",
        threshold_value=5.0,
        threshold_unit="$B",
        description="Forecast -$60B, actual ≥-$55B or ≤-$65B"
    ),
    "US_INITIAL_JOBLESS_CLAIMS": DeviationThreshold(
        event_name="US Initial Jobless Claims",
        threshold_value=20.0,
        threshold_unit="K",
        description="Forecast 220K, actual ≥240K or ≤200K"
    ),
    
    # UK Events
    "UK_CPI_YOY": DeviationThreshold(
        event_name="UK CPI (YoY)",
        threshold_value=0.3,
        threshold_unit="%",
        description="Similar to US CPI threshold"
    ),
    "UK_GDP_QOQ": DeviationThreshold(
        event_name="UK GDP (QoQ)",
        threshold_value=0.5,
        threshold_unit="%",
        description="Similar to US GDP threshold"
    ),
    "UK_BOE_INTEREST_RATE": DeviationThreshold(
        event_name="UK Bank of England Rate",
        threshold_value=25.0,
        threshold_unit="bps",
        description="±25 bps OR qualitative statement shift"
    ),
    
    # EU Events
    "EU_CPI_YOY": DeviationThreshold(
        event_name="EU CPI (YoY)",
        threshold_value=0.3,
        threshold_unit="%",
        description="Similar to US CPI threshold"
    ),
    "EU_GDP_QOQ": DeviationThreshold(
        event_name="EU GDP (QoQ)",
        threshold_value=0.5,
        threshold_unit="%",
        description="Similar to US GDP threshold"
    ),
    "EU_ECB_INTEREST_RATE": DeviationThreshold(
        event_name="EU ECB Interest Rate",
        threshold_value=25.0,
        threshold_unit="bps",
        description="±25 bps OR qualitative statement shift"
    ),
}


# ============================================================================
# EVENT TO CURRENCY MAPPING
# ============================================================================

# Maps event categories to affected currencies
EVENT_CURRENCY_MAP: Dict[str, str] = {
    # US Events
    "US_CPI_YOY": "USD",
    "US_CORE_CPI_YOY": "USD",
    "US_NFP": "USD",
    "US_UNEMPLOYMENT_RATE": "USD",
    "US_FED_INTEREST_RATE": "USD",
    "US_GDP_QOQ": "USD",
    "US_RETAIL_SALES": "USD",
    "US_PMI_MANUFACTURING": "USD",
    "US_TRADE_BALANCE": "USD",
    "US_INITIAL_JOBLESS_CLAIMS": "USD",
    
    # UK Events
    "UK_CPI_YOY": "GBP",
    "UK_GDP_QOQ": "GBP",
    "UK_BOE_INTEREST_RATE": "GBP",
    
    # EU Events
    "EU_CPI_YOY": "EUR",
    "EU_GDP_QOQ": "EUR",
    "EU_ECB_INTEREST_RATE": "EUR",
}


# ============================================================================
# EVENT TO ASSET MAPPING (Multi-Asset Support)
# ============================================================================

# Maps events to tradeable assets
# These are pre-mapped sets - NO dynamic discovery allowed in V1.0
EVENT_ASSET_MAP: Dict[str, List[str]] = {
    # US Events (USD-based)
    "US_CPI_YOY": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"],
    "US_CORE_CPI_YOY": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"],
    "US_NFP": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "NAS100", "US30"],
    "US_UNEMPLOYMENT_RATE": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"],
    "US_FED_INTEREST_RATE": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "NAS100", "US30"],
    "US_GDP_QOQ": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "NAS100", "US30"],
    "US_RETAIL_SALES": ["EURUSD", "GBPUSD", "USDJPY", "NAS100", "US30"],
    "US_PMI_MANUFACTURING": ["EURUSD", "USDJPY", "NAS100"],
    "US_TRADE_BALANCE": ["EURUSD", "USDJPY"],
    "US_INITIAL_JOBLESS_CLAIMS": ["EURUSD", "USDJPY"],
    
    # UK Events (GBP-based)
    "UK_CPI_YOY": ["GBPUSD", "EURGBP"],
    "UK_GDP_QOQ": ["GBPUSD", "EURGBP"],
    "UK_BOE_INTEREST_RATE": ["GBPUSD", "EURGBP"],
    
    # EU Events (EUR-based)
    "EU_CPI_YOY": ["EURUSD", "EURGBP"],
    "EU_GDP_QOQ": ["EURUSD", "EURGBP"],
    "EU_ECB_INTEREST_RATE": ["EURUSD", "EURGBP"],
}


# ============================================================================
# FOREXFACTORY EVENT NAME MAPPING
# ============================================================================

# Maps ForexFactory event names to our internal event codes
# ForexFactory uses inconsistent naming, this normalizes them
FOREXFACTORY_EVENT_MAP: Dict[str, str] = {
    # US Events
    "CPI y/y": "US_CPI_YOY",
    "Core CPI y/y": "US_CORE_CPI_YOY",
    "Non-Farm Employment Change": "US_NFP",
    "Unemployment Rate": "US_UNEMPLOYMENT_RATE",
    "Federal Funds Rate": "US_FED_INTEREST_RATE",
    "FOMC Statement": "US_FED_INTEREST_RATE",
    "GDP q/q": "US_GDP_QOQ",
    "Retail Sales m/m": "US_RETAIL_SALES",
    "Manufacturing PMI": "US_PMI_MANUFACTURING",
    "Trade Balance": "US_TRADE_BALANCE",
    "Initial Jobless Claims": "US_INITIAL_JOBLESS_CLAIMS",
    
    # UK Events
    "CPI y/y (UK)": "UK_CPI_YOY",
    "GDP q/q (UK)": "UK_GDP_QOQ",
    "Official Bank Rate": "UK_BOE_INTEREST_RATE",
    "MPC Rate Statement": "UK_BOE_INTEREST_RATE",
    
    # EU Events
    "CPI y/y (EU)": "EU_CPI_YOY",
    "GDP q/q (EU)": "EU_GDP_QOQ",
    "Main Refinancing Rate": "EU_ECB_INTEREST_RATE",
    "ECB Press Conference": "EU_ECB_INTEREST_RATE",
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_event_code(forexfactory_name: str, currency: str) -> Optional[str]:
    """
    Convert ForexFactory event name to internal event code
    
    Args:
        forexfactory_name: Event name from ForexFactory
        currency: Currency code (USD, GBP, EUR)
    
    Returns:
        Internal event code or None if not whitelisted
    
    Example:
        >>> get_event_code("CPI y/y", "USD")
        "US_CPI_YOY"
    """
    # Try direct mapping first
    if forexfactory_name in FOREXFACTORY_EVENT_MAP:
        return FOREXFACTORY_EVENT_MAP[forexfactory_name]
    
    # Try with currency suffix
    key_with_currency = f"{forexfactory_name} ({currency})"
    if key_with_currency in FOREXFACTORY_EVENT_MAP:
        return FOREXFACTORY_EVENT_MAP[key_with_currency]
    
    return None


def is_event_whitelisted(event_code: str) -> bool:
    """
    Check if event is whitelisted for trading
    
    Args:
        event_code: Internal event code
    
    Returns:
        True if event is whitelisted, False otherwise
    """
    return event_code in DEVIATION_THRESHOLDS


def get_mapped_assets(event_code: str) -> List[str]:
    """
    Get list of assets mapped to this event
    
    Args:
        event_code: Internal event code
    
    Returns:
        List of asset symbols, empty list if event not mapped
    
    Reference:
        quantitative_thresholds.md Section 7 (Multi-Asset)
    """
    return EVENT_ASSET_MAP.get(event_code, [])


# ============================================================================
# VALIDATION
# ============================================================================

def validate_allowed_events() -> bool:
    """
    Validate event configurations
    
    Returns:
        True if all configurations are valid
    
    Raises:
        AssertionError: If any configuration is invalid
    """
    # Ensure all events have deviation thresholds
    for event_code in EVENT_CURRENCY_MAP.keys():
        assert event_code in DEVIATION_THRESHOLDS, \
            f"Event {event_code} missing deviation threshold"
    
    # Ensure all events have asset mappings
    for event_code in EVENT_CURRENCY_MAP.keys():
        assert event_code in EVENT_ASSET_MAP, \
            f"Event {event_code} missing asset mapping"
    
    # Ensure all mapped events point to valid internal codes
    for ff_name, event_code in FOREXFACTORY_EVENT_MAP.items():
        assert event_code in DEVIATION_THRESHOLDS, \
            f"ForexFactory mapping '{ff_name}' points to invalid event code '{event_code}'"
    
    return True


if __name__ == "__main__":
    # Run validation
    validate_allowed_events()
    print("✓ All event configurations validated")
    
    # Show summary
    print(f"\nWhitelisted events: {len(DEVIATION_THRESHOLDS)}")
    print(f"ForexFactory mappings: {len(FOREXFACTORY_EVENT_MAP)}")
    
    # Test example
    event_code = get_event_code("CPI y/y", "USD")
    if event_code:
        threshold = DEVIATION_THRESHOLDS[event_code]
        assets = get_mapped_assets(event_code)
        print(f"\nExample: {threshold.event_name}")
        print(f"  Threshold: ±{threshold.threshold_value}{threshold.threshold_unit}")
        print(f"  Mapped assets: {', '.join(assets)}")
