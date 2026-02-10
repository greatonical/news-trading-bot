"""
System state management for News Trading Bot V1.0

Reference: /docs/quantitative_thresholds.md Section 12
Last Updated: 2025-12-30

Purpose: Track system state, positions, P&L, persistence, recovery
"""

import json
from datetime import datetime, date
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.logging.trade_logger import get_logger
from config.risk_profiles import RiskMode


@dataclass
class Position:
    """Open position data"""
    ticket: str
    symbol: str
    direction: str  # "LONG" or "SHORT"
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float  # lots
    entry_time: datetime
    event_name: str
    risk_mode: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['entry_time'] = self.entry_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Position':
        """Create from dictionary"""
        data['entry_time'] = datetime.fromisoformat(data['entry_time'])
        return cls(**data)


class SystemState:
    """
    System state manager
    
    Reference: quantitative_thresholds.md Section 12
    
    Features:
    - Current risk mode tracking
    - Open positions tracking
    - Daily P&L calculation
    - Consecutive loss counter
    - System status (ACTIVE, PAUSED, EMERGENCY_STOP)
    - Persistence to JSON file
    - Recovery on startup
    """
    
    def __init__(self, state_file: str = "state/system_state.json"):
        """
        Initialize system state
        
        Args:
            state_file: Path to state persistence file
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = get_logger()
        
        # System status
        self.status: str = "ACTIVE"  # ACTIVE, PAUSED, EMERGENCY_STOP
        self.risk_mode: RiskMode = "LOW_RISK"
        
        # Positions
        self.open_positions: Dict[str, Position] = {}
        
        # Daily tracking
        self.current_date: date = date.today()
        self.daily_pnl: float = 0.0
        self.daily_trades: int = 0
        
        # Consecutive losses
        self.consecutive_losses: int = 0
        self.last_trade_result: Optional[str] = None  # "WIN", "LOSS", "BREAKEVEN"
        
        # Load persisted state if exists
        self.load_state()
    
    def set_status(self, new_status: str, reason: str = "") -> None:
        """
        Change system status
        
        Args:
            new_status: New status (ACTIVE, PAUSED, EMERGENCY_STOP)
            reason: Reason for status change
        
        Reference:
            quantitative_thresholds.md Section 12
        """
        old_status = self.status
        self.status = new_status
        
        self.logger.log_system_state_change(old_status, new_status, reason)
        self.save_state()
    
    def set_risk_mode(self, mode: RiskMode) -> None:
        """
        Set risk mode
        
        Args:
            mode: LOW_RISK or HIGH_RISK
        """
        self.risk_mode = mode
        self.logger.info(f"Risk mode set to: {mode}")
        self.save_state()
    
    def add_position(self, position: Position) -> None:
        """
        Add open position
        
        Args:
            position: Position object
        """
        self.open_positions[position.ticket] = position
        self.logger.log_position_update(
            action="OPEN",
            symbol=position.symbol,
            position_id=position.ticket,
            entry_price=position.entry_price,
        )
        self.save_state()
    
    def close_position(
        self,
        ticket: str,
        exit_price: float,
        pnl: float,
        exit_reason: str,
    ) -> None:
        """
        Close position and update P&L
        
        Args:
            ticket: Position ticket ID
            exit_price: Exit price
            pnl: Realized P&L
            exit_reason: Reason for exit (SL, TP, TIME, MANUAL)
        
        Reference:
            quantitative_thresholds.md Section 12
        """
        if ticket not in self.open_positions:
            self.logger.error(f"Position {ticket} not found in open positions")
            return
        
        position = self.open_positions[ticket]
        
        # Update daily P&L
        self.daily_pnl += pnl
        self.daily_trades += 1
        
        # Update consecutive losses
        if pnl < 0:
            self.last_trade_result = "LOSS"
            self.consecutive_losses += 1
        elif pnl > 0:
            self.last_trade_result = "WIN"
            self.consecutive_losses = 0  # Reset on win
        else:
            self.last_trade_result = "BREAKEVEN"
            # Don't reset or increment on breakeven
        
        # Log position close
        self.logger.log_position_update(
            action="CLOSE",
            symbol=position.symbol,
            position_id=ticket,
            exit_price=exit_price,
            pnl=pnl,
            exit_reason=exit_reason,
        )
        
        # Remove from open positions
        del self.open_positions[ticket]
        
        self.save_state()
    
    def reset_daily_stats(self) -> None:
        """
        Reset daily statistics (call at start of new trading day)
        
        Reference:
            quantitative_thresholds.md Section 4
        """
        self.current_date = date.today()
        self.daily_pnl = 0.0
        self.daily_trades = 0
        
        self.logger.info("Daily statistics reset")
        self.save_state()
    
    def check_new_day(self) -> None:
        """
        Check if it's a new trading day and reset if needed
        """
        if date.today() != self.current_date:
            self.logger.info("New trading day detected")
            self.reset_daily_stats()
    
    def get_positions_per_currency(self) -> Dict[str, int]:
        """
        Get position count per base currency
        
        Returns:
            Dict mapping currency to position count
        
        Reference:
            quantitative_thresholds.md Section 4
        """
        from config.instruments import get_base_currency
        
        positions_per_currency = {}
        
        for position in self.open_positions.values():
            currency = get_base_currency(position.symbol)
            positions_per_currency[currency] = positions_per_currency.get(currency, 0) + 1
        
        return positions_per_currency
    
    def save_state(self) -> None:
        """
        Save state to JSON file
        
        Reference:
            quantitative_thresholds.md Section 12
        """
        try:
            state_data = {
                "status": self.status,
                "risk_mode": self.risk_mode,
                "current_date": self.current_date.isoformat(),
                "daily_pnl": self.daily_pnl,
                "daily_trades": self.daily_trades,
                "consecutive_losses": self.consecutive_losses,
                "last_trade_result": self.last_trade_result,
                "open_positions": {
                    ticket: pos.to_dict()
                    for ticket, pos in self.open_positions.items()
                },
                "last_updated": datetime.now().isoformat(),
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            self.logger.debug(f"State saved to {self.state_file}")
        
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def load_state(self) -> bool:
        """
        Load state from JSON file
        
        Returns:
            True if loaded successfully, False otherwise
        
        Reference:
            quantitative_thresholds.md Section 12 (System Startup)
        """
        if not self.state_file.exists():
            self.logger.info("No saved state found, starting fresh")
            return False
        
        try:
            with open(self.state_file, 'r') as f:
                state_data = json.load(f)
            
            self.status = state_data.get("status", "ACTIVE")
            self.risk_mode = state_data.get("risk_mode", "LOW_RISK")
            self.current_date = date.fromisoformat(state_data.get("current_date", date.today().isoformat()))
            self.daily_pnl = state_data.get("daily_pnl", 0.0)
            self.daily_trades = state_data.get("daily_trades", 0)
            self.consecutive_losses = state_data.get("consecutive_losses", 0)
            self.last_trade_result = state_data.get("last_trade_result")
            
            # Load open positions
            self.open_positions = {}
            for ticket, pos_data in state_data.get("open_positions", {}).items():
                self.open_positions[ticket] = Position.from_dict(pos_data)
            
            self.logger.info(
                f"State loaded: status={self.status}, mode={self.risk_mode}, "
                f"daily_pnl=${self.daily_pnl:.2f}, open_positions={len(self.open_positions)}"
            )
            
            # Check if new day
            self.check_new_day()
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            return False
    
    def reconcile_with_mt5(self, mt5_positions: List[Dict]) -> None:
        """
        Reconcile internal state with MT5 positions
        
        Args:
            mt5_positions: List of position dicts from MT5
        
        Reference:
            quantitative_thresholds.md Section 12 (System Startup)
        
        Logic:
            1. Query MT5 for all open positions
            2. Load internal state from last saved checkpoint
            3. Reconcile: MT5 positions vs internal records
            4. If mismatch → log error, apply MT5 state as truth
        """
        mt5_tickets = {str(pos['ticket']) for pos in mt5_positions}
        internal_tickets = set(self.open_positions.keys())
        
        # Find mismatches
        only_in_mt5 = mt5_tickets - internal_tickets
        only_in_internal = internal_tickets - mt5_tickets
        
        if only_in_mt5:
            self.logger.warning(
                f"Positions in MT5 but not in internal state: {only_in_mt5}"
            )
            # MT5 is source of truth - these positions exist
            # In a full implementation, we'd add them to internal state
        
        if only_in_internal:
            self.logger.warning(
                f"Positions in internal state but not in MT5: {only_in_internal}"
            )
            # MT5 is source of truth - these positions don't exist
            for ticket in only_in_internal:
                self.logger.error(f"Removing orphaned position {ticket}")
                del self.open_positions[ticket]
        
        if only_in_mt5 or only_in_internal:
            self.logger.warning("State reconciliation completed, MT5 is source of truth")
            self.save_state()
        else:
            self.logger.info("State reconciliation: all positions match")


if __name__ == "__main__":
    # Test system state
    print("Testing System State...")
    
    state = SystemState(state_file="state/test_state.json")
    
    # Test 1: Add position
    print("\n=== Test 1: Add Position ===")
    position = Position(
        ticket="12345",
        symbol="EURUSD",
        direction="LONG",
        entry_price=1.0850,
        stop_loss=1.0825,
        take_profit=1.0900,
        position_size=0.1,
        entry_time=datetime.now(),
        event_name="US CPI",
        risk_mode="LOW_RISK",
    )
    state.add_position(position)
    print(f"Open positions: {len(state.open_positions)}")
    
    # Test 2: Close position with profit
    print("\n=== Test 2: Close Position (Win) ===")
    state.close_position(
        ticket="12345",
        exit_price=1.0900,
        pnl=50.0,
        exit_reason="TP",
    )
    print(f"Daily P&L: ${state.daily_pnl:.2f}")
    print(f"Consecutive losses: {state.consecutive_losses}")
    
    # Test 3: Add and close losing trade
    print("\n=== Test 3: Losing Trade ===")
    position2 = Position(
        ticket="12346",
        symbol="GBPUSD",
        direction="SHORT",
        entry_price=1.2700,
        stop_loss=1.2725,
        take_profit=1.2650,
        position_size=0.1,
        entry_time=datetime.now(),
        event_name="UK GDP",
        risk_mode="LOW_RISK",
    )
    state.add_position(position2)
    state.close_position(
        ticket="12346",
        exit_price=1.2725,
        pnl=-25.0,
        exit_reason="SL",
    )
    print(f"Daily P&L: ${state.daily_pnl:.2f}")
    print(f"Consecutive losses: {state.consecutive_losses}")
    
    # Test 4: State persistence
    print("\n=== Test 4: State Persistence ===")
    print(f"State file: {state.state_file}")
    
    # Create new state instance (should load from file)
    state2 = SystemState(state_file="state/test_state.json")
    print(f"Loaded daily P&L: ${state2.daily_pnl:.2f}")
    print(f"Loaded consecutive losses: {state2.consecutive_losses}")
    
    # Test 5: Position count per currency
    print("\n=== Test 5: Positions Per Currency ===")
    position3 = Position(
        ticket="12347",
        symbol="EURUSD",
        direction="LONG",
        entry_price=1.0860,
        stop_loss=1.0835,
        take_profit=1.0910,
        position_size=0.1,
        entry_time=datetime.now(),
        event_name="US NFP",
        risk_mode="LOW_RISK",
    )
    state.add_position(position3)
    
    positions_per_currency = state.get_positions_per_currency()
    print(f"Positions per currency: {positions_per_currency}")
    
    print("\n✓ System state test completed")
