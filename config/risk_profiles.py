"""
Risk profiles and limits for News Trading Bot V1.0

All values extracted from: /docs/quantitative_thresholds.md Section 4
Last Updated: 2025-12-30
"""

from typing import Dict, Literal
from dataclasses import dataclass

# ============================================================================
# RISK MODES (Section 4)
# ============================================================================

RiskMode = Literal["LOW_RISK", "HIGH_RISK"]


@dataclass
class RiskProfile:
    """
    Risk profile configuration for a trading mode
    
    Reference: quantitative_thresholds.md Section 4
    """
    mode: RiskMode
    risk_per_trade_percent: float  # Percentage of account balance
    description: str
    requires_volatility_confirmation: bool
    requires_direction_confirmation: bool
    requires_deviation_threshold: bool
    auto_revert_after_trade: bool


# ============================================================================
# RISK PROFILES
# ============================================================================

LOW_RISK_PROFILE = RiskProfile(
    mode="LOW_RISK",
    risk_per_trade_percent=1.0,  # 1.0% of account balance
    description="Default mode - requires volatility spike + direction confirmation",
    requires_volatility_confirmation=True,
    requires_direction_confirmation=True,
    requires_deviation_threshold=False,
    auto_revert_after_trade=False,
)

HIGH_RISK_PROFILE = RiskProfile(
    mode="HIGH_RISK",
    risk_per_trade_percent=0.5,  # 0.5% of account balance (reduced due to execution risk)
    description="Immediate execution on significant deviation from forecast",
    requires_volatility_confirmation=False,  # Immediate execution
    requires_direction_confirmation=False,   # Immediate execution
    requires_deviation_threshold=True,       # Must meet deviation threshold
    auto_revert_after_trade=True,            # Auto-revert to LOW_RISK after one trade
)

# Map mode names to profiles
RISK_PROFILES: Dict[RiskMode, RiskProfile] = {
    "LOW_RISK": LOW_RISK_PROFILE,
    "HIGH_RISK": HIGH_RISK_PROFILE,
}

# ============================================================================
# GLOBAL RISK LIMITS (Section 4)
# ============================================================================

# Daily risk limit
DAILY_LOSS_LIMIT_PERCENT: float = 3.0  # 3.0% of account balance
# Action: System stops trading until next day (manual override required)

# Consecutive loss protection
MAX_CONSECUTIVE_LOSSES: int = 3  # 3 trades in a row hitting stop loss
# Action: System pauses, requires manual review before resuming
# Purpose: Detect broken logic or adverse market regime

# Position limits
MAX_OPEN_POSITIONS_TOTAL: int = 3  # Maximum 3 open positions at any time
MAX_POSITIONS_PER_BASE_CURRENCY: int = 2  # Max 2 positions per base currency
# Example: Can't have EURUSD + EURGBP + EURJPY simultaneously

# Multi-asset limits (Section 5)
MAX_ASSETS_PER_EVENT: int = 3  # Hard limit, only if multi-asset enabled

# ============================================================================
# MULTI-ASSET RISK ALLOCATION (Section 5)
# ============================================================================

# Aggregate risk cap per event
MULTI_ASSET_AGGREGATE_RISK: Dict[RiskMode, float] = {
    "LOW_RISK": 1.0,   # 1.0% total risk per event
    "HIGH_RISK": 0.5,  # 0.5% total risk per event
}

# Distribution rule: Divided evenly across selected assets
# Formula: risk_per_asset = total_event_risk / num_selected_assets


def calculate_multi_asset_risk(
    mode: RiskMode,
    num_assets: int
) -> float:
    """
    Calculate risk per asset in multi-asset mode
    
    Args:
        mode: Risk mode (LOW_RISK or HIGH_RISK)
        num_assets: Number of assets selected for this event (1-3)
    
    Returns:
        Risk percentage per asset
    
    Raises:
        ValueError: If num_assets > MAX_ASSETS_PER_EVENT
    
    Reference:
        quantitative_thresholds.md Section 5
    
    Example:
        >>> calculate_multi_asset_risk("LOW_RISK", 2)
        0.5  # 1.0% / 2 assets = 0.5% per asset
    """
    if num_assets > MAX_ASSETS_PER_EVENT:
        raise ValueError(
            f"Cannot select {num_assets} assets. "
            f"Maximum is {MAX_ASSETS_PER_EVENT} per event."
        )
    
    if num_assets < 1:
        raise ValueError("Must select at least 1 asset")
    
    total_event_risk = MULTI_ASSET_AGGREGATE_RISK[mode]
    risk_per_asset = total_event_risk / num_assets
    
    return risk_per_asset


# ============================================================================
# RISK VALIDATION
# ============================================================================

def validate_risk_limits(
    account_balance: float,
    daily_pnl: float,
    consecutive_losses: int,
    open_positions: int,
    positions_per_currency: Dict[str, int],
) -> tuple[bool, str]:
    """
    Validate all risk limits before allowing a trade
    
    Args:
        account_balance: Current MT5 account balance
        daily_pnl: Cumulative realized P&L for today (negative = loss)
        consecutive_losses: Number of consecutive losing trades
        open_positions: Current number of open positions
        positions_per_currency: Dict mapping base currency to position count
    
    Returns:
        Tuple of (is_valid, reason_code)
        - is_valid: True if all limits pass, False otherwise
        - reason_code: Reason code if rejected (e.g., "NO_TRADE_004")
    
    Reference:
        quantitative_thresholds.md Section 4
    """
    # Check daily loss limit
    daily_loss_percent = abs(daily_pnl / account_balance * 100)
    if daily_pnl < 0 and daily_loss_percent >= DAILY_LOSS_LIMIT_PERCENT:
        return False, "NO_TRADE_004"  # Daily loss limit reached
    
    # Check consecutive losses
    if consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
        return False, "NO_TRADE_005"  # Consecutive loss limit reached
    
    # Check total position limit
    if open_positions >= MAX_OPEN_POSITIONS_TOTAL:
        return False, "NO_TRADE_007"  # Position limit reached
    
    # Check per-currency position limit
    for currency, count in positions_per_currency.items():
        if count >= MAX_POSITIONS_PER_BASE_CURRENCY:
            return False, "NO_TRADE_007"  # Position limit reached
    
    return True, ""


# ============================================================================
# VALIDATION
# ============================================================================

def validate_risk_profiles() -> bool:
    """
    Validate risk profiles against quantitative_thresholds.md
    
    Returns:
        True if all profiles are valid
    
    Raises:
        AssertionError: If any profile parameter is incorrect
    """
    # LOW_RISK checks
    assert LOW_RISK_PROFILE.risk_per_trade_percent == 1.0, \
        "LOW_RISK per-trade risk must be 1.0%"
    
    # HIGH_RISK checks
    assert HIGH_RISK_PROFILE.risk_per_trade_percent == 0.5, \
        "HIGH_RISK per-trade risk must be 0.5%"
    
    # Global limits
    assert DAILY_LOSS_LIMIT_PERCENT == 3.0, \
        "Daily loss limit must be 3.0%"
    assert MAX_CONSECUTIVE_LOSSES == 3, \
        "Consecutive loss limit must be 3"
    assert MAX_OPEN_POSITIONS_TOTAL == 3, \
        "Max open positions must be 3"
    assert MAX_POSITIONS_PER_BASE_CURRENCY == 2, \
        "Max positions per currency must be 2"
    assert MAX_ASSETS_PER_EVENT == 3, \
        "Max assets per event must be 3"
    
    # Multi-asset checks
    assert MULTI_ASSET_AGGREGATE_RISK["LOW_RISK"] == 1.0, \
        "LOW_RISK aggregate risk must be 1.0%"
    assert MULTI_ASSET_AGGREGATE_RISK["HIGH_RISK"] == 0.5, \
        "HIGH_RISK aggregate risk must be 0.5%"
    
    return True


if __name__ == "__main__":
    # Run validation
    validate_risk_profiles()
    print("✓ All risk profiles validated against quantitative_thresholds.md")
    
    # Test multi-asset calculation
    print("\nMulti-asset risk allocation examples:")
    print(f"LOW_RISK, 2 assets: {calculate_multi_asset_risk('LOW_RISK', 2):.3f}% per asset")
    print(f"HIGH_RISK, 3 assets: {calculate_multi_asset_risk('HIGH_RISK', 3):.3f}% per asset")
